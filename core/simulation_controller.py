"""
Simulation Controller Module for BioDockify MD Universal
Controls MD simulation execution
"""

import os
import subprocess
import logging
import time
import threading
from typing import Optional, Dict, Callable, Any
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
        
        # DIAGNOSTIC: Check WSL availability
        import subprocess
        try:
            wsl_check = subprocess.run(
                "wsl --status",
                shell=True,
                capture_output=True,
                timeout=10
            )
            logger.info(f"WSL status check: returncode={wsl_check.returncode}")
        except Exception as e:
            logger.warning(f"WSL may not be available: {e}")
        
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
            # Add checkpoint file to command - properly quoted to handle spaces
            # DIAGNOSTIC: Log checkpoint path for debugging
            logger.info(f"Resume checkpoint file: {checkpoint_file}")
            if ' ' in checkpoint_file:
                logger.warning(f"Checkpoint path contains spaces - will use quoted form")
                cmd += f' "{checkpoint_file}"'
            else:
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
        """Parse progress information from log file with enhanced accuracy"""
        try:
            if not os.path.exists(log_file):
                return None
                
            with open(log_file, 'r') as f:
                content = f.read()
                lines = content.split('\n')
            
            result = {
                "log_file": log_file,
                "status": "unknown",
                "progress_percent": 0.0,
                "current_step": 0,
                "total_steps": 0,
                "current_time_ps": 0.0,
                "target_time_ps": 0.0,
                "ns_per_day": None,
                "eta_hours": None,
                "temperature": None,
                "pressure": None,
                "density": None,
                "energies": {},
                "warnings": [],
                "errors": []
            }
            
            # Look for progress information in last 100 lines
            recent_lines = lines[-100:] if len(lines) > 100 else lines
            
            for line in recent_lines:
                # Parse step and time
                if "Step" in line and "Time" in line:
                    result["status"] = "running"
                    
                # Parse actual step data
                if line.strip() and line[0].isdigit():
                    parts = line.split()
                    if len(parts) >= 2:
                        try:
                            result["current_step"] = int(parts[0])
                            result["current_time_ps"] = float(parts[1])
                        except (ValueError, IndexError):
                            pass
                            
                # Parse performance metrics (ns/day)
                if "ns/day" in line.lower() or "ns/day" in line:
                    try:
                        # Extract ns/day value
                        for part in line.split():
                            if "ns/day" in part.lower():
                                idx = line.split().index(part)
                                if idx > 0:
                                    ns_val = line.split()[idx - 1]
                                    result["ns_per_day"] = float(ns_val)
                                    break
                    except (ValueError, IndexError):
                        pass
                
                # Parse temperature
                if "Temperature" in line:
                    try:
                        parts = line.split('=')
                        if len(parts) > 1:
                            temp = parts[1].split()[0]
                            result["temperature"] = float(temp)
                    except (ValueError, IndexError):
                        pass
                
                # Parse pressure
                if "Pressure" in line:
                    try:
                        parts = line.split('=')
                        if len(parts) > 1:
                            press = parts[1].split()[0]
                            result["pressure"] = float(press)
                    except (ValueError, IndexError):
                        pass
                
                # Parse density
                if "Density" in line:
                    try:
                        parts = line.split('=')
                        if len(parts) > 1:
                            dens = parts[1].split()[0]
                            result["density"] = float(dens)
                    except (ValueError, IndexError):
                        pass
                
                # Parse potential energy
                if "Potential" in line and "Kinetic" not in line:
                    try:
                        parts = line.split('=')
                        if len(parts) > 1:
                            e_val = parts[1].split()[0]
                            result["energies"]["potential"] = float(e_val)
                    except (ValueError, IndexError):
                        pass
                
                # Parse kinetic energy
                if "Kinetic En." in line:
                    try:
                        parts = line.split('=')
                        if len(parts) > 1:
                            e_val = parts[1].split()[0]
                            result["energies"]["kinetic"] = float(e_val)
                    except (ValueError, IndexError):
                        pass
                
                # Parse total energy
                if "Total Energy" in line or "Etot" in line:
                    try:
                        parts = line.split('=')
                        if len(parts) > 1:
                            e_val = parts[1].split()[0]
                            result["energies"]["total"] = float(e_val)
                    except (ValueError, IndexError):
                        pass
                
                # Check for warnings
                if "WARNING" in line.upper():
                    result["warnings"].append(line.strip())
                
                # Check for errors
                if "ERROR" in line.upper() or "FAILED" in line.upper():
                    result["errors"].append(line.strip())
                    result["status"] = "error"
            
            # Try to get total steps from MDP content if available
            # This is a simplification - in practice you'd parse from .mdp or .tpr
            if result["current_time_ps"] > 0:
                # Estimate progress if we have target info
                result["status"] = "running"
            
            return result
                    
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
        if not self.process or not self.current_segment_id:
            return None
            
        try:
            # Try to find the log file from output prefix
            # This is a placeholder - actual implementation would need
            # the output prefix passed in
            return None
        except Exception as e:
            logger.debug(f"Error estimating time: {e}")
            return None
    
    def get_progress_details(self, output_prefix: str = None) -> Dict[str, Any]:
        """
        Get detailed progress information for a simulation.
        
        Args:
            output_prefix: Output file prefix (optional)
            
        Returns:
            Dictionary with detailed progress info
        """
        if not output_prefix:
            output_prefix = f"{self.project_path}/md"
            
        log_file = f"{output_prefix}.log"
        
        progress = {
            "is_running": self.is_running,
            "segment_id": self.current_segment_id,
            "backend": self.backend,
            "progress": 0.0,
            "current_step": 0,
            "target_steps": 0,
            "current_time_ps": 0.0,
            "target_time_ps": 0.0,
            "progress_ns": 0.0,
            "target_ns": 0.0,
            "ns_per_day": None,
            "eta_hours": None,
            "temperature": None,
            "pressure": None,
            "density": None,
            "energies": {},
            "warnings": [],
            "errors": [],
            "status": "unknown"
        }
        
        if self.is_running:
            progress["status"] = "running"
            log_progress = self._parse_progress(log_file)
            if log_progress:
                progress.update(log_progress)
                
                # Calculate progress percentage
                if progress.get("current_time_ps", 0) > 0 and progress.get("target_time_ps", 0) > 0:
                    progress["progress_percent"] = min(
                        100.0,
                        (progress["current_time_ps"] / progress["target_time_ps"]) * 100
                    )
                
                # Calculate ETA if we have ns/day
                if progress.get("ns_per_day"):
                    remaining_ns = progress.get("target_ns", 0) - progress.get("progress_ns", 0)
                    if remaining_ns > 0:
                        progress["eta_hours"] = remaining_ns / progress["ns_per_day"] * 24
        else:
            progress["status"] = "stopped"
        
        return progress
        
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
        from .backend_selector import get_gmx_command_prefix
        
        tpr_file = f"{output_prefix}.tpr"
        
        # Use appropriate GROMACS command prefix based on WSL availability
        gmx_prefix = get_gmx_command_prefix()
        cmd = f"{gmx_prefix} grompp -f {mdp_file} -c {structure_file} -o {tpr_file} -p topol.top"
        
        logger.info(f"Running grompp: {cmd}")
        
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
