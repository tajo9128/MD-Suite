"""
GPU Detection Module for BioDockify MD Universal
Detects available GPU hardware (NVIDIA, AMD, Intel) or falls back to CPU
"""

import subprocess
import os
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


def detect_gpu() -> Dict[str, any]:
    """
    Detect available GPU hardware using WSL lspci command.
    
    Returns:
        Dict containing:
            - vendor: str - GPU vendor ("NVIDIA", "AMD", "Intel", "CPU")
            - vram: int - VRAM in MB (0 for CPU)
            - compute_capability: Optional[str] - For NVIDIA GPUs
    """
    result = {
        "vendor": "CPU",
        "vram": 0,
        "compute_capability": None,
        "device_name": "CPU Fallback"
    }
    
    try:
        # Try to detect GPU via WSL
        output = subprocess.check_output(
            "wsl lspci | grep -i vga",
            shell=True,
            stderr=subprocess.DEVNULL
        ).decode("utf-8", errors="ignore")
        
        logger.info(f"PCI detection output: {output}")
        
        if "NVIDIA" in output or "nvidia" in output:
            result["vendor"] = "NVIDIA"
            result["device_name"] = _get_nvidia_device_name()
            result["compute_capability"] = _get_nvidia_compute_capability()
            result["vram"] = _get_nvidia_vram()
            
        elif "AMD" in output or "Radeon" in output:
            result["vendor"] = "AMD"
            result["device_name"] = _get_amd_device_name()
            result["vram"] = _get_amd_vram()
            
        elif "Intel" in output or "Intel" in output:
            result["vendor"] = "Intel"
            result["device_name"] = "Intel Integrated Graphics"
            result["vram"] = _get_intel_vram()
        else:
            logger.warning("No GPU detected, using CPU fallback")
            
    except subprocess.CalledProcessError as e:
        logger.warning(f"WSL lspci failed, trying Windows detection: {e}")
        result = _detect_via_windows()
        
    except Exception as e:
        logger.error(f"GPU detection error: {e}")
        
    logger.info(f"Detected hardware: {result}")
    return result


def _get_nvidia_device_name() -> str:
    """Get NVIDIA GPU device name via nvidia-smi"""
    try:
        output = subprocess.check_output(
            "wsl nvidia-smi --query-gpu=name --format=csv,noheader",
            shell=True,
            stderr=subprocess.DEVNULL
        ).decode("utf-8", errors="ignore").strip()
        return output.split('\n')[0] if output else "NVIDIA GPU"
    except:
        return "NVIDIA GPU"


def _get_nvidia_compute_capability() -> Optional[str]:
    """Get NVIDIA GPU compute capability"""
    try:
        output = subprocess.check_output(
            "wsl nvidia-smi --query-gpu=compute_cap --format=csv,noheader",
            shell=True,
            stderr=subprocess.DEVNULL
        ).decode("utf-8", errors="ignore").strip()
        return output.split('\n')[0] if output else None
    except:
        return None


def _get_nvidia_vram() -> int:
    """Get NVIDIA GPU VRAM in MB"""
    try:
        output = subprocess.check_output(
            "wsl nvidia-smi --query-gpu=memory.total --format=csv,noheader",
            shell=True,
            stderr=subprocess.DEVNULL
        ).decode("utf-8", errors="ignore").strip()
        if output:
            # Extract number from "1234 MiB"
            return int(output.split()[0])
        return 0
    except:
        return 0


def _get_amd_device_name() -> str:
    """Get AMD GPU device name"""
    try:
        output = subprocess.check_output(
            "wsl lspci | grep -i vga | grep -i amd",
            shell=True,
            stderr=subprocess.DEVNULL
        ).decode("utf-8", errors="ignore").strip()
        return output if output else "AMD GPU"
    except:
        return "AMD GPU"


def _get_amd_vram() -> int:
    """Get AMD GPU VRAM (limited detection)"""
    # AMD detection is more limited in WSL
    return 8192  # Assume 8GB as default


def _get_intel_vram() -> int:
    """Get Intel GPU VRAM (usually shared system memory)"""
    return 4096  # Assume 4GB shared as default


def _detect_via_windows() -> Dict[str, any]:
    """Fallback: Try to detect GPU via Windows commands"""
    result = {
        "vendor": "CPU",
        "vram": 0,
        "compute_capability": None,
        "device_name": "CPU Fallback"
    }
    
    try:
        # Try wmic command for Windows GPU detection
        output = subprocess.check_output(
            "wmic path win32_VideoController get name",
            shell=True,
            stderr=subprocess.DEVNULL
        ).decode("utf-8", errors="ignore")
        
        if "NVIDIA" in output:
            result["vendor"] = "NVIDIA"
            result["device_name"] = "NVIDIA GPU"
        elif "AMD" in output or "Radeon" in output:
            result["vendor"] = "AMD"
            result["device_name"] = "AMD GPU"
        elif "Intel" in output:
            result["vendor"] = "Intel"
            result["device_name"] = "Intel GPU"
            
    except Exception as e:
        logger.debug(f"Windows GPU detection failed: {e}")
        
    return result


def is_gpu_available() -> bool:
    """Quick check if any GPU is available"""
    gpu_info = detect_gpu()
    return gpu_info["vendor"] != "CPU"


def get_backend_for_gpu(gpu_info: Dict[str, any]) -> str:
    """
    Get the appropriate GROMACS backend for the detected GPU.
    
    Args:
        gpu_info: GPU information from detect_gpu()
        
    Returns:
        Backend name: "gmx_cuda", "gmx_sycl", or "gmx_cpu"
    """
    from .backend_selector import select_backend
    return select_backend(gpu_info)


if __name__ == "__main__":
    # Test GPU detection
    print("Testing GPU Detection...")
    info = detect_gpu()
    print(f"Detected: {info}")
