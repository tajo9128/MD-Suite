"""
Progress Analyzer - Analyzes simulation progress and determines status
"""

import logging
from typing import Dict, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class SimulationStatus(Enum):
    """Simulation status"""
    NOT_STARTED = "not_started"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    UNKNOWN = "unknown"


class ProgressAnalyzer:
    """Analyzes simulation progress"""
    
    def __init__(self, total_ns: float = 100.0):
        self.total_ns = total_ns
        
    def evaluate_progress(self, current_ns: float, is_running: bool = True, is_complete: bool = False) -> Dict:
        """Evaluate simulation progress"""
        
        if is_complete:
            status = SimulationStatus.COMPLETED
            progress_percent = 100.0
        elif current_ns <= 0:
            status = SimulationStatus.NOT_STARTED
            progress_percent = 0.0
        elif is_running:
            status = SimulationStatus.RUNNING
            progress_percent = min(100.0, (current_ns / self.total_ns) * 100)
        else:
            status = SimulationStatus.PAUSED
            progress_percent = min(100.0, (current_ns / self.total_ns) * 100)
            
        remaining_ns = max(0, self.total_ns - current_ns)
        
        return {
            "status": status.value,
            "current_ns": current_ns,
            "total_ns": self.total_ns,
            "progress_percent": progress_percent,
            "remaining_ns": remaining_ns,
            "is_complete": status == SimulationStatus.COMPLETED,
            "is_running": status == SimulationStatus.RUNNING
        }
    
    def should_continue(self, current_ns: float, is_running: bool = True) -> bool:
        """Determine if simulation should continue"""
        return current_ns < self.total_ns and is_running
    
    def get_eta_hours(self, current_ns: float, ns_per_hour: float) -> Optional[float]:
        """Estimate time to completion"""
        if ns_per_hour <= 0:
            return None
        remaining = self.total_ns - current_ns
        return remaining / ns_per_hour


def evaluate_progress(current_ns: float, total_ns: float = 100.0, is_running: bool = True, is_complete: bool = False) -> Dict:
    """Standalone function to evaluate progress"""
    analyzer = ProgressAnalyzer(total_ns)
    return analyzer.evaluate_progress(current_ns, is_running, is_complete)
