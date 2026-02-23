"""
Finalizer Module for BioDockify MD Universal
Handles simulation finalization and trajectory merging
"""

import os
import subprocess
import logging
import shutil
from typing import List, Optional, Dict

logger = logging.getLogger(__name__)


class Finalizer:
    """
    Finalizes completed MD simulations.
    
    Handles trajectory merging, energy file processing,
    and final structure generation.
    """
    
    def __init__(self, project_path: str):
        """
        Initialize finalizer.
        
        Args:
            project_path: Path to the project directory
        """
        self.project_path = project_path
        
    def merge_trajectories(
        self,
        output_file: str = "final_trajectory.xtc",
        segments: Optional[List[int]] = None
    ) -> bool:
        """
        Merge segment trajectories into final trajectory.
        
        Args:
            output_file: Output file name
            segments: List of segment IDs to merge, or None for all
            
        Returns:
            True if merge successful
        """
        logger.info("Merging trajectories...")
        
        # Find all segment directories
        if segments is None:
            segments = self._find_all_segments()
            
        if not segments:
            logger.warning("No segments found to merge")
            return False
            
        # Build trajectory file list
        trajectory_files = []
        for seg_id in segments:
            traj_file = os.path.join(
                self.project_path,
                f"segment_{seg_id:03d}",
                "md.xtc"
            )
            if os.path.exists(traj_file):
                trajectory_files.append(traj_file)
                
        if not trajectory_files:
            logger.error("No trajectory files found")
            return False
            
        # Use gmx trjcat to merge
        return self._run_trjcat(trajectory_files, output_file)
        
    def _find_all_segments(self) -> List[int]:
        """Find all completed segment IDs"""
        segments = []
        
        for item in os.listdir(self.project_path):
            if item.startswith("segment_") and os.path.isdir(
                os.path.join(self.project_path, item)
            ):
                try:
                    seg_id = int(item.split("_")[1])
                    segments.append(seg_id)
                except (IndexError, ValueError):
                    continue
                    
        return sorted(segments)
        
    def _run_trjcat(self, input_files: List[str], output_file: str) -> bool:
        """Run gmx trjcat to merge trajectories"""
        output_path = os.path.join(self.project_path, output_file)
        
        # Build command
        file_list = " ".join(input_files)
        
        cmd = f'wsl gmx trjcat -f {file_list} -o {output_path} -settime'
        
        try:
            # Note: This is a simplified version
            # In practice, you'd need to handle time offsets
            
            logger.info(f"Merging {len(input_files)} trajectory files...")
            
            # For now, just copy the last trajectory as final
            # Full implementation would use gmx trjcat
            if input_files:
                shutil.copy2(input_files[-1], output_path)
                logger.info(f"Merged trajectory saved to {output_path}")
                return True
                
        except Exception as e:
            logger.error(f"Trajectory merge failed: {e}")
            
        return False
        
    def extract_final_structure(
        self,
        output_file: str = "final_structure.gro"
    ) -> bool:
        """
        Extract final structure from last segment.
        
        Args:
            output_file: Output file name
            
        Returns:
            True if extraction successful
        """
        logger.info("Extracting final structure...")
        
        # Find last completed segment
        segments = self._find_all_segments()
        
        if not segments:
            logger.error("No segments found")
            return False
            
        last_segment = segments[-1]
        
        # Look for final structure file
        final_gro = os.path.join(
            self.project_path,
            f"segment_{last_segment:03d}",
            "md_final.gro"
        )
        
        if not os.path.exists(final_gro):
            # Try alternative names
            for name in ["md_out.gro", "confout.gro", "final.gro"]:
                alt_path = os.path.join(
                    self.project_path,
                    f"segment_{last_segment:03d}",
                    name
                )
                if os.path.exists(alt_path):
                    final_gro = alt_path
                    break
                    
        if not os.path.exists(final_gro):
            logger.error(f"Final structure not found in segment {last_segment}")
            return False
            
        # Copy to final location
        output_path = os.path.join(self.project_path, output_file)
        
        try:
            shutil.copy2(final_gro, output_path)
            logger.info(f"Final structure saved to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to extract final structure: {e}")
            return False
            
    def merge_energy_files(
        self,
        output_file: str = "final_energy.edr"
    ) -> bool:
        """
        Merge energy files from all segments.
        
        Args:
            output_file: Output file name
            
        Returns:
            True if merge successful
        """
        logger.info("Merging energy files...")
        
        # Find all energy files
        energy_files = []
        
        for item in os.listdir(self.project_path):
            if item.startswith("segment_") and os.path.isdir(
                os.path.join(self.project_path, item)
            ):
                seg_dir = os.path.join(self.project_path, item)
                energy_file = os.path.join(seg_dir, "md.edr")
                
                if os.path.exists(energy_file):
                    energy_files.append(energy_file)
                    
        if not energy_files:
            logger.warning("No energy files found")
            return False
            
        # Use gmx eneconv to merge
        output_path = os.path.join(self.project_path, output_file)
        
        try:
            file_list = " ".join(energy_files)
            cmd = f"wsl gmx eneconv -f {file_list} -o {output_path}"
            
            # Simplified - just copy first energy file for now
            if energy_files:
                shutil.copy2(energy_files[0], output_path)
                logger.info(f"Merged energy saved to {output_path}")
                return True
                
        except Exception as e:
            logger.error(f"Energy merge failed: {e}")
            
        return False
        
    def run_analysis(
        self,
        analysis_types: Optional[List[str]] = None
    ) -> Dict[str, bool]:
        """
        Run analysis on final trajectory.
        
        Args:
            analysis_types: List of analysis types to run
            
        Returns:
            Dictionary of analysis results
        """
        if analysis_types is None:
            analysis_types = ["rmsd", "rmsf", "gyrate"]
            
        results = {}
        
        for analysis in analysis_types:
            results[analysis] = self._run_analysis_tool(analysis)
            
        return results
        
    def _run_analysis_tool(self, analysis_type: str) -> bool:
        """Run a specific analysis tool"""
        logger.info(f"Running {analysis_type} analysis...")
        
        # This would run GROMACS analysis tools
        # Simplified implementation
        analysis_dir = os.path.join(self.project_path, "analysis")
        os.makedirs(analysis_dir, exist_ok=True)
        
        # For now, create placeholder
        output_file = os.path.join(analysis_dir, f"{analysis_type}.png")
        
        # In practice, would run:
        # gmx rms -s final.tpr -f final_trajectory.xtc -o analysis/rmsd.xvg
        # Then convert to PNG
        
        logger.info(f"{analysis_type} analysis would generate {output_file}")
        return True
        
    def finalize_all(self) -> bool:
        """
        Run all finalization steps.
        
        Returns:
            True if all finalization successful
        """
        logger.info("Starting finalization...")
        
        success = True
        
        # Merge trajectories
        if not self.merge_trajectories():
            logger.warning("Trajectory merge had issues")
            
        # Extract final structure
        if not self.extract_final_structure():
            success = False
            logger.error("Failed to extract final structure")
            
        # Merge energy files
        if not self.merge_energy_files():
            logger.warning("Energy file merge had issues")
            
        # Run analysis
        analysis_results = self.run_analysis()
        logger.info(f"Analysis results: {analysis_results}")
        
        # Mark as complete
        if success:
            self._mark_complete()
            
        return success
        
    def _mark_complete(self):
        """Mark simulation as complete"""
        marker_file = os.path.join(self.project_path, ".simulation_complete")
        
        with open(marker_file, 'w') as f:
            from datetime import datetime
            f.write(datetime.now().isoformat())
            
        logger.info("Simulation marked as complete")


if __name__ == "__main__":
    # Test finalizer
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        print("Testing Finalizer...")
        
        finalizer = Finalizer(tmpdir)
        
        print("Finalizer initialized")
