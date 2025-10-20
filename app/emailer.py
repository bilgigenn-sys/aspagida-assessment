import smtplib
from email.message import EmailMessage
from typing import Optional
from sqlalchemy.orm import Session
from .models import SMTPSettings
from .config import settings as app_settings

def get_smtp_settings(db: Session) -> SMTPSettings:
    row = db.query(SMTPSettings).first()
    if not row:
        row = SMTPSettings(
            host=app_settings.SMTP_HOST,
            port=app_settings.SMTP_PORT,
            username=app_settings.SMTP_USERNAME,
            password=app_settings.SMTP_PASSWORD,
            use_tls=app_settings.SMTP_USE_TLS,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
    return row

def send_mail(db: Session, subject: str, body: str, to: Optional[str] = None, attachments: Optional[list] = None):
    cfg = get_smtp_settings(db)
    to_addr = to or str(app_settings.REPORT_SEND_TO)
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = cfg.username or "no-reply@bilgigen.local"
    msg["To"] = to_addr
    msg.set_content(body)

    for att in attachments or []:
        path, mime = att.get("path"), att.get("mime", "application/octet-stream")
        name = att.get("name")
        if path and name:
            with open(path, "rb") as f:
                msg.add_attachment(f.read(), maintype=mime.split("/")[0], subtype=mime.split("/")[1], filename=name)

    with smtplib.SMTP(cfg.host, cfg.port) as server:
        if cfg.use_tls:
            server.starttls()
        if cfg.username and cfg.password:
            server.login(cfg.username, cfg.password)
        server.send_message(msg)
