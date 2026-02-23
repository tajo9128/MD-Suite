"""
Notifier Module for BioDockify MD Universal
Handles notifications (Telegram, Email, etc.) for simulation events
"""

import os
import logging
import requests
from typing import Dict, Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class NotificationType(Enum):
    """Notification types"""
    PROGRESS = "progress"
    ERROR = "error"
    WARNING = "warning"
    COMPLETION = "completion"
    HEALTH_WARNING = "health_warning"
    CRITICAL_ALERT = "critical_alert"
    CUSTOM = "custom"


class Notifier:
    """
    Handles notifications for simulation events.
    
    Supports Telegram, email, and console notifications.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize notifier.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        
        # Telegram settings
        self.enable_telegram = self.config.get("enable_telegram", False)
        self.telegram_token = self.config.get("telegram_bot_token", "")
        self.telegram_chat_id = self.config.get("telegram_chat_id", "")
        
        # Email settings
        self.enable_email = self.config.get("enable_email", False)
        self.email_smtp = self.config.get("email_smtp", "")
        self.email_port = self.config.get("email_port", 587)
        self.email_user = self.config.get("email_user", "")
        self.email_password = self.config.get("email_password", "")
        self.email_from = self.config.get("email_from", "")
        self.email_to = self.config.get("email_to", "")
        
        # Console notifications
        self.enable_console = self.config.get("enable_console", True)
        
    def send_progress_update(self, state) -> bool:
        """
        Send progress update notification.
        
        Args:
            state: SimulationState object
            
        Returns:
            True if notification sent successfully
        """
        message = self._format_progress_message(state)
        
        return self._send_notification(
            message,
            NotificationType.PROGRESS
        )
        
    def send_error(self, title: str, message: str) -> bool:
        """
        Send error notification.
        
        Args:
            title: Error title
            message: Error message
            
        Returns:
            True if notification sent successfully
        """
        full_message = f"🔴 ERROR: {title}\n\n{message}"
        
        return self._send_notification(
            full_message,
            NotificationType.ERROR
        )
        
    def send_health_warning(self, health: Dict) -> bool:
        """
        Send health warning notification.
        
        Args:
            health: Health check dictionary
            
        Returns:
            True if notification sent successfully
        """
        message = f"⚠️ Health Warning\n\n{health.get('message', 'Unknown issue')}"
        
        return self._send_notification(
            message,
            NotificationType.HEALTH_WARNING
        )
        
    def send_critical_alert(self, health: Dict) -> bool:
        """
        Send critical alert notification.
        
        Args:
            health: Health check dictionary
            
        Returns:
            True if notification sent successfully
        """
        message = f"🚨 CRITICAL ALERT\n\n{health.get('message', 'Immediate attention required')}"
        
        return self._send_notification(
            message,
            NotificationType.CRITICAL_ALERT
        )
        
    def send_completion_notification(self, state) -> bool:
        """
        Send simulation completion notification.
        
        Args:
            state: SimulationState object
            
        Returns:
            True if notification sent successfully
        """
        message = self._format_completion_message(state)
        
        return self._send_notification(
            message,
            NotificationType.COMPLETION
        )
        
    def send_custom_message(self, message: str) -> bool:
        """
        Send custom message.
        
        Args:
            message: Message to send
            
        Returns:
            True if notification sent successfully
        """
        return self._send_notification(
            message,
            NotificationType.CUSTOM
        )
        
    def _send_notification(self, message: str, notification_type: NotificationType) -> bool:
        """
        Send notification via all enabled channels.
        
        Args:
            message: Message to send
            notification_type: Type of notification
            
        Returns:
            True if all notifications sent successfully
        """
        success = True
        
        # Console notification
        if self.enable_console:
            self._send_console(message, notification_type)
            
        # Telegram notification
        if self.enable_telegram:
            if not self._send_telegram(message):
                success = False
                
        # Email notification
        if self.enable_email:
            if not self._send_email(message, notification_type):
                success = False
                
        return success
        
    def _format_progress_message(self, state) -> str:
        """Format progress update message"""
        return f"""
📊 Simulation Progress Update

Project: {state.project_path}
Segment: {state.current_segment}/{state.total_segments}
Progress: {state.progress_percent:.1f}%
Simulated: {state.simulated_ns:.2f} ns
Time Elapsed: {state.elapsed_time}
"""
        
    def _format_completion_message(self, state) -> str:
        """Format completion message"""
        return f"""
✅ Simulation Complete!

Project: {state.project_path}
Total Segments: {state.total_segments}
Total Simulated: {state.simulated_ns:.2f} ns
Total Time: {state.elapsed_time}

Publication package will be generated shortly.
"""
        
    def _send_console(self, message: str, notification_type: NotificationType):
        """Send console notification"""
        prefix = {
            NotificationType.PROGRESS: "📊",
            NotificationType.ERROR: "🔴",
            NotificationType.WARNING: "⚠️",
            NotificationType.COMPLETION: "✅",
            NotificationType.HEALTH_WARNING: "⚠️",
            NotificationType.CRITICAL_ALERT: "🚨",
            NotificationType.CUSTOM: "📢"
        }.get(notification_type, "📢")
        
        logger.info(f"{prefix} {message}")
        
    def _send_telegram(self, message: str) -> bool:
        """Send Telegram notification"""
        if not self.telegram_token or not self.telegram_chat_id:
            logger.warning("Telegram not configured")
            return False
            
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            
            data = {
                "chat_id": self.telegram_chat_id,
                "text": f"🧬 BioDockify MD\n\n{message}",
                "parse_mode": "Markdown"
            }
            
            response = requests.post(url, json=data, timeout=10)
            
            if response.status_code == 200:
                logger.info("Telegram notification sent")
                return True
            else:
                logger.error(f"Telegram API error: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Telegram notification failed: {e}")
            return False
            
    def _send_email(self, message: str, notification_type: NotificationType) -> bool:
        """Send email notification"""
        if not all([self.email_smtp, self.email_user, self.email_to]):
            logger.warning("Email not configured")
            return False
            
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            # Create message
            msg = MIMEMultipart()
            msg["From"] = self.email_from or self.email_user
            msg["To"] = self.email_to
            
            # Set subject based on type
            subject_prefix = {
                NotificationType.PROGRESS: "Progress",
                NotificationType.ERROR: "ERROR",
                NotificationType.WARNING: "Warning",
                NotificationType.COMPLETION: "Complete",
                NotificationType.HEALTH_WARNING: "Health Warning",
                NotificationType.CRITICAL_ALERT: "CRITICAL",
                NotificationType.CUSTOM: "Update"
            }.get(notification_type, "Update")
            
            msg["Subject"] = f"BioDockify MD - {subject_prefix}"
            
            # Attach body
            msg.attach(MIMEText(message, "plain"))
            
            # Send
            server = smtplib.SMTP(self.email_smtp, self.email_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            server.send_message(msg)
            server.quit()
            
            logger.info("Email notification sent")
            return True
            
        except Exception as e:
            logger.error(f"Email notification failed: {e}")
            return False
            
    def test_telegram(self) -> bool:
        """Test Telegram configuration"""
        return self._send_telegram("🔬 BioDockify MD Universal - Test Notification")


def send_notification(
    message: str,
    notification_type: NotificationType = NotificationType.CUSTOM,
    config: Optional[Dict] = None
) -> bool:
    """
    Standalone function to send notification.
    
    Args:
        message: Message to send
        notification_type: Type of notification
        config: Optional configuration
        
    Returns:
        True if notification sent successfully
    """
    notifier = Notifier(config)
    return notifier._send_notification(message, notification_type)


if __name__ == "__main__":
    # Test notifier
    print("Testing Notifier...")
    
    notifier = Notifier({"enable_console": True})
    
    print("\nSending progress update...")
    # Create mock state
    from datetime import timedelta
    class MockState:
        project_path = "/test/project"
        is_running = True
        current_segment = 5
        total_segments = 10
        progress_percent = 50.0
        elapsed_time = timedelta(hours=2)
        simulated_ns = 50.0
        errors = []
        warnings = []
        
    state = MockState()
    notifier.send_progress_update(state)
    
    print("\nSending error...")
    notifier.send_error("Test Error", "This is a test error message")
    
    print("\nNotifier test complete")
