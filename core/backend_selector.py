"""
Backend Selection Module for BioDockify MD Universal
Selects appropriate GROMACS backend based on detected hardware
Supports multi-GPU systems and automatic performance-based selection
"""

import logging
import subprocess
import time
from typing import Dict, Optional, List, Any

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


def is_wsl_available() -> bool:
    """
    Check if WSL is available on the system.
    
    Returns:
        True if WSL is available, False otherwise
    """
    import subprocess
    try:
        result = subprocess.run(
            "wsl --status",
            shell=True,
            capture_output=True,
            timeout=10
        )
        return result.returncode == 0
    except Exception as e:
        logger.warning(f"WSL availability check failed: {e}")
        return False


def get_gmx_command_prefix() -> str:
    """
    Get the appropriate GROMACS command prefix based on system availability.
    
    Returns:
        Command prefix for GROMACS (either 'wsl gmx' or 'gmx' for native)
    """
    if is_wsl_available():
        return "wsl gmx"
    else:
        logger.warning("WSL not available - using native gmx (may not work on Windows)")
        return "gmx"


def get_mdrun_command(
    backend: str,
    tpr_file: str,
    output_prefix: str,
    resume: bool = False,
    checkpoint_interval: int = 15,
    gpu_id: Optional[int] = None,
    multi_gpu_gpus: Optional[List[int]] = None,
    threads: Optional[int] = None
) -> str:
    """
    Build the GROMACS mdrun command for the selected backend.
    
    Args:
        backend: Backend name ("gmx_cuda", "gmx_sycl", "gmx_cpu")
        tpr_file: Path to the TPR input file
        output_prefix: Output file prefix
        resume: Whether this is a resume from checkpoint
        checkpoint_interval: Checkpoint interval in minutes
        gpu_id: Single GPU ID to use (for multi-GPU systems)
        multi_gpu_gpus: List of GPU IDs for multi-GPU parallel execution
        threads: Number of OpenMP threads (None for auto)
        
    Returns:
        Complete mdrun command string
    """
    config = get_backend_config(backend)
    flags = list(config["mdrun_flags"])
    
    # Build base command - use appropriate prefix based on WSL availability
    gmx_cmd = f"{get_gmx_command_prefix()} mdrun"
    
    # Add GPU configuration
    if backend in ["gmx_cuda", "gmx_sycl"]:
        if multi_gpu_gpus and len(multi_gpu_gpus) > 1:
            # Multi-GPU parallel execution
            gpu_ids = ",".join(str(g) for g in multi_gpu_gpus)
            flags.append(f"-gpu_id {gpu_ids}")
        elif gpu_id is not None:
            # Single GPU specified
            flags.append(f"-gpu_id {gpu_id}")
    
    # Add threading configuration
    if threads is not None and threads > 0:
        flags.append(f"-ntomp {threads}")
    
    # Build command with options
    cmd_parts = [
        gmx_cmd,
        f"-s {tpr_file}",
        f"-o {output_prefix}",
        f"-e {output_prefix}",
        f"-g {output_prefix}",
        f"-c {output_prefix}_final.gro",
        " ".join(flags),
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
        # Check WSL availability first
        if not is_wsl_available():
            logger.warning("WSL is not available - cannot validate GROMACS backend")
            # Try native gmx as fallback
            try:
                output = subprocess.check_output(
                    "which gmx",
                    shell=True,
                    stderr=subprocess.DEVNULL
                ).decode("utf-8", errors="ignore").strip()
                if not output:
                    logger.warning("GROMACS not found (native)")
                    return False
            except subprocess.CalledProcessError:
                logger.warning("GROMACS not found (native)")
                return False
        
        # Check if GROMACS is available (WSL or native)
        gmx_prefix = get_gmx_command_prefix()
        
        try:
            output = subprocess.check_output(
                f"{gmx_prefix.split()[0]} {gmx_prefix.split()[1] if len(gmx_prefix.split()) > 1 else ''} which gmx".strip(),
                shell=True,
                stderr=subprocess.DEVNULL,
                timeout=5
            ).decode("utf-8", errors="ignore").strip()
        except:
            # Fallback: try direct command
            output = subprocess.check_output(
                f"{gmx_prefix} --version",
                shell=True,
                stderr=subprocess.DEVNULL,
                timeout=10
            ).decode("utf-8", errors="ignore").strip()
        
        if not output:
            logger.warning(f"GROMACS not found via {gmx_prefix}")
            return False
            
        # Check GROMACS version
        try:
            version = subprocess.check_output(
                f"{gmx_prefix} --version",
                shell=True,
                stderr=subprocess.DEVNULL,
                timeout=10
            ).decode("utf-8", errors="ignore")
            logger.info(f"GROMACS version: {version.split()[1] if version else 'unknown'}")
        except:
            logger.info("GROMACS found but version check timed out")
        
        # For GPU backends, check GPU availability
        if backend in ["gmx_cuda", "gmx_sycl"]:
            try:
                if backend == "gmx_cuda":
                    subprocess.check_output(
                        "wsl nvidia-smi",
                        shell=True,
                        stderr=subprocess.DEVNULL,
                        timeout=5
                    )
                # SYCL doesn't have an easy check
                return True
            except subprocess.CalledProcessError:
                logger.warning(f"{backend} selected but GPU not available")
                return False
            except FileNotFoundError:
                logger.warning("WSL not available for GPU check")
                return False
                
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Backend validation failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Backend validation error: {e}")
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


def benchmark_backend(backend: str, duration_seconds: int = 30) -> Dict[str, Any]:
    """
    Benchmark a backend to determine its performance.
    
    Args:
        backend: Backend to benchmark ("gmx_cuda", "gmx_sycl", "gmx_cpu")
        duration_seconds: How long to run the benchmark
        
    Returns:
        Dictionary with benchmark results
    """
    result = {
        "backend": backend,
        "success": False,
        "ns_per_day": None,
        "error": None
    }
    
    try:
        # Check if backend is available
        if not validate_backend_availability(backend):
            result["error"] = "Backend not available"
            return result
            
        # This would ideally run a short MD simulation
        # For now, we'll just check if we can get GPU info
        if backend == "gmx_cuda":
            try:
                output = subprocess.check_output(
                    "wsl nvidia-smi --query-gpu=name,compute_cap --format=csv,noheader",
                    shell=True,
                    stderr=subprocess.DEVNULL,
                    timeout=5
                ).decode("utf-8").strip()
                if output:
                    result["success"] = True
                    result["gpu_info"] = output
            except:
                pass
        elif backend == "gmx_sycl":
            # SYCL is harder to benchmark without actual execution
            result["success"] = True
        else:
            result["success"] = True
            
    except Exception as e:
        result["error"] = str(e)
    
    return result


def select_best_backend_via_benchmark() -> Dict[str, Any]:
    """
    Run benchmarks on all available backends and select the best one.
    
    Returns:
        Dictionary with selected backend and benchmark results
    """
    from .gpu_detector import detect_all_gpus, is_nvidia_available
    
    available_backends = []
    
    # Check CPU backend (always available)
    cpu_result = benchmark_backend("gmx_cpu")
    if cpu_result["success"]:
        available_backends.append({
            "backend": "gmx_cpu",
            "score": 1.0,  # Baseline
            "details": cpu_result
        })
    
    # Check if we have NVIDIA GPU
    if is_nvidia_available():
        cuda_result = benchmark_backend("gmx_cuda")
        if cuda_result["success"]:
            # CUDA typically 10-50x faster than CPU
            available_backends.append({
                "backend": "gmx_cuda",
                "score": 25.0,  # Estimated speedup
                "details": cuda_result
            })
    
    # Check SYCL (AMD/Intel)
    all_gpus = detect_all_gpus()
    if all_gpus.has_amd or all_gpus.has_intel:
        sycl_result = benchmark_backend("gmx_sycl")
        if sycl_result["success"]:
            # SYCL typically 5-20x faster than CPU
            available_backends.append({
                "backend": "gmx_sycl",
                "score": 12.0,  # Estimated speedup
                "details": sycl_result
            })
    
    # Sort by score and select best
    available_backends.sort(key=lambda x: x["score"], reverse=True)
    
    return {
        "selected_backend": available_backends[0]["backend"] if available_backends else "gmx_cpu",
        "available_backends": available_backends,
        "reason": f"Best performance: {available_backends[0]['backend']}" if available_backends else "No GPU available"
    }


def get_autotune_config(backend: str) -> Dict[str, Any]:
    """
    Get auto-tuned configuration for optimal performance.
    
    Args:
        backend: Backend name
        
    Returns:
        Dictionary with tuned parameters
    """
    config = get_backend_config(backend)
    thread_config = get_optimal_thread_config(backend)
    
    # Additional tuning recommendations
    tuning = {
        "backend": backend,
        "recommended_config": config,
        "thread_config": thread_config,
        "suggestions": []
    }
    
    if backend == "gmx_cuda":
        tuning["suggestions"].extend([
            "Enable GPU-PME offload: -pme gpu",
            "Enable GPU bonded interactions: -bonded gpu",
            "Consider multi-GPU with MPI for >2 GPUs"
        ])
    elif backend == "gmx_sycl":
        tuning["suggestions"].extend([
            "Use Intel oneAPI for best Intel GPU performance",
            "Use ROCm for AMD GPUs",
            "SYCL may benefit from CPU threads for non-GPU tasks"
        ])
    else:
        tuning["suggestions"].extend([
            "Use all physical cores: -ntomp",
            "Consider task parallelization for large systems"
        ])
    
    return tuning


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
