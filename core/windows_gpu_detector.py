"""
Native Windows GPU Detection Module for BioDockify MD Universal
Detects GPU hardware directly on Windows without requiring WSL
Provides unified GPU detection API for both Windows native and WSL modes
"""

import subprocess
import logging
import os
import platform
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class WindowsGPUInfo:
    """Represents a GPU detected on Windows"""
    index: int
    name: str
    vendor: str
    vram_bytes: int = 0
    driver_version: str = ""
    cuda_support: bool = False
    directx_version: str = ""
    vram_mb: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "name": self.name,
            "vendor": self.vendor,
            "vram_bytes": self.vram_bytes,
            "vram_mb": self.vram_mb,
            "driver_version": self.driver_version,
            "cuda_support": self.cuda_support,
            "directx_version": self.directx_version
        }


def is_running_on_windows() -> bool:
    """Check if running on Windows"""
    return platform.system() == "Windows"


def detect_windows_gpus() -> List[WindowsGPUInfo]:
    """
    Detect GPUs on Windows using native Windows commands.
    Falls back gracefully if detection fails.
    
    Returns:
        List of WindowsGPUInfo objects
    """
    gpus = []
    
    if not is_running_on_windows():
        logger.debug("Not running on Windows, skipping native detection")
        return gpus
    
    # Try multiple detection methods
    gpus = _detect_via_powershell()
    
    if not gpus:
        gpus = _detect_via_wmic()
    
    # Add indices
    for i, gpu in enumerate(gpus):
        gpu.index = i
    
    logger.info(f"Detected {len(gpus)} GPU(s) on Windows")
    return gpus


def _detect_via_powershell() -> List[WindowsGPUInfo]:
    """Detect GPUs using PowerShell"""
    gpus = []
    
    try:
        # Use Get-CimInstance for GPU info
        ps_command = """
        Get-CimInstance Win32_VideoController | Select-Object Name, AdapterRAM, DriverVersion, DriverDate | ConvertTo-Json
        """
        
        output = subprocess.check_output(
            ["powershell", "-Command", ps_command],
            stderr=subprocess.DEVNULL,
            timeout=10,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
        )
        
        if output:
            import json
            try:
                data = json.loads(output.decode('utf-8', errors='ignore'))
                if isinstance(data, list):
                    devices = data
                else:
                    devices = [data]
                
                for dev in devices:
                    if dev.get("Name"):
                        gpu = _parse_gpu_info(dev)
                        if gpu:
                            gpus.append(gpu)
            except json.JSONDecodeError:
                logger.debug("Failed to parse PowerShell GPU output")
                
    except subprocess.TimeoutExpired:
        logger.debug("PowerShell GPU detection timed out")
    except FileNotFoundError:
        logger.debug("PowerShell not available")
    except Exception as e:
        logger.debug(f"PowerShell GPU detection error: {e}")
    
    return gpus


def _detect_via_wmic() -> List[WindowsGPUInfo]:
    """Detect GPUs using WMIC (legacy Windows)"""
    gpus = []
    
    try:
        output = subprocess.check_output(
            "wmic path win32_VideoController get Name,AdapterRAM,DriverVersion /format:csv",
            shell=True,
            stderr=subprocess.DEVNULL,
            timeout=10
        )
        
        lines = output.decode('utf-8', errors='ignore').strip().split('\n')
        
        for line in lines[1:]:  # Skip header
            if line.strip():
                parts = line.split(',')
                if len(parts) >= 3:
                    name = parts[1].strip()
                    if name and name != "Name":
                        vram_str = parts[2].strip() if len(parts) > 2 else "0"
                        driver = parts[3].strip() if len(parts) > 3 else ""
                        
                        try:
                            vram = int(vram_str) if vram_str.isdigit() else 0
                        except ValueError:
                            vram = 0
                        
                        vendor = _identify_vendor(name)
                        
                        gpus.append(WindowsGPUInfo(
                            index=len(gpus),
                            name=name,
                            vendor=vendor,
                            vram_bytes=vram,
                            vram_mb=vram // (1024 * 1024),
                            driver_version=driver
                        ))
                        
    except subprocess.TimeoutExpired:
        logger.debug("WMIC GPU detection timed out")
    except Exception as e:
        logger.debug(f"WMIC GPU detection error: {e}")
    
    return gpus


def _parse_gpu_info(dev: Dict) -> Optional[WindowsGPUInfo]:
    """Parse GPU info from PowerShell output"""
    try:
        name = dev.get("Name", "")
        if not name:
            return None
        
        vendor = _identify_vendor(name)
        
        # Get VRAM
        vram_bytes = dev.get("AdapterRAM", 0)
        if isinstance(vram_bytes, str):
            try:
                vram_bytes = int(vram_bytes)
            except ValueError:
                vram_bytes = 0
        
        vram_mb = vram_bytes // (1024 * 1024) if vram_bytes > 0 else 0
        
        # Get driver version
        driver = dev.get("DriverVersion", "")
        
        return WindowsGPUInfo(
            index=0,
            name=name,
            vendor=vendor,
            vram_bytes=vram_bytes,
            vram_mb=vram_mb,
            driver_version=driver,
            cuda_support="NVIDIA" in name.upper() or "GeForce" in name
        )
        
    except Exception as e:
        logger.debug(f"Failed to parse GPU info: {e}")
        return None


def _identify_vendor(gpu_name: str) -> str:
    """Identify GPU vendor from name"""
    name_upper = gpu_name.upper()
    
    if "NVIDIA" in name_upper or "GEFORCE" in name_upper or "QUADRO" in name_upper:
        return "NVIDIA"
    elif "AMD" in name_upper or "RADEON" in name_upper:
        return "AMD"
    elif "INTEL" in name_upper or "HD GRAPHICS" in name_upper or "IRIS" in name_upper:
        return "Intel"
    elif "Matrox" in name_upper:
        return "Matrox"
    else:
        return "Unknown"


def get_windows_gpu_utilization(gpu_name: str = None) -> Optional[Dict[str, Any]]:
    """
    Get GPU utilization on Windows using nvidia-smi or other tools.
    
    Args:
        gpu_name: Optional GPU name to target
        
    Returns:
        Dictionary with utilization info or None
    """
    # Try nvidia-smi first (works even without WSL if NVIDIA driver installed)
    try:
        output = subprocess.check_output(
            "nvidia-smi --query-gpu=index,name,temperature.gpu,utilization.gpu,memory.used,memory.total --format=csv,noheader",
            shell=True,
            stderr=subprocess.DEVNULL,
            timeout=5
        ).decode("utf-8", errors="ignore").strip()
        
        if output:
            lines = output.split('\n')
            for line in lines:
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 5:
                    # Check if this is the requested GPU
                    if gpu_name and gpu_name not in parts[1]:
                        continue
                        
                    return {
                        "index": int(parts[0]),
                        "name": parts[1],
                        "temperature_celsius": int(parts[2]) if parts[2].isdigit() else None,
                        "utilization_percent": int(parts[3]) if parts[3].isdigit() else None,
                        "memory_used_mb": int(parts[4]) if parts[4].isdigit() else None,
                        "memory_total_mb": int(parts[5]) if parts[5].isdigit() else None
                    }
                    
    except subprocess.CalledProcessError:
        pass
    except Exception as e:
        logger.debug(f"GPU utilization check error: {e}")
    
    return None


def check_windows_nvidia_driver() -> Dict[str, Any]:
    """
    Check if NVIDIA driver is installed on Windows.
    
    Returns:
        Dictionary with driver status
    """
    result = {
        "installed": False,
        "version": None,
        "cuda_version": None,
        "gpus": []
    }
    
    try:
        output = subprocess.check_output(
            "nvidia-smi",
            shell=True,
            stderr=subprocess.DEVNULL,
            timeout=5
        ).decode("utf-8", errors="ignore")
        
        if output:
            result["installed"] = True
            
            # Try to extract driver version
            for line in output.split('\n'):
                if "Driver Version:" in line:
                    result["version"] = line.split(':')[-1].strip().split()[0]
                if "CUDA Version:" in line:
                    result["cuda_version"] = line.split(':')[-1].strip()
                    
    except subprocess.CalledProcessError:
        pass
    except Exception as e:
        logger.debug(f"NVIDIA driver check error: {e}")
    
    return result


def get_windows_gpu_memory_info(gpu_index: int = 0) -> Optional[Dict[str, Any]]:
    """
    Get detailed GPU memory info on Windows.
    
    Args:
        gpu_index: GPU index to query
        
    Returns:
        Dictionary with memory info
    """
    try:
        output = subprocess.check_output(
            f"nvidia-smi --query-gpu=index,memory.total,memory.used,memory.free,memory.max_used --format=csv,noheader --id={gpu_index}",
            shell=True,
            stderr=subprocess.DEVNULL,
            timeout=5
        ).decode("utf-8", errors="ignore").strip()
        
        if output:
            parts = [p.strip() for p in output.split(',')]
            if len(parts) >= 5:
                return {
                    "index": int(parts[0]),
                    "total_mb": int(parts[1]) if parts[1].isdigit() else 0,
                    "used_mb": int(parts[2]) if parts[2].isdigit() else 0,
                    "free_mb": int(parts[3]) if parts[3].isdigit() else 0,
                    "max_used_mb": int(parts[4]) if parts[4].isdigit() else 0
                }
                
    except subprocess.CalledProcessError:
        pass
    except Exception as e:
        logger.debug(f"GPU memory info error: {e}")
    
    return None


if __name__ == "__main__":
    print("=" * 60)
    print("Windows GPU Detection Test")
    print("=" * 60)
    
    print(f"\nRunning on: {platform.system()}")
    
    # Check NVIDIA driver
    print("\n1. Checking NVIDIA Driver...")
    nvidia = check_windows_nvidia_driver()
    print(f"   Installed: {nvidia['installed']}")
    if nvidia['installed']:
        print(f"   Driver Version: {nvidia['version']}")
        print(f"   CUDA Version: {nvidia['cuda_version']}")
    
    # Detect GPUs
    print("\n2. Detecting GPUs...")
    gpus = detect_windows_gpus()
    print(f"   Found {len(gpus)} GPU(s)")
    
    for gpu in gpus:
        print(f"   - GPU {gpu.index}: {gpu.vendor} {gpu.name}")
        print(f"     VRAM: {gpu.vram_mb} MB")
        print(f"     Driver: {gpu.driver_version}")
    
    # Get utilization
    print("\n3. Checking GPU Utilization...")
    util = get_windows_gpu_utilization()
    if util:
        print(f"   Temperature: {util.get('temperature_celsius', 'N/A')}°C")
        print(f"   Utilization: {util.get('utilization_percent', 'N/A')}%")
        print(f"   Memory: {util.get('memory_used_mb', 'N/A')}/{util.get('memory_total_mb', 'N/A')} MB")
    else:
        print("   Could not get utilization")
    
    print("\n" + "=" * 60)
