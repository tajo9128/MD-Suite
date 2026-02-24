# BioDockify MD Universal

**Autonomous Multi-GPU Molecular Dynamics Platform**

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![GPU Support](https://img.shields.io/badge/GPU-NVIDIA%20%7C%20AMD%20%7C%20Intel-orange)
![Platform](https://img.shields.io/badge/platform-Windows%20%2B%20WSL2-lightgrey)
![Engine](https://img.shields.io/badge/Engine-GROMACS-red)

BioDockify MD Universal is a desktop molecular dynamics platform built on GROMACS with an intelligent supervisory system called **Nanobot Brain**.

It enables PG and PhD students to run fully automated, resume-safe molecular dynamics simulations with publication-ready output.

---

# What This Software Does

BioDockify MD Universal allows you to:

- Add protein and ligand files
- Select total simulation time (10-200+ ns)
- Run automated MD workflow
- Resume after shutdown
- Monitor progress live
- Receive notifications
- Generate analysis plots automatically
- Download a publication-ready package

No manual GROMACS commands required.

---

# System Requirements

## Minimum System Requirements

- Windows 10 / 11 (64-bit)
- 16 GB RAM (minimum recommended)
- 50 GB free disk space
- WSL2 enabled
- Python 3.10+

## GPU Requirement

BioDockify MD Universal supports:

| GPU Type | Minimum Requirement        | Recommended        |
| -------- | ------------------------ | ----------------- |
| NVIDIA   | GTX 1650 (4 GB VRAM)       | RTX 3060 or higher |
| AMD      | RX 5600 XT (6 GB VRAM)     | RX 6600 or higher  |
| Intel    | Intel Arc A380 (6 GB VRAM) | Arc A750 or higher |
| No GPU   | CPU fallback (very slow)   | Not recommended    |

### Important Notes

- Minimum **4 GB VRAM** required for small systems (~50k atoms).
- For protein-ligand systems >100k atoms - **6-8 GB VRAM recommended**.
- If no GPU is detected, simulation runs on CPU (slow but functional).
- Laptop GPUs may throttle under heavy load.

---

# Features Summary

- Universal GPU detection (CUDA / SYCL / CPU fallback)
- Segmented & resume-safe MD execution
- Autonomous Nanobot monitoring system
- Live progress tracking
- Overheat & disk protection
- Automatic RMSD / RMSF / Energy analysis
- Publication-ready packaging
- Telegram & Email alerts
- Dynamic simulation time selection

---

# One-Time Setup

## Step 1 - Install Python

Download and install Python 3.10+:

https://www.python.org/downloads/

During installation:
- Check "Add Python to PATH"

## Step 2 - Install WSL2

Open PowerShell as Administrator:

```powershell
wsl --install
```

Restart your PC if required.

Install Ubuntu from Microsoft Store if prompted.

## Step 3 - Install GROMACS Inside WSL

Open Ubuntu terminal:

```bash
sudo apt update
sudo apt install gromacs
```

Verify installation:

```bash
gmx --version
```

If version displays - success.

## Step 4 - Install Python Dependencies

Inside project folder:

```bash
pip install -r requirements.txt
```

---

# How to Launch BioDockify

1. Extract the downloaded ZIP file.
2. Open the extracted folder.
3. Double-click:

```
start.bat
```

The BioDockify MD window will open.

---

# How to Create a Simulation

1. Click **Add Protein (.pdb)**
2. Click **Add Ligand (.mol2 / .sdf)**
3. Select output folder
4. Choose simulation time:
   - 10 ns (Testing run)
   - 50 ns (Moderate study)
   - 100 ns (Publication standard)
   - Custom value
5. Click **Run Full Workflow**

Nanobot will now:

- Prepare the system
- Run minimization
- Run equilibration
- Run segmented production MD
- Monitor continuously

---

# Simulation Time Selection

You can select total simulation length.

Example:

- 10 ns - Testing run
- 50 ns - Moderate study
- 100 ns - Publication standard
- 200+ ns - Advanced research

Simulation is segmented internally (default 10 ns per segment) to ensure:

- Resume safety
- Minimal data loss
- Stable long-term execution

---

# Resume After Shutdown

If your PC shuts down:

- Do not worry.
- Reopen BioDockify.
- Simulation resumes automatically from last checkpoint.

Maximum possible data loss: ~15 minutes.

---

# Monitoring Dashboard

The Monitor tab displays:

- Current simulation time (ns)
- Segment number
- GPU detected
- Backend in use (CUDA / SYCL / CPU)
- GPU temperature
- Estimated completion time
- Error alerts (if any)

---

# Notifications (Optional)

You can enable:

- Telegram alerts
- Email updates

Notifications are sent when:

- Simulation starts
- 25%, 50%, 75% progress reached
- Error detected
- Final package ready

---

# Final Output (Publication Ready)

After completion, BioDockify automatically generates:

```
Project_Publication/
   final_trajectory.xtc
   final_energy.edr
   final_structure.gro
   topology.top
   mdp_parameters.txt
   simulation_metadata.json
   analysis/
   publication_package.zip
```

Click:

```
Download Final Package
```

Files are ready for:

- Journal submission
- Thesis integration
- Data repository upload

---

# Safety & Stability Features

Nanobot Brain continuously:

- Monitors simulation logs
- Checks checkpoint integrity
- Tracks GPU temperature
- Detects stalled runs
- Prevents corrupted merges
- Protects against disk overflow

---

# Expected Performance (Approximate)

| GPU      | Approx Speed |
| -------- | ------------ |
| GTX 1650 | 6-10 ns/day  |
| RTX 3060 | 15-25 ns/day |
| RTX 4090 | 30+ ns/day   |
| CPU only | 1-2 ns/day   |

Actual speed depends on:

- System size
- Force field
- Solvent model
- GPU clock stability

---

# Troubleshooting Guide

## Issue: Application does not start

- Ensure Python 3.10+ is installed
- Ensure `pip install -r requirements.txt` completed successfully
- Try running manually: `python main.py`

## Issue: WSL not found

Run in PowerShell (Admin):

```powershell
wsl --install
```

Restart your PC.

## Issue: GROMACS not detected

Open Ubuntu (WSL) and test:

```bash
gmx --version
```

If not found:

```bash
sudo apt update
sudo apt install gromacs
```

## Issue: GPU not detected

### NVIDIA:

```bash
wsl nvidia-smi
```

### AMD:

Ensure latest AMD drivers installed and WSL GPU support enabled.

### Intel:

Ensure latest Intel Arc drivers installed.

## Issue: Simulation paused automatically

Possible reasons:

- GPU temperature > 85C
- Disk space < 5 GB
- Simulation stall detected
- Checkpoint not updating

Check Monitor tab for details.

## Issue: Simulation very slow

Possible causes:

- CPU fallback mode
- Thermal throttling
- Large system size
- Background heavy processes

Check Monitor tab for backend in use.

## Issue: Resume not working

Ensure:

- `status.json` exists in project folder
- `md.cpt` checkpoint file exists
- Do not manually delete segment folders

---

# FAQ - For PG Students

## Q1: How long should my MD simulation be?

- 10 ns - Testing
- 50 ns - Preliminary results
- 100 ns - Publication standard
- 200+ ns - Advanced studies

## Q2: Can I shut down my PC during simulation?

Yes.

BioDockify automatically resumes from last checkpoint when reopened.

Maximum data loss: ~15 minutes.

## Q3: What happens if my GPU overheats?

Nanobot pauses simulation automatically and resumes when safe.

## Q4: Do I need to know GROMACS commands?

No.

BioDockify automates the entire workflow.

## Q5: Can I change simulation time after starting?

Yes - you can extend total simulation time.
You cannot reduce below completed progress.

## Q6: Where are my final files stored?

Inside:

```
Project_Name_Publication/
```

You can click:

```
Download Final Package
```

## Q7: What files should I include in my thesis?

From publication folder:

- final_trajectory.xtc
- final_structure.gro
- RMSD plot
- RMSF plot
- Energy plot
- simulation_metadata.json

## Q8: Can this replace commercial MD software?

BioDockify is built on GROMACS which is widely used in academia and industry.

It provides automation and monitoring on top of it.

## Q9: What if I have no GPU?

Simulation will run on CPU, but very slowly.
GPU is strongly recommended.

## Q10: How accurate are the results?

Accuracy depends on:

- Force field selection
- System preparation
- Simulation time
- Convergence

BioDockify ensures technical stability, but scientific validation remains your responsibility.

---

# About Nanobot Brain

Nanobot is an autonomous supervision engine that:

- Monitors simulation continuously
- Synchronizes state data
- Detects instability
- Protects hardware
- Automates final packaging
- Sends notifications

It acts as a scientific assistant during MD execution.

---

# Citation

This platform is built on top of:

**GROMACS** - https://www.gromacs.org/

Please cite GROMACS appropriately in your publication.

---

# Recommended Academic Workflow

1. Run 10 ns test simulation
2. Check RMSD stability
3. Increase to 50-100 ns
4. Confirm convergence
5. Download publication package
6. Insert analysis figures into thesis

---

# Quick Commands

| Command | Description |
|---------|-------------|
| `python main.py --detect-gpu` | Detect available GPU |
| `python main.py --create-project name` | Create new project |
| `python main.py --project ./name --run` | Run simulation |
| `python main.py --project ./name --ai` | Run with AI |
| `python main.py --ui` | Launch GUI |

---

# License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

---

# Roadmap

## v1.1.0 (Planned)
- Docking integration (AutoDock Vina)
- Enhanced ligand parameterization
- Basic free energy calculations

## v1.2.0 (Planned)
- Cloud hybrid mode
- Multi-GPU scaling support
- Advanced sampling methods

## v2.0.0 (Vision)
- AI-driven parameter optimization
- Automated research reporting
- Integration with BioDockify ecosystem

---

*BioDockify MD Universal - Built for researchers, by researchers.*
