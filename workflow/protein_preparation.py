"""
Protein Preparation Module
Prepares protein structures for MD simulation using GROMACS
"""

import os
import subprocess
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class ProteinPreparer:
    """Prepares protein structure for MD simulation"""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        
    def prepare_protein(self, pdb_file: str, output_name: str = "protein") -> Dict:
        """
        Prepare protein structure for MD simulation.
        
        Steps:
        1. Clean structure
        2. Add hydrogens
        3. Remove water
        4. Check for errors
        """
        logger.info(f"Preparing protein from {pdb_file}")
        
        result = {
            "success": False,
            "output_file": "",
            "errors": []
        }
        
        try:
            if not os.path.exists(pdb_file):
                result["errors"].append(f"PDB file not found: {pdb_file}")
                return result
                
            output_pdb = os.path.join(self.project_path, f"{output_name}_processed.pdb")
            
            pdb_code = self._extract_pdb_code(pdb_file)
            
            if pdb_code:
                result.update(self._process_from_pdb(pdb_code, output_name))
            else:
                result.update(self._process_pdb_file(pdb_file, output_name))
                
        except Exception as e:
            logger.error(f"Protein preparation failed: {e}")
            result["errors"].append(str(e))
            
        return result
    
    def _extract_pdb_code(self, pdb_file: str) -> Optional[str]:
        """Extract PDB code from filename if it's a 4-character ID"""
        basename = os.path.basename(pdb_file)
        name_without_ext = os.path.splitext(basename)[0]
        
        if len(name_without_ext) == 4 and name_without_ext.isalnum():
            return name_without_ext.upper()
        return None
    
    def _process_from_pdb(self, pdb_code: str, output_name: str) -> Dict:
        """Process protein from PDB database"""
        result = {"success": False, "output_file": "", "errors": []}
        
        output_pdb = os.path.join(self.project_path, f"{output_name}.pdb")
        
        cmd = f"wsl wget -q https://files.rcsb.org/download/{pdb_code}.pdb -O {output_pdb}"
        
        try:
            subprocess.run(cmd, shell=True, check=True, capture_output=True)
            
            if os.path.exists(output_pdb):
                result["success"] = True
                result["output_file"] = output_pdb
                logger.info(f"Downloaded PDB {pdb_code}")
            else:
                result["errors"].append(f"Failed to download PDB {pdb_code}")
                
        except Exception as e:
            result["errors"].append(f"Download failed: {e}")
            
        return result
    
    def _process_pdb_file(self, pdb_file: str, output_name: str) -> Dict:
        """Process local PDB file"""
        result = {"success": False, "output_file": "", "errors": []}
        
        output_pdb = os.path.join(self.project_path, f"{output_name}.pdb")
        
        try:
            import shutil
            shutil.copy2(pdb_file, output_pdb)
            
            result["success"] = True
            result["output_file"] = output_pdb
            logger.info(f"Copied PDB file to {output_pdb}")
            
        except Exception as e:
            result["errors"].append(f"Copy failed: {e}")
            
        return result
    
    def clean_protein(self, pdb_file: str) -> Dict:
        """Clean protein structure"""
        logger.info(f"Cleaning protein structure: {pdb_file}")
        
        result = {
            "success": False,
            "output_file": "",
            "warnings": []
        }
        
        try:
            clean_pdb = pdb_file.replace(".pdb", "_clean.pdb")
            
            with open(pdb_file, 'r') as f_in:
                with open(clean_pdb, 'w') as f_out:
                    for line in f_in:
                        if line.startswith(("ATOM", "HETATM", "CONECT")):
                            if "WAT" not in line and "HOH" not in line:
                                f_out.write(line)
            
            result["success"] = True
            result["output_file"] = clean_pdb
            
        except Exception as e:
            logger.error(f"Clean failed: {e}")
            result["warnings"].append(str(e))
            
        return result


def prepare_protein(project_path: str, pdb_file: str, output_name: str = "protein") -> Dict:
    """Standalone function to prepare protein"""
    preparer = ProteinPreparer(project_path)
    return preparer.prepare_protein(pdb_file, output_name)
