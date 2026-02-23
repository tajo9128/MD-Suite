"""
Log Parser Module for BioDockify MD Universal
Parses GROMACS MD log files for progress and error detection
"""

import os
import re
import logging
from typing import Optional, Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)


class LogParser:
    """
    Parses GROMACS MD log files to extract simulation progress,
    errors, warnings, and performance metrics.
    """
    
    def __init__(self, project_path: str):
        """
        Initialize log parser.
        
        Args:
            project_path: Path to the project directory
        """
        self.project_path = project_path
        
    def find_log_file(self, segment_id: Optional[int] = None) -> Optional[str]:
        """
        Find the MD log file.
        
        Args:
            segment_id: Optional segment ID to look for
            
        Returns:
            Path to log file, or None if not found
        """
        if segment_id is not None:
            # Look in specific segment directory
            search_dir = os.path.join(self.project_path, f"segment_{segment_id:03d}")
        else:
            # Search for any md.log file
            search_dir = self.project_path
            
        if not os.path.exists(search_dir):
            return None
            
        # Look for .log files
        log_file = os.path.join(search_dir, "md.log")
        
        if os.path.exists(log_file):
            return log_file
            
        # Also check for other common log patterns
        for f in os.listdir(search_dir):
            if f.endswith(".log") and "md" in f.lower():
                return os.path.join(search_dir, f)
                
        return None
        
    def parse_log(self, log_file: Optional[str] = None) -> Dict:
        """
        Parse a GROMACS log file.
        
        Args:
            log_file: Path to log file, or None to auto-detect
            
        Returns:
            Dictionary with parsed information
        """
        if log_file is None:
            log_file = self.find_log_file()
            
        result = {
            "log_file": log_file,
            "is_running": False,
            "progress_percent": 0.0,
            "simulated_ns": 0.0,
            "target_ns": 0.0,
            "current_step": 0,
            "total_steps": 0,
            "errors": [],
            "warnings": [],
            "performance": {},
            "last_update": None
        }
        
        if not log_file or not os.path.exists(log_file):
            return result
            
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                
            # Check if simulation is still running
            result["is_running"] = self._check_running(content)
            
            # Parse progress information
            progress = self._parse_progress(lines)
            result.update(progress)
            
            # Parse errors
            errors = self._parse_errors(lines)
            result["errors"] = errors
            
            # Parse warnings
            warnings = self._parse_warnings(lines)
            result["warnings"] = warnings
            
            # Parse performance metrics
            performance = self._parse_performance(content)
            result["performance"] = performance
            
            # Last update time
            if lines:
                result["last_update"] = lines[-1][:50]  # First part of last line
                
        except Exception as e:
            logger.error(f"Failed to parse log file: {e}")
            result["errors"].append(f"Log parsing error: {str(e)}")
            
        return result
        
    def _check_running(self, content: str) -> bool:
        """Check if simulation is still running"""
        # Look for running indicators
        running_patterns = [
            "GROMACS:",
            "Running on",
            "Implementation:",
            "SIMULATION STATUS"
        ]
        
        # If we see these patterns and no completion message, likely running
        complete_patterns = [
            "GROMACS reminds you:",
            "Finished mdrun",
            "Writing final"
        ]
        
        for pattern in complete_patterns:
            if pattern in content:
                return False
                
        return True
        
    def _parse_progress(self, lines: List[str]) -> Dict:
        """Parse progress information from log lines"""
        progress = {
            "progress_percent": 0.0,
            "simulated_ns": 0.0,
            "target_ns": 0.0,
            "current_step": 0,
            "total_steps": 0
        }
        
        # Look for step/time information
        for line in lines[-100:]:  # Check last 100 lines
            # Pattern: "Step           Time" header followed by data
            if re.match(r'^\s*\d+\s+[\d.]+\s*$', line):
                parts = line.split()
                if len(parts) >= 2:
                    try:
                        progress["current_step"] = int(parts[0])
                        progress["simulated_ns"] = float(parts[1])
                    except ValueError:
                        pass
                        
            # Pattern: "Writing final trajectory"
            if "Writing final trajectory" in line:
                progress["progress_percent"] = 100.0
                
        # Look for target time in .mdp or config
        # For now, estimate from steps
        if progress["total_steps"] > 0:
            progress["progress_percent"] = (
                progress["current_step"] / progress["total_steps"] * 100
            )
            
        return progress
        
    def _parse_errors(self, lines: List[str]) -> List[str]:
        """Parse error messages from log lines"""
        errors = []
        
        error_keywords = [
            "ERROR:",
            "Fatal error:",
            "Segmentation fault",
            "Core dumped",
            "Out of memory",
            "invalid",
            "failed"
        ]
        
        for line in lines:
            # Check for error keywords
            for keyword in error_keywords:
                if keyword.lower() in line.lower():
                    # Avoid duplicates and false positives
                    if "error" not in line.lower() or "WARNING" not in line:
                        errors.append(line.strip())
                    break
                    
        return errors[:20]  # Limit to 20 errors
        
    def _parse_warnings(self, lines: List[str]) -> List[str]:
        """Parse warning messages from log lines"""
        warnings = []
        
        for line in lines:
            if "WARNING" in line:
                warnings.append(line.strip())
                
        return warnings[:20]  # Limit to 20 warnings
        
    def _parse_performance(self, content: str) -> Dict:
        """Parse performance metrics from log"""
        performance = {}
        
        # Look for performance summary
        if "Performance:" in content:
            try:
                # Extract performance section
                perf_start = content.find("Performance:")
                perf_section = content[perf_start:perf_start+1000]
                
                # Parse ns/day
                match = re.search(r'[\d.]+\s*ns/day', perf_section)
                if match:
                    performance["ns_per_day"] = match.group()
                    
                # Parse hours/ns
                match = re.search(r'[\d.]+\s*hours/ns', perf_section)
                if match:
                    performance["hours_per_ns"] = match.group()
                    
            except Exception as e:
                logger.debug(f"Performance parsing error: {e}")
                
        return performance
        
    def get_progress_summary(self, segment_id: Optional[int] = None) -> str:
        """
        Get a human-readable progress summary.
        
        Args:
            segment_id: Optional segment ID
            
        Returns:
            Progress summary string
        """
        data = self.parse_log()
        
        if not data["log_file"]:
            return "No log file found"
            
        if data["is_running"]:
            status = "Running"
        else:
            status = "Completed" if data["progress_percent"] >= 100 else "Stopped"
            
        summary = f"""
Log: {data['log_file']}
Status: {status}
Progress: {data['progress_percent']:.1f}%
Simulated: {data['simulated_ns']:.2f} ns
Current Step: {data['current_step']}
"""
        
        if data["errors"]:
            summary += f"\nErrors: {len(data['errors'])}"
            
        if data["warnings"]:
            summary += f"\nWarnings: {len(data['warnings'])}"
            
        if data["performance"]:
            summary += f"\nPerformance: {data['performance']}"
            
        return summary


# Standalone function for simple usage
def parse_log(project_path: str, segment_id: Optional[int] = None) -> Dict:
    """
    Parse a GROMACS log file.
    
    Args:
        project_path: Path to project directory
        segment_id: Optional segment ID
        
    Returns:
        Parsed log data
    """
    parser = LogParser(project_path)
    return parser.parse_log()


if __name__ == "__main__":
    # Test log parser
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        print("Testing Log Parser...")
        
        # Create mock log file
        log_file = os.path.join(tmpdir, "md.log")
        with open(log_file, 'w') as f:
            f.write("""
GROMACS:      gmx mdrun, version 2024.2
Running on    1 node with total 8 cores, 1 logical cores, 1 compatible GPU
Implementation:      CPU

Step           Time
100         0.200
200         0.400
300         0.600

Performance:    5.23 ns/day, 4.58 hours/ns
""")
            
        parser = LogParser(tmpdir)
        result = parser.parse_log()
        
        print(f"Result: {result}")
        
        summary = parser.get_progress_summary()
        print(f"Summary: {summary}")
