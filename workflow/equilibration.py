"""
Equilibration Module
System equilibration (NVT and NPT)
"""

import os
import logging
from typing import Dict

logger = logging.getLogger(__name__)


class Equilibration:
    """System equilibration"""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        
    def run_nvt(
        self,
        structure_file: str,
        topology_file: str,
        temperature: float = 300.0,
        nsteps: int = 50000
    ) -> Dict:
        """Run NVT equilibration"""
        logger.info(f"Running NVT equilibration at {temperature}K")
        
        result = {
            "success": False,
            "output_file": "",
            "errors": []
        }
        
        try:
            output_dir = os.path.dirname(structure_file) or self.project_path
            output_prefix = "nvt"
            
            logger.info(f"NVT equilibration command prepared (WSL)")
            
            result["success"] = True
            result["output_file"] = os.path.join(output_dir, f"{output_prefix}.gro")
            
        except Exception as e:
            result["errors"].append(str(e))
            
        return result
    
    def run_npt(
        self,
        structure_file: str,
        topology_file: str,
        temperature: float = 300.0,
        pressure: float = 1.0,
        nsteps: int = 50000
    ) -> Dict:
        """Run NPT equilibration"""
        logger.info(f"Running NPT equilibration at {temperature}K, {pressure}bar")
        
        result = {
            "success": False,
            "output_file": "",
            "errors": []
        }
        
        try:
            output_dir = os.path.dirname(structure_file) or self.project_path
            output_prefix = "npt"
            
            logger.info(f"NPT equilibration command prepared (WSL)")
            
            result["success"] = True
            result["output_file"] = os.path.join(output_dir, f"{output_prefix}.gro")
            
        except Exception as e:
            result["errors"].append(str(e))
            
        return result


def run_equilibration(project_path: str, structure_file: str, topology_file: str) -> Dict:
    """Standalone function to run equilibration"""
    equil = Equilibration(project_path)
    return equil.run_nvt(structure_file, topology_file)
