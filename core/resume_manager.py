"""
Resume Manager Module for BioDockify MD Universal
Manages simulation resume from checkpoints
"""

import os
import logging
import json
from typing import Optional, Dict, List, Tuple
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class ResumeManager:
    """
    Manages simulation resume from checkpoints.
    
    Handles detection of incomplete simulations and automatic
    continuation from the last valid checkpoint.
    """
    
    def __init__(self, project_path: str):
        """
        Initialize resume manager.
        
        Args:
            project_path: Path to the project directory
        """
        self.project_path = project_path
        
    def find_last_completed_segment(self) -> Optional[int]:
        """
        Find the last completed segment number.
        
        Returns:
            Segment ID of last completed segment, or None if none found
        """
        if not os.path.exists(self.project_path):
            return None
            
        segment_dirs = []
        for item in os.listdir(self.project_path):
            if item.startswith("segment_") and os.path.isdir(
                os.path.join(self.project_path, item)
            ):
                try:
                    seg_num = int(item.split("_")[1])
                    segment_dirs.append(seg_num)
                except (IndexError, ValueError):
                    continue
                    
        if not segment_dirs:
            return None
            
        # Find last completed segment (has final output)
        max_seg = max(segment_dirs)
        
        # Check if segment has complete output
        seg_dir = os.path.join(self.project_path, f"segment_{max_seg:03d}")
        
        # Check for required output files
        required_files = ["md_final.gro"]  # At minimum, we need final structure
        
        for req_file in required_files:
            if not os.path.exists(os.path.join(seg_dir, req_file)):
                # Segment may not be complete
                # Check if there's a checkpoint to resume from
                cpt_files = [f for f in os.listdir(seg_dir) if f.endswith(".cpt")]
                if cpt_files:
                    logger.info(f"Segment {max_seg} has checkpoint, can resume")
                    return max_seg
                return max_seg - 1 if max_seg > 0 else None
                
        return max_seg
        
    def find_checkpoint_to_resume(self, segment_id: int) -> Optional[str]:
        """
        Find the checkpoint file to resume from.
        
        Args:
            segment_id: Segment ID to find checkpoint for
            
        Returns:
            Path to checkpoint file, or None if not found
        """
        seg_dir = os.path.join(self.project_path, f"segment_{segment_id:03d}")
        
        if not os.path.exists(seg_dir):
            return None
            
        # Look for checkpoint files (.cpt)
        cpt_files = []
        for f in os.listdir(seg_dir):
            if f.endswith(".cpt"):
                cpt_files.append(os.path.join(seg_dir, f))
                
        if cpt_files:
            # Return most recent checkpoint
            latest = max(cpt_files, key=os.path.getmtime)
            logger.info(f"Found checkpoint: {latest}")
            return latest
            
        return None
        
    def check_simulation_complete(self) -> bool:
        """
        Check if the entire simulation is complete.
        
        Returns:
            True if simulation is complete
        """
        # Look for completion marker
        complete_marker = os.path.join(self.project_path, ".simulation_complete")
        
        if os.path.exists(complete_marker):
            return True
            
        # Also check for final trajectory
        final_trajectory = os.path.join(self.project_path, "final_trajectory.xtc")
        
        return os.path.exists(final_trajectory)
        
    def get_resume_info(self) -> Optional[Dict]:
        """
        Get information needed to resume simulation.
        
        Returns:
            Dictionary with resume information, or None if nothing to resume
        """
        if self.check_simulation_complete():
            logger.info("Simulation already complete")
            return None
            
        last_segment = self.find_last_completed_segment()
        
        if last_segment is None:
            logger.info("No previous segments found, starting fresh")
            return None
            
        # Find checkpoint to resume from
        checkpoint = self.find_checkpoint_to_resume(last_segment)
        
        resume_info = {
            "segment_id": last_segment,
            "checkpoint_file": checkpoint,
            "resume_type": "checkpoint" if checkpoint else "restart"
        }
        
        logger.info(f"Resume info: {resume_info}")
        return resume_info
        
    def create_resume_marker(self, segment_id: int):
        """Create a marker file indicating resume is in progress"""
        marker_file = os.path.join(
            self.project_path, 
            f".resume_segment_{segment_id}"
        )
        
        with open(marker_file, 'w') as f:
            f.write(datetime.now().isoformat())
            
        logger.info(f"Created resume marker for segment {segment_id}")
        
    def clear_resume_marker(self, segment_id: int):
        """Clear resume marker after successful segment start"""
        marker_file = os.path.join(
            self.project_path, 
            f".resume_segment_{segment_id}"
        )
        
        if os.path.exists(marker_file):
            os.remove(marker_file)
            
    def get_simulation_metadata(self) -> Dict:
        """Get simulation metadata from project"""
        metadata_file = os.path.join(self.project_path, "simulation_metadata.json")
        
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r') as f:
                return json.load(f)
                
        return {}
        
    def save_simulation_metadata(self, metadata: Dict):
        """Save simulation metadata to project"""
        metadata_file = os.path.join(self.project_path, "simulation_metadata.json")
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
            
        logger.info("Saved simulation metadata")
        
    def update_progress(self, segment_id: int, progress_ns: float):
        """Update simulation progress"""
        metadata = self.get_simulation_metadata()
        
        if "segments" not in metadata:
            metadata["segments"] = {}
            
        metadata["segments"][str(segment_id)] = {
            "progress_ns": progress_ns,
            "last_update": datetime.now().isoformat()
        }
        
        metadata["last_segment"] = segment_id
        metadata["last_update"] = datetime.now().isoformat()
        
        self.save_simulation_metadata(metadata)
        
    def get_disk_usage(self) -> Dict:
        """Get disk usage information for project"""
        import shutil
        
        if not os.path.exists(self.project_path):
            return {"total_mb": 0, "free_mb": 0}
            
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(self.project_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if os.path.exists(fp):
                    total_size += os.path.getsize(fp)
                    
        return {
            "total_mb": total_size / (1024 * 1024),
            "total_gb": total_size / (1024 * 1024 * 1024)
        }
        
    def validate_project_structure(self) -> Tuple[bool, List[str]]:
        """
        Validate that project has required structure.
        
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        if not os.path.exists(self.project_path):
            issues.append(f"Project path does not exist: {self.project_path}")
            return False, issues
            
        # Check for required directories
        required_dirs = ["."]
        
        # Check for structure file
        structure_file = os.path.join(
            self.project_path, 
            "project_structure.json"
        )
        
        if os.path.exists(structure_file):
            with open(structure_file, 'r') as f:
                structure = json.load(f)
                required_dirs = structure.get("required_directories", ["."])
                
        for req_dir in required_dirs:
            full_path = os.path.join(self.project_path, req_dir)
            if not os.path.exists(full_path):
                issues.append(f"Required directory missing: {req_dir}")
                
        return len(issues) == 0, issues
        
    def cleanup_incomplete_segments(self):
        """Clean up incomplete or failed segment directories"""
        if not os.path.exists(self.project_path):
            return
            
        for item in os.listdir(self.project_path):
            if not item.startswith("segment_"):
                continue
                
            seg_dir = os.path.join(self.project_path, item)
            if not os.path.isdir(seg_dir):
                continue
                
            # Check if segment is incomplete
            has_final = os.path.exists(os.path.join(seg_dir, "md_final.gro"))
            has_cpt = any(f.endswith(".cpt") for f in os.listdir(seg_dir))
            
            if not has_final and not has_cpt:
                logger.info(f"Cleaning up incomplete segment: {item}")
                try:
                    import shutil
                    shutil.rmtree(seg_dir)
                except Exception as e:
                    logger.error(f"Failed to clean up {item}: {e}")


if __name__ == "__main__":
    # Test resume manager
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        print("Testing Resume Manager...")
        
        manager = ResumeManager(tmpdir)
        
        # Test with no previous segments
        info = manager.get_resume_info()
        print(f"Resume info (empty): {info}")
        
        # Test validation
        valid, issues = manager.validate_project_structure()
        print(f"Valid: {valid}, Issues: {issues}")
