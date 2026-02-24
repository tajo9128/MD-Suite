# BioDockify MD Universal

**Autonomous Multi-GPU Molecular Dynamics Platform**

BioDockify MD Universal is a desktop molecular dynamics platform built on
GROMACS with an intelligent supervisory system called **Nanobot Brain**.

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
| -------- | -------------------------- | ------------------ |
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

# Support

If you face issues:

1. Confirm WSL is running
2. Confirm GROMACS installed inside Ubuntu
3. Check GPU drivers updated
4. Ensure sufficient disk space

For advanced support, open an issue on GitHub.

---

# BioDockify Vision

BioDockify MD Universal is not just a GROMACS interface.

It is:

> A resume-safe, GPU-adaptive, autonomous molecular dynamics research platform
> Designed for PG & PhD researchers.

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

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

*BioDockify MD Universal - Built for researchers, by researchers.*
