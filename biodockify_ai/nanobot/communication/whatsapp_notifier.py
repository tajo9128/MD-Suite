"""
WhatsApp Notifier - Sends notifications via WhatsApp
"""

import logging
from typing import Optional
import requests

logger = logging.getLogger(__name__)


class WhatsAppNotifier:
    """Sends notifications via WhatsApp"""
    
    def __init__(self, api_url: str = "", phone: str = ""):
        self.api_url = api_url
        self.phone = phone
        self.enabled = bool(api_url and phone)
        
    def send_message(self, message: str) -> bool:
        """Send message via WhatsApp"""
        if not self.enabled:
            logger.debug(f"WhatsApp disabled: {message}")
            return False
            
        try:
            data = {
                "phone": self.phone,
                "message": f"BioDockify MD\n\n{message}"
            }
            response = requests.post(self.api_url, json=data, timeout=10)
            
            if response.status_code in [200, 201]:
                logger.info("WhatsApp notification sent")
                return True
            else:
                logger.error(f"WhatsApp API error: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"WhatsApp notification failed: {e}")
            return False
    
    def send_progress(self, current_ns: float, total_ns: float) -> bool:
        """Send progress update"""
        progress = (current_ns / total_ns * 100) if total_ns > 0 else 0
        message = f"Progress: {current_ns:.1f} / {total_ns} ns ({progress:.1f}%)"
        return self.send_message(message)


def send_whatsapp(message: str, api_url: str = "", phone: str = "") -> bool:
    """Standalone function to send WhatsApp message"""
    notifier = WhatsAppNotifier(api_url, phone)
    return notifier.send_message(message)
