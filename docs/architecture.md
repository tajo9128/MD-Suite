# System Architecture

BioDockify MD Universal consists of five primary layers working together to provide an automated molecular dynamics experience.

## Architecture Overview

```
+----------------------------------------------------------+
|                    User Interface Layer                   |
|            (CLI / GUI / API)                            |
+----------------------------------------------------------+
                          |
                          v
+----------------------------------------------------------+
|              Project Management Layer                     |
|        (Project creation, file management)             |
+----------------------------------------------------------+
                          |
                          v
+----------------------------------------------------------+
|              Nanobot Supervisory Layer                   |
|    (Continuous monitoring, decision making, alerts)     |
+----------------------------------------------------------+
                          |
                          v
+----------------------------------------------------------+
|                Workflow Engine Layer                     |
|   (Protein prep -> Topology -> Solvation -> MD)        |
+----------------------------------------------------------+
                          |
                          v
+----------------------------------------------------------+
|            Adaptive Compute Backend Layer                 |
|      (CUDA / SYCL / CPU)                              |
+----------------------------------------------------------+
                          |
                          v
+----------------------------------------------------------+
|             Analysis & Publication Layer                |
|    (RMSD/RMSF analysis, trajectory merge, packaging)   |
+----------------------------------------------------------+
```

## Core Components

### 1. User Interface Layer

Provides multiple ways to interact with the system:
- Command Line Interface (CLI)
- Graphical User Interface (GUI)
- Programmatic API

### 2. Project Management Layer

Handles:
- Project creation and configuration
- File validation (PDB, MOL2, SDF)
- Simulation parameter management
- State persistence

### 3. Nanobot Supervisory Layer

The intelligent monitoring system that:
- Continuously monitors simulation state
- Makes autonomous decisions
- Communicates with users
- Protects against failures

See [Nanobot Design](nanobot_design.md) for details.

### 4. Workflow Engine Layer

Executes the MD pipeline:
- Protein preparation
- Ligand preparation
- Topology generation
- Solvation and ion addition
- Energy minimization
- System equilibration (NVT, NPT)
- Production MD

### 5. Adaptive Compute Backend Layer

Automatically selects the best available compute backend:
- **CUDA**: For NVIDIA GPUs
- **SYCL**: For AMD/Intel GPUs
- **CPU**: Fallback for systems without GPU

### 6. Analysis & Publication Layer

Generates publication-ready outputs:
- RMSD analysis
- RMSF analysis
- Radius of gyration
- Energy analysis
- SASA calculation
- Trajectory merging
- Package creation

## Data Flow

1. User creates project and selects simulation parameters
2. Workflow engine prepares the system
3. Nanobot begins continuous supervision
4. Simulation runs on selected backend
5. Nanobot monitors and synchronizes state
6. On completion, analysis engine generates results
7. Publication engine creates downloadable package

## State Synchronization

Nanobot maintains real-time synchronization via `status.json`:
- Current simulation progress
- GPU status
- System health
- Error states

This ensures the UI always displays accurate information and enables safe resume after interruptions.

## Security & Stability

The system includes:
- Shutdown guards
- Checkpoint integrity verification
- Hardware protection (temperature, disk space)
- Error detection and recovery

---

*See related documentation: [Nanobot Design](nanobot_design.md), [GPU Backend](gpu_backend.md)*
