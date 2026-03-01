"""
BioDockify AI Brain - Autonomous MD Simulation Manager
The central intelligence for monitoring, maintaining, and managing MD simulations
"""

import os
import sys
import logging
import threading
import time
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class MDTask:
    """Represents an MD simulation task"""
    task_id: str
    project_path: str
    total_ns: float
    segment_ns: float
    status: str = "pending"  # pending, running, completed, failed, paused
    current_segment: int = 0
    progress_percent: float = 0.0
    simulated_ns: float = 0.0
    errors: List[str] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


@dataclass
class SystemHealth:
    """System health status"""
    status: str = "healthy"  # healthy, warning, critical
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    disk_free_gb: float = 0.0
    gpu_available: bool = False
    gpu_temp_celsius: int = 0
    gpu_utilization: int = 0
    issues: List[str] = field(default_factory=list)


class BioDockifyAIBrain:
    """
    Autonomous AI Brain for MD Simulations.
    
    Responsibilities:
    - Monitoring: Track simulation progress, system health, logs
    - Maintenance: Auto-resume, checkpoint management, cleanup
    - Communication: Notify users via Telegram/Discord/etc.
    - Task Completion: Execute MD tasks autonomously
    
    Uses Nanobot architecture with:
    - Perception Layer: log_watcher, gpu_monitor, disk_monitor
    - Reasoning Layer: error_detector, progress_analyzer, stability_checker
    - Action Layer: simulation_control, finalization_trigger
    - Communication Layer: telegram, whatsapp, discord, email
    - Memory Layer: state_manager
    """
    
    def __init__(
        self,
        project_path: str,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize BioDockify AI Brain.
        
        Args:
            project_path: Path to MD project
            config: Configuration dictionary
        """
        self.project_path = project_path
        self.config = config or {}
        
        self.is_running = False
        self.supervision_thread: Optional[threading.Thread] = None
        self.check_interval = self.config.get("check_interval_seconds", 30)
        
        self.current_task: Optional[MDTask] = None
        self.system_health = SystemHealth()
        
        self._initialize_subsystems()
        
    def _initialize_subsystems(self):
        """Initialize all subsystems including Nanobot architecture"""
        logger.info("Initializing BioDockify AI subsystems...")
        
        try:
            from core.gpu_detector import detect_gpu
            from core.backend_selector import select_backend
            from core.segment_manager import SegmentManager
            from core.resume_manager import ResumeManager
            from core.shutdown_guard import register_shutdown_handler
        except ImportError:
            import sys
            from pathlib import Path
            project_root = Path(__file__).parent.parent
            sys.path.insert(0, str(project_root))
            from core.gpu_detector import detect_gpu
            from core.backend_selector import select_backend
            from core.segment_manager import SegmentManager
            from core.resume_manager import ResumeManager
            from core.shutdown_guard import register_shutdown_handler
        
        self.gpu_info = detect_gpu()
        self.backend = select_backend(self.gpu_info)
        
        total_ns = self.config.get("total_ns", 100)
        segment_ns = self.config.get("segment_ns", 10)
        
        self.segment_manager = SegmentManager(self.project_path, total_ns, segment_ns)
        self.resume_manager = ResumeManager(self.project_path)
        
        # Initialize Nanobot subsystems
        self._init_nanobot_subsystems()
        
        self._init_notification_system()
        self._init_monitoring()
        
        logger.info(f"BioDockify AI initialized - Backend: {self.backend}")
        
    def _init_nanobot_subsystems(self):
        """Initialize Nanobot perception, reasoning, action, and memory layers"""
        try:
            # Perception Layer
            from biodockify_ai.nanobot.perception.log_watcher import LogWatcher
            from biodockify_ai.nanobot.perception.gpu_monitor import GPUMonitor
            from biodockify_ai.nanobot.perception.disk_monitor import DiskMonitor
            
            self.nanobot_log_watcher = LogWatcher(self.project_path)
            self.nanobot_gpu_monitor = GPUMonitor()
            self.nanobot_disk_monitor = DiskMonitor(self.project_path)
            
            # Reasoning Layer
            from biodockify_ai.nanobot.reasoning.error_detector import ErrorDetector
            from biodockify_ai.nanobot.reasoning.progress_analyzer import ProgressAnalyzer
            from biodockify_ai.nanobot.reasoning.stability_checker import StabilityChecker
            
            total_ns = self.config.get("total_ns", 100)
            self.nanobot_error_detector = ErrorDetector(self.project_path)
            self.nanobot_progress_analyzer = ProgressAnalyzer(total_ns)
            self.nanobot_stability_checker = StabilityChecker(self.project_path)
            
            # Action Layer
            from biodockify_ai.nanobot.actions.simulation_control import SimulationControl
            from biodockify_ai.nanobot.actions.finalization_trigger import FinalizationTrigger
            
            self.nanobot_sim_control = SimulationControl(self.project_path)
            self.nanobot_finalizer = FinalizationTrigger(self.project_path)
            
            # Memory Layer
            from biodockify_ai.nanobot.memory.state_manager import StateManager
            self.nanobot_state = StateManager(self.project_path)
            
            # Communication Layer (initialized separately)
            self.nanobot_telegram = None
            self.nanobot_whatsapp = None
            self.nanobot_discord = None
            self.nanobot_email = None
            
            logger.info("Nanobot subsystems initialized successfully")
            
        except Exception as e:
            logger.warning(f"Nanobot init failed: {e}")
            
    def _init_notification_system(self):
        """Initialize notification system"""
        self.notification_enabled = True
        logger.info("Notification system initialized (basic mode)")
            
    def _init_monitoring(self):
        """Initialize monitoring subsystem"""
        try:
            self.monitor = MDMonitor(self.project_path)
            logger.info("Monitoring system initialized")
        except Exception as e:
            logger.warning(f"Monitor init failed: {e}")
            self.monitor = None
            
    def start(self):
        """Start the BioDockify AI brain"""
        if self.is_running:
            logger.warning("BioDockify AI already running")
            return
            
        logger.info("Starting BioDockify AI...")
        self.is_running = True
        
        self.supervision_thread = threading.Thread(
            target=self._supervision_loop,
            daemon=True,
            name="BioDockifyAI-Supervisor"
        )
        self.supervision_thread.start()
        
        self._notify_user("BioDockify AI Started", 
                         f"Monitoring project: {self.project_path}", use_emoji=False)
        
    def stop(self):
        """Stop the BioDockify AI brain"""
        if not self.is_running:
            return
            
        logger.info("Stopping BioDockify AI...")
        self.is_running = False
        
        if self.supervision_thread:
            self.supervision_thread.join(timeout=10)
            
        self._notify_user("BioDockify AI Stopped",
                         "AI supervision has ended", use_emoji=False)
        
    def _supervision_loop(self):
        """Main supervision loop - runs continuously"""
        logger.info("Supervision loop started")
        
        while self.is_running:
            try:
                self._check_system_health()
                self._check_simulation_status()
                self._perform_maintenance()
                self._decide_and_act()
                
            except Exception as e:
                logger.error(f"Supervision error: {e}")
                
            time.sleep(self.check_interval)
            
        logger.info("Supervision loop ended")
        
    def _check_system_health(self):
        """Check system health metrics"""
        try:
            import psutil
            
            self.system_health.cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            self.system_health.memory_percent = memory.percent
            
            disk = psutil.disk_usage('/')
            self.system_health.disk_free_gb = disk.free / (1024**3)
            
            if self.system_health.cpu_percent > 95:
                self.system_health.status = "critical"
                self.system_health.issues.append(f"CPU critical: {self.system_health.cpu_percent}%")
            elif self.system_health.cpu_percent > 80:
                self.system_health.status = "warning"
                
            if self.system_health.memory_percent > 90:
                self.system_health.status = "critical"
                self.system_health.issues.append(f"Memory critical: {self.system_health.memory_percent}%")
                
            if self.system_health.disk_free_gb < 5:
                self.system_health.status = "critical"
                self.system_health.issues.append(f"Disk low: {self.system_health.disk_free_gb:.1f}GB")
                
            self._check_gpu_health()
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            
    def _check_gpu_health(self):
        """Check GPU health"""
        try:
            import subprocess
            output = subprocess.check_output(
                "wsl nvidia-smi --query-gpu=temperature.gpu,utilization.gpu --format=csv,noheader",
                shell=True,
                stderr=subprocess.DEVNULL
            ).decode().strip()
            
            if output:
                parts = output.split(',')
                self.system_health.gpu_available = True
                self.system_health.gpu_temp_celsius = int(parts[0].strip())
                self.system_health.gpu_utilization = int(parts[1].strip())
                
                if self.system_health.gpu_temp_celsius > 85:
                    self.system_health.status = "critical"
                    self.system_health.issues.append(f"GPU hot: {self.system_health.gpu_temp_celsius}°C")
                    
        except Exception:
            self.system_health.gpu_available = False
            
    def _check_simulation_status(self):
        """Check current simulation status"""
        if not self.segment_manager:
            return
            
        try:
            completed, total = self.segment_manager.get_progress()
            
            if self.current_task:
                self.current_task.progress_percent = self.segment_manager.get_progress_percentage()
                self.current_task.simulated_ns = self.segment_manager.get_simulated_ns()
                self.current_task.current_segment = completed
                
        except Exception as e:
            logger.error(f"Simulation status check failed: {e}")
            
    def _perform_maintenance(self):
        """Perform maintenance tasks"""
        try:
            self._check_resume()
            self._cleanup_old_checkpoints()
            
        except Exception as e:
            logger.error(f"Maintenance error: {e}")
            
    def _check_resume(self):
        """Check if simulation can be resumed"""
        if self.resume_manager:
            resume_info = self.resume_manager.get_resume_info()
            if resume_info and not self._is_simulation_running():
                logger.info(f"Found incomplete simulation, resuming from segment {resume_info['segment_id']}")
                self._notify_user("Resuming Simulation",
                                 f"Continuing from segment {resume_info['segment_id']}", use_emoji=False)
                
    def _cleanup_old_checkpoints(self):
        """Clean up old checkpoint files"""
        pass
        
    def _is_simulation_running(self) -> bool:
        """Check if simulation is currently running"""
        try:
            import subprocess
            result = subprocess.run(
                "wsl ps aux | grep gmx | grep -v grep",
                shell=True,
                capture_output=True
            )
            return result.returncode == 0
        except:
            return False
            
    def _decide_and_act(self):
        """AI decision making - analyze situation and take action"""
        if self.system_health.status == "critical":
            self._handle_critical_state()
            return
            
        if self._is_simulation_running():
            self._monitor_running_simulation()
        else:
            self._start_or_resume_simulation()
            
    def _handle_critical_state(self):
        """Handle critical system state"""
        issues = "; ".join(self.system_health.issues)
        self._notify_user("WARNING: Critical System State", issues, use_emoji=False)
        
        if "disk" in issues.lower():
            logger.warning("Low disk space - simulation may fail")
            
    def _monitor_running_simulation(self):
        """Monitor a running simulation"""
        if self.monitor:
            status = self.monitor.check_progress()
            
            if status.get("errors"):
                self._notify_user("WARNING: Simulation Error",
                                "\n".join(status["errors"][:3]), use_emoji=False)
                
    def _start_or_resume_simulation(self):
        """Start new or resume existing simulation"""
        if self.current_task and self.current_task.status == "completed":
            return
            
        if self.resume_manager:
            resume_info = self.resume_manager.get_resume_info()
            
        self._notify_user("Starting Simulation",
                         f"Backend: {self.backend}\nGPU: {self.gpu_info.get('vendor', 'CPU')}", use_emoji=False)
        
    def _notify_user(self, title: str, message: str, use_emoji: bool = True):
        """Send notification to user"""
        if not use_emoji:
            title = title.replace(chr(0x1F408), "").replace(chr(0x26A0), "").replace(chr(0x25B6), "").strip()
        
        if not self.notification_enabled:
            logger.info(f"Notification: {title} - {message}")
            return
            
        logger.info(f"Notifying user: {title}")
        
    def get_status(self) -> Dict[str, Any]:
        """Get current status"""
        return {
            "is_running": self.is_running,
            "project_path": self.project_path,
            "backend": self.backend,
            "gpu_info": self.gpu_info,
            "system_health": {
                "status": self.system_health.status,
                "cpu": self.system_health.cpu_percent,
                "memory": self.system_health.memory_percent,
                "disk_gb": self.system_health.disk_free_gb,
                "gpu_available": self.system_health.gpu_available,
                "gpu_temp": self.system_health.gpu_temp_celsius
            },
            "task": {
                "status": self.current_task.status if self.current_task else None,
                "progress": self.current_task.progress_percent if self.current_task else 0,
                "segment": self.current_task.current_segment if self.current_task else 0
            }
        }


class MDMonitor:
    """Monitor for MD simulation progress and health"""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        
    def check_progress(self) -> Dict[str, Any]:
        """Check simulation progress"""
        import os
        
        result = {
            "is_running": False,
            "progress_percent": 0.0,
            "simulated_ns": 0.0,
            "errors": [],
            "warnings": []
        }
        
        for root, dirs, files in os.walk(self.project_path):
            for f in files:
                if f == "md.log":
                    result.update(self._parse_log(os.path.join(root, f)))
                    break
                    
        return result
        
    def _parse_log(self, log_file: str) -> Dict[str, Any]:
        """Parse GROMACS log file"""
        import re
        
        result = {"is_running": False, "errors": [], "warnings": []}
        
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            if "Finished mdrun" not in content and "GROMACS reminds you" not in content:
                result["is_running"] = True
                
            for line in content.split('\n'):
                if "ERROR" in line:
                    result["errors"].append(line.strip()[:100])
                if "WARNING" in line:
                    result["warnings"].append(line.strip()[:100])
                    
        except Exception as e:
            logger.error(f"Log parse error: {e}")
            
        return result


def create_biobot(
    project_path: str,
    config: Optional[Dict[str, Any]] = None
) -> BioDockifyAIBrain:
    """
    Factory function to create BioDockify AI Brain.
    
    Args:
        project_path: Path to MD project
        config: Optional configuration
        
    Returns:
        BioDockifyAIBrain instance
    """
    return BioDockifyAIBrain(project_path, config)
