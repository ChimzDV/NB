import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app import db
from app.models.document import Document
from app.models.loan import Loan

main = Blueprint("main", __name__)

@main.route("/")
def home():
    return redirect(url_for("auth.login"))

@main.route("/dashboard")
@login_required
def dashboard():

    loan_count = Loan.query.filter_by(
        user_id=current_user.id
    ).count()

    return render_template(
        "dashboard/dashboard.html",
        user=current_user,
        loan_count=loan_count
    )

@main.route("/upload-document", methods=["GET", "POST"])
@login_required
def upload_document():

    if request.method == "GET":
        return render_template(
            "dashboard/upload_documents.html"
        )

    file = request.files["document"]

    filename = file.filename

    upload_path = os.path.join(
        current_app.config["UPLOAD_FOLDER"],
        filename
    )

    # Ensure upload directory exists
    os.makedirs(os.path.dirname(upload_path), exist_ok=True)
    file.save(upload_path)

    document = Document(
        user_id=current_user.id,
        document_type=request.form["document_type"],
        file_name=filename,
        file_path=upload_path
    )

    db.session.add(document)
    db.session.commit()

    flash("Document Uploaded Successfully!", "success")
    return redirect(url_for("main.my_documents"))

@main.route("/my-documents")
@login_required
def my_documents():

    documents = Document.query.filter_by(
        user_id=current_user.id
    ).all()

    return render_template(
        "dashboard/my_documents.html",
        documents=documents
    )        

@main.route("/my-loans")
@login_required
def my_loans():
    loans = Loan.query.filter_by(
        user_id=current_user.id
    ).all()
    return render_template(
        "dashboard/my_loans.html",
        loans=loans
    )

@main.route("/apply-loan", methods=["GET", "POST"])
@login_required
def apply_loan():

    if request.method == "GET":
        return render_template(
            "dashboard/apply_loan.html"
        )

    loan_amount = float(
        request.form["loan_amount"]
    )

    loan = Loan(
        user_id=current_user.id,
        loan_amount=loan_amount,
        purpose=request.form["purpose"],
        total_amount=loan_amount,
        remaining_balance=loan_amount,
        due_date=request.form["due_date"]
    )

    db.session.add(loan)
    db.session.commit()

    flash("Loan Application Submitted Successfully!", "success")
    return redirect(url_for("main.my_loans"))

@main.app_context_processor
def inject_unread_notifications_count():
    from app.models.notification import Notification
    if current_user.is_authenticated:
        try:
            count = Notification.query.filter_by(user_id=current_user.id, status="unread").count()
            return dict(unread_notifications_count=count)
        except Exception:
            return dict(unread_notifications_count=0)
    return dict(unread_notifications_count=0)

@main.route("/notifications")
@login_required
def notifications():
    from app.models.notification import Notification
    unread = Notification.query.filter_by(user_id=current_user.id, status="unread").all()
    for n in unread:
        n.status = "read"
    db.session.commit()
    
    all_notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.id.desc()).all()
    return render_template("dashboard/notifications.html", notifications=all_notifications)