"""
Discord Notifier - Sends notifications via Discord webhooks
"""

import logging
from typing import Optional
import requests

logger = logging.getLogger(__name__)


class DiscordNotifier:
    """Sends notifications via Discord webhooks"""
    
    def __init__(self, webhook_url: str = ""):
        self.webhook_url = webhook_url
        self.enabled = bool(webhook_url)
        
    def send_message(self, message: str, title: str = "BioDockify MD") -> bool:
        """Send message via Discord webhook"""
        if not self.enabled:
            logger.debug(f"Discord disabled: {message}")
            return False
            
        try:
            data = {
                "embeds": [{
                    "title": title,
                    "description": message,
                    "color": 3447003
                }]
            }
            response = requests.post(self.webhook_url, json=data, timeout=10)
            
            if response.status_code in [200, 204]:
                logger.info("Discord notification sent")
                return True
            else:
                logger.error(f"Discord API error: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Discord notification failed: {e}")
            return False
    
    def send_progress(self, current_ns: float, total_ns: float) -> bool:
        """Send progress update"""
        progress = (current_ns / total_ns * 100) if total_ns > 0 else 0
        message = f"Progress: {current_ns:.1f} / {total_ns} ns ({progress:.1f}%)"
        return self.send_message(message, "Simulation Progress")
    
    def send_error(self, error_message: str) -> bool:
        """Send error notification"""
        return self.send_message(error_message, "ERROR")
    
    def send_completion(self, project_path: str) -> bool:
        """Send completion notification"""
        return self.send_message(f"Simulation completed!\nProject: {project_path}", "Complete")


def send_discord(message: str, webhook_url: str = "", title: str = "BioDockify MD") -> bool:
    """Standalone function to send Discord message"""
    notifier = DiscordNotifier(webhook_url)
    return notifier.send_message(message, title)
