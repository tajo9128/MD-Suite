"""
Continuous Event Loop for Nanobot
Runs continuous supervision of MD simulation
"""

import time
import logging
import threading
from typing import Optional, Callable
from datetime import datetime

logger = logging.getLogger(__name__)


class NanobotEventLoop:
    """
    Continuous event loop for Nanobot supervision.
    Monitors MD simulation every N seconds.
    """
    
    def __init__(
        self,
        project_path: str,
        interval_seconds: int = 5,
        on_event: Optional[Callable] = None
    ):
        self.project_path = project_path
        self.interval_seconds = interval_seconds
        self.on_event = on_event
        
        self.is_running = False
        self.loop_thread: Optional[threading.Thread] = None
        
        self.event_count = 0
        self.last_event_time = None
        
    def start(self):
        """Start the event loop"""
        if self.is_running:
            logger.warning("Event loop already running")
            return
            
        logger.info(f"Starting Nanobot event loop (interval: {self.interval_seconds}s)")
        self.is_running = True
        
        self.loop_thread = threading.Thread(
            target=self._run_loop,
            daemon=True,
            name="NanobotEventLoop"
        )
        self.loop_thread.start()
        
    def stop(self):
        """Stop the event loop"""
        if not self.is_running:
            return
            
        logger.info("Stopping Nanobot event loop")
        self.is_running = False
        
        if self.loop_thread:
            self.loop_thread.join(timeout=10)
            
    def _run_loop(self):
        """Main event loop"""
        logger.info("Nanobot event loop started")
        
        while self.is_running:
            try:
                self._process_cycle()
                self.event_count += 1
                self.last_event_time = datetime.now()
                
            except Exception as e:
                logger.error(f"Event loop error: {e}")
                
            time.sleep(self.interval_seconds)
            
        logger.info("Nanobot event loop stopped")
        
    def _process_cycle(self):
        """Process one monitoring cycle"""
        from biodockify_ai.nanobot.perception.log_watcher import LogWatcher
        from biodockify_ai.nanobot.perception.gpu_monitor import GPUMonitor
        from biodockify_ai.nanobot.perception.disk_monitor import DiskMonitor
        
        watcher = LogWatcher(self.project_path)
        gpu_monitor = GPUMonitor()
        disk_monitor = DiskMonitor(self.project_path)
        
        progress = watcher.read_progress()
        gpu_status = gpu_monitor.get_gpu_status()
        disk_status = disk_monitor.get_disk_status()
        
        cycle_data = {
            "timestamp": datetime.now().isoformat(),
            "progress": progress,
            "gpu": gpu_status,
            "disk": disk_status,
            "event_count": self.event_count
        }
        
        if self.on_event:
            self.on_event(cycle_data)
            
    def get_status(self) -> dict:
        """Get event loop status"""
        return {
            "is_running": self.is_running,
            "event_count": self.event_count,
            "last_event_time": self.last_event_time.isoformat() if self.last_event_time else None,
            "interval_seconds": self.interval_seconds
        }


class ContinuousSupervisor:
    """
    High-level continuous supervisor that combines
    event loop with decision making.
    """
    
    def __init__(self, project_path: str, config: Optional[dict] = None):
        self.project_path = project_path
        self.config = config or {}
        
        self.event_loop = NanobotEventLoop(
            project_path,
            interval_seconds=self.config.get("monitor_interval", 5),
            on_event=self._on_monitoring_event
        )
        
        self.is_supervising = False
        
    def start_supervision(self):
        """Start continuous supervision"""
        logger.info(f"Starting continuous supervision for {self.project_path}")
        self.is_supervising = True
        self.event_loop.start()
        
    def stop_supervision(self):
        """Stop continuous supervision"""
        logger.info("Stopping continuous supervision")
        self.is_supervising = False
        self.event_loop.stop()
        
    def _on_monitoring_event(self, data: dict):
        """Handle monitoring event"""
        progress = data.get("progress", {})
        gpu = data.get("gpu", {})
        disk = data.get("disk", {})
        
        if progress.get("is_running"):
            pass
            
        if gpu.get("temperature_celsius", 0) > 85:
            logger.warning("GPU overheating detected")
            
        if disk.get("free_gb", 100) < 5:
            logger.warning("Low disk space")


def start_continuous_supervision(project_path: str, interval: int = 5):
    """Start continuous supervision"""
    supervisor = ContinuousSupervisor(project_path, {"monitor_interval": interval})
    supervisor.start_supervision()
    return supervisor


def stop_continuous_supervision(supervisor: ContinuousSupervisor):
    """Stop continuous supervision"""
    supervisor.stop_supervision()
