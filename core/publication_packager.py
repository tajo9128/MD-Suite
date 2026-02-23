"""
Publication Packager Module for BioDockify MD Universal
Creates publication-ready packages from simulation results
"""

import os
import shutil
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class PublicationPackager:
    """
    Creates publication-ready packages from MD simulation results.
    
    Generates zip archives with all necessary files for publication
    including trajectories, structures, parameters, and analysis.
    """
    
    def __init__(self, project_path: str):
        """
        Initialize publication packager.
        
        Args:
            project_path: Path to the project directory
        """
        self.project_path = project_path
        self.package_name = None
        
    def create_publication_package(
        self,
        output_path: Optional[str] = None,
        include_analysis: bool = True,
        compress: bool = True
    ) -> Optional[str]:
        """
        Create a publication-ready package.
        
        Args:
            output_path: Output path for the package
            include_analysis: Include analysis files
            compress: Create compressed zip archive
            
        Returns:
            Path to created package, or None on failure
        """
        logger.info("Creating publication package...")
        
        # Determine package name
        project_name = os.path.basename(self.project_path)
        
        if output_path:
            if os.path.isdir(output_path):
                package_dir = os.path.join(output_path, f"{project_name}_Publication")
            else:
                # Use provided path
                package_dir = output_path
        else:
            package_dir = os.path.join(
                os.path.dirname(self.project_path),
                f"{project_name}_Publication"
            )
            
        # Create package directory
        os.makedirs(package_dir, exist_ok=True)
        
        # Copy required files
        success = self._copy_publication_files(
            package_dir,
            include_analysis
        )
        
        if not success:
            logger.error("Failed to copy publication files")
            return None
            
        # Generate README
        self._generate_readme(package_dir)
        
        # Generate metadata
        self._generate_metadata(package_dir)
        
        # Create zip archive if requested
        if compress:
            archive_path = self._create_archive(package_dir)
            self.package_name = archive_path
            logger.info(f"Publication package created: {archive_path}")
            return archive_path
        else:
            self.package_name = package_dir
            logger.info(f"Publication directory created: {package_dir}")
            return package_dir
            
    def _copy_publication_files(
        self,
        package_dir: str,
        include_analysis: bool
    ) -> bool:
        """Copy required files to package directory"""
        
        # Files to include
        required_files = [
            ("final_trajectory.xtc", "trajectory"),
            ("final_structure.gro", "structure"),
            ("final_energy.edr", "energy"),
        ]
        
        for filename, file_type in required_files:
            src = os.path.join(self.project_path, filename)
            
            if os.path.exists(src):
                dest = os.path.join(package_dir, filename)
                try:
                    shutil.copy2(src, dest)
                    logger.info(f"Copied {filename}")
                except Exception as e:
                    logger.error(f"Failed to copy {filename}: {e}")
            else:
                logger.warning(f"Optional file not found: {filename}")
                
        # Copy MDP parameters if available
        mdp_files = self._find_mdp_files()
        if mdp_files:
            mdp_dir = os.path.join(package_dir, "mdp_parameters")
            os.makedirs(mdp_dir, exist_ok=True)
            
            for mdp_file in mdp_files:
                try:
                    shutil.copy2(mdp_file, mdp_dir)
                except Exception as e:
                    logger.error(f"Failed to copy MDP file: {e}")
                    
        # Copy topology files
        for top_file in ["topol.top", "index.ndx", "posre.itp"]:
            src = os.path.join(self.project_path, top_file)
            if os.path.exists(src):
                try:
                    shutil.copy2(src, package_dir)
                except Exception as e:
                    logger.error(f"Failed to copy {top_file}: {e}")
                    
        # Copy analysis if requested
        if include_analysis:
            analysis_src = os.path.join(self.project_path, "analysis")
            if os.path.exists(analysis_src):
                analysis_dest = os.path.join(package_dir, "analysis")
                try:
                    shutil.copytree(analysis_src, analysis_dest)
                except Exception as e:
                    logger.error(f"Failed to copy analysis: {e}")
                    
        return True
        
    def _find_mdp_files(self) -> List[str]:
        """Find MDP parameter files"""
        mdp_files = []
        
        for root, dirs, files in os.walk(self.project_path):
            for f in files:
                if f.endswith(".mdp"):
                    mdp_files.append(os.path.join(root, f))
                    
        return mdp_files
        
    def _generate_readme(self, package_dir: str):
        """Generate README for reproducibility"""
        readme_content = """# MD Simulation Publication Package

## Contents

- `final_trajectory.xtc` - Combined trajectory file
- `final_structure.gro` - Final system structure
- `final_energy.edr` - Energy file
- `topol.top` - System topology
- `index.ndx` - Index file
- `mdp_parameters/` - MDP parameter files used
- `analysis/` - Analysis results (RMSD, RMSF, etc.)

## Reproduction Instructions

1. Ensure GROMACS is installed (version 2024.x recommended)
2. Extract this package
3. Re-run simulation using included MDP files:
   ```
   gmx grompp -f mdp_parameters/production.mdp -c final_structure.gro -o simulation.tpr
   gmx mdrun -s simulation.tpr
   ```

## System Information

- This package was generated automatically by BioDockify MD Universal
- Generation date: {date}
- Project: {project}

## Analysis Commands

### RMSD
```
gmx rms -s final_structure.gro -f final_trajectory.xtc -o analysis/rmsd.xvg
```

### RMSF
```
gmx rmsf -s final_structure.gro -f final_trajectory.xtc -o analysis/rmsf.xvg
```

### Radius of Gyration
```
gmx gyrate -s final_structure.gro -f final_trajectory.xtc -o analysis/gyrate.xvg
```

### Energy Analysis
```
gmx energy -f final_energy.edr -o analysis/energy.xvg
```

---
Generated by BioDockify MD Universal
""".format(
            date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            project=os.path.basename(self.project_path)
        )
        
        readme_path = os.path.join(package_dir, "README_reproducibility.txt")
        
        with open(readme_path, 'w') as f:
            f.write(readme_content)
            
        logger.info("Generated README")
        
    def _generate_metadata(self, package_dir: str):
        """Generate simulation metadata JSON"""
        metadata = {
            "package_info": {
                "generator": "BioDockify MD Universal",
                "version": "1.0.0",
                "created": datetime.now().isoformat(),
                "project": os.path.basename(self.project_path)
            },
            "files": self._list_package_files(package_dir)
        }
        
        # Try to load existing simulation metadata
        meta_file = os.path.join(self.project_path, "simulation_metadata.json")
        if os.path.exists(meta_file):
            try:
                with open(meta_file, 'r') as f:
                    sim_meta = json.load(f)
                    metadata["simulation"] = sim_meta
            except Exception as e:
                logger.warning(f"Could not load simulation metadata: {e}")
                
        # Save metadata
        meta_path = os.path.join(package_dir, "simulation_metadata.json")
        
        with open(meta_path, 'w') as f:
            json.dump(metadata, f, indent=2)
            
        logger.info("Generated metadata")
        
    def _list_package_files(self, package_dir: str) -> List[Dict]:
        """List all files in package"""
        files = []
        
        for root, dirs, filenames in os.walk(package_dir):
            for f in filenames:
                filepath = os.path.join(root, f)
                relpath = os.path.relpath(filepath, package_dir)
                
                stat = os.stat(filepath)
                
                files.append({
                    "path": relpath,
                    "size_bytes": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
                
        return files
        
    def _create_archive(self, package_dir: str) -> str:
        """Create zip archive of package"""
        import zipfile
        
        archive_path = f"{package_dir}.zip"
        
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(package_dir):
                for file in files:
                    filepath = os.path.join(root, file)
                    arcname = os.path.relpath(filepath, os.path.dirname(package_dir))
                    zipf.write(filepath, arcname)
                    
        logger.info(f"Created archive: {archive_path}")
        
        return archive_path
        
    def validate_package(self, package_path: str) -> Dict:
        """
        Validate a publication package.
        
        Args:
            package_path: Path to package
            
        Returns:
            Validation results
        """
        results = {
            "valid": True,
            "missing_files": [],
            "warnings": []
        }
        
        required_files = [
            "final_trajectory.xtc",
            "final_structure.gro",
            "topol.top"
        ]
        
        # Check if path is directory or zip
        if os.path.isdir(package_path):
            base_dir = package_path
        elif package_path.endswith(".zip"):
            # Check zip contents
            import zipfile
            with zipfile.ZipFile(package_path, 'r') as zipf:
                names = zipf.namelist()
                for req_file in required_files:
                    if req_file not in names:
                        results["missing_files"].append(req_file)
                        results["valid"] = False
                return results
        else:
            results["valid"] = False
            results["missing_files"].append("Package not found")
            return results
            
        # Check directory
        for req_file in required_files:
            if not os.path.exists(os.path.join(base_dir, req_file)):
                results["missing_files"].append(req_file)
                results["valid"] = False
                
        return results


def create_publication_package(project_path: str, output_path: str = None) -> Optional[str]:
    """
    Standalone function to create publication package.
    
    Args:
        project_path: Path to project
        output_path: Optional output path
        
    Returns:
        Path to created package
    """
    packager = PublicationPackager(project_path)
    return packager.create_publication_package(output_path)


if __name__ == "__main__":
    # Test publication packager
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        print("Testing Publication Packager...")
        
        # Create mock project
        project_dir = os.path.join(tmpdir, "test_project")
        os.makedirs(project_dir)
        
        # Create dummy files
        with open(os.path.join(project_dir, "final_structure.gro"), 'w') as f:
            f.write("Test")
            
        with open(os.path.join(project_dir, "topol.top"), 'w') as f:
            f.write("Test")
            
        packager = PublicationPackager(project_dir)
        package = packager.create_publication_package()
        
        print(f"Package created: {package}")
