from __future__ import annotations
import smtplib
from email.message import EmailMessage
from app.core.config import get_settings
from app.core.models import EmailDraft


class SMTPMailer:
    def __init__(self) -> None:
        self.settings = get_settings()

    def is_configured(self) -> bool:
        s = self.settings
        return bool(s.smtp_host and s.smtp_user and s.smtp_password and s.smtp_from)

    def send(self, draft: EmailDraft) -> str:
        if not draft.approved:
            return 'Sicherheitsstopp: Entwurf ist nicht freigegeben.'
        if not draft.to_email:
            return 'Keine Empfängeradresse vorhanden.'
        if not self.is_configured():
            return 'SMTP ist noch nicht konfiguriert.'
        msg = EmailMessage()
        msg['From'] = self.settings.smtp_from
        msg['To'] = str(draft.to_email)
        msg['Subject'] = draft.subject
        msg.set_content(draft.body)
        with smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port, timeout=30) as server:
            if self.settings.smtp_use_tls:
                server.starttls()
            server.login(self.settings.smtp_user, self.settings.smtp_password)
            server.send_message(msg)
        return 'E-Mail wurde versendet.'
