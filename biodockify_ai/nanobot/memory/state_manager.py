"""
State Manager - Manages Nanobot state persistence
"""

import json
import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class StateManager:
    """Manages Nanobot state persistence"""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.state_file = os.path.join(project_path, "nanobot_state.json")
        
    def load_state(self) -> Dict:
        """Load state from file"""
        if not os.path.exists(self.state_file):
            return self._default_state()
            
        try:
            with open(self.state_file, 'r') as f:
                state = json.load(f)
                logger.info(f"Loaded state from {self.state_file}")
                return state
        except Exception as e:
            logger.error(f"Failed to load state: {e}")
            return self._default_state()
    
    def save_state(self, state: Dict) -> bool:
        """Save state to file"""
        try:
            state["last_updated"] = datetime.now().isoformat()
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
            logger.info(f"Saved state to {self.state_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
            return False
    
    def _default_state(self) -> Dict:
        """Get default state"""
        return {
            "project_path": self.project_path,
            "last_ns": 0.0,
            "current_segment": 0,
            "total_segments": 0,
            "status": "not_started",
            "last_updated": datetime.now().isoformat(),
            "notifications_sent": [],
            "errors": [],
            "warnings": []
        }
    
    def update_progress(self, current_ns: float, segment: int) -> bool:
        """Update progress in state"""
        state = self.load_state()
        state["last_ns"] = current_ns
        state["current_segment"] = segment
        state["status"] = "running"
        return self.save_state(state)
    
    def set_status(self, status: str) -> bool:
        """Set simulation status"""
        state = self.load_state()
        state["status"] = status
        return self.save_state(state)
    
    def add_notification(self, notification_type: str, message: str) -> bool:
        """Add notification to history"""
        state = self.load_state()
        state["notifications_sent"].append({
            "type": notification_type,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        return self.save_state(state)
    
    def add_error(self, error: str) -> bool:
        """Add error to history"""
        state = self.load_state()
        state["errors"].append({
            "error": error,
            "timestamp": datetime.now().isoformat()
        })
        return self.save_state(state)


def load_state(project_path: str) -> Dict:
    """Standalone function to load state"""
    manager = StateManager(project_path)
    return manager.load_state()


def save_state(project_path: str, state: Dict) -> bool:
    """Standalone function to save state"""
    manager = StateManager(project_path)
    return manager.save_state(state)
