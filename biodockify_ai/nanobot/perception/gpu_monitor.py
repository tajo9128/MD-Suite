"""
GPU Monitor - Monitors GPU health and utilization
Supports NVIDIA (nvidia-smi), AMD (rocm-smi), and Intel GPUs
"""

import subprocess
import logging
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)


class GPUMonitor:
    """Monitors GPU status"""
    
    def __init__(self):
        self.gpu_type = self._detect_gpu_type()
        
    def _detect_gpu_type(self) -> str:
        """Detect GPU type"""
        try:
            subprocess.run("wsl nvidia-smi", shell=True, capture_output=True, timeout=5)
            return "nvidia"
        except:
            pass
            
        try:
            subprocess.run("wsl rocm-smi", shell=True, capture_output=True, timeout=5)
            return "amd"
        except:
            pass
            
        return "unknown"
    
    def get_gpu_status(self) -> Dict:
        """Get current GPU status"""
        result = {
            "available": False,
            "type": self.gpu_type,
            "temperature_celsius": 0,
            "utilization_percent": 0,
            "memory_used_mb": 0,
            "memory_total_mb": 0,
            "power_watts": 0,
            "error": None
        }
        
        if self.gpu_type == "nvidia":
            return self._get_nvidia_status(result)
        elif self.gpu_type == "amd":
            return self._get_amd_status(result)
        else:
            result["error"] = "No GPU detected"
            return result
    
    def _get_nvidia_status(self, result: Dict) -> Dict:
        """Get NVIDIA GPU status"""
        try:
            output = subprocess.check_output(
                "wsl nvidia-smi --query-gpu=index,name,temperature.gpu,utilization.gpu,memory.used,memory.total,power.draw --format=csv,noheader",
                shell=True,
                stderr=subprocess.DEVNULL,
                timeout=10
            ).decode("utf-8", errors="ignore").strip()
            
            if output:
                lines = output.split('\n')
                gpu_info = []
                for line in lines:
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) >= 6:
                        gpu_info.append({
                            "index": int(parts[0]),
                            "name": parts[1],
                            "temperature_celsius": int(parts[2]),
                            "utilization_percent": int(parts[3]),
                            "memory_used_mb": int(parts[4]),
                            "memory_total_mb": int(parts[5]),
                            "power_watts": float(parts[6]) if len(parts) > 6 else 0
                        })
                        
                result["available"] = True
                if gpu_info:
                    result["temperature_celsius"] = gpu_info[0]["temperature_celsius"]
                    result["utilization_percent"] = gpu_info[0]["utilization_percent"]
                    result["memory_used_mb"] = gpu_info[0]["memory_used_mb"]
                    result["memory_total_mb"] = gpu_info[0]["memory_total_mb"]
                    result["power_watts"] = gpu_info[0]["power_watts"]
                    result["gpu_info"] = gpu_info
                    
        except subprocess.CalledProcessError as e:
            result["error"] = "nvidia-smi command failed"
            logger.debug(f"GPU status error: {e}")
        except Exception as e:
            result["error"] = str(e)
            
        return result
    
    def _get_amd_status(self, result: Dict) -> Dict:
        """Get AMD GPU status"""
        try:
            output = subprocess.check_output(
                "wsl rocm-smi --query-gpu=index,name,temperature.gpu,utilization.gpu,memory.used,memory.total,power.draw --format=csv,noheader",
                shell=True,
                stderr=subprocess.DEVNULL,
                timeout=10
            ).decode("utf-8", errors="ignore").strip()
            
            if output:
                result["available"] = True
                result["error"] = "AMD GPU detected (parsing not implemented)"
                
        except Exception as e:
            result["error"] = str(e)
            
        return result
    
    def is_overheating(self, threshold: int = 85) -> bool:
        """Check if GPU is overheating"""
        status = self.get_gpu_status()
        return status.get("temperature_celsius", 0) > threshold
    
    def is_available(self) -> bool:
        """Check if GPU is available"""
        status = self.get_gpu_status()
        return status.get("available", False)


def get_gpu_status() -> Dict:
    """Standalone function to get GPU status"""
    monitor = GPUMonitor()
    return monitor.get_gpu_status()
