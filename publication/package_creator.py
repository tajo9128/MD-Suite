"""
Package Creator Module
Creates final publication package
"""

import os
import shutil
import logging
from typing import Dict

logger = logging.getLogger(__name__)


class PackageCreator:
    """Creates publication package"""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        
    def create_package(self, output_name: str = None) -> Dict:
        logger.info("Creating publication package")
        
        result = {"success": False, "package_file": "", "errors": []}
        
        try:
            if output_name is None:
                output_name = os.path.basename(self.project_path) + "_Publication"
                
            pub_dir = os.path.join(self.project_path, output_name)
            os.makedirs(pub_dir, exist_ok=True)
            
            files_to_copy = [
                "final_trajectory.xtc",
                "final_energy.edr",
                "final_structure.gro",
                "topology.top",
                "mdp_parameters.txt"
            ]
            
            for f in files_to_copy:
                src = os.path.join(self.project_path, f)
                if os.path.exists(src):
                    shutil.copy2(src, pub_dir)
                    
            analysis_src = os.path.join(self.project_path, "analysis")
            if os.path.exists(analysis_src):
                analysis_dst = os.path.join(pub_dir, "analysis")
                shutil.copytree(analysis_src, analysis_dst)
                
            zip_path = shutil.make_archive(pub_dir, 'zip', self.project_path, output_name)
            
            result["success"] = True
            result["package_file"] = zip_path
            
        except Exception as e:
            logger.error(f"Package creation failed: {e}")
            result["errors"].append(str(e))
            
        return result
    
    def open_in_explorer(self, package_path: str) -> bool:
        """Open package location in file explorer"""
        try:
            import subprocess
            folder = os.path.dirname(package_path)
            subprocess.Popen(f'explorer /select,"{package_path}"')
            return True
        except Exception as e:
            logger.error(f"Failed to open explorer: {e}")
            return False


def create_package(project_path: str, output_name: str = None) -> Dict:
    creator = PackageCreator(project_path)
    return creator.create_package(output_name)
