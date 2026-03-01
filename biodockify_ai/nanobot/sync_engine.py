"""
Synchronization Engine for Nanobot
Keeps project state synchronized in real-time
"""

import os
import json
import time
import logging
from typing import Dict, Optional, Any
from datetime import datetime
from threading import Lock

logger = logging.getLogger(__name__)


class SyncEngine:
    """
    Synchronization engine that keeps project state
    updated in real-time for UI consumption.
    """
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.status_file = os.path.join(project_path, "status.json")
        self._lock = Lock()
        
        self._last_progress = 0.0
        self._last_checkpoint_time = None
        self._file_sizes = {}
        
    def synchronize_state(
        self,
        current_ns: float = 0.0,
        total_ns: float = 100.0,
        is_running: bool = False,
        segment: int = 0,
        gpu_temp: int = 0,
        gpu_available: bool = False,
        disk_free_gb: float = 0.0,
        errors: list = None
    ) -> bool:
        """
        Synchronize project state to status.json.
        This is what UI reads for live updates.
        """
        with self._lock:
            try:
                state_data = {
                    "project_path": self.project_path,
                    "timestamp": datetime.now().isoformat(),
                    "simulation": {
                        "current_ns": current_ns,
                        "total_ns": total_ns,
                        "progress_percent": (current_ns / total_ns * 100) if total_ns > 0 else 0,
                        "is_running": is_running,
                        "segment": segment
                    },
                    "hardware": {
                        "gpu_available": gpu_available,
                        "gpu_temp_celsius": gpu_temp,
                        "disk_free_gb": disk_free_gb
                    },
                    "errors": errors or [],
                    "last_update": time.time()
                }
                
                with open(self.status_file, 'w') as f:
                    json.dump(state_data, f, indent=2)
                    
                self._last_progress = current_ns
                return True
                
            except Exception as e:
                logger.error(f"State sync failed: {e}")
                return False
    
    def read_status(self) -> Dict:
        """Read current status from file"""
        try:
            if os.path.exists(self.status_file):
                with open(self.status_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read status: {e}")
            
        return self._default_status()
    
    def _default_status(self) -> Dict:
        """Get default status"""
        return {
            "project_path": self.project_path,
            "simulation": {
                "current_ns": 0.0,
                "total_ns": 100.0,
                "progress_percent": 0.0,
                "is_running": False,
                "segment": 0
            },
            "hardware": {
                "gpu_available": False,
                "gpu_temp_celsius": 0,
                "disk_free_gb": 0.0
            },
            "errors": []
        }
    
    def update_progress_only(self, current_ns: float, total_ns: float) -> bool:
        """Quick update of progress only"""
        status = self.read_status()
        status["simulation"]["current_ns"] = current_ns
        status["simulation"]["progress_percent"] = (current_ns / total_ns * 100) if total_ns > 0 else 0
        status["timestamp"] = datetime.now().isoformat()
        
        try:
            with open(self.status_file, 'w') as f:
                json.dump(status, f, indent=2)
            return True
        except:
            return False


class FileSizeTracker:
    """Tracks file sizes to detect simulation freezes"""
    
    def __init__(self):
        self._sizes = {}
        self._times = {}
        
    def update(self, filepath: str) -> Optional[float]:
        """Update file size and return delta since last check"""
        if not os.path.exists(filepath):
            return None
            
        current_size = os.path.getsize(filepath)
        current_time = time.time()
        
        if filepath in self._sizes:
            delta_size = current_size - self._sizes[filepath]
            delta_time = current_time - self._times[filepath]
            
            self._sizes[filepath] = current_size
            self._times[filepath] = current_time
            
            if delta_time > 0:
                return delta_size / delta_time
        else:
            self._sizes[filepath] = current_size
            self._times[filepath] = current_time
            
        return 0.0
    
    def get_size(self, filepath: str) -> int:
        """Get current file size"""
        if os.path.exists(filepath):
            return os.path.getsize(filepath)
        return 0
    
    def is_growing(self, filepath: str, threshold_seconds: int = 60) -> bool:
        """Check if file is still growing"""
        if filepath not in self._sizes:
            return True
            
        current_size = self.get_size(filepath)
        last_size = self._sizes.get(filepath, 0)
        
        return current_size > last_size


def synchronize_state(project_path: str, **kwargs) -> bool:
    """Standalone function to sync state"""
    engine = SyncEngine(project_path)
    return engine.synchronize_state(**kwargs)
