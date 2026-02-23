"""
Shutdown Guard Module for BioDockify MD Universal
Handles graceful shutdown and ensures safe simulation resume
"""

import signal
import sys
import os
import logging
from typing import Optional, Callable
from datetime import datetime

logger = logging.getLogger(__name__)

# Global state for shutdown handling
_shutdown_handler_registered = False
_simulation_running = False
_cleanup_callback: Optional[Callable] = None
_shutdown_time: Optional[datetime] = None


def register_shutdown_handler(cleanup_callback: Optional[Callable] = None):
    """
    Register signal handlers for graceful shutdown.
    
    Args:
        cleanup_callback: Optional callback function to execute on shutdown
    """
    global _shutdown_handler_registered, _cleanup_callback
    
    _cleanup_callback = cleanup_callback
    
    def signal_handler(signum, frame):
        """Handle shutdown signals gracefully"""
        global _simulation_running, _shutdown_time
        
        signal_name = signal.Signals(signum).name
        logger.warning(f"Received {signal_name} signal!")
        
        _shutdown_time = datetime.now()
        
        if _simulation_running:
            logger.info("Simulation is running...")
            logger.info("Checkpoint will be saved automatically by GROMACS")
            logger.info("Resume will continue on next startup")
            
            # Save state file for resume
            _save_shutdown_state()
            
            # Execute cleanup callback if provided
            if _cleanup_callback:
                try:
                    _cleanup_callback()
                except Exception as e:
                    logger.error(f"Cleanup callback failed: {e}")
        
        logger.info("Shutdown complete. Run again to resume simulation.")
        sys.exit(0)
    
    # Register handlers for common shutdown signals
    signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)   # Kill command
    signal.signal(signal.SIGBREAK, signal_handler)  # Ctrl+Break on Windows
    
    _shutdown_handler_registered = True
    logger.info("Shutdown handler registered")


def _save_shutdown_state():
    """Save shutdown state to file for resume detection"""
    try:
        state_file = os.path.join(os.getcwd(), ".biodockify_shutdown_state")
        
        state_data = {
            "timestamp": datetime.now().isoformat(),
            "shutdown_time": _shutdown_time.isoformat() if _shutdown_time else None,
            "cwd": os.getcwd(),
            "simulation_pid": os.getpid()
        }
        
        import json
        with open(state_file, 'w') as f:
            json.dump(state_data, f, indent=2)
            
        logger.info(f"Shutdown state saved to {state_file}")
        
    except Exception as e:
        logger.error(f"Failed to save shutdown state: {e}")


def load_shutdown_state() -> Optional[dict]:
    """Load shutdown state from file if it exists"""
    try:
        state_file = os.path.join(os.getcwd(), ".biodockify_shutdown_state")
        
        if os.path.exists(state_file):
            import json
            with open(state_file, 'r') as f:
                state = json.load(f)
            logger.info(f"Found previous shutdown state: {state.get('timestamp')}")
            return state
            
    except Exception as e:
        logger.error(f"Failed to load shutdown state: {e}")
        
    return None


def clear_shutdown_state():
    """Clear the shutdown state file"""
    try:
        state_file = os.path.join(os.getcwd(), ".biodockify_shutdown_state")
        if os.path.exists(state_file):
            os.remove(state_file)
            logger.info("Shutdown state cleared")
    except Exception as e:
        logger.error(f"Failed to clear shutdown state: {e}")


def set_simulation_running(running: bool = True):
    """
    Set the simulation running state.
    
    Args:
        running: Whether simulation is currently running
    """
    global _simulation_running
    _simulation_running = running
    
    if running:
        logger.info("Simulation started")
    else:
        logger.info("Simulation stopped")


def is_simulation_running() -> bool:
    """Check if simulation is marked as running"""
    return _simulation_running


class SimulationGuard:
    """
    Context manager for simulation execution with shutdown protection.
    
    Usage:
        with SimulationGuard():
            run_simulation()
    """
    
    def __init__(self, cleanup_callback: Optional[Callable] = None):
        self.cleanup_callback = cleanup_callback
        
    def __enter__(self):
        global _simulation_running
        _simulation_running = True
        
        # Check for previous shutdown
        state = load_shutdown_state()
        if state:
            logger.info("Resuming from previous session")
            
        register_shutdown_handler(self.cleanup_callback)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        global _simulation_running
        _simulation_running = False
        
        if exc_type is not None:
            logger.error(f"Simulation error: {exc_val}")
            _save_shutdown_state()
        else:
            clear_shutdown_state()
            
        return False  # Don't suppress exceptions


def check_disk_space(min_gb: float = 5.0) -> bool:
    """
    Check available disk space before starting simulation.
    
    Args:
        min_gb: Minimum required free space in GB
        
    Returns:
        True if enough space available
    """
    try:
        import psutil
        disk = psutil.disk_usage('/')
        free_gb = disk.free / (1024**3)
        
        logger.info(f"Free disk space: {free_gb:.2f} GB")
        
        if free_gb < min_gb:
            logger.warning(f"Low disk space: {free_gb:.2f} GB < {min_gb} GB")
            return False
            
        return True
        
    except Exception as e:
        logger.error(f"Disk space check failed: {e}")
        return True  # Allow to proceed if check fails


def check_temperature_limit(max_celsius: float = 85.0) -> bool:
    """
    Check system temperature (if available).
    
    Args:
        max_celsius: Maximum allowed temperature
        
    Returns:
        True if temperature is acceptable
    """
    try:
        # Try to get GPU temperature via nvidia-smi
        import subprocess
        output = subprocess.check_output(
            "wsl nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader",
            shell=True,
            stderr=subprocess.DEVNULL
        ).decode("utf-8", errors="ignore").strip()
        
        if output:
            temp = int(output.split()[0])
            logger.info(f"GPU Temperature: {temp}°C")
            
            if temp > max_celsius:
                logger.warning(f"GPU temperature too high: {temp}°C > {max_celsius}°C")
                return False
                
        return True
        
    except Exception as e:
        logger.debug(f"Temperature check not available: {e}")
        return True  # Allow to proceed if check fails


if __name__ == "__main__":
    # Test shutdown handler
    logging.basicConfig(level=logging.INFO)
    
    print("Testing Shutdown Guard...")
    register_shutdown_handler()
    
    print("Simulation running... Press Ctrl+C to test")
    import time
    set_simulation_running(True)
    time.sleep(2)
    set_simulation_running(False)
    
    print("Shutdown guard test complete")
