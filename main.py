"""
BioDockify MD Universal - Main Entry Point
Professional Multi-GPU Molecular Dynamics Simulation Framework
"""

import sys
import os
import logging
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('biodockify_md.log')
    ]
)

logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='BioDockify MD Universal - Multi-GPU Molecular Dynamics Framework'
    )
    
    parser.add_argument(
        '--project',
        type=str,
        help='Project directory path'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Configuration file path'
    )
    
    parser.add_argument(
        '--ui',
        action='store_true',
        help='Launch GUI (default: CLI mode)'
    )
    
    parser.add_argument(
        '--detect-gpu',
        action='store_true',
        help='Detect and display GPU information'
    )
    
    parser.add_argument(
        '--create-project',
        type=str,
        metavar='NAME',
        help='Create new project with given name'
    )
    
    parser.add_argument(
        '--run',
        action='store_true',
        help='Run simulation'
    )
    
    parser.add_argument(
        '--resume',
        action='store_true',
        help='Resume from checkpoint'
    )
    
    parser.add_argument(
        '--package',
        action='store_true',
        help='Create publication package'
    )
    
    parser.add_argument(
        '--version',
        action='store_true',
        help='Display version information'
    )
    
    return parser.parse_args()


def load_config(config_file: str) -> dict:
    """Load configuration from YAML file"""
    import yaml
    
    config_path = Path(__file__).parent / config_file
    
    if not config_path.exists():
        logger.warning(f"Config file not found: {config_file}")
        return {}
        
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return {}


def detect_and_display_gpu():
    """Detect and display GPU information"""
    from core.gpu_detector import detect_gpu
    from core.backend_selector import select_backend, get_backend_config
    
    logger.info("Detecting hardware...")
    
    gpu_info = detect_gpu()
    backend = select_backend(gpu_info)
    config = get_backend_config(backend)
    
    print("\n" + "="*50)
    print("BioDockify MD Universal - Hardware Detection")
    print("="*50)
    print(f"\nGPU Vendor: {gpu_info.get('vendor', 'Unknown')}")
    print(f"Device Name: {gpu_info.get('device_name', 'N/A')}")
    print(f"VRAM: {gpu_info.get('vram', 0)} MB")
    print(f"Compute Capability: {gpu_info.get('compute_capability', 'N/A')}")
    print(f"\nSelected Backend: {backend}")
    print(f"Backend Name: {config.get('name', 'Unknown')}")
    print(f"Description: {config.get('description', 'N/A')}")
    print(f"Typical Speedup: {config.get('typical_speedup', 'N/A')}")
    print("\n" + "="*50 + "\n")
    
    return gpu_info, backend


def create_new_project(project_name: str):
    """Create a new project directory"""
    from core.metadata_logger import MetadataLogger
    
    # Get current directory as base
    base_dir = os.getcwd()
    project_path = os.path.join(base_dir, project_name)
    
    # Create project directory
    os.makedirs(project_path, exist_ok=True)
    
    # Create required subdirectories
    os.makedirs(os.path.join(project_path, "segment_000"), exist_ok=True)
    os.makedirs(os.path.join(project_path, "analysis"), exist_ok=True)
    
    # Copy default MDP file
    template_mdp = Path(__file__).parent / "templates" / "default.mdp"
    if template_mdp.exists():
        import shutil
        dest_mdp = os.path.join(project_path, "default.mdp")
        shutil.copy2(template_mdp, dest_mdp)
    
    # Initialize metadata
    metadata = MetadataLogger(project_path)
    metadata.initialize(
        project_name=project_name,
        total_ns=100,
        segment_ns=10,
        backend="unknown",
        gpu_info={"vendor": "unknown"}
    )
    
    logger.info(f"Created new project: {project_path}")
    print(f"Project created: {project_path}")
    print(f"  - segment_000/ directory")
    print(f"  - analysis/ directory")
    print(f"  - default.mdp")
    print(f"  - simulation_metadata.json")
    
    return project_path


def run_simulation_cli(project_path: str, config: dict):
    """Run simulation in CLI mode"""
    from core.segment_manager import SegmentManager
    from core.resume_manager import ResumeManager
    from core.gpu_detector import detect_gpu
    from core.backend_selector import select_backend
    from core.simulation_controller import SimulationController
    from core.shutdown_guard import register_shutdown_handler, SimulationGuard
    
    logger.info(f"Running simulation in: {project_path}")
    
    # Detect hardware
    gpu_info = detect_gpu()
    backend = select_backend(gpu_info)
    
    print(f"\nBackend: {backend}")
    print(f"GPU: {gpu_info.get('vendor', 'CPU')}")
    
    # Initialize managers
    total_ns = config.get('total_simulation_ns', 100)
    segment_ns = config.get('default_segment_ns', 10)
    
    segment_manager = SegmentManager(project_path, total_ns, segment_ns)
    resume_manager = ResumeManager(project_path)
    
    # Check for resume
    resume_info = resume_manager.get_resume_info()
    
    if resume_info:
        print(f"\nResuming from segment {resume_info['segment_id']}")
    else:
        print(f"\nStarting new simulation: {total_ns} ns in {segment_ns} ns segments")
    
    # Register shutdown handler
    register_shutdown_handler()
    
    # Run simulation
    with SimulationGuard():
        print("\nSimulation running... Press Ctrl+C to stop")
        
        # This would start the actual simulation
        # For now, just print status
        progress = segment_manager.get_progress_percentage()
        print(f"Progress: {progress:.1f}%")


def create_publication_package(project_path: str):
    """Create publication package"""
    from core.publication_packager import PublicationPackager
    
    logger.info(f"Creating publication package for: {project_path}")
    
    packager = PublicationPackager(project_path)
    package_path = packager.create_publication_package()
    
    if package_path:
        print(f"Publication package created: {package_path}")
    else:
        print("Failed to create publication package")


def launch_gui():
    """Launch the GUI application"""
    from ui.main_window import launch_ui
    from core.shutdown_guard import register_shutdown_handler
    
    # Register shutdown handler
    register_shutdown_handler()
    
    # Launch UI
    logger.info("Launching GUI...")
    launch_ui()


def main():
    """Main entry point"""
    args = parse_arguments()
    
    # Display version
    if args.version:
        print("BioDockify MD Universal v1.0.0")
        print("Multi-GPU Molecular Dynamics Simulation Framework")
        print("For BioDockify Ecosystem")
        return 0
    
    # Load configuration
    config = load_config(args.config)
    
    # GPU detection only
    if args.detect_gpu:
        detect_and_display_gpu()
        return 0
    
    # Create new project
    if args.create_project:
        create_new_project(args.create_project)
        return 0
    
    # CLI mode
    if args.ui:
        # Launch GUI
        launch_gui()
    else:
        # CLI mode
        if args.project:
            if args.run:
                run_simulation_cli(args.project, config)
            elif args.resume:
                run_simulation_cli(args.project, config)  # Resume is handled internally
            elif args.package:
                create_publication_package(args.project)
            else:
                print("Please specify --run, --resume, or --package")
        else:
            # No project specified, show help
            print("BioDockify MD Universal")
            print("\nUsage:")
            print("  --detect-gpu         Detect and display GPU information")
            print("  --create-project NAME Create new project")
            print("  --ui                 Launch GUI")
            print("  --project PATH --run Run simulation")
            print("  --project PATH --package Create publication package")
            print("\nExamples:")
            print("  python main.py --detect-gpu")
            print("  python main.py --create-project my_simulation")
            print("  python main.py --ui")
            print("  python main.py --project ./my_sim --run")
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        sys.exit(1)
