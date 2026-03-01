"""
Telegram Notifier - Sends notifications via Telegram
"""

import logging
from typing import Optional
import requests

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Sends notifications via Telegram"""
    
    def __init__(self, token: str = "", chat_id: str = ""):
        self.token = token
        self.chat_id = chat_id
        self.enabled = bool(token and chat_id)
        
    def send_message(self, message: str) -> bool:
        """Send message via Telegram"""
        if not self.enabled:
            logger.debug(f"Telegram disabled: {message}")
            return False
            
        try:
            url = f"https://api.telegram.org/bot{self.token}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": f"BioDockify MD\n\n{message}",
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
    
    def send_progress(self, current_ns: float, total_ns: float) -> bool:
        """Send progress update"""
        progress = (current_ns / total_ns * 100) if total_ns > 0 else 0
        message = f"Progress: {current_ns:.1f} / {total_ns} ns ({progress:.1f}%)"
        return self.send_message(message)
    
    def send_error(self, error_message: str) -> bool:
        """Send error notification"""
        return self.send_message(f"[ERROR] {error_message}")
    
    def send_completion(self, project_path: str) -> bool:
        """Send completion notification"""
        return self.send_message(f"[COMPLETE] Simulation completed!\nProject: {project_path}")


def send_telegram(message: str, token: str = "", chat_id: str = "") -> bool:
    """Standalone function to send Telegram message"""
    notifier = TelegramNotifier(token, chat_id)
    return notifier.send_message(message)
