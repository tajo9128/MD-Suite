"""
Health Monitor Module for BioDockify MD Universal
Monitors system health during MD simulations
"""

import os
import logging
import subprocess
from typing import Dict, Optional
import psutil

logger = logging.getLogger(__name__)


class HealthMonitor:
    """
    Monitors system health during MD simulations.
    
    Tracks CPU, memory, GPU, and disk usage to ensure
    simulations run reliably.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize health monitor.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        
        # Thresholds
        self.cpu_limit = self.config.get("cpu_limit_percent", 95)
        self.memory_limit = self.config.get("memory_limit_percent", 90)
        self.disk_limit = self.config.get("disk_limit_gb", 5)
        self.gpu_temp_limit = self.config.get("gpu_temp_limit_celsius", 85)
        
        # Last health check
        self._last_health: Optional[Dict] = None
        
    def check_health(self) -> Dict:
        """
        Perform comprehensive health check.
        
        Returns:
            Dictionary with health status
        """
        health = {
            "status": "healthy",
            "cpu": {},
            "memory": {},
            "disk": {},
            "gpu": {},
            "issues": []
        }
        
        # Check CPU
        cpu_health = self._check_cpu()
        health["cpu"] = cpu_health
        if cpu_health["status"] != "ok":
            health["issues"].append(cpu_health["message"])
            if cpu_health["status"] == "critical":
                health["status"] = "critical"
                
        # Check memory
        memory_health = self._check_memory()
        health["memory"] = memory_health
        if memory_health["status"] != "ok":
            health["issues"].append(memory_health["message"])
            if memory_health["status"] == "critical":
                health["status"] = "critical"
                
        # Check disk
        disk_health = self._check_disk()
        health["disk"] = disk_health
        if disk_health["status"] != "ok":
            health["issues"].append(disk_health["message"])
            if disk_health["status"] == "critical":
                health["status"] = "critical"
                
        # Check GPU
        gpu_health = self._check_gpu()
        health["gpu"] = gpu_health
        if gpu_health["status"] != "ok":
            health["issues"].append(gpu_health["message"])
            if gpu_health["status"] == "critical":
                health["status"] = "critical"
                
        # Set overall status
        if not health["issues"]:
            health["status"] = "healthy"
        elif health["status"] != "critical":
            health["status"] = "warning"
            
        # Add message
        if health["issues"]:
            health["message"] = "; ".join(health["issues"])
        else:
            health["message"] = "All systems healthy"
            
        self._last_health = health
        return health
        
    def _check_cpu(self) -> Dict:
        """Check CPU health"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            result = {
                "percent": cpu_percent,
                "count": cpu_count,
                "status": "ok"
            }
            
            if cpu_percent > self.cpu_limit:
                result["status"] = "critical"
                result["message"] = f"CPU usage critical: {cpu_percent:.1f}%"
            elif cpu_percent > 80:
                result["status"] = "warning"
                result["message"] = f"CPU usage high: {cpu_percent:.1f}%"
                
            return result
            
        except Exception as e:
            logger.error(f"CPU check failed: {e}")
            return {"status": "unknown", "error": str(e)}
            
    def _check_memory(self) -> Dict:
        """Check memory health"""
        try:
            memory = psutil.virtual_memory()
            
            result = {
                "percent": memory.percent,
                "available_gb": memory.available / (1024**3),
                "total_gb": memory.total / (1024**3),
                "status": "ok"
            }
            
            if memory.percent > self.memory_limit:
                result["status"] = "critical"
                result["message"] = f"Memory usage critical: {memory.percent:.1f}%"
            elif memory.percent > 75:
                result["status"] = "warning"
                result["message"] = f"Memory usage high: {memory.percent:.1f}%"
                
            return result
            
        except Exception as e:
            logger.error(f"Memory check failed: {e}")
            return {"status": "unknown", "error": str(e)}
            
    def _check_disk(self) -> Dict:
        """Check disk health"""
        try:
            disk = psutil.disk_usage('/')
            free_gb = disk.free / (1024**3)
            
            result = {
                "percent": disk.percent,
                "free_gb": free_gb,
                "total_gb": disk.total / (1024**3),
                "status": "ok"
            }
            
            if free_gb < self.disk_limit:
                result["status"] = "critical"
                result["message"] = f"Disk space critical: {free_gb:.2f}GB free"
            elif free_gb < self.disk_limit * 2:
                result["status"] = "warning"
                result["message"] = f"Disk space low: {free_gb:.2f}GB free"
                
            return result
            
        except Exception as e:
            logger.error(f"Disk check failed: {e}")
            return {"status": "unknown", "error": str(e)}
            
    def _check_gpu(self) -> Dict:
        """Check GPU health via nvidia-smi"""
        result = {
            "available": False,
            "status": "ok",
            "details": {}
        }
        
        try:
            # Try NVIDIA GPU
            output = subprocess.check_output(
                "wsl nvidia-smi --query-gpu=index,name,temperature.gpu,utilization.gpu,memory.used,memory.total --format=csv,noheader",
                shell=True,
                stderr=subprocess.DEVNULL
            ).decode("utf-8", errors="ignore").strip()
            
            if output:
                result["available"] = True
                lines = output.split('\n')
                
                gpu_info = []
                for line in lines:
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) >= 5:
                        gpu_info.append({
                            "index": parts[0],
                            "name": parts[1],
                            "temp_celsius": int(parts[2]),
                            "utilization_percent": int(parts[3]),
                            "memory_used_mb": int(parts[4]),
                            "memory_total_mb": int(parts[5])
                        })
                        
                result["details"] = gpu_info
                
                # Check for issues
                for gpu in gpu_info:
                    if gpu["temp_celsius"] > self.gpu_temp_limit:
                        result["status"] = "critical"
                        result["message"] = f"GPU temperature critical: {gpu['temp_celsius']}°C"
                    elif gpu["temp_celsius"] > 75:
                        result["status"] = "warning"
                        result["message"] = f"GPU temperature high: {gpu['temp_celsius']}°C"
                        
        except subprocess.CalledProcessError:
            # No NVIDIA GPU
            result["available"] = False
            logger.debug("No NVIDIA GPU detected")
            
        except Exception as e:
            logger.debug(f"GPU check failed: {e}")
            result["error"] = str(e)
            
        return result
        
    def get_last_health(self) -> Optional[Dict]:
        """Get the last health check result"""
        return self._last_health
        
    def get_system_info(self) -> Dict:
        """Get detailed system information"""
        return {
            "cpu": {
                "count": psutil.cpu_count(logical=False),
                "logical_count": psutil.cpu_count(logical=True),
                "percent": psutil.cpu_percent(interval=1, percpu=True)
            },
            "memory": psutil.virtual_memory()._asdict(),
            "disk": psutil.disk_usage('/')._asdict(),
            "boot_time": psutil.boot_time(),
            "platform": os.name
        }


def monitor_system() -> Dict:
    """
    Standalone function to monitor system health.
    
    Returns:
        Health status dictionary
    """
    monitor = HealthMonitor()
    return monitor.check_health()


if __name__ == "__main__":
    # Test health monitor
    print("Testing Health Monitor...")
    
    monitor = HealthMonitor()
    health = monitor.check_health()
    
    print(f"Status: {health['status']}")
    print(f"Message: {health['message']}")
    print(f"CPU: {health['cpu']}")
    print(f"Memory: {health['memory']}")
    print(f"Disk: {health['disk']}")
    print(f"GPU: {health['gpu']}")
