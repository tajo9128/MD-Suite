# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-22

### Added
- Initial release of BioDockify MD Universal
- Universal GPU support (NVIDIA CUDA, AMD SYCL, Intel SYCL, CPU fallback)
- BioDockify AI brain with autonomous supervision
- Nanobot continuous monitoring system:
  - Perception layer (log_watcher, gpu_monitor, disk_monitor)
  - Reasoning layer (error_detector, progress_analyzer, stability_checker)
  - Action layer (simulation_control, finalization_trigger)
  - Communication layer (Telegram, WhatsApp, Discord, Email)
  - Memory layer (state_manager)
- Continuous event loop for real-time monitoring
- State synchronization engine for UI updates
- Checkpoint integrity verification
- Workflow modules:
  - Protein preparation
  - Ligand preparation
  - Topology generation
  - Solvation
  - Energy minimization
  - System equilibration (NVT, NPT)
  - Production MD
- Analysis modules:
  - RMSD calculation
  - RMSF calculation
  - Radius of Gyration
  - Energy analysis
  - SASA calculation
  - Report generation
- Publication modules:
  - Trajectory merging
  - Energy merging
  - Reproducibility reports
  - Package creation
- CLI and GUI interfaces
- Shutdown protection and resume capability

### Fixed
- Syntax errors in gmx_sycl engine
- Import issues in backend_selector

---

## [Unreleased]

### Planned
- GPU-accelerated analysis
- Cloud backup synchronization
- Advanced quality control checks
- Integration with BioDockify docking pipeline
