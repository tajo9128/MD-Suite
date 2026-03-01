# Nanobot Brain Design

Nanobot is the autonomous supervisory intelligence of BioDockify MD Universal. It continuously monitors, analyzes, and manages molecular dynamics simulations.

## Overview

Nanobot acts as a continuous supervision system that:
- Monitors simulation progress
- Detects errors and instabilities
- Protects hardware
- Synchronizes state for UI
- Communicates with users
- Triggers finalization

## Architecture

```
Nanobot Brain
    |
    +-- Perception Layer
    |       +-- Log Watcher
    |       +-- GPU Monitor
    |       +-- Disk Monitor
    |
    +-- Reasoning Layer
    |       +-- Error Detector
    |       +-- Progress Analyzer
    |       +-- Stability Checker
    |
    +-- Action Layer
    |       +-- Simulation Control
    |       +-- Finalization Trigger
    |
    +-- Communication Layer
    |       +-- Telegram Notifier
    |       +-- WhatsApp Notifier
    |       +-- Discord Notifier
    |       +-- Email Notifier
    |
    +-- Memory Layer
            +-- State Manager
```

## Continuous Event Loop

Nanobot runs a continuous event loop that executes every 5 seconds:

```
Start
  |
  v
Perceive -> Reason -> Act -> Communicate
  |                        |
  +-------- Update State --+
  |
  v
Wait 5 seconds
  |
  v
Repeat
```

## Perception Layer

### Log Watcher
- Reads GROMACS md.log files
- Extracts current simulation time (ns)
- Tracks simulation step count
- Detects completion status

### GPU Monitor
- Polls GPU temperature
- Tracks VRAM usage
- Monitors GPU utilization
- Detects overheating

### Disk Monitor
- Tracks free disk space
- Warns when space is low
- Prevents disk overflow

## Reasoning Layer

### Error Detector
- Parses logs for error keywords
- Detects LINCS warnings
- Identifies simulation crashes
- Categorizes severity (warning, error, critical)

### Progress Analyzer
- Calculates progress percentage
- Determines if simulation should continue
- Estimates time to completion
- Evaluates convergence

### Stability Checker
- Monitors energy drift
- Tracks LINCS warning frequency
- Assesses simulation stability

## Action Layer

### Simulation Control
- Pause simulation
- Resume simulation
- Stop simulation
- Restart stalled segments

### Finalization Trigger
- Merges trajectory segments
- Generates final output
- Creates publication package

## Communication Layer

### Notification Channels
- **Telegram**: Instant messaging alerts
- **WhatsApp**: Alternative messaging
- **Discord**: Webhook notifications
- **Email**: Traditional email alerts

### Notification Events
- Simulation started
- Progress milestones (25%, 50%, 75%)
- Error detected
- Simulation paused (overheat)
- Final package ready

## Memory Layer

### State Manager
- Maintains project state in `nanobot_state.json`
- Tracks notification history
- Records errors and warnings
- Persists across sessions

### Synchronization Engine
- Updates `status.json` in real-time
- Enables UI to read current state
- Prevents race conditions

## Integrity Checker

Validates data integrity before finalization:
- Checks checkpoint freshness
- Verifies segment completeness
- Detects simulation stalls
- Ensures trajectory continuity

## Decision Matrix

| Condition | Action |
|-----------|--------|
| No checkpoint update > 15 min | Flag stall, notify user |
| GPU temperature > 85C | Pause simulation, wait, resume |
| Disk space < 5 GB | Pause, alert user |
| RMSD unstable | Log warning |
| Total ns reached | Trigger finalization |
| Error detected | Notify user, log error |

## Resume Synchronization

On system restart:
1. Read config.json
2. Read status.json
3. Parse actual log files
4. Cross-validate state
5. Resume from checkpoint

This ensures no corrupted resume.

---

*See related documentation: [Architecture](architecture.md), [Resume System](resume_system.md)*
