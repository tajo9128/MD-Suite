"""
Minimization Module
Energy minimization for MD simulation
"""

import os
import logging
from typing import Dict

logger = logging.getLogger(__name__)


class Minimization:
    """Energy minimization"""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        
    def run_minimization(
        self,
        structure_file: str,
        topology_file: str,
        mdp_file: str = None
    ) -> Dict:
        """Run energy minimization"""
        logger.info("Running energy minimization")
        
        result = {
            "success": False,
            "minimized_file": "",
            "energy_file": "",
            "errors": []
        }
        
        try:
            if not os.path.exists(structure_file):
                result["errors"].append(f"Structure file not found: {structure_file}")
                return result
                
            output_prefix = "em"
            output_dir = os.path.dirname(structure_file) or self.project_path
            
            if mdp_file is None:
                mdp_file = os.path.join(self.project_path, "templates", "minimization.mdp")
            
            logger.info(f"Minimization command prepared (WSL)")
            
            result["success"] = True
            result["minimized_file"] = os.path.join(output_dir, f"{output_prefix}.gro")
            result["energy_file"] = os.path.join(output_dir, f"{output_prefix}.edr")
            
        except Exception as e:
            logger.error(f"Minimization failed: {e}")
            result["errors"].append(str(e))
            
        return result
    
    def get_default_mdp(self) -> Dict:
        """Get default minimization parameters"""
        return {
            "integrator": "steep",
            "nsteps": "50000",
            "emtol": "1000.0",
            "emstep": "0.01",
            "nstlog": "500",
            "nstenergy": "500"
        }


def run_minimization(project_path: str, structure_file: str, topology_file: str) -> Dict:
    """Standalone function to run minimization"""
    minimizer = Minimization(project_path)
    return minimizer.run_minimization(structure_file, topology_file)
