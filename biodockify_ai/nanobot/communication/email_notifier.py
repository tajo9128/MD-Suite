"""
Email Notifier - Sends notifications via Email
"""

import logging
import smtplib
from typing import Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)


class EmailNotifier:
    """Sends notifications via Email"""
    
    def __init__(
        self,
        smtp_server: str = "",
        smtp_port: int = 587,
        username: str = "",
        password: str = "",
        from_email: str = "",
        to_email: str = ""
    ):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email or username
        self.to_email = to_email
        self.enabled = bool(smtp_server and username and password and to_email)
        
    def send_email(self, subject: str, message: str) -> bool:
        """Send email notification"""
        if not self.enabled:
            logger.debug(f"Email disabled: {subject}")
            return False
            
        try:
            msg = MIMEMultipart()
            msg["From"] = self.from_email
            msg["To"] = self.to_email
            msg["Subject"] = f"BioDockify MD - {subject}"
            
            body = f"""BioDockify MD Simulation Update

{message}

---
BioDockify MD Universal
"""
            msg.attach(MIMEText(body, "plain"))
            
            if self.smtp_port == 465:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
                
            server.login(self.username, self.password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email notification sent: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Email notification failed: {e}")
            return False
    
    def send_progress(self, current_ns: float, total_ns: float) -> bool:
        """Send progress update"""
        progress = (current_ns / total_ns * 100) if total_ns > 0 else 0
        subject = "Simulation Progress Update"
        message = f"Progress: {current_ns:.1f} / {total_ns} ns ({progress:.1f}%)"
        return self.send_email(subject, message)
    
    def send_error(self, error_message: str) -> bool:
        """Send error notification"""
        return self.send_email("ERROR Alert", error_message)
    
    def send_completion(self, project_path: str) -> bool:
        """Send completion notification"""
        return self.send_email(
            "Simulation Complete",
            f"Simulation has completed successfully!\nProject: {project_path}"
        )


def send_email(
    subject: str,
    message: str,
    smtp_server: str = "",
    smtp_port: int = 587,
    username: str = "",
    password: str = "",
    from_email: str = "",
    to_email: str = ""
) -> bool:
    """Standalone function to send email"""
    notifier = EmailNotifier(
        smtp_server, smtp_port, username, password, from_email, to_email
    )
    return notifier.send_email(subject, message)
