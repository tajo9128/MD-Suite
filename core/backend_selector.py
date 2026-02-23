"""
Backend Selection Module for BioDockify MD Universal
Selects appropriate GROMACS backend based on detected hardware
"""

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


def select_backend(gpu_info: Dict[str, any]) -> str:
    """
    Select the appropriate GROMACS backend based on GPU vendor.
    
    Args:
        gpu_info: GPU information from gpu_detector.detect_gpu()
        
    Returns:
        Backend name: "gmx_cuda", "gmx_sycl", or "gmx_cpu"
    """
    vendor = gpu_info.get("vendor", "CPU")
    
    if vendor == "NVIDIA":
        logger.info("Selecting GROMACS CUDA backend for NVIDIA GPU")
        return "gmx_cuda"
    
    elif vendor == "AMD":
        logger.info("Selecting GROMACS SYCL backend for AMD GPU")
        return "gmx_sycl"
    
    elif vendor == "Intel":
        logger.info("Selecting GROMACS SYCL backend for Intel GPU")
        return "gmx_sycl"
    
    else:
        logger.info("No GPU detected, using CPU backend")
        return "gmx_cpu"


def get_backend_config(backend: str) -> Dict[str, any]:
    """
    Get configuration parameters for the selected backend.
    
    Args:
        backend: Backend name from select_backend()
        
    Returns:
        Dictionary with backend-specific configuration
    """
    configs = {
        "gmx_cuda": {
            "name": "GROMACS CUDA",
            "description": "NVIDIA GPU acceleration via CUDA",
            "mdrun_flags": ["-nb gpu", "-pme gpu", "-bonded gpu"],
            "requires": ["nvidia-smi", "gmx_mpi"],
            "typical_speedup": "10-50x vs CPU"
        },
        "gmx_sycl": {
            "name": "GROMACS SYCL",
            "description": "AMD/Intel GPU acceleration via SYCL",
            "mdrun_flags": ["-nb gpu", "-pme gpu", "-bonded gpu", "-sycl"],
            "requires": ["gmx_sycl", "oneAPI"],
            "typical_speedup": "5-20x vs CPU"
        },
        "gmx_cpu": {
            "name": "GROMACS CPU",
            "description": "CPU-only execution",
            "mdrun_flags": ["-nb cpu", "-pme cpu"],
            "requires": ["gmx"],
            "typical_speedup": "1x (baseline)"
        }
    }
    
    return configs.get(backend, configs["gmx_cpu"])


def get_mdrun_command(
    backend: str,
    tpr_file: str,
    output_prefix: str,
    resume: bool = False,
    checkpoint_interval: int = 15
) -> str:
    """
    Build the GROMACS mdrun command for the selected backend.
    
    Args:
        backend: Backend name ("gmx_cuda", "gmx_sycl", "gmx_cpu")
        tpr_file: Path to the TPR input file
        output_prefix: Output file prefix
        resume: Whether this is a resume from checkpoint
        checkpoint_interval: Checkpoint interval in minutes
        
    Returns:
        Complete mdrun command string
    """
    config = get_backend_config(backend)
    flags = " ".join(config["mdrun_flags"])
    
    # Build base command
    if backend == "gmx_cuda":
        gmx_cmd = "wsl gmx mdrun"
    elif backend == "gmx_sycl":
        gmx_cmd = "wsl gmx mdrun"
    else:
        gmx_cmd = "wsl gmx mdrun"
    
    # Build command with options
    cmd_parts = [
        gmx_cmd,
        f"-s {tpr_file}",
        f"-o {output_prefix}",
        f"-e {output_prefix}",
        f"-g {output_prefix}",
        f"-c {output_prefix}_final.gro",
        flags,
        f"-cpt {checkpoint_interval}",
    ]
    
    if resume:
        cmd_parts.append("-cpi")  # Continue from checkpoint
        cmd_parts.append("-append")  # Append to existing trajectory
    
    return " ".join(cmd_parts)


def validate_backend_availability(backend: str) -> bool:
    """
    Validate that the selected backend is actually available.
    
    Args:
        backend: Backend name to validate
        
    Returns:
        True if backend is available, False otherwise
    """
    import subprocess
    
    try:
        # Check if GROMACS is available in WSL
        output = subprocess.check_output(
            "wsl which gmx",
            shell=True,
            stderr=subprocess.DEVNULL
        ).decode("utf-8", errors="ignore").strip()
        
        if not output:
            logger.warning("GROMACS not found in WSL")
            return False
            
        # Check GROMACS version
        version = subprocess.check_output(
            "wsl gmx --version",
            shell=True,
            stderr=subprocess.DEVNULL
        ).decode("utf-8", errors="ignore")
        
        logger.info(f"GROMACS version: {version.split()[1] if version else 'unknown'}")
        
        # For GPU backends, check GPU availability
        if backend in ["gmx_cuda", "gmx_sycl"]:
            try:
                if backend == "gmx_cuda":
                    subprocess.check_output(
                        "wsl nvidia-smi",
                        shell=True,
                        stderr=subprocess.DEVNULL
                    )
                # SYCL doesn't have an easy check
                return True
            except subprocess.CalledProcessError:
                logger.warning(f"{backend} selected but GPU not available")
                return False
                
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Backend validation failed: {e}")
        return False


def get_optimal_thread_config(backend: str) -> Dict[str, int]:
    """
    Get optimal thread configuration for the backend.
    
    Args:
        backend: Backend name
        
    Returns:
        Dictionary with thread configuration
    """
    import psutil
    
    cpu_count = psutil.cpu_count(logical=False)  # Physical cores
    logical_count = psutil.cpu_count(logical=True)
    
    if backend == "gmx_cuda":
        # NVIDIA: use all cores with threading
        return {
            "omp_threads": max(4, cpu_count // 2),
            "mpi_tasks": 1,
            "gpu_id": 0
        }
    elif backend == "gmx_sycl":
        # SYCL: similar to CUDA
        return {
            "omp_threads": max(4, cpu_count // 2),
            "mpi_tasks": 1,
            "gpu_id": 0
        }
    else:
        # CPU: use all cores
        return {
            "omp_threads": cpu_count,
            "mpi_tasks": 1,
            "gpu_id": None
        }


if __name__ == "__main__":
    # Test backend selection
    from .gpu_detector import detect_gpu
    
    print("Testing Backend Selection...")
    gpu_info = detect_gpu()
    backend = select_backend(gpu_info)
    config = get_backend_config(backend)
    
    print(f"GPU: {gpu_info['vendor']}")
    print(f"Backend: {backend}")
    print(f"Config: {config}")
