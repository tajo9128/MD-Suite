# BioDockify MD Universal - Installation Guide

This guide will help you set up BioDockify MD Universal on Windows with WSL2.

---

## System Requirements

### Minimum Requirements
- **OS:** Windows 10/11 with WSL2
- **Python:** 3.10 or higher
- **RAM:** 8 GB
- **Storage:** 50 GB free space

### Recommended Requirements
- **OS:** Windows 11 with WSL2
- **Python:** 3.11
- **RAM:** 16 GB or higher
- **GPU:** NVIDIA RTX series or AMD RX series (optional)
- **Storage:** 100 GB free space (for simulation outputs)

---

## Installation Steps

### Step 1: Install Python

1. Download Python 3.10+ from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. **Important:** Check "Add Python to PATH"
4. Click "Install Now"

To verify:
```bash
python --version
```

---

### Step 2: Enable WSL2

Open PowerShell as Administrator and run:

```powershell
wsl --install
```

Restart your computer when prompted.

After restart, open Ubuntu (or your preferred WSL distribution) and:
1. Create a username and password
2. Update packages:
```bash
sudo apt update && sudo apt upgrade
```

---

### Step 3: Install GROMACS

In WSL (Ubuntu), run:

```bash
# Add GROMACS repository
sudo apt install software-properties-common
sudo add-apt-repository ppa:ubi-kernel/gromacs

# Install GROMACS
sudo apt update
sudo apt install gromacs
```

Verify installation:
```bash
gmx --version
```

---

### Step 4: Install BioDockify MD Universal

#### Option A: Download ZIP

1. Go to [GitHub Releases](https://github.com/tajo9128/MD-lite/releases)
2. Download the latest version ZIP
3. Extract to your desired location (e.g., `C:\BioDockify_MD`)

#### Option B: Git Clone

```bash
git clone https://github.com/tajo9128/MD-lite.git
cd MD-lite
```

---

### Step 5: Set Up Python Environment

Open Command Prompt and navigate to the BioDockify directory:

```bash
cd C:\Path\To\BioDockify_MD

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

### Step 6: Configure (Optional)

Edit `config.yaml` to customize:

```yaml
checkpoint_interval_minutes: 15
default_segment_ns: 10
analysis_dpi: 300
temperature_limit_celsius: 85
min_disk_space_gb: 5
```

---

## Running the Application

### Using start.bat (Recommended)

Simply double-click `start.bat` in the BioDockify folder.

### Using Command Line

Activate the virtual environment:

```bash
venv\Scripts\activate
```

#### Detect GPU
```bash
python main.py --detect-gpu
```

#### Create New Project
```bash
python main.py --create-project my_simulation
```

#### Run Simulation
```bash
python main.py --project ./my_simulation --run
```

#### Launch AI Autonomous Mode
```bash
python main.py --project ./my_simulation --ai
```

#### Launch GUI
```bash
python main.py --ui
```

---

## First-Time Setup Checklist

- [ ] Python 3.10+ installed
- [ ] WSL2 enabled
- [ ] Ubuntu installed in WSL
- [ ] GROMACS installed in WSL
- [ ] BioDockify MD downloaded/cloned
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] GPU detected (`python main.py --detect-gpu`)

---

## Troubleshooting

### GROMACS Not Found

Make sure GROMACS is installed in WSL:
```bash
which gmx
```

If not found, reinstall:
```bash
sudo apt install gromacs
```

### Python Not Found

Ensure Python is in PATH:
```bash
where python
```

### WSL Not Working

Open PowerShell as Administrator:
```bash
wsl --set-default-version 2
wsl --install -d Ubuntu
```

### Import Errors

Reinstall dependencies:
```bash
pip install -r requirements.txt
```

---

## Quick Start Commands

| Command | Description |
|---------|-------------|
| `python main.py --detect-gpu` | Detect available GPU |
| `python main.py --create-project name` | Create new project |
| `python main.py --project ./name --run` | Run simulation |
| `python main.py --project ./name --ai` | Run with AI |
| `python main.py --ui` | Launch GUI |

---

## Support

For issues, please open an issue on GitHub:
https://github.com/tajo9128/MD-lite/issues

---

*Last updated: February 2026*
