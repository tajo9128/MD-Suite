"""
Disk Monitor - Monitors disk space for simulation storage
"""

import os
import logging
import psutil
from typing import Dict

logger = logging.getLogger(__name__)


class DiskMonitor:
    """Monitors disk space"""
    
    def __init__(self, path: str = "/"):
        self.path = path
        
    def get_disk_status(self) -> Dict:
        """Get disk space status"""
        try:
            disk = psutil.disk_usage(self.path)
            
            result = {
                "total_gb": disk.total / (1024**3),
                "used_gb": disk.used / (1024**3),
                "free_gb": disk.free / (1024**3),
                "percent": disk.percent,
                "path": self.path,
                "error": None
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Disk status error: {e}")
            return {
                "total_gb": 0,
                "used_gb": 0,
                "free_gb": 0,
                "percent": 0,
                "path": self.path,
                "error": str(e)
            }
    
    def is_space_low(self, threshold_gb: float = 5.0) -> bool:
        """Check if disk space is low"""
        status = self.get_disk_status()
        return status.get("free_gb", 0) < threshold_gb
    
    def get_free_space_gb(self) -> float:
        """Get free space in GB"""
        status = self.get_disk_status()
        return status.get("free_gb", 0)


def get_disk_status(path: str = "/") -> Dict:
    """Standalone function to get disk status"""
    monitor = DiskMonitor(path)
    return monitor.get_disk_status()
