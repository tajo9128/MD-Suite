"""
Integrity Checker for Nanobot
Verifies checkpoint and data integrity
"""

import os
import time
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class IntegrityChecker:
    """
    Verifies checkpoint and data integrity
    to prevent corruption and detect freezes.
    """
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        self._last_checkpoint_time = None
        self._last_xtc_size = 0
        self._last_edr_size = 0
        
    def check_checkpoint_integrity(self, segment_dir: str = None) -> Dict:
        """
        Check if checkpoint is being updated.
        Returns integrity status.
        """
        result = {
            "is_valid": True,
            "checkpoint_age_seconds": None,
            "issues": []
        }
        
        checkpoint_file = self._find_checkpoint(segment_dir)
        
        if not checkpoint_file:
            result["is_valid"] = False
            result["issues"].append("No checkpoint file found")
            return result
            
        try:
            mtime = os.path.getmtime(checkpoint_file)
            age = time.time() - mtime
            
            result["checkpoint_age_seconds"] = age
            result["checkpoint_file"] = checkpoint_file
            
            if age > 900:
                result["is_valid"] = False
                result["issues"].append(f"Checkpoint older than 15 minutes ({age/60:.1f} min)")
                
        except Exception as e:
            result["is_valid"] = False
            result["issues"].append(f"Checkpoint check failed: {e}")
            
        return result
    
    def _find_checkpoint(self, segment_dir: str = None) -> Optional[str]:
        """Find checkpoint file"""
        if segment_dir is None:
            for item in os.listdir(self.project_path):
                if "segment" in item:
                    segment_dir = os.path.join(self.project_path, item)
                    break
                    
        if segment_dir and os.path.exists(segment_dir):
            for f in os.listdir(segment_dir):
                if f.endswith(".cpt"):
                    return os.path.join(segment_dir, f)
                    
        return None
    
    def check_file_growth(self, segment_dir: str = None) -> Dict:
        """
        Check if trajectory and energy files are growing.
        Detects simulation freezes.
        """
        result = {
            "is_growing": True,
            "xtc_delta_bytes": 0,
            "edr_delta_bytes": 0,
            "issues": []
        }
        
        if segment_dir is None:
            for item in os.listdir(self.project_path):
                if "segment" in item:
                    segment_dir = os.path.join(self.project_path, item)
                    break
                    
        if not segment_dir:
            result["issues"].append("No segment directory found")
            return result
            
        xtc_file = os.path.join(segment_dir, "md.xtc")
        edr_file = os.path.join(segment_dir, "md.edr")
        
        try:
            if os.path.exists(xtc_file):
                current_size = os.path.getsize(xtc_file)
                result["xtc_delta_bytes"] = current_size - self._last_xtc_size
                self._last_xtc_size = current_size
                
            if os.path.exists(edr_file):
                current_size = os.path.getsize(edr_file)
                result["edr_delta_bytes"] = current_size - self._last_edr_size
                self._last_edr_size = current_size
                
            if result["xtc_delta_bytes"] == 0 and result["edr_delta_bytes"] == 0:
                result["is_growing"] = False
                result["issues"].append("Files not growing - possible freeze")
                
        except Exception as e:
            result["issues"].append(f"Growth check failed: {e}")
            
        return result
    
    def verify_segment_completeness(self) -> Dict:
        """
        Verify all segments are complete and sequential.
        """
        result = {
            "is_complete": True,
            "segments": [],
            "missing_segments": [],
            "issues": []
        }
        
        try:
            segments = []
            for item in os.listdir(self.project_path):
                if os.path.isdir(os.path.join(self.project_path, item)) and "segment" in item:
                    segments.append(item)
                    
            segments.sort()
            
            expected = 0
            for seg in segments:
                if f"segment_{expected:03d}" == seg:
                    result["segments"].append(seg)
                    expected += 1
                else:
                    result["missing_segments"].append(f"segment_{expected:03d}")
                    result["is_complete"] = False
                    
        except Exception as e:
            result["issues"].append(str(e))
            result["is_complete"] = False
            
        return result
    
    def check_data_consistency(self) -> Dict:
        """
        Check overall data consistency before finalization.
        """
        result = {
            "is_consistent": True,
            "checks": [],
            "issues": []
        }
        
        checkpoint = self.check_checkpoint_integrity()
        result["checks"].append(checkpoint)
        if not checkpoint["is_valid"]:
            result["is_consistent"] = False
            
        growth = self.check_file_growth()
        result["checks"].append(growth)
        
        segments = self.verify_segment_completeness()
        result["checks"].append(segments)
        if not segments["is_complete"]:
            result["is_consistent"] = False
            
        return result


def check_integrity(project_path: str) -> Dict:
    """Standalone integrity check"""
    checker = IntegrityChecker(project_path)
    return checker.check_data_consistency()
