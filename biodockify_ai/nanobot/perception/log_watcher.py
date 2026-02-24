"""
Log Watcher - Monitors MD simulation progress from GROMACS log files
"""

import os
import re
import logging
from typing import Dict, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class LogWatcher:
    """Watches and parses GROMACS MD log files"""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        
    def find_log_file(self, segment_id: Optional[int] = None) -> Optional[str]:
        """Find the MD log file"""
        if segment_id is not None:
            search_dir = os.path.join(self.project_path, f"segment_{segment_id:03d}")
        else:
            search_dir = self.project_path
            
        if not os.path.exists(search_dir):
            return None
            
        log_file = os.path.join(search_dir, "md.log")
        if os.path.exists(log_file):
            return log_file
            
        for f in os.listdir(search_dir):
            if f.endswith(".log") and "md" in f.lower():
                return os.path.join(search_dir, f)
                
        return None
    
    def read_progress(self) -> Dict:
        """Read simulation progress from log file"""
        result = {
            "current_ns": 0.0,
            "current_step": 0,
            "total_steps": 0,
            "is_running": False,
            "is_complete": False,
            "last_update": None
        }
        
        log_file = self.find_log_file()
        if not log_file or not os.path.exists(log_file):
            return result
            
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                
            if "Finished mdrun" in content or "GROMACS reminds you" in content:
                result["is_complete"] = True
                result["is_running"] = False
            else:
                result["is_running"] = True
                
            for line in reversed(lines[-100:]):
                if re.match(r'^\s*\d+\s+[\d.]+\s*$', line):
                    parts = line.split()
                    if len(parts) >= 2:
                        try:
                            result["current_step"] = int(parts[0])
                            result["current_ns"] = float(parts[1])
                        except ValueError:
                            pass
                            
            if lines:
                result["last_update"] = lines[-1][:50]
                
        except Exception as e:
            logger.error(f"Failed to read log file: {e}")
            
        return result
    
    def get_simulated_ns(self) -> float:
        """Get current simulated nanoseconds"""
        progress = self.read_progress()
        return progress.get("current_ns", 0.0)
    
    def is_simulation_running(self) -> bool:
        """Check if simulation is currently running"""
        progress = self.read_progress()
        return progress.get("is_running", False)
    
    def is_simulation_complete(self) -> bool:
        """Check if simulation is complete"""
        progress = self.read_progress()
        return progress.get("is_complete", False)


def read_progress(project_path: str) -> Dict:
    """Standalone function to read progress"""
    watcher = LogWatcher(project_path)
    return watcher.read_progress()
