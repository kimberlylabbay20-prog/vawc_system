import smtplib
import logging
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

logger = logging.getLogger(__name__)


def send_officer_registration_email(full_name: str, username: str, email: str, barangay: str):
    admin_email = os.getenv("ADMIN_EMAIL", "")
    smtp_host = os.getenv("SMTP_HOST", "")
    smtp_port = os.getenv("SMTP_PORT", "587")
    smtp_user = os.getenv("SMTP_USERNAME", "")
    smtp_pass = os.getenv("SMTP_PASSWORD", "")

    if not all([admin_email, smtp_host, smtp_user, smtp_pass]):
        logger.warning("Email config incomplete — skipping email alert")
        return

    subject = "New Officer Registration Request — VAWC System"

    body = f"""
New officer registration request.

Name:           {full_name}
Username:       {username}
Email:          {email}
Barangay:       {barangay or 'N/A'}
Registered:     {datetime.now().strftime('%Y-%m-%d %H:%M')}

Please log in to the VAWC system to approve or reject this request.
"""

    msg = MIMEMultipart()
    msg["From"] = smtp_user
    msg["To"] = admin_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(smtp_host, int(smtp_port), timeout=10) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        logger.info("Registration alert email sent to %s", admin_email)
    except Exception as e:
        logger.warning("Failed to send registration email: %s — continuing", e)
