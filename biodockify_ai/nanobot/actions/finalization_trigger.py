"""
Finalization Trigger - Triggers simulation finalization and packaging
"""

import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)


class FinalizationTrigger:
    """Triggers simulation finalization"""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        
    def trigger_finalization(self) -> bool:
        """Trigger finalization and packaging"""
        logger.info(f"Triggering finalization for {self.project_path}")
        
        try:
            import sys
            from pathlib import Path
            
            project_root = Path(__file__).parent.parent.parent.parent
            sys.path.insert(0, str(project_root))
            
            from core.publication_packager import PublicationPackager
            
            packager = PublicationPackager(self.project_path)
            package_path = packager.create_publication_package()
            
            if package_path:
                logger.info(f"Publication package created: {package_path}")
                return True
            else:
                logger.error("Failed to create publication package")
                return False
                
        except Exception as e:
            logger.error(f"Finalization failed: {e}")
            return False
    
    def merge_trajectories(self) -> bool:
        """Merge segment trajectories"""
        logger.info("Merging trajectories")
        
        try:
            import subprocess
            
            segment_dirs = []
            import os
            for item in os.listdir(self.project_path):
                if os.path.isdir(os.path.join(self.project_path, item)) and "segment" in item:
                    segment_dirs.append(item)
                    
            if not segment_dirs:
                logger.warning("No segments found to merge")
                return False
                
            segment_dirs.sort()
            
            cmd = f'wsl gmx trjcat -f '
            for seg in segment_dirs:
                cmd += f'{self.project_path}/{seg}/md.xtc '
            cmd += f'-o {self.project_path}/final_trajectory.xtc'
            
            result = subprocess.run(cmd, shell=True, capture_output=True)
            
            if result.returncode == 0:
                logger.info("Trajectories merged successfully")
                return True
            else:
                logger.error(f"Trajectory merge failed: {result.stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"Trajectory merge error: {e}")
            return False


def trigger_finalization(project_path: str) -> bool:
    """Standalone function to trigger finalization"""
    trigger = FinalizationTrigger(project_path)
    return trigger.trigger_finalization()
