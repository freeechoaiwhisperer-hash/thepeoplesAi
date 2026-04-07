#!/usr/bin/env bash
# ============================================================
#  FreedomForge AI — One-Click Installer (Linux / macOS)
#  Copyright (c) 2026 Ryan Dennison
#  Licensed under AGPL-3.0 + Commons Clause
#
#  Dedicated to Miranda.  She will never be forgotten.
# ============================================================

set -euo pipefail

# ── Colors ───────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
GOLD='\033[0;33m'; CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'

ok()   { echo -e "  ${GREEN}✅  $*${RESET}"; }
warn() { echo -e "  ${YELLOW}⚠️   $*${RESET}"; }
err()  { echo -e "  ${RED}❌  $*${RESET}"; }
info() { echo -e "  ${CYAN}$*${RESET}"; }
step() { echo; echo -e "  ${BOLD}${GOLD}── $* ${RESET}"; }

clear
echo
echo -e "  ${GOLD}${BOLD}⚒️   FreedomForge AI — Installer${RESET}"
echo -e "  ${CYAN}Free. Private. Yours. For Everyone.${RESET}"
echo -e "  ${CYAN}Dedicated to Miranda. She will never be forgotten.${RESET}"
echo "  ─────────────────────────────────────────────────"
echo

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$APP_DIR/.venv"
OS="$(uname -s)"

cd "$APP_DIR"

# ── Detect Debian/Ubuntu/Mint ────────────────────────────────
IS_DEBIAN=false
if [[ "$OS" == "Linux" ]] && [[ -f /etc/os-release ]]; then
    . /etc/os-release
    case "${ID:-}:${ID_LIKE:-}" in
        *debian*|*ubuntu*) IS_DEBIAN=true ;;
    esac
fi

# ── System packages (Debian/Ubuntu/Mint) ─────────────────────
if [[ "$IS_DEBIAN" == "true" ]]; then
    step "System packages (Debian/Ubuntu/Mint)"

    # Required packages for the app to run and build
    REQUIRED_APT=(
        python3
        python3-venv
        python3-pip
        python3-tk
        portaudio19-dev
        build-essential
        pkg-config
        libssl-dev
        libffi-dev
    )

    MISSING_APT=()
    for pkg in "${REQUIRED_APT[@]}"; do
        if ! dpkg -s "$pkg" &>/dev/null 2>&1; then
            MISSING_APT+=("$pkg")
        fi
    done

    if [[ ${#MISSING_APT[@]} -gt 0 ]]; then
        info "Missing packages: ${MISSING_APT[*]}"
        info "sudo is required to install system packages — you may be prompted for your password."
        if ! sudo apt-get update; then
            err "apt-get update failed. Check your internet connection and try again."
            exit 1
        fi
        if ! sudo apt-get install -y "${MISSING_APT[@]}"; then
            err "Failed to install: ${MISSING_APT[*]}"
            err "Run manually: sudo apt-get install -y ${MISSING_APT[*]}"
            exit 1
        fi
    fi

    ok "System packages ready"
fi

# ── Python check ─────────────────────────────────────────────
step "Checking Python"

if ! command -v python3 &>/dev/null; then
    err "Python 3 not found."
    if [[ "$OS" == "Darwin" ]]; then
        echo "  Install with: brew install python3"
    elif [[ "$IS_DEBIAN" == "true" ]]; then
        echo "  Install with: sudo apt-get install -y python3 python3-venv python3-pip"
    else
        echo "  Install with your distro's package manager (e.g. dnf install python3)"
    fi
    exit 1
fi

PY_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PY_MAJOR=$(python3 -c 'import sys; print(sys.version_info.major)')
PY_MINOR=$(python3 -c 'import sys; print(sys.version_info.minor)')

if [[ "$PY_MAJOR" -lt 3 || ( "$PY_MAJOR" -eq 3 && "$PY_MINOR" -lt 10 ) ]]; then
    err "Python 3.10+ required. Found: $PY_VER"
    exit 1
fi
ok "Python $PY_VER"

# ── System packages (non-Debian Linux — best-effort) ─────────
if [[ "$OS" == "Linux" ]] && [[ "$IS_DEBIAN" == "false" ]]; then
    step "System packages"

    if ! python3 -c "import tkinter" &>/dev/null 2>&1; then
        warn "tkinter not found — install it for your distro (e.g. dnf install python3-tkinter)"
    fi

    ok "System package check done (non-Debian distro — install tkinter/portaudio manually if needed)"
fi

# ── Virtual environment ──────────────────────────────────────
step "Virtual environment"

if [[ ! -d "$VENV" ]]; then
    info "Creating .venv..."
    python3 -m venv "$VENV"
else
    info "Reusing existing .venv"
fi

source "$VENV/bin/activate"
pip install --upgrade pip setuptools wheel --quiet
ok ".venv ready ($VENV)"

# ── Core Python packages ─────────────────────────────────────
step "Installing Python packages"

info "Installing core dependencies..."
CORE_PACKAGES=(
    "customtkinter>=5.2.0"
    "psutil>=5.9.0"
    "setuptools>=68.0.0"
    "requests>=2.28.0"
    "SpeechRecognition>=3.10.0"
    "pyttsx3>=2.90"
    "cryptography>=41.0.0"
    "Pillow>=10.0.0"
)
if ! pip install "${CORE_PACKAGES[@]}"; then
    err "Failed to install core Python packages — see errors above."
    err "Fix the issues and re-run install.sh"
    exit 1
fi
ok "Core packages installed"

# GPUtil — optional; needs setuptools (distutils shim) on Python 3.12+
info "Installing GPU utilities (optional)..."
pip install "gputil>=1.4.0" 2>/dev/null \
    || warn "GPUtil not installed — GPU% monitor will be disabled. (optional)"

# pyaudio — optional; needs portaudio system lib
info "Installing audio support (optional)..."
if ! pip install "pyaudio>=0.2.13" 2>/dev/null; then
    if [[ "$IS_DEBIAN" == "true" ]]; then
        warn "pyaudio not installed — voice input disabled."
        warn "  To enable: sudo apt-get install -y portaudio19-dev && pip install pyaudio"
    else
        warn "pyaudio not installed — voice input disabled."
        warn "  To enable: install portaudio for your distro, then run: pip install pyaudio"
    fi
fi

ok "All packages done"

# ── AI engine (llama-cpp-python) ─────────────────────────────
step "AI engine (llama-cpp-python)"
info "Detecting hardware..."

CUDA_BUILD=false
METAL_BUILD=false

# NVIDIA GPU
if command -v nvidia-smi &>/dev/null && nvidia-smi &>/dev/null 2>&1; then
    CUDA_VER=$(nvidia-smi | grep -oP 'CUDA Version: \K[\d.]+' || echo "")
    info "NVIDIA GPU detected (CUDA $CUDA_VER) — building with GPU support"
    CUDA_BUILD=true
fi

# Apple Silicon
if [[ "$OS" == "Darwin" ]] && [[ "$(uname -m)" == "arm64" ]]; then
    info "Apple Silicon detected — building with Metal support"
    METAL_BUILD=true
fi

if [[ "$CUDA_BUILD" == "true" ]]; then
    CMAKE_ARGS="-DGGML_CUDA=on" FORCE_CMAKE=1 \
        pip install "llama-cpp-python>=0.2.0" --quiet 2>/dev/null \
    || pip install "llama-cpp-python>=0.2.0" --quiet 2>/dev/null \
    || warn "AI engine install failed — run: pip install llama-cpp-python"
elif [[ "$METAL_BUILD" == "true" ]]; then
    CMAKE_ARGS="-DGGML_METAL=on" FORCE_CMAKE=1 \
        pip install "llama-cpp-python>=0.2.0" --quiet 2>/dev/null \
    || pip install "llama-cpp-python>=0.2.0" --quiet 2>/dev/null \
    || warn "AI engine install failed — run: pip install llama-cpp-python"
else
    info "CPU-only build (no GPU detected)"
    pip install "llama-cpp-python>=0.2.0" --quiet \
        --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu \
    || pip install "llama-cpp-python>=0.2.0" --quiet \
    || warn "AI engine install failed — run: pip install llama-cpp-python"
fi

python3 -c "import llama_cpp; print()" 2>/dev/null \
    && ok "AI engine ready" \
    || warn "AI engine not installed — app runs but cannot load models until you install it"

# ── Launch script ────────────────────────────────────────────
step "Creating launch script"

cat > "$APP_DIR/launch.sh" << 'LAUNCHER_EOF'
#!/usr/bin/env bash
# ============================================================
#  FreedomForge AI — Launcher
# ============================================================
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$APP_DIR/.venv"
LOG_DIR="$APP_DIR/crash_reports"
LOG_FILE="$LOG_DIR/launcher.log"

RED='\033[0;31m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; RESET='\033[0m'

err()  { echo -e "  ${RED}❌  $*${RESET}" >&2; }
warn() { echo -e "  ${YELLOW}⚠️   $*${RESET}" >&2; }
info() { echo -e "  ${CYAN}$*${RESET}"; }

# 1) Check .venv exists
if [[ ! -d "$VENV" ]]; then
    err "Virtual environment not found: $VENV"
    err "Please run install.sh first:"
    err "  bash $APP_DIR/install.sh"
    exit 1
fi

# 2) Check display (Linux only)
if [[ "$(uname -s)" == "Linux" ]]; then
    if [[ -z "${DISPLAY:-}" && -z "${WAYLAND_DISPLAY:-}" ]]; then
        err "No display detected (\$DISPLAY and \$WAYLAND_DISPLAY are both unset)."
        err "FreedomForge AI requires a desktop environment to run."
        err "If you are on SSH, try: ssh -X user@host  or use a VNC/remote desktop."
        exit 1
    fi
fi

# 3) Verify tkinter
source "$VENV/bin/activate"
if ! python3 -c "import tkinter" &>/dev/null 2>&1; then
    err "tkinter is not available in your Python installation."
    err "Install it with:  sudo apt-get install -y python3-tk"
    err "Then re-run:      bash $APP_DIR/install.sh"
    exit 1
fi

# 4) Prepare log dir and launch
mkdir -p "$LOG_DIR"
info "Launching FreedomForge AI... (log: $LOG_FILE)"
python3 -u "$APP_DIR/main.py" "$@" 2>&1 | tee "$LOG_FILE"
LAUNCHER_EOF

chmod +x "$APP_DIR/launch.sh"
ok "launch.sh created"

# ── Desktop shortcut (Linux GNOME/KDE) ───────────────────────
if [[ "$OS" == "Linux" ]]; then
    step "Desktop shortcut"
    DESKTOP="$HOME/Desktop"
    mkdir -p "$DESKTOP"
    ICON="$APP_DIR/assets/icon.png"
    [[ ! -f "$ICON" ]] && ICON=""

    cat > "$DESKTOP/FreedomForgeAI.desktop" << SHORTCUT
[Desktop Entry]
Version=1.0
Type=Application
Name=FreedomForge AI
Comment=Free local AI — Dedicated to Miranda
Exec=$APP_DIR/.venv/bin/python3 $APP_DIR/main.py
Icon=$ICON
Terminal=false
StartupNotify=true
StartupWMClass=FreedomForgeAI
Categories=Utility;Science;Education;
SHORTCUT
    chmod +x "$DESKTOP/FreedomForgeAI.desktop"
    gio set "$DESKTOP/FreedomForgeAI.desktop" metadata::trusted true 2>/dev/null || true
    ok "Desktop shortcut created"
fi

# ── macOS app bundle ──────────────────────────────────────────
if [[ "$OS" == "Darwin" ]]; then
    step "macOS launcher"
    APPBUNDLE="$HOME/Desktop/FreedomForgeAI.app"
    mkdir -p "$APPBUNDLE/Contents/MacOS"
    cat > "$APPBUNDLE/Contents/MacOS/FreedomForgeAI" << MACAPP
#!/usr/bin/env bash
cd "$APP_DIR"
source "$APP_DIR/.venv/bin/activate"
exec python3 "$APP_DIR/main.py"
MACAPP
    chmod +x "$APPBUNDLE/Contents/MacOS/FreedomForgeAI"
    cat > "$APPBUNDLE/Contents/Info.plist" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>CFBundleName</key><string>FreedomForgeAI</string>
<key>CFBundleExecutable</key><string>FreedomForgeAI</string>
<key>CFBundleIdentifier</key><string>com.freedomforgeai.app</string>
<key>CFBundleVersion</key><string>0.1.0</string>
<key>CFBundlePackageType</key><string>APPL</string>
</dict></plist>
PLIST
    ok "macOS app bundle created on Desktop"
fi

# ── Done ─────────────────────────────────────────────────────
echo
echo "  ─────────────────────────────────────────────────"
ok "FreedomForge AI is installed!"
echo
echo -e "  ${GOLD}${BOLD}To launch:${RESET}"
echo -e "  ${CYAN}  bash $APP_DIR/launch.sh${RESET}"
[[ "$OS" == "Linux" ]] && echo -e "  ${CYAN}  or double-click FreedomForgeAI on your Desktop${RESET}"
[[ "$OS" == "Darwin" ]] && echo -e "  ${CYAN}  or double-click FreedomForgeAI.app on your Desktop${RESET}"
echo
echo -e "  ${CYAN}🪄  Dedicated to Miranda.${RESET}"
echo -e "  ${CYAN}    She will never be forgotten.${RESET}"
echo "  ─────────────────────────────────────────────────"
echo

# Auto-launch
read -r -t 8 -p "  Launch now? [Y/n] " REPLY 2>/dev/null || REPLY="Y"
REPLY="${REPLY:-Y}"
if [[ "$REPLY" =~ ^[Yy]$ ]]; then
    info "Launching FreedomForge AI..."
    bash "$APP_DIR/launch.sh" &
fi
