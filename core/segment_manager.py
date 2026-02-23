"""
Segment Manager Module for BioDockify MD Universal
Manages segmented MD simulation execution
"""

import os
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class SegmentInfo:
    """Information about a simulation segment"""
    segment_id: int
    start_ns: float
    end_ns: float
    status: str  # "pending", "running", "completed", "failed"
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    checkpoint_file: Optional[str] = None
    output_dir: Optional[str] = None


class SegmentManager:
    """
    Manages segmented MD simulation execution.
    
    Segments allow long simulations to be broken into manageable chunks
    with automatic checkpoint/resume capability.
    """
    
    def __init__(
        self,
        project_path: str,
        total_ns: float,
        segment_ns: float = 10.0
    ):
        """
        Initialize segment manager.
        
        Args:
            project_path: Path to the project directory
            total_ns: Total simulation time in nanoseconds
            segment_ns: Length of each segment in nanoseconds
        """
        self.project_path = project_path
        self.total_ns = total_ns
        self.segment_ns = segment_ns
        self.segments: List[SegmentInfo] = []
        
        self._initialize_segments()
        
    def _initialize_segments(self):
        """Initialize segment information"""
        num_segments = self.calculate_num_segments()
        
        self.segments = []
        for i in range(num_segments):
            start_ns = i * self.segment_ns
            end_ns = min((i + 1) * self.segment_ns, self.total_ns)
            
            segment = SegmentInfo(
                segment_id=i,
                start_ns=start_ns,
                end_ns=end_ns,
                status="pending",
                output_dir=os.path.join(self.project_path, f"segment_{i:03d}")
            )
            self.segments.append(segment)
            
        logger.info(f"Initialized {len(self.segments)} segments of {self.segment_ns}ns each")
        
    def calculate_num_segments(self) -> int:
        """
        Calculate the number of segments needed.
        
        Returns:
            Number of segments
        """
        return int((self.total_ns + self.segment_ns - 1) // self.segment_ns)
        
    def get_next_segment(self) -> Optional[SegmentInfo]:
        """
        Get the next pending segment to run.
        
        Returns:
            SegmentInfo for the next segment, or None if all complete
        """
        for segment in self.segments:
            if segment.status == "pending":
                return segment
                
        # Check for failed segments to retry
        for segment in self.segments:
            if segment.status == "failed":
                logger.warning(f"Retrying failed segment {segment.segment_id}")
                return segment
                
        return None
        
    def get_current_segment(self) -> Optional[SegmentInfo]:
        """Get the currently running segment"""
        for segment in self.segments:
            if segment.status == "running":
                return segment
        return None
        
    def get_completed_segments(self) -> List[SegmentInfo]:
        """Get list of completed segments"""
        return [s for s in self.segments if s.status == "completed"]
        
    def get_segment_by_id(self, segment_id: int) -> Optional[SegmentInfo]:
        """Get segment by ID"""
        for segment in self.segments:
            if segment.segment_id == segment_id:
                return segment
        return None
        
    def start_segment(self, segment_id: int):
        """Mark a segment as started"""
        segment = self.get_segment_by_id(segment_id)
        if segment:
            segment.status = "running"
            segment.start_time = datetime.now()
            logger.info(f"Started segment {segment_id} ({segment.start_ns}-{segment.end_ns} ns)")
            
    def complete_segment(self, segment_id: int, checkpoint_file: str = None):
        """Mark a segment as completed"""
        segment = self.get_segment_by_id(segment_id)
        if segment:
            segment.status = "completed"
            segment.end_time = datetime.now()
            segment.checkpoint_file = checkpoint_file
            
            duration = segment.end_time - segment.start_time
            logger.info(
                f"Completed segment {segment_id} in {duration.total_seconds():.1f}s"
            )
            
    def fail_segment(self, segment_id: int, error: str = None):
        """Mark a segment as failed"""
        segment = self.get_segment_by_id(segment_id)
        if segment:
            segment.status = "failed"
            segment.end_time = datetime.now()
            logger.error(f"Failed segment {segment_id}: {error}")
            
    def get_progress(self) -> Tuple[int, int]:
        """
        Get current progress.
        
        Returns:
            Tuple of (completed_segments, total_segments)
        """
        completed = len(self.get_completed_segments())
        total = len(self.segments)
        return completed, total
        
    def get_progress_percentage(self) -> float:
        """Get progress as percentage"""
        completed, total = self.get_progress()
        if total == 0:
            return 0.0
        return (completed / total) * 100
    
    def get_simulated_ns(self) -> float:
        """Get total simulated nanoseconds"""
        completed = self.get_completed_segments()
        total = 0.0
        for segment in completed:
            total += (segment.end_ns - segment.start_ns)
        return total
        
    def save_state(self, state_file: str = None):
        """Save segment state to file"""
        import json
        
        if state_file is None:
            state_file = os.path.join(self.project_path, ".segment_state.json")
            
        state = {
            "total_ns": self.total_ns,
            "segment_ns": self.segment_ns,
            "segments": [
                {
                    "segment_id": s.segment_id,
                    "start_ns": s.start_ns,
                    "end_ns": s.end_ns,
                    "status": s.status,
                    "start_time": s.start_time.isoformat() if s.start_time else None,
                    "end_time": s.end_time.isoformat() if s.end_time else None,
                    "checkpoint_file": s.checkpoint_file,
                    "output_dir": s.output_dir
                }
                for s in self.segments
            ]
        }
        
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)
            
        logger.debug(f"Segment state saved to {state_file}")
        
    @classmethod
    def load_state(cls, project_path: str, state_file: str = None) -> 'SegmentManager':
        """Load segment state from file"""
        import json
        
        if state_file is None:
            state_file = os.path.join(project_path, ".segment_state.json")
            
        if not os.path.exists(state_file):
            raise FileNotFoundError(f"No segment state file found: {state_file}")
            
        with open(state_file, 'r') as f:
            state = json.load(f)
            
        manager = cls(
            project_path=project_path,
            total_ns=state["total_ns"],
            segment_ns=state["segment_ns"]
        )
        
        # Update segment states
        for seg_state in state["segments"]:
            segment = manager.get_segment_by_id(seg_state["segment_id"])
            if segment:
                segment.status = seg_state["status"]
                if seg_state["start_time"]:
                    segment.start_time = datetime.fromisoformat(seg_state["start_time"])
                if seg_state["end_time"]:
                    segment.end_time = datetime.fromisoformat(seg_state["end_time"])
                segment.checkpoint_file = seg_state.get("checkpoint_file")
                
        logger.info(f"Loaded segment state from {state_file}")
        return manager
        
    def get_segment_output_prefix(self, segment_id: int) -> str:
        """Get the output file prefix for a segment"""
        segment = self.get_segment_by_id(segment_id)
        if segment and segment.output_dir:
            return os.path.join(segment.output_dir, f"md")
        return os.path.join(self.project_path, f"segment_{segment_id:03d}", "md")
        
    def get_latest_checkpoint(self, segment_id: int) -> Optional[str]:
        """Get the latest checkpoint file for a segment"""
        segment = self.get_segment_by_id(segment_id)
        if not segment:
            return None
            
        # Check for checkpoint files
        output_dir = segment.output_dir or os.path.join(
            self.project_path, f"segment_{segment_id:03d}"
        )
        
        # Look for .cpt files
        cpt_files = []
        if os.path.exists(output_dir):
            for f in os.listdir(output_dir):
                if f.endswith(".cpt"):
                    cpt_files.append(os.path.join(output_dir, f))
                    
        if cpt_files:
            # Return most recent
            return max(cpt_files, key=os.path.getmtime)
            
        return None


if __name__ == "__main__":
    # Test segment manager
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        print("Testing Segment Manager...")
        
        manager = SegmentManager(tmpdir, total_ns=100, segment_ns=10)
        
        print(f"Total segments: {manager.calculate_num_segments()}")
        print(f"Progress: {manager.get_progress_percentage():.1f}%")
        
        # Simulate running a segment
        seg = manager.get_next_segment()
        if seg:
            print(f"Next segment: {seg.segment_id}")
            manager.start_segment(seg.segment_id)
            manager.complete_segment(seg.segment_id)
            
        print(f"Progress: {manager.get_progress_percentage():.1f}%")
        
        manager.save_state()
        
        # Test loading
        manager2 = SegmentManager.load_state(tmpdir)
        print(f"Loaded segments: {len(manager2.segments)}")
