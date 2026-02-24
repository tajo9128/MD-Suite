# BioDockify MD Universal

[![Version](https://img.shields.io/badge/version-1.0.0-blue)](https://github.com/tajo9128/MD-lite)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-orange)](https://www.python.org/)
[![GROMACS](https://img.shields.io/badge/GROMACS-2024+-cyan)](https://www.gromacs.org/)

**Multi-GPU Molecular Dynamics Simulation Framework with Autonomous AI Supervision**

---

## Overview

BioDockify MD Universal is a professional molecular dynamics (MD) simulation platform built on top of GROMACS. It provides an intelligent orchestration layer for running MD simulations with universal GPU support, autonomous monitoring, and publication-ready output generation.

This software does not replace GROMACS but enhances it with AI-powered automation, making it ideal for PG students and researchers who need a streamlined workflow.

---

## Features

### Universal GPU Support
- **NVIDIA** (CUDA backend)
- **AMD** (SYCL backend)
- **Intel** (SYCL backend)
- **CPU** fallback

### Autonomous Nanobot Brain
- Continuous simulation monitoring
- Real-time state synchronization
- Checkpoint integrity verification
- Hardware protection (temperature/disk guards)
- Intelligent error detection

### Advanced Workflow
- Segmented execution with resume capability
- Dynamic simulation time control
- Shutdown-resistant execution
- Auto-resume across reboots

### Analysis & Publication
- Automated RMSD, RMSF, Gyration, Energy, SASA analysis
- Trajectory merging and finalization
- Publication-ready package generation
- Reproducibility documentation

### Communication
- Telegram notifications
- WhatsApp notifications
- Discord webhooks
- Email alerts

---

## Architecture

```
Windows Native UI / CLI
        |
        v
BioDockify AI Brain (Nanobot)
   - Perception Layer (log, GPU, disk monitoring)
   - Reasoning Layer (error detection, progress analysis)
   - Action Layer (simulation control, finalization)
   - Communication Layer (Telegram, Discord, Email)
        |
        v
Workflow Engine
   - Protein Preparation → Topology → Solvation
   - Minimization → Equilibration → Production
        |
        v
Adaptive GROMACS Backend
   - gmx_cuda (NVIDIA)
   - gmx_sycl (AMD/Intel)
   - gmx_cpu (fallback)
        |
        v
Segment + Resume Engine
        |
        v
Publication Engine
   - Analysis → Trajectory Merge → Package
```

---

## Installation

### Prerequisites

1. **Windows 10/11** with WSL2 enabled
2. **GROMACS 2024+** installed in WSL2
3. **Python 3.10+**
4. **NVIDIA CUDA Toolkit** (for NVIDIA GPUs) or **ROCm** (for AMD GPUs)

### Setup

```bash
# Clone repository
git clone https://github.com/tajo9128/MD-lite.git
cd MD-lite

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### GROMACS Setup

Ensure GROMACS is installed in WSL2:

```bash
# In WSL2
wsl
sudo apt-get update
sudo apt-get install gromacs
```

---

## Quick Start

### Command Line Interface

```bash
# Detect GPU
python main.py --detect-gpu

# Create new project
python main.py --create-project my_simulation

# Run simulation
python main.py --project ./my_simulation --run

# Launch autonomous AI mode
python main.py --project ./my_simulation --ai

# Launch GUI
python main.py --ui
```

### Autonomous Mode

```bash
# Start with Nanobot AI supervision
python main.py --project ./my_sim --ai --ai-model ollama/llama2
```

Nanobot will:
- Continuously monitor simulation progress
- Detect and report errors automatically
- Protect against hardware issues
- Send notifications via Telegram/Discord
- Resume automatically after interruptions

---

## Configuration

Edit `config.yaml`:

```yaml
checkpoint_interval_minutes: 15
default_segment_ns: 10
analysis_dpi: 300
temperature_limit_celsius: 85
min_disk_space_gb: 5
enable_telegram: false
```

---

## Project Structure

```
biodockify_md_universal/
├── main.py                  # CLI entry point
├── config.yaml             # Configuration
├── requirements.txt         # Dependencies
│
├── core/                   # Core system
│   ├── gpu_detector.py     # GPU detection
│   ├── backend_selector.py # Backend selection
│   ├── segment_manager.py  # Segmented execution
│   ├── resume_manager.py  # Resume logic
│   └── ...
│
├── biodockify_ai/          # AI Brain
│   ├── brain.py           # Main brain
│   ├── nanobot/           # Autonomous supervisor
│   │   ├── event_loop.py
│   │   ├── sync_engine.py
│   │   ├── integrity_checker.py
│   │   ├── perception/
│   │   ├── reasoning/
│   │   ├── actions/
│   │   └── communication/
│   └── ...
│
├── workflow/              # MD pipeline
├── analysis/             # Analysis tools
├── publication/          # Output packaging
└── backends/             # GROMACS backends
```

---

## Usage Examples

### Running a Production MD

```bash
# Create project with protein
python main.py --create-project lysozyme_sim

# Configure simulation time (100ns, 10ns segments)
# Edit config.yaml or use GUI

# Run with AI supervision
python main.py --project ./lysozyme_sim --ai
```

### Monitoring Progress

Nanobot continuously updates `status.json` which can be read by the UI:

```json
{
  "simulation": {
    "current_ns": 45.2,
    "total_ns": 100.0,
    "progress_percent": 45.2,
    "segment": 4
  },
  "hardware": {
    "gpu_available": true,
    "gpu_temp_celsius": 72
  }
}
```

---

## Academic Use

If you use BioDockify MD Universal in your research, please cite:

```bibtex
@software{biodockify_md_universal,
  title = {BioDockify MD Universal},
  author = {Shaik, Tajuddin},
  version = {1.0.0},
  date = {2026-02-22},
  url = {https://github.com/tajo9128/MD-lite}
}
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Note:** This software uses GROMACS which is released under the LGPL license. BioDockify MD Universal is an orchestration layer and does not modify GROMACS itself.

---

## Acknowledgments

- [GROMACS](https://www.gromacs.org/) - Molecular dynamics simulation engine
- [HKUDS/nanobot](https://github.com/HKUDS/nanobot) - AI assistant framework (adapted for MD supervision)

---

## Support

For issues and feature requests, please open an issue on GitHub.

---

*Built for researchers, by researchers.*
