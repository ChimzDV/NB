from flask_mail import Message
from app import mail
from flask import current_app

def send_email_safe(subject, recipient_email, body_html):
    """Sends email notifications safely, catching errors to avoid thread crashes."""
    try:
        sender_email = current_app.config.get("MAIL_USERNAME", "notifications@novabridge.com")
        msg = Message(
            subject=subject,
            recipients=[recipient_email],
            html=body_html,
            sender=("NovaBridge", sender_email)
        )
        mail.send(msg)
        print(f"[Email Service] Mail sent successfully: '{subject}' to {recipient_email}")
        return True
    except Exception as e:
        print(f"[Email Service] Failed to send email '{subject}' to {recipient_email}: {e}")
        return False

def get_base_template(content_html):
    """Base responsive HTML template matching the premium theme of NovaBridge."""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: 'Plus Jakarta Sans', Arial, sans-serif;
                background-color: #0b0d19;
                color: #f8fafc;
                margin: 0;
                padding: 40px 20px;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background: rgba(20, 24, 46, 0.95);
                border: 1px solid rgba(139, 92, 246, 0.2);
                border-radius: 16px;
                padding: 40px;
                box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .logo {{
                font-size: 24px;
                font-weight: 800;
                color: #a78bfa;
                text-decoration: none;
            }}
            .content {{
                line-height: 1.6;
                font-size: 15px;
                color: #cbd5e1;
            }}
            .highlight {{
                color: #a78bfa;
                font-weight: 600;
            }}
            .footer {{
                text-align: center;
                margin-top: 40px;
                font-size: 12px;
                color: #64748b;
                border-top: 1px solid rgba(255, 255, 255, 0.08);
                padding-top: 20px;
            }}
            .btn {{
                display: inline-block;
                padding: 12px 24px;
                background: linear-gradient(135deg, #a855f7 0%, #6366f1 100%);
                color: #ffffff !important;
                text-decoration: none;
                font-weight: 600;
                border-radius: 8px;
                margin-top: 20px;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <a href="#" class="logo">NovaBridge</a>
            </div>
            <div class="content">
                {content_html}
            </div>
            <div class="footer">
                &copy; 2026 NovaBridge. All rights reserved.<br>
                This is an automated operational notification.
            </div>
        </div>
    </body>
    </html>
    """

def send_loan_approved_email(user, loan):
    subject = f"Loan Application Approved - Loan #{loan.id}"
    content = f"""
    <h2>Congratulations, {user.full_name}!</h2>
    <p>We are pleased to inform you that your loan application <span class="highlight">#{loan.id}</span> has been approved.</p>
    <table style="width: 100%; margin: 20px 0; border-collapse: collapse;">
        <tr>
            <td style="padding: 8px 0; color: #94a3b8;">Approved Amount:</td>
            <td style="padding: 8px 0; font-weight: bold; text-align: right;">${loan.loan_amount:,.2f}</td>
        </tr>
        <tr>
            <td style="padding: 8px 0; color: #94a3b8;">Due Date:</td>
            <td style="padding: 8px 0; font-weight: bold; text-align: right;">{loan.due_date}</td>
        </tr>
    </table>
    <p>The funds will be disbursed to your account shortly.</p>
    <a href="http://localhost:5000/dashboard" class="btn">View Dashboard</a>
    """
    return send_email_safe(subject, user.email, get_base_template(content))

def send_loan_rejected_email(user, loan):
    subject = f"Update on Loan Application - Loan #{loan.id}"
    content = f"""
    <h2>Dear {user.full_name},</h2>
    <p>Thank you for submitting your loan application <span class="highlight">#{loan.id}</span>.</p>
    <p>After careful underwriting review, unfortunately, we are unable to approve your application at this time.</p>
    <p>If you have any questions or would like to submit additional documentation, please visit our document upload portal.</p>
    <a href="http://localhost:5000/dashboard" class="btn">Upload Documents</a>
    """
    return send_email_safe(subject, user.email, get_base_template(content))

def send_payment_received_email(user, loan, amount_paid):
    subject = f"Payment Received - Loan #{loan.id}"
    content = f"""
    <h2>Payment Confirmed</h2>
    <p>Dear {user.full_name},</p>
    <p>We have successfully received a payment of <span class="highlight">${amount_paid:,.2f}</span> for your loan <span class="highlight">#{loan.id}</span>.</p>
    <table style="width: 100%; margin: 20px 0; border-collapse: collapse;">
        <tr>
            <td style="padding: 8px 0; color: #94a3b8;">Remaining Balance:</td>
            <td style="padding: 8px 0; font-weight: bold; text-align: right;">${loan.remaining_balance:,.2f}</td>
        </tr>
    </table>
    <p>Thank you for choosing NovaBridge!</p>
    <a href="http://localhost:5000/my-loans" class="btn">My Loans</a>
    """
    return send_email_safe(subject, user.email, get_base_template(content))

def send_loan_completed_email(user, loan):
    subject = f"Loan Fully Repaid! - Loan #{loan.id}"
    content = f"""
    <h2>Congratulations!</h2>
    <p>Dear {user.full_name},</p>
    <p>Your loan <span class="highlight">#{loan.id}</span> of <span class="highlight">${loan.loan_amount:,.2f}</span> has been fully repaid.</p>
    <p>Your account is in excellent standing. Thank you for your business, and we look forward to helping you with any future credit needs!</p>
    <a href="http://localhost:5000/apply-loan" class="btn">Apply For New Loan</a>
    """
    return send_email_safe(subject, user.email, get_base_template(content))

def send_loan_due_tomorrow_email(user, loan):
    subject = f"Repayment Reminder: Loan #{loan.id} Due Tomorrow"
    content = f"""
    <h2>Repayment Reminder</h2>
    <p>Dear {user.full_name},</p>
    <p>This is a reminder that your loan repayment for loan <span class="highlight">#{loan.id}</span> is due tomorrow, <span class="highlight">{loan.due_date}</span>.</p>
    <table style="width: 100%; margin: 20px 0; border-collapse: collapse;">
        <tr>
            <td style="padding: 8px 0; color: #94a3b8;">Outstanding Balance:</td>
            <td style="padding: 8px 0; font-weight: bold; text-align: right;">${loan.remaining_balance:,.2f}</td>
        </tr>
    </table>
    <p>Please ensure sufficient funds are available to make your payment.</p>
    <a href="http://localhost:5000/my-loans" class="btn">Pay Now</a>
    """
    return send_email_safe(subject, user.email, get_base_template(content))

def send_loan_overdue_email(user, loan):
    subject = f"URGENT: Loan #{loan.id} is Overdue"
    content = f"""
    <h2 style="color: #ef4444;">Overdue Notice</h2>
    <p>Dear {user.full_name},</p>
    <p>Your loan repayment for loan <span class="highlight">#{loan.id}</span> is currently <span class="highlight" style="color: #ef4444;">Overdue</span>.</p>
    <table style="width: 100%; margin: 20px 0; border-collapse: collapse;">
        <tr>
            <td style="padding: 8px 0; color: #94a3b8;">Past Due Balance:</td>
            <td style="padding: 8px 0; font-weight: bold; text-align: right; color: #ef4444;">${loan.remaining_balance:,.2f}</td>
        </tr>
        <tr>
            <td style="padding: 8px 0; color: #94a3b8;">Original Due Date:</td>
            <td style="padding: 8px 0; font-weight: bold; text-align: right;">{loan.due_date}</td>
        </tr>
    </table>
    <p>Please log in and settle your balance immediately to avoid additional penalties or impacts to your credit score.</p>
    <a href="http://localhost:5000/my-loans" class="btn" style="background: #ef4444;">Pay Outstanding Balance</a>
    """
    return send_email_safe(subject, user.email, get_base_template(content))

def send_document_status_email(user, doc):
    approved = doc.verification_status == "approved"
    status_text = "Approved" if approved else "Rejected"
    subject = f"Verification Document {status_text} - {doc.document_type}"
    
    rejection_info = ""
    if not approved and doc.rejection_reason:
        rejection_info = f"""
        <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.2); padding: 15px; border-radius: 8px; margin: 20px 0;">
            <strong style="color: #ef4444;">Rejection Reason:</strong><br>
            <span style="color: #cbd5e1;">{doc.rejection_reason}</span>
        </div>
        """
        
    content = f"""
    <h2>Document Review Completed</h2>
    <p>Dear {user.full_name},</p>
    <p>Your uploaded <span class="highlight">{doc.document_type}</span> document has been reviewed and <span class="highlight" style="color: {'#10b981' if approved else '#ef4444'};">{status_text}</span>.</p>
    {rejection_info}
    <p>Current KYC status of your profile: <span class="highlight">{user.kyc_status}</span></p>
    <a href="http://localhost:5000/upload-document" class="btn">Go to Verification Center</a>
    """
    return send_email_safe(subject, user.email, get_base_template(content))
