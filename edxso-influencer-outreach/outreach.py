import os
import smtplib
from email.message import EmailMessage

def send_email(to_email, subject, body):
    required = ["SMTP_HOST", "SMTP_PORT", "SMTP_USERNAME", "SMTP_PASSWORD", "SMTP_FROM_EMAIL"]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        raise RuntimeError("SMTP not configured: " + ", ".join(missing))
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = os.getenv("SMTP_FROM_EMAIL")
    msg["To"] = to_email
    msg.set_content(body)
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
    with smtplib.SMTP(host, port, timeout=20) as server:
        if use_tls:
            server.starttls()
        server.login(os.getenv("SMTP_USERNAME"), os.getenv("SMTP_PASSWORD"))
        server.send_message(msg)

def split_subject_body(email_message):
    lines = email_message.splitlines()
    subject = "Collaboration opportunity"
    body_lines = []
    for line in lines:
        if line.lower().startswith("subject:"):
            subject = line.split(":", 1)[1].strip()
        else:
            body_lines.append(line)
    return subject, "\n".join(body_lines).strip()
