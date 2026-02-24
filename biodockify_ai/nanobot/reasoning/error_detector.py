"""
Error Detector - Detects errors in MD simulation logs
"""

import os
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ErrorDetector:
    """Detects errors in MD simulation"""
    
    ERROR_KEYWORDS = [
        "ERROR:",
        "Fatal error:",
        "Segmentation fault",
        "Core dumped",
        "Out of memory",
        "SIGSEGV",
        "SIGABRT",
        "Assertion failed",
        "invalid",
        "failed"
    ]
    
    WARNING_KEYWORDS = [
        "LINCS WARNING",
        "LINCS warning",
        "WARN:",
        "WARNING:",
        "Pressure coupling",
        "Temperature coupling"
    ]
    
    CRITICAL_ERRORS = [
        "Fatal error",
        "Segmentation fault",
        "Core dumped",
        "Out of memory",
        "SIGSEGV",
        "SIGABRT"
    ]
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        
    def detect_errors(self) -> Optional[Dict]:
        """Detect errors in log file"""
        log_file = self._find_log_file()
        if not log_file:
            return None
            
        errors = []
        warnings = []
        
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                
            for line in lines:
                line_lower = line.lower()
                for keyword in self.CRITICAL_ERRORS:
                    if keyword.lower() in line_lower:
                        errors.append({
                            "type": "critical",
                            "keyword": keyword,
                            "message": line.strip()[:200]
                        })
                        break
                        
            for line in lines:
                for keyword in self.ERROR_KEYWORDS:
                    if keyword.lower() in line.lower() and "warning" not in line.lower():
                        if not any(e["message"] == line.strip()[:200] for e in errors):
                            errors.append({
                                "type": "error",
                                "keyword": keyword,
                                "message": line.strip()[:200]
                            })
                            
            for line in lines:
                for keyword in self.WARNING_KEYWORDS:
                    if keyword.lower() in line.lower():
                        warnings.append({
                            "keyword": keyword,
                            "message": line.strip()[:200]
                        })
                        
        except Exception as e:
            logger.error(f"Error detection failed: {e}")
            
        if errors:
            return {
                "has_errors": True,
                "errors": errors[:10],
                "warnings": warnings[:10],
                "error_count": len(errors),
                "warning_count": len(warnings)
            }
            
        return {
            "has_errors": False,
            "errors": [],
            "warnings": warnings[:10],
            "error_count": 0,
            "warning_count": len(warnings)
        }
    
    def _find_log_file(self) -> Optional[str]:
        """Find log file"""
        for root, dirs, files in os.walk(self.project_path):
            for f in files:
                if f == "md.log":
                    return os.path.join(root, f)
        return None
    
    def has_critical_errors(self) -> bool:
        """Check if there are critical errors"""
        result = self.detect_errors()
        if not result:
            return False
        return any(e["type"] == "critical" for e in result.get("errors", []))


def detect_errors(project_path: str) -> Optional[Dict]:
    """Standalone function to detect errors"""
    detector = ErrorDetector(project_path)
    return detector.detect_errors()
