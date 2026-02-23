"""
Simulation Controller Module for BioDockify MD Universal
Controls MD simulation execution
"""

import os
import subprocess
import logging
import time
import threading
from typing import Optional, Dict, Callable
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class SimulationController:
    """
    Controls MD simulation execution.
    
    Manages the lifecycle of GROMACS simulations including
    starting, monitoring, and stopping simulations.
    """
    
    def __init__(
        self,
        project_path: str,
        backend: str = "gmx_cuda",
        checkpoint_interval: int = 15
    ):
        """
        Initialize simulation controller.
        
        Args:
            project_path: Path to the project directory
            backend: GROMACS backend to use
            checkpoint_interval: Checkpoint interval in minutes
        """
        self.project_path = project_path
        self.backend = backend
        self.checkpoint_interval = checkpoint_interval
        
        self.process: Optional[subprocess.Popen] = None
        self.is_running = False
        self.current_segment_id: Optional[int] = None
        
        # Callbacks
        self.on_progress: Optional[Callable] = None
        self.on_complete: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
        
    def run_simulation(
        self,
        tpr_file: str,
        output_prefix: str,
        resume: bool = False,
        checkpoint_file: Optional[str] = None,
        segment_id: Optional[int] = None
    ) -> bool:
        """
        Run a GROMACS simulation.
        
        Args:
            tpr_file: Path to TPR input file
            output_prefix: Output file prefix
            resume: Whether this is a resume
            checkpoint_file: Checkpoint file to resume from
            segment_id: Current segment ID
            
        Returns:
            True if simulation started successfully
        """
        from .backend_selector import get_mdrun_command
        
        self.current_segment_id = segment_id
        
        # Build the mdrun command
        cmd = get_mdrun_command(
            backend=self.backend,
            tpr_file=tpr_file,
            output_prefix=output_prefix,
            resume=resume,
            checkpoint_interval=self.checkpoint_interval
        )
        
        if resume and checkpoint_file:
            # Add checkpoint file to command
            cmd += f" {checkpoint_file}"
            
        logger.info(f"Starting simulation: {cmd}")
        
        try:
            # Create output directory
            output_dir = os.path.dirname(output_prefix)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            # Start simulation process
            self.process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=output_dir or self.project_path
            )
            
            self.is_running = True
            
            # Start monitoring thread
            monitor_thread = threading.Thread(
                target=self._monitor_simulation,
                args=(output_prefix,),
                daemon=True
            )
            monitor_thread.start()
            
            logger.info(f"Simulation started with PID {self.process.pid}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start simulation: {e}")
            self.is_running = False
            
            if self.on_error:
                self.on_error(str(e))
                
            return False
            
    def _monitor_simulation(self, output_prefix: str):
        """Monitor simulation progress"""
        log_file = f"{output_prefix}.log"
        
        while self.is_running and self.process:
            # Check if process is still running
            if self.process.poll() is not None:
                self.is_running = False
                
                # Get exit code
                exit_code = self.process.returncode
                
                if exit_code == 0:
                    logger.info("Simulation completed successfully")
                    
                    if self.on_complete:
                        self.on_complete(output_prefix)
                else:
                    logger.error(f"Simulation failed with exit code {exit_code}")
                    
                    if self.on_error:
                        self.on_error(f"Exit code: {exit_code}")
                
                break
                
            # Try to parse progress from log file
            try:
                if os.path.exists(log_file):
                    progress = self._parse_progress(log_file)
                    
                    if progress and self.on_progress:
                        self.on_progress(progress)
                        
            except Exception as e:
                logger.debug(f"Progress parse error: {e}")
                
            time.sleep(10)  # Check every 10 seconds
            
    def _parse_progress(self, log_file: str) -> Optional[Dict]:
        """Parse progress information from log file"""
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
                
            # Look for performance/progress lines
            for line in lines[-20:]:  # Last 20 lines
                if "Performance:" in line:
                    # Try to extract timing info
                    return {
                        "log_file": log_file,
                        "status": "running"
                    }
                    
                if "Step           Time" in line:
                    return {
                        "log_file": log_file,
                        "status": "running"
                    }
                    
        except Exception as e:
            logger.debug(f"Failed to parse log: {e}")
            
        return None
        
    def stop_simulation(self):
        """Stop the running simulation"""
        if self.process and self.is_running:
            logger.info("Stopping simulation...")
            
            try:
                # Try graceful shutdown first
                self.process.terminate()
                
                # Wait for process to terminate
                try:
                    self.process.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    # Force kill if graceful fails
                    logger.warning("Graceful shutdown failed, forcing kill")
                    self.process.kill()
                    self.process.wait()
                    
            except Exception as e:
                logger.error(f"Error stopping simulation: {e}")
                
            finally:
                self.is_running = False
                self.process = None
                logger.info("Simulation stopped")
                
    def get_status(self) -> Dict:
        """Get current simulation status"""
        status = {
            "is_running": self.is_running,
            "backend": self.backend,
            "segment_id": self.current_segment_id,
            "process": None
        }
        
        if self.process:
            status["process"] = {
                "pid": self.process.pid,
                "running": self.process.poll() is None
            }
            
        return status
        
    def wait_for_completion(self, timeout: Optional[int] = None) -> bool:
        """
        Wait for simulation to complete.
        
        Args:
            timeout: Optional timeout in seconds
            
        Returns:
            True if completed successfully
        """
        if not self.process:
            return False
            
        try:
            self.process.wait(timeout=timeout)
            return self.process.returncode == 0
        except subprocess.TimeoutExpired:
            logger.warning(f"Simulation timed out after {timeout}s")
            return False
            
    def get_estimated_time_remaining(self) -> Optional[float]:
        """Estimate remaining simulation time based on log file"""
        # This would require parsing GROMACS log for detailed timing
        # Simplified implementation
        return None
        
    def validate_input_files(self, tpr_file: str) -> tuple[bool, list]:
        """
        Validate input files before starting simulation.
        
        Args:
            tpr_file: Path to TPR file
            
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        if not os.path.exists(tpr_file):
            issues.append(f"TPR file not found: {tpr_file}")
            return False, issues
            
        # Check file size (should be > 0)
        if os.path.getsize(tpr_file) == 0:
            issues.append("TPR file is empty")
            return False, issues
            
        return True, []
        
    def prepare_gromacs_input(
        self,
        structure_file: str,
        mdp_file: str,
        output_prefix: str
    ) -> Optional[str]:
        """
        Prepare GROMACS input using grompp.
        
        Args:
            structure_file: Structure file (.gro/.pdb)
            mdp_file: MDP parameter file
            output_prefix: Output prefix for TPR file
            
        Returns:
            Path to generated TPR file, or None on failure
        """
        tpr_file = f"{output_prefix}.tpr"
        
        cmd = f"wsl gmx grompp -f {mdp_file} -c {structure_file} -o {tpr_file} -p topol.top"
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                cwd=self.project_path,
                timeout=120
            )
            
            if result.returncode == 0:
                logger.info(f"Created TPR file: {tpr_file}")
                return tpr_file
            else:
                logger.error(f"grompp failed: {result.stderr}")
                
                if self.on_error:
                    self.on_error(f"grompp failed: {result.stderr}")
                    
                return None
                
        except subprocess.TimeoutExpired:
            logger.error("grompp timed out")
            return None
            
        except Exception as e:
            logger.error(f"grompp error: {e}")
            return None


class SimulationRunner:
    """
    High-level simulation runner that coordinates segments.
    """
    
    def __init__(self, project_path: str, config: Dict):
        self.project_path = project_path
        self.config = config
        
        self.segment_manager = None
        self.resume_manager = None
        self.controller: Optional[SimulationController] = None
        
    def initialize(self):
        """Initialize the runner"""
        from .segment_manager import SegmentManager
        from .resume_manager import ResumeManager
        
        # Initialize managers
        total_ns = self.config.get("total_ns", 100)
        segment_ns = self.config.get("segment_ns", 10)
        
        self.segment_manager = SegmentManager(
            self.project_path,
            total_ns=total_ns,
            segment_ns=segment_ns
        )
        
        self.resume_manager = ResumeManager(self.project_path)
        
        # Check for resume
        resume_info = self.resume_manager.get_resume_info()
        
        if resume_info:
            logger.info(f"Will resume from segment {resume_info['segment_id']}")
            
    def run_next_segment(self) -> bool:
        """Run the next simulation segment"""
        if not self.segment_manager:
            return False
            
        # Get next segment
        segment = self.segment_manager.get_next_segment()
        
        if not segment:
            logger.info("No more segments to run")
            return False
            
        # Start segment
        self.segment_manager.start_segment(segment.segment_id)
        
        # Create controller
        backend = self.config.get("backend", "gmx_cuda")
        checkpoint_interval = self.config.get("checkpoint_interval", 15)
        
        self.controller = SimulationController(
            self.project_path,
            backend=backend,
            checkpoint_interval=checkpoint_interval
        )
        
        # Setup callbacks
        self.controller.on_complete = lambda x: self._on_segment_complete(
            segment.segment_id, x
        )
        
        # Determine if this is a resume
        checkpoint = None
        if segment.segment_id > 0:
            checkpoint = self.segment_manager.get_latest_checkpoint(
                segment.segment_id - 1
            )
            
        # Run simulation
        tpr_file = os.path.join(segment.output_dir, "md.tpr")
        output_prefix = self.segment_manager.get_segment_output_prefix(
            segment.segment_id
        )
        
        success = self.controller.run_simulation(
            tpr_file=tpr_file,
            output_prefix=output_prefix,
            resume=checkpoint is not None,
            checkpoint_file=checkpoint,
            segment_id=segment.segment_id
        )
        
        return success
        
    def _on_segment_complete(self, segment_id: int, output_prefix: str):
        """Handle segment completion"""
        logger.info(f"Segment {segment_id} completed")
        
        if self.segment_manager:
            self.segment_manager.complete_segment(segment_id)
            self.segment_manager.save_state()
            
    def run_all_segments(self) -> bool:
        """Run all simulation segments"""
        while True:
            segment = self.segment_manager.get_next_segment()
            
            if not segment:
                break
                
            success = self.run_next_segment()
            
            if not success:
                logger.error(f"Failed to run segment {segment.segment_id}")
                return False
                
            # Wait for completion
            if self.controller:
                self.controller.wait_for_completion()
                
        return True


if __name__ == "__main__":
    # Test simulation controller
    import tempfile
    
    logging.basicConfig(level=logging.INFO)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        print("Testing Simulation Controller...")
        
        controller = SimulationController(tmpdir, backend="gmx_cpu")
        status = controller.get_status()
        
        print(f"Status: {status}")
        
        # Test input validation
        valid, issues = controller.validate_input_files("/nonexistent.tpr")
        print(f"Valid: {valid}, Issues: {issues}")
