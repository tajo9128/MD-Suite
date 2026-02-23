"""
Metadata Logger Module for BioDockify MD Universal
Logs and manages simulation metadata
"""

import os
import json
import logging
from typing import Dict, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class SimulationMetadata:
    """Simulation metadata structure"""
    project_name: str
    project_path: str
    start_time: str
    end_time: Optional[str] = None
    total_ns: float = 0.0
    segment_ns: float = 10.0
    num_segments: int = 0
    completed_segments: int = 0
    backend: str = "unknown"
    gpu_vendor: str = "unknown"
    status: str = "initialized"  # initialized, running, paused, completed, failed
    errors: list = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class MetadataLogger:
    """
    Manages simulation metadata logging.
    
    Tracks all simulation parameters, progress, and events
    for reproducibility and debugging.
    """
    
    def __init__(self, project_path: str):
        """
        Initialize metadata logger.
        
        Args:
            project_path: Path to the project directory
        """
        self.project_path = project_path
        self.metadata_file = os.path.join(project_path, "simulation_metadata.json")
        
        self.metadata: Optional[SimulationMetadata] = None
        self._load_metadata()
        
    def _load_metadata(self):
        """Load existing metadata if available"""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r') as f:
                    data = json.load(f)
                    self.metadata = SimulationMetadata(**data)
                    logger.info(f"Loaded existing metadata from {self.metadata_file}")
            except Exception as e:
                logger.warning(f"Could not load metadata: {e}")
                self.metadata = None
                
    def _save_metadata(self):
        """Save metadata to file"""
        if self.metadata is None:
            return
            
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(asdict(self.metadata), f, indent=2)
            logger.debug("Metadata saved")
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")
            
    def initialize(
        self,
        project_name: str,
        total_ns: float,
        segment_ns: float,
        backend: str,
        gpu_info: Dict[str, Any]
    ):
        """
        Initialize metadata for new simulation.
        
        Args:
            project_name: Name of the project
            total_ns: Total simulation time in ns
            segment_ns: Segment length in ns
            backend: GROMACS backend used
            gpu_info: GPU information
        """
        import math
        
        self.metadata = SimulationMetadata(
            project_name=project_name,
            project_path=self.project_path,
            start_time=datetime.now().isoformat(),
            total_ns=total_ns,
            segment_ns=segment_ns,
            num_segments=math.ceil(total_ns / segment_ns),
            backend=backend,
            gpu_vendor=gpu_info.get("vendor", "unknown"),
            status="initialized"
        )
        
        self._save_metadata()
        logger.info(f"Initialized metadata for project: {project_name}")
        
    def start_simulation(self):
        """Mark simulation as started"""
        if self.metadata:
            self.metadata.status = "running"
            self._save_metadata()
            
    def update_progress(
        self,
        completed_segments: int,
        simulated_ns: float = None
    ):
        """
        Update simulation progress.
        
        Args:
            completed_segments: Number of completed segments
            simulated_ns: Total simulated time
        """
        if self.metadata:
            self.metadata.completed_segments = completed_segments
            
            if simulated_ns is not None:
                self.metadata.total_ns = simulated_ns
                
            self._save_metadata()
            
    def add_error(self, error: str):
        """Add an error message"""
        if self.metadata:
            if self.metadata.errors is None:
                self.metadata.errors = []
            self.metadata.errors.append({
                "time": datetime.now().isoformat(),
                "error": error
            })
            self._save_metadata()
            
    def complete_simulation(self):
        """Mark simulation as completed"""
        if self.metadata:
            self.metadata.status = "completed"
            self.metadata.end_time = datetime.now().isoformat()
            self._save_metadata()
            
    def fail_simulation(self, error: str):
        """Mark simulation as failed"""
        if self.metadata:
            self.metadata.status = "failed"
            self.metadata.end_time = datetime.now().isoformat()
            self.add_error(error)
            self._save_metadata()
            
    def get_metadata(self) -> Optional[Dict]:
        """Get current metadata"""
        if self.metadata:
            return asdict(self.metadata)
        return None
        
    def get_status(self) -> str:
        """Get current simulation status"""
        if self.metadata:
            return self.metadata.status
        return "unknown"
        
    def get_progress(self) -> float:
        """Get progress percentage"""
        if self.metadata and self.metadata.num_segments > 0:
            return (self.metadata.completed_segments / self.metadata.num_segments) * 100
        return 0.0
        
    def log_event(self, event_type: str, event_data: Dict[str, Any]):
        """
        Log a simulation event.
        
        Args:
            event_type: Type of event
            event_data: Event data
        """
        if self.metadata is None:
            return
            
        event_file = os.path.join(self.project_path, "simulation_events.json")
        
        events = []
        if os.path.exists(event_file):
            try:
                with open(event_file, 'r') as f:
                    events = json.load(f)
            except:
                events = []
                
        event = {
            "type": event_type,
            "timestamp": datetime.now().isoformat(),
            "data": event_data
        }
        
        events.append(event)
        
        try:
            with open(event_file, 'w') as f:
                json.dump(events, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to log event: {e}")
            
    def export_summary(self, output_file: str):
        """
        Export metadata summary.
        
        Args:
            output_file: Output file path
        """
        if self.metadata is None:
            logger.warning("No metadata to export")
            return
            
        summary = {
            "project": self.metadata.project_name,
            "status": self.metadata.status,
            "progress": f"{self.get_progress():.1f}%",
            "completed_segments": self.metadata.completed_segments,
            "total_segments": self.metadata.num_segments,
            "total_ns": self.metadata.total_ns,
            "backend": self.metadata.backend,
            "gpu": self.metadata.gpu_vendor,
            "start_time": self.metadata.start_time,
            "end_time": self.metadata.end_time
        }
        
        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2)
            
        logger.info(f"Exported summary to {output_file}")
        
    def validate(self) -> Dict:
        """
        Validate metadata.
        
        Returns:
            Validation results
        """
        results = {
            "valid": True,
            "issues": []
        }
        
        if self.metadata is None:
            results["valid"] = False
            results["issues"].append("No metadata available")
            return results
            
        # Check required fields
        required_fields = ["project_name", "project_path", "start_time", "backend"]
        
        for field in required_fields:
            if not getattr(self.metadata, field, None):
                results["issues"].append(f"Missing required field: {field}")
                results["valid"] = False
                
        # Check status
        valid_statuses = ["initialized", "running", "paused", "completed", "failed"]
        if self.metadata.status not in valid_statuses:
            results["issues"].append(f"Invalid status: {self.metadata.status}")
            results["valid"] = False
            
        return results


def create_metadata_logger(project_path: str) -> MetadataLogger:
    """
    Factory function to create metadata logger.
    
    Args:
        project_path: Path to project
        
    Returns:
        MetadataLogger instance
    """
    return MetadataLogger(project_path)


if __name__ == "__main__":
    # Test metadata logger
    import tempfile
    
    logging.basicConfig(level=logging.INFO)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        print("Testing Metadata Logger...")
        
        logger = MetadataLogger(tmpdir)
        
        # Initialize
        logger.initialize(
            project_name="test_project",
            total_ns=100,
            segment_ns=10,
            backend="gmx_cuda",
            gpu_info={"vendor": "NVIDIA"}
        )
        
        print(f"Status: {logger.get_status()}")
        
        # Update progress
        logger.update_progress(5, 50.0)
        print(f"Progress: {logger.get_progress():.1f}%")
        
        # Complete
        logger.complete_simulation()
        
        print(f"Final status: {logger.get_status()}")
        
        # Get metadata
        meta = logger.get_metadata()
        print(f"Metadata: {json.dumps(meta, indent=2)}")
