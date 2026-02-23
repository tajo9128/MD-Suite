"""
GROMACS CPU Backend for BioDockify MD Universal
CPU-only execution fallback
"""

import subprocess
import logging
import psutil
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class GMXCPUBackend:
    """
    GROMACS CPU backend for CPU-only execution.
    
    Used when no GPU is available or as fallback.
    """
    
    NAME = "gmx_cpu"
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        
    def get_mdrun_flags(self) -> Dict[str, str]:
        """
        Get optimized mdrun flags for CPU backend.
        
        Returns:
            Dictionary of mdrun flags
        """
        cpu_count = psutil.cpu_count(logical=False) or 4
        
        return {
            "nb": "cpu",
            "pme": "cpu",
            "bonded": "cpu",
            "pin": "on",
            "nt": str(cpu_count),
            "ntomp": str(max(4, cpu_count // 2))
        }
        
    def build_mdrun_command(
        self,
        tpr_file: str,
        output_prefix: str,
        resume: bool = False,
        checkpoint_interval: int = 15
    ) -> str:
        """
        Build mdrun command for CPU backend.
        
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
        
        # Add CPU-specific flags
        cmd_parts.extend([
            f"-nb {flags['nb']}",
            f"-pme {flags['pme']}",
            f"-bonded {flags['bonded']}",
            f"-pin {flags['pin']}",
            f"-nt {flags['nt']}",
            f"-ntomp {flags['ntomp']}"
        ])
        
        if resume:
            cmd_parts.extend(["-cpi", "-append"])
            
        return " ".join(cmd_parts)
        
    def validate(self) -> bool:
        """
        Validate CPU backend availability.
        
        Returns:
            True if CPU backend is available
        """
        try:
            result = subprocess.run(
                "wsl gmx --version",
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return result.returncode == 0
            
        except Exception as e:
            logger.error(f"CPU backend validation failed: {e}")
            return False
            
    def get_system_info(self) -> Dict:
        """Get CPU system information"""
        cpu_count = psutil.cpu_count(logical=False) or 0
        logical_count = psutil.cpu_count(logical=True) or 0
        
        return {
            "physical_cores": cpu_count,
            "logical_cores": logical_count,
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_total_gb": psutil.virtual_memory().total / (1024**3),
            "memory_available_gb": psutil.virtual_memory().available / (1024**3)
        }


def create_cpu_backend(config: Optional[Dict] = None) -> GMXCPUBackend:
    """Factory function to create CPU backend"""
    return GMXCPUBackend(config)


if __name__ == "__main__":
    print("Testing CPU Backend...")
    
    backend = GMXCPUBackend()
    print(f"Backend: {backend.NAME}")
    print(f"Flags: {backend.get_mdrun_flags()}")
    
    cmd = backend.build_mdrun_command("simulation.tpr", "md")
    print(f"Command: {cmd}")
    
    sys_info = backend.get_system_info()
    print(f"System Info: {sys_info}")
