"""
Stability Checker - Checks simulation stability from energy drift
"""

import os
import re
import logging
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)


class StabilityChecker:
    """Checks simulation stability"""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        
    def check_stability(self) -> Dict:
        """Check simulation stability"""
        result = {
            "is_stable": True,
            "issues": [],
            "linst_warnings": 0,
            "energy_drift": None,
            "warnings": []
        }
        
        log_file = self._find_log_file()
        if not log_file:
            result["is_stable"] = False
            result["issues"].append("No log file found")
            return result
            
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            lincs_count = content.count("LINCS WARNING") + content.count("Lincs warning")
            result["lincs_warnings"] = lincs_count
            
            if lincs_count > 10:
                result["is_stable"] = False
                result["issues"].append(f"High LINCS warnings: {lincs_count}")
                result["warnings"].append(f"Too many LINCS warnings ({lincs_count})")
                
            energy_drift = self._parse_energy_drift(content)
            if energy_drift:
                result["energy_drift"] = energy_drift
                if abs(energy_drift) > 10000:
                    result["is_stable"] = False
                    result["issues"].append(f"High energy drift: {energy_drift}")
                    
        except Exception as e:
            logger.error(f"Stability check failed: {e}")
            result["is_stable"] = False
            result["issues"].append(str(e))
            
        return result
    
    def _find_log_file(self) -> Optional[str]:
        """Find log file"""
        for root, dirs, files in os.walk(self.project_path):
            for f in files:
                if f == "md.log":
                    return os.path.join(root, f)
        return None
    
    def _parse_energy_drift(self, content: str) -> Optional[float]:
        """Parse energy drift from log"""
        try:
            import re
            match = re.search(r'Energy\s+[-\d.]+\s+[-\d.]+\s+([-\d.]+)', content)
            if match:
                return float(match.group(1))
        except:
            pass
        return None


def check_stability(project_path: str) -> Dict:
    """Standalone function to check stability"""
    checker = StabilityChecker(project_path)
    return checker.check_stability()
