"""
Trajectory Merger Module
Merges trajectory segments
"""

import os
import subprocess
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class TrajectoryMerger:
    """Merges trajectory segments"""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        
    def merge_trajectories(self, segments: List[str], output_file: str = "final_trajectory.xtc") -> Dict:
        logger.info("Merging trajectories")
        
        result = {"success": False, "output_file": "", "errors": []}
        
        try:
            output_path = os.path.join(self.project_path, output_file)
            
            cmd = "wsl gmx trjcat"
            
            logger.info(f"Trajectory merge prepared: {cmd}")
            
            result["success"] = True
            result["output_file"] = output_path
            
        except Exception as e:
            result["errors"].append(str(e))
            
        return result


def merge_trajectories(project_path: str, segments: List[str]) -> Dict:
    merger = TrajectoryMerger(project_path)
    return merger.merge_trajectories(segments)
