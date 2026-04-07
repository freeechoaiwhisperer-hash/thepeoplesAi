# FreedomForge AI

> Free. Private. Yours. For Everyone.  
> *Dedicated to Miranda. She will never be forgotten.*

FreedomForge AI is a local, privacy-first AI assistant with a graphical interface.  
It runs entirely on your machine — no cloud required.

---

## Quick Start

### Linux Mint / Ubuntu / Debian

**Prerequisites** — the installer handles these automatically, but if you want to install them first:

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip python3-tk \
    portaudio19-dev build-essential pkg-config libssl-dev libffi-dev
```

**Install and launch:**

```bash
# 1. Clone the repo (or download and extract the zip)
git clone https://github.com/freeechoaiwhisperer-hash/thepeoplesAi.git
cd thepeoplesAi

# 2. Run the installer (will ask for sudo to install system packages)
bash install.sh

# 3. Launch
bash launch.sh
```

The installer also creates a **Desktop shortcut** (FreedomForgeAI.desktop) you can double-click.

**Running from terminal (recommended for debugging):**

```bash
bash launch.sh
# Logs are saved to crash_reports/launcher.log
```

---

### macOS

**Prerequisites:** [Homebrew](https://brew.sh/) recommended.

```bash
brew install python3
```

**Install and launch:**

```bash
bash install.sh
bash launch.sh
```

The installer creates a `FreedomForgeAI.app` bundle on your Desktop.

---

### Windows

Double-click `install.bat` (or run `install.ps1` in PowerShell) and follow the prompts.  
A `launch.bat` will be created when the install finishes.

---

## Requirements

| Requirement | Minimum |
|---|---|
| Python | 3.10+ |
| OS | Linux (Ubuntu 22.04+ / Mint 21+), macOS 12+, Windows 10+ |
| RAM | 4 GB (8 GB+ recommended for local AI models) |
| Disk | 2 GB free (more for AI models) |

---

## Troubleshooting

### "No module named tkinter"

```bash
sudo apt-get install -y python3-tk
bash install.sh   # re-run to refresh the venv
```

### Voice input not working

```bash
sudo apt-get install -y portaudio19-dev
source .venv/bin/activate && pip install pyaudio
```

### App won't open / crashes silently

Run from terminal and check the log:

```bash
bash launch.sh
cat crash_reports/launcher.log
```

### "No display detected" error

You are running on a headless server or SSH session without X forwarding.  
FreedomForge AI requires a desktop environment.  
If you're on SSH, connect with X forwarding:

```bash
ssh -X user@yourhost
cd thepeoplesAi && bash launch.sh
```

### Environment self-check

Run the doctor script to verify your environment:

```bash
bash scripts/doctor.sh
```

---

## Project Structure

```
thepeoplesAi/
├── install.sh        # Linux / macOS installer
├── install.ps1       # Windows installer
├── launch.sh         # Linux / macOS launcher
├── main.py           # Application entry point
├── requirements.txt  # Python dependencies
├── scripts/
│   └── doctor.sh     # Environment self-check
├── core/             # Core services (config, logging, etc.)
├── ui/               # GUI components (customtkinter)
├── modules/          # Feature modules (agent, voice, video, etc.)
├── plugins/          # Pluggable tools
└── crash_reports/    # Crash / launch logs
```

---

## License

AGPL-3.0 + Commons Clause — see [VISION.md](VISION.md) for project philosophy.
