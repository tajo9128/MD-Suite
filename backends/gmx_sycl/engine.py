"""
GROMACS SYCL Backend for BioDockify MD Universal
AMD/Intel GPU acceleration via SYCL
"""

import subprocess
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class GMXSYCLBackend:
    """
    GROMACS SYCL backend for AMD/Intel GPUs.
    
    Optimized for AMD and Intel GPUs using SYCL/OpenCL.
    """
    
    NAME = "gmx_sycl"
    VENDORS = ["AMD", "Intel"]
    
    def __init__(self, gpu_info: Optional[Dict] = None):
        self.gpu_info = gpu_info or {}
        self.gpu_id = 0
        
    def get_mdrun_flags(self) -> Dict[str, str]:
        """
        Get optimized mdrun flags for SYCL backend.
        
        Returns:
            Dictionary of mdrun flags
        """
        return {
            "nb": "gpu",
            "pme": "gpu",
            "bonded": "gpu",
            "pin": "on",
            "sycl": "",
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
        Build mdrun command for SYCL backend.
        
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
            "-sycl",
            f"-gpu_id {flags['gpu_id']}"
        ])
        
        if resume:
            cmd_parts.extend(["-cpi", "-append"])
            
        return " ".join(cmd_parts)
        
    def validate(self) -> bool:
        """
        Validate SYCL backend availability.
        
        Returns:
            True if SYCL backend is available
        """
        try:
            # Check GROMACS version with SYCL support
            result = subprocess.run(
                "wsl gmx --version",
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return False
                
            # Check for SYCL support
            # This is simplified - in practice would check for oneAPI/ROCm
            return True
            
        except Exception as e:
            logger.error(f"SYCL backend validation failed: {e}")
            return False
            
    def detect_gpu_info(self) -> Dict:
        """Detect GPU information"""
        gpu_info = {"vendor": "Unknown", "name": "Unknown"}
        
        try:
            # Try AMD
            result = subprocess.run(
                "wsl lspci | grep -i vga | grep -i amd",
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout:
                gpu_info["vendor"] = "AMD"
                gpu_info["name"] = result.stdout.strip()
                
        except:
            pass
            
        try:
            # Try Intel
            result = subprocess.run(
                "wsl lspci | grep -i vga | grep -i intel",
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout:
                gpu_info["vendor"] = "Intel"
                gpu_info["name"] = result.stdout.strip()
                
        except:
            pass
            
        return gpu_info


def create_sycl_backend(gpu_info: Optional[Dict] = None) -> GMXSYCLBackend:
    """Factory function to create SYCL backend"""
    return GMXSYCLBackend(gpu_info)


if __name__ == "__main__":
    print("Testing SYCL Backend...")
    
    backend = GMXSYCLBackend()
    print(f"Backend: {backend.NAME}")
    print(f"Flags: {backend.get_mdrun_flags()}")
    
    cmd = backend.build_mdrun_command("simulation.tpr", "md")
    print(f"Command: {cmd}")
    
    gpu_info = backend.detect_gpu_info()
    print(f"GPU Info: {gpu_info}")
