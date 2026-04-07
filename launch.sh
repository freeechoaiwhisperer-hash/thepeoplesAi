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
    if [[ -z "${DISPLAY:-}" ]] && [[ -z "${WAYLAND_DISPLAY:-}" ]]; then
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
