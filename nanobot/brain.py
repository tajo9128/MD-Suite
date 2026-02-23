"""
Nanobot Brain Module for BioDockify MD Universal
Central supervision and coordination for MD simulations
"""

import os
import logging
import time
import threading
from typing import Optional, Dict, List, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SimulationState:
    """Current state of the simulation"""
    project_path: str
    is_running: bool
    current_segment: int
    total_segments: int
    progress_percent: float
    elapsed_time: timedelta
    simulated_ns: float
    errors: List[str]
    warnings: List[str]


class NanobotBrain:
    """
    Nanobot Brain - Central supervision system for MD simulations.
    
    Coordinates log parsing, health monitoring, and notifications
    to ensure reliable simulation execution.
    """
    
    def __init__(
        self,
        project_path: str,
        config: Optional[Dict] = None,
        on_state_change: Optional[Callable] = None
    ):
        """
        Initialize Nanobot Brain.
        
        Args:
            project_path: Path to the project directory
            config: Optional configuration dictionary
            on_state_change: Callback for state changes
        """
        self.project_path = project_path
        self.config = config or {}
        self.on_state_change = on_state_change
        
        # Initialize subsystems
        from .log_parser import LogParser
        from .health_monitor import HealthMonitor
        from .notifier import Notifier
        
        self.log_parser = LogParser(project_path)
        self.health_monitor = HealthMonitor(config)
        self.notifier = Notifier(config)
        
        # State
        self.current_state: Optional[SimulationState] = None
        self.is_supervising = False
        self.supervision_thread: Optional[threading.Thread] = None
        
        # Last notification times
        self.last_health_notification = datetime.min
        self.last_progress_notification = datetime.min
        
    def start_supervision(self):
        """Start the supervision loop"""
        if self.is_supervising:
            logger.warning("Supervision already running")
            return
            
        logger.info("Starting Nanobot supervision...")
        
        self.is_supervising = True
        
        # Initialize state
        self.current_state = SimulationState(
            project_path=self.project_path,
            is_running=False,
            current_segment=0,
            total_segments=0,
            progress_percent=0.0,
            elapsed_time=timedelta(),
            simulated_ns=0.0,
            errors=[],
            warnings=[]
        )
        
        # Start supervision thread
        self.supervision_thread = threading.Thread(
            target=self._supervision_loop,
            daemon=True
        )
        self.supervision_thread.start()
        
        logger.info("Nanobot supervision started")
        
    def stop_supervision(self):
        """Stop the supervision loop"""
        if not self.is_supervising:
            return
            
        logger.info("Stopping Nanobot supervision...")
        
        self.is_supervising = False
        
        if self.supervision_thread:
            self.supervision_thread.join(timeout=5)
            
        logger.info("Nanobot supervision stopped")
        
    def _supervision_loop(self):
        """Main supervision loop"""
        check_interval = self.config.get("check_interval_seconds", 30)
        
        while self.is_supervising:
            try:
                self._check_simulation()
                self._check_health()
                self._notify_if_needed()
                
            except Exception as e:
                logger.error(f"Supervision error: {e}")
                
            time.sleep(check_interval)
            
    def _check_simulation(self):
        """Check simulation status via log parser"""
        if not self.current_state:
            return
            
        # Parse log file
        log_status = self.log_parser.parse_log()
        
        if log_status:
            # Update state
            self.current_state.is_running = log_status.get("is_running", False)
            self.current_state.progress_percent = log_status.get("progress_percent", 0.0)
            self.current_state.simulated_ns = log_status.get("simulated_ns", 0.0)
            self.current_state.errors = log_status.get("errors", [])
            self.current_state.warnings = log_status.get("warnings", [])
            
            # Notify on errors
            if log_status.get("errors"):
                self.notifier.send_error(
                    "Simulation Error Detected",
                    "\n".join(log_status["errors"])
                )
                
    def _check_health(self):
        """Check system health"""
        health = self.health_monitor.check_health()
        
        if health.get("status") == "warning":
            # Send health warning
            self.notifier.send_health_warning(health)
            
        elif health.get("status") == "critical":
            # Critical health issue - send alert
            self.notifier.send_critical_alert(health)
            
    def _notify_if_needed(self):
        """Send periodic notifications"""
        now = datetime.now()
        
        # Progress notification every hour
        progress_interval = self.config.get(
            "progress_notification_interval_minutes", 60
        )
        
        if now - self.last_progress_notification > timedelta(minutes=progress_interval):
            if self.current_state and self.current_state.is_running:
                self.notifier.send_progress_update(self.current_state)
                self.last_progress_notification = now
                
    def update_segment(self, segment_id: int, total_segments: int):
        """Update current segment information"""
        if self.current_state:
            self.current_state.current_segment = segment_id
            self.current_state.total_segments = total_segments
            
    def set_running(self, is_running: bool):
        """Set simulation running state"""
        if self.current_state:
            old_state = self.current_state.is_running
            self.current_state.is_running = is_running
            
            if old_state and not is_running:
                # Simulation just stopped
                self.notifier.send_completion_notification(self.current_state)
                
    def get_state(self) -> SimulationState:
        """Get current simulation state"""
        return self.current_state
        
    def get_diagnostics(self) -> Dict:
        """Get diagnostic information"""
        return {
            "project_path": self.project_path,
            "is_supervising": self.is_supervising,
            "state": self.current_state,
            "health": self.health_monitor.get_last_health(),
            "config": self.config
        }
        
    def force_notification(self, message: str):
        """Force send a notification"""
        self.notifier.send_custom_message(message)
        
    def validate_simulation_health(self) -> Dict:
        """
        Perform a comprehensive health validation.
        
        Returns:
            Dictionary with validation results
        """
        results = {
            "valid": True,
            "issues": [],
            "warnings": []
        }
        
        # Check log parser health
        log_status = self.log_parser.parse_log()
        if log_status.get("errors"):
            results["valid"] = False
            results["issues"].extend(log_status["errors"])
            
        # Check system health
        health = self.health_monitor.check_health()
        if health.get("status") == "critical":
            results["valid"] = False
            results["issues"].append(f"Critical: {health.get('message')}")
        elif health.get("status") == "warning":
            results["warnings"].append(health.get("message"))
            
        return results


def create_nanobot(
    project_path: str,
    config: Optional[Dict] = None,
    enable_notifications: bool = True
) -> NanobotBrain:
    """
    Factory function to create a Nanobot instance.
    
    Args:
        project_path: Project directory path
        config: Optional configuration
        enable_notifications: Whether to enable notifications
        
    Returns:
        NanobotBrain instance
    """
    if config is None:
        config = {}
        
    if not enable_notifications:
        config["enable_notifications"] = False
        
    return NanobotBrain(project_path, config)


if __name__ == "__main__":
    # Test Nanobot Brain
    import tempfile
    
    logging.basicConfig(level=logging.INFO)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        print("Testing Nanobot Brain...")
        
        brain = NanobotBrain(tmpdir)
        
        print("Starting supervision...")
        brain.start_supervision()
        
        time.sleep(2)
        
        state = brain.get_state()
        print(f"State: {state}")
        
        brain.stop_supervision()
        
        print("Nanobot Brain test complete")
