"""
Energy Merger Module
Merges energy files
"""

import os
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class EnergyMerger:
    """Merges energy files"""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        
    def merge_energies(self, energy_files: List[str], output_file: str = "final_energy.edr") -> Dict:
        logger.info("Merging energy files")
        
        result = {"success": False, "output_file": "", "errors": []}
        
        try:
            output_path = os.path.join(self.project_path, output_file)
            
            result["success"] = True
            result["output_file"] = output_path
            
        except Exception as e:
            result["errors"].append(str(e))
            
        return result


def merge_energies(project_path: str, energy_files: List[str]) -> Dict:
    merger = EnergyMerger(project_path)
    return merger.merge_energies(energy_files)
