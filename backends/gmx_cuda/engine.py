"""
GROMACS CUDA Backend for BioDockify MD Universal
NVIDIA GPU acceleration via CUDA
"""

import subprocess
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class GMXCUDABackend:
    """
    GROMACS CUDA backend for NVIDIA GPUs.
    
    Optimized for NVIDIA GPU acceleration with CUDA.
    """
    
    NAME = "gmx_cuda"
    VENDOR = "NVIDIA"
    
    def __init__(self, gpu_info: Optional[Dict] = None):
        self.gpu_info = gpu_info or {}
        self.gpu_id = 0
        
    def get_mdrun_flags(self) -> Dict[str, str]:
        """
        Get optimized mdrun flags for CUDA backend.
        
        Returns:
            Dictionary of mdrun flags
        """
        return {
            "nb": "gpu",
            "pme": "gpu",
            "bonded": "gpu",
            "pin": "on",
            "pinoffset": "0",
            "pinstride": "1",
            "gpu_id": str(self.gpu_id)
        }
        
    def build_mdrun_command(
        self,
        tpr_file: str,
        output_prefix: str,
        resume: bool = False,
        checkpoint_interval: int = 15
    ) -> str:
        """
        Build mdrun command for CUDA backend.
        
        Args:
            tpr_file: Input TPR file
            output_prefix: Output file prefix
            resume: Whether to resume from checkpoint
            checkpoint_interval: Checkpoint interval in minutes
            
        Returns:
            Complete mdrun command string
        """
        flags = self.get_mdrun_flags()
        
        cmd_parts = [
            "wsl gmx mdrun",
            f"-s {tpr_file}",
            f"-o {output_prefix}.xtc",
            f"-e {output_prefix}.edr",
            f"-g {output_prefix}.log",
            f"-c {output_prefix}_final.gro",
            f"-cpt {checkpoint_interval}",
        ]
        
        # Add GPU-specific flags
        cmd_parts.extend([
            f"-nb {flags['nb']}",
            f"-pme {flags['pme']}",
            f"-bonded {flags['bonded']}",
            f"-pin {flags['pin']}",
            f"-gpu_id {flags['gpu_id']}"
        ])
        
        if resume:
            cmd_parts.extend(["-cpi", "-append"])
            
        return " ".join(cmd_parts)
        
    def validate(self) -> bool:
        """
        Validate CUDA backend availability.
        
        Returns:
            True if CUDA backend is available
        """
        try:
            # Check GROMACS version
            result = subprocess.run(
                "wsl gmx --version",
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return False
                
            # Check CUDA availability
            result = subprocess.run(
                "wsl nvidia-smi",
                shell=True,
                capture_output=True,
                timeout=10
            )
            
            return result.returncode == 0
            
        except Exception as e:
            logger.error(f"CUDA backend validation failed: {e}")
            return False
            
    def get_gpu_utilization(self) -> Optional[int]:
        """Get current GPU utilization percentage"""
        try:
            result = subprocess.run(
                "wsl nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits",
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return int(result.stdout.strip())
                
        except Exception as e:
            logger.debug(f"GPU utilization check failed: {e}")
            
        return None
        
    def get_gpu_memory_usage(self) -> Optional[Dict]:
        """Get GPU memory usage information"""
        try:
            result = subprocess.run(
                "wsl nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader,nounits",
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                used, total = result.stdout.strip().split(',')
                return {
                    "used_mb": int(used.strip()),
                    "total_mb": int(total.strip()),
                    "percent": (int(used.strip()) / int(total.strip())) * 100
                }
                
        except Exception as e:
            logger.debug(f"GPU memory check failed: {e}")
            
        return None


def create_cuda_backend(gpu_info: Optional[Dict] = None) -> GMXCUDABackend:
    """Factory function to create CUDA backend"""
    return GMXCUDABackend(gpu_info)


if __name__ == "__main__":
    print("Testing CUDA Backend...")
    
    backend = GMXCUDABackend()
    print(f"Backend: {backend.NAME}")
    print(f"Flags: {backend.get_mdrun_flags()}")
    
    cmd = backend.build_mdrun_command("simulation.tpr", "md")
    print(f"Command: {cmd}")
    
    valid = backend.validate()
    print(f"Valid: {valid}")
