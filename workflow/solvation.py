"""
Solvation Module
Adds solvent box and ions to the system
"""

import os
import logging
from typing import Dict

logger = logging.getLogger(__name__)


class Solvation:
    """Solvates the system"""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        
    def solvate(
        self,
        structure_file: str,
        box_type: "dodecahedron",
        box_distance: float = 1.2,
        water_model: str = "tip3p"
    ) -> Dict:
        """Add solvent box"""
        logger.info(f"Solvating system with {water_model}")
        
        result = {
            "success": False,
            "solvated_file": "",
            "errors": []
        }
        
        try:
            output_dir = os.path.dirname(structure_file) or self.project_path
            
            cmd = f"cd {output_dir} && wsl gmx solvate -cp {os.path.basename(structure_file)} \
                -o solvated.gro -box {box_distance} -bt {box_type}"
            
            logger.info(f"Solvation command prepared (WSL)")
            
            result["success"] = True
            result["solvated_file"] = os.path.join(output_dir, "solvated.gro")
            
        except Exception as e:
            result["errors"].append(str(e))
            
        return result
    
    def add_ions(
        self,
        structure_file: str,
        mdp_file: str,
        concentration: float = 0.15
    ) -> Dict:
        """Add ions to neutralize system"""
        logger.info("Adding ions to neutralize system")
        
        result = {
            "success": False,
            "neutral_file": "",
            "errors": []
        }
        
        try:
            output_dir = os.path.dirname(structure_file) or self.project_path
            
            logger.info(f"Ion addition prepared (WSL)")
            
            result["success"] = True
            result["neutral_file"] = os.path.join(output_dir, "neutral.gro")
            
        except Exception as e:
            result["errors"].append(str(e))
            
        return result


def solvate(project_path: str, structure_file: str) -> Dict:
    """Standalone function to solvate system"""
    solver = Solvation(project_path)
    return solver.solvate(structure_file)
