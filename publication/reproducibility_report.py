"""
Reproducibility Report Module
Generates reproducibility documentation
"""

import os
import logging
from datetime import datetime
from typing import Dict

logger = logging.getLogger(__name__)


class ReproducibilityReport:
    """Generates reproducibility report"""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        
    def generate_report(self, metadata: Dict) -> Dict:
        logger.info("Generating reproducibility report")
        
        result = {"success": False, "report_file": "", "errors": []}
        
        try:
            report_file = os.path.join(self.project_path, "README_reproducibility.txt")
            
            with open(report_file, 'w') as f:
                f.write("=" * 60 + "\n")
                f.write("BioDockify MD Universal - Reproducibility Report\n")
                f.write("=" * 60 + "\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n\n")
                
                f.write("SYSTEM INFORMATION\n")
                f.write("-" * 60 + "\n")
                for key, value in metadata.get("system", {}).items():
                    f.write(f"{key}: {value}\n")
                    
                f.write("\nSIMULATION PARAMETERS\n")
                f.write("-" * 60 + "\n")
                for key, value in metadata.get("simulation", {}).items():
                    f.write(f"{key}: {value}\n")
                    
                f.write("\nREPRODUCTION INSTRUCTIONS\n")
                f.write("-" * 60 + "\n")
                f.write("1. Install GROMACS\n")
                f.write("2. Run: gmx mdrun -s final.tpr\n")
                
            result["success"] = True
            result["report_file"] = report_file
            
        except Exception as e:
            result["errors"].append(str(e))
            
        return result


def generate_reproducibility_report(project_path: str, metadata: Dict) -> Dict:
    report = ReproducibilityReport(project_path)
    return report.generate_report(metadata)
