"""
Simulation Control - Controls MD simulation execution
"""

import subprocess
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)


class SimulationControl:
    """Controls MD simulation execution"""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        
    def pause_simulation(self) -> bool:
        """Pause running simulation"""
        try:
            result = subprocess.run(
                "wsl pkill -STOP gmx",
                shell=True,
                capture_output=True
            )
            logger.info("Simulation paused")
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Failed to pause simulation: {e}")
            return False
    
    def resume_simulation(self) -> bool:
        """Resume paused simulation"""
        try:
            result = subprocess.run(
                "wsl pkill -CONT gmx",
                shell=True,
                capture_output=True
            )
            logger.info("Simulation resumed")
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Failed to resume simulation: {e}")
            return False
    
    def stop_simulation(self) -> bool:
        """Stop simulation completely"""
        try:
            result = subprocess.run(
                "wsl pkill gmx",
                shell=True,
                capture_output=True
            )
            logger.info("Simulation stopped")
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Failed to stop simulation: {e}")
            return False
    
    def is_simulation_running(self) -> bool:
        """Check if simulation is running"""
        try:
            result = subprocess.run(
                "wsl ps aux | grep gmx | grep -v grep",
                shell=True,
                capture_output=True
            )
            return result.returncode == 0
        except:
            return False
    
    def get_simulation_pid(self) -> Optional[int]:
        """Get simulation process ID"""
        try:
            result = subprocess.run(
                "wsl pgrep -f gmx",
                shell=True,
                capture_output=True,
                text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                return int(result.stdout.strip().split()[0])
        except:
            pass
        return None


def pause_simulation(project_path: str = "") -> bool:
    """Standalone function to pause simulation"""
    control = SimulationControl(project_path)
    return control.pause_simulation()


def stop_simulation(project_path: str = "") -> bool:
    """Standalone function to stop simulation"""
    control = SimulationControl(project_path)
    return control.stop_simulation()
