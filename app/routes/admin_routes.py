from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app import db
from app.models.user import User
from app.models.loan import Loan
from app.models.document import Document
from app.models.payment import Payment
from app.models.notification import Notification
from datetime import datetime
from app.services.email_service import (
    send_loan_approved_email,
    send_loan_rejected_email,
    send_payment_received_email,
    send_loan_completed_email,
    send_document_status_email
)

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/', methods=['GET'])
@login_required
def admin_dashboard():
    """Retrieve administrative metrics and display all loan applications."""
    # 1. Total Loans Issued (Sum of all approved/completed/overdue loans)
    total_loans_amount = db.session.query(db.func.sum(Loan.loan_amount)).filter(
        Loan.status.in_(["approved", "completed", "overdue"])
    ).scalar() or 0.0

    # 2. Total Repayments
    total_repayments = db.session.query(db.func.sum(Payment.amount_paid)).scalar() or 0.0

    # 3. Outstanding Balances (approved and overdue loans)
    outstanding_balances = db.session.query(db.func.sum(Loan.remaining_balance)).filter(
        Loan.status.in_(["approved", "overdue"])
    ).scalar() or 0.0

    # 4. Active Borrowers (approved and overdue loans)
    active_borrowers = db.session.query(Loan.user_id).filter(
        Loan.status.in_(["approved", "overdue"])
    ).distinct().count()

    # 5. Overdue Loans
    overdue_count = Loan.query.filter_by(status="overdue").count()

    # 6. Completed Loans
    completed_count = Loan.query.filter_by(status="completed").count()

    # 7. Pending Approvals
    pending_approvals = Loan.query.filter_by(status="pending").count()

    # 8. Total Users
    total_users = User.query.count()

    # 9. Monthly Repayment Totals (MySQL query using date_format)
    # Group payments by month, e.g. 'YYYY-MM'
    repayments_by_month = db.session.query(
        db.func.date_format(Payment.payment_date, '%Y-%m').label('month'),
        db.func.sum(Payment.amount_paid).label('total')
    ).group_by('month').order_by('month').all()

    monthly_labels = [str(r.month) for r in repayments_by_month]
    monthly_data = [float(r.total) for r in repayments_by_month]

    # 10. Loan Status Distribution
    status_distribution = db.session.query(
        Loan.status,
        db.func.count(Loan.id)
    ).group_by(Loan.status).all()

    status_labels = [str(s[0]) for s in status_distribution]
    status_data = [int(s[1]) for s in status_distribution]

    # Load loans along with user details
    loans = Loan.query.order_by(Loan.id.desc()).all()
    loans_with_users = []
    for loan in loans:
        user = User.query.get(loan.user_id)
        loans_with_users.append({
            'loan': loan,
            'user': user
        })

    return render_template(
        "admin/dashboard.html",
        loans_with_users=loans_with_users,
        stats={
            "total_loans_issued": float(total_loans_amount),
            "total_repayments": float(total_repayments),
            "outstanding_balances": float(outstanding_balances),
            "active_borrowers": active_borrowers,
            "overdue_count": overdue_count,
            "completed_count": completed_count,
            "pending_approvals": pending_approvals,
            "total_users": total_users,
            "monthly_labels": monthly_labels,
            "monthly_data": monthly_data,
            "status_labels": status_labels,
            "status_data": status_data
        }
    )

@admin_bp.route('/approve-loan/<int:loan_id>', methods=['GET', 'POST'])
@login_required
def approve_loan(loan_id):
    """Approve a pending loan application."""
    loan = Loan.query.get_or_404(loan_id)
    
    # Validation: Prevent loan approval if critical KYC documents are missing or rejected
    if loan.user.kyc_status != "Verified":
        flash(f"Cannot approve loan #{loan.id}. Customer KYC status is '{loan.user.kyc_status}'. Critical KYC documents (National ID and Payslip) must be approved first.", "danger")
        return redirect(url_for('admin.admin_dashboard'))
        
    loan.status = "approved"
    loan.remaining_balance = loan.loan_amount
    
    # Create notification for client
    notification = Notification(
        user_id=loan.user_id,
        message=f"Your loan application #{loan.id} of ${loan.loan_amount:,.2f} has been approved.",
        notification_date=datetime.now().date(),
        status="unread"
    )
    db.session.add(notification)
    db.session.commit()
    
    # Send email
    send_loan_approved_email(loan.user, loan)
    
    flash(f"Loan #{loan.id} for amount ${loan.loan_amount:,.2f} has been APPROVED successfully!", "success")
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/reject-loan/<int:loan_id>', methods=['GET', 'POST'])
@login_required
def reject_loan(loan_id):
    """Reject a pending loan application."""
    loan = Loan.query.get_or_404(loan_id)
    loan.status = "rejected"
    
    # Create notification for client
    notification = Notification(
        user_id=loan.user_id,
        message=f"Your loan application #{loan.id} has been rejected.",
        notification_date=datetime.now().date(),
        status="unread"
    )
    db.session.add(notification)
    db.session.commit()
    
    # Send email
    send_loan_rejected_email(loan.user, loan)
    
    flash(f"Loan #{loan.id} for amount ${loan.loan_amount:,.2f} has been REJECTED.", "danger")
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/customer/<int:user_id>', methods=['GET'])
@login_required
def customer_details(user_id):
    """Show specific customer profile, documents list, and loan history."""
    customer = User.query.get_or_404(user_id)
    documents = Document.query.filter_by(user_id=user_id).all()
    loans = Loan.query.filter_by(user_id=user_id).order_by(Loan.id.desc()).all()
    
    # Fetch all payments for all loans belonging to this customer
    loan_ids = [l.id for l in loans]
    payments = []
    if loan_ids:
        payments = Payment.query.filter(Payment.loan_id.in_(loan_ids)).order_by(Payment.payment_date.desc()).all()
    
    return render_template(
        "admin/customer_details.html",
        customer=customer,
        documents=documents,
        loans=loans,
        payments=payments
    )

@admin_bp.route('/add-payment/<int:loan_id>', methods=['POST'])
@login_required
def add_payment(loan_id):
    """Record a payment for an approved loan."""
    loan = Loan.query.get_or_404(loan_id)
    
    # Validation: Prevent payments on non-approved loans
    if loan.status != "approved":
        flash("Payments can only be recorded for approved loans.", "danger")
        return redirect(url_for('admin.admin_dashboard'))
        
    try:
        amount_val = request.form.get("amount")
        if not amount_val:
            flash("Payment amount is required.", "danger")
            return redirect(url_for('admin.admin_dashboard'))
            
        amount = float(amount_val)
    except ValueError:
        flash("Invalid payment amount.", "danger")
        return redirect(url_for('admin.admin_dashboard'))
        
    # Validation: Prevent negative or zero payments
    if amount <= 0:
        flash("Payment amount must be greater than zero.", "danger")
        return redirect(url_for('admin.admin_dashboard'))
        
    # Validation: Prevent payments greater than remaining balance
    # If remaining_balance is None, initialize it to the loan_amount
    if loan.remaining_balance is None:
        loan.remaining_balance = loan.loan_amount
        
    if amount > float(loan.remaining_balance):
        flash(f"Payment amount cannot exceed the remaining balance of ${loan.remaining_balance:,.2f}.", "danger")
        return redirect(url_for('admin.admin_dashboard'))
        
    # Process payment
    new_balance = float(loan.remaining_balance) - amount
    if new_balance <= 0:
        loan.remaining_balance = 0.0
        loan.status = "completed"
        flash_msg = f"Payment of ${amount:,.2f} recorded successfully. Loan #{loan.id} is now fully repaid and completed!"
        flash_category = "success"
    else:
        loan.remaining_balance = new_balance
        flash_msg = f"Payment of ${amount:,.2f} recorded successfully. Remaining balance: ${loan.remaining_balance:,.2f}."
        flash_category = "success"
        
    # Record payment entry
    payment = Payment(
        loan_id=loan.id,
        amount_paid=amount,
        payment_date=datetime.now()
    )
    db.session.add(payment)
    
    # Create notification for payment received
    notif = Notification(
        user_id=loan.user_id,
        message=f"A payment of ${amount:,.2f} has been received for loan #{loan.id}.",
        notification_date=datetime.now().date(),
        status="unread"
    )
    db.session.add(notif)
    
    # Send payment email
    send_payment_received_email(loan.user, loan, amount)
    
    if new_balance <= 0:
        # Create notification for loan completed
        notif2 = Notification(
            user_id=loan.user_id,
            message=f"Your loan #{loan.id} has been fully repaid.",
            notification_date=datetime.now().date(),
            status="unread"
        )
        db.session.add(notif2)
        
        # Send loan completed email
        send_loan_completed_email(loan.user, loan)
        
    db.session.commit()
    
    flash(flash_msg, flash_category)
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/documents', methods=['GET'])
@login_required
def documents_list():
    """List all uploaded customer verification documents."""
    documents = Document.query.order_by(Document.id.desc()).all()
    docs_with_users = []
    for doc in documents:
        user = User.query.get(doc.user_id)
        docs_with_users.append({
            'doc': doc,
            'user': user
        })
    return render_template("admin/documents.html", docs_with_users=docs_with_users)

@admin_bp.route('/approve-document/<int:document_id>', methods=['GET', 'POST'])
@login_required
def approve_document(document_id):
    """Approve an uploaded verification document."""
    doc = Document.query.get_or_404(document_id)
    doc.verification_status = "approved"
    doc.verified_at = datetime.now()
    doc.rejection_reason = None
    
    user = User.query.get(doc.user_id)
    if user:
        # Create notification for customer
        notification = Notification(
            user_id=user.id,
            message=f"Your verification document ({doc.document_type}) has been approved.",
            notification_date=datetime.now().date(),
            status="unread"
        )
        db.session.add(notification)
        db.session.commit()
        # Send email
        send_document_status_email(user, doc)
        
    flash(f"Document #{doc.id} ({doc.document_type}) has been approved successfully.", "success")
    return redirect(url_for('admin.documents_list'))

@admin_bp.route('/reject-document/<int:document_id>', methods=['GET', 'POST'])
@login_required
def reject_document(document_id):
    """Reject an uploaded verification document with a reason."""
    doc = Document.query.get_or_404(document_id)
    user = User.query.get(doc.user_id)
    
    if request.method == "POST":
        reason = request.form.get("rejection_reason", "Document does not meet verification requirements.")
        doc.verification_status = "rejected"
        doc.verified_at = datetime.now()
        doc.rejection_reason = reason
        
        if user:
            # Create notification for customer
            notification = Notification(
                user_id=user.id,
                message=f"Your verification document ({doc.document_type}) has been rejected. Reason: {reason}",
                notification_date=datetime.now().date(),
                status="unread"
            )
            db.session.add(notification)
            db.session.commit()
            # Send email
            send_document_status_email(user, doc)
            
        flash(f"Document #{doc.id} ({doc.document_type}) has been rejected.", "danger")
        return redirect(url_for('admin.documents_list'))
        
    return render_template("admin/reject_document.html", doc=doc, user=user)
