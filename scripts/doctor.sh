#!/usr/bin/env bash
# ============================================================
#  FreedomForge AI — Environment Doctor
#  Run this to diagnose common setup problems.
#  Usage:  bash scripts/doctor.sh
# ============================================================

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="$APP_DIR/.venv"

GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'

ok()   { echo -e "  ${GREEN}✅  $*${RESET}"; }
fail() { echo -e "  ${RED}❌  $*${RESET}"; FAIL=1; }
warn() { echo -e "  ${YELLOW}⚠️   $*${RESET}"; }
info() { echo -e "  ${CYAN}$*${RESET}"; }
hdr()  { echo; echo -e "  ${BOLD}$*${RESET}"; }

FAIL=0

echo
echo -e "  ${BOLD}${CYAN}FreedomForge AI — Environment Doctor${RESET}"
echo "  ─────────────────────────────────────────────────"

# ── OS / Platform ────────────────────────────────────────────
hdr "Platform"
OS="$(uname -s)"
info "OS kernel : $(uname -sr)"
if [[ "$OS" == "Linux" ]] && [[ -f /etc/os-release ]]; then
    . /etc/os-release
    info "Distro    : ${PRETTY_NAME:-unknown}"
fi
info "Arch      : $(uname -m)"

# ── Display ──────────────────────────────────────────────────
hdr "Display"
if [[ "$OS" == "Linux" ]]; then
    if [[ -n "${DISPLAY:-}" ]]; then
        ok "DISPLAY=$DISPLAY"
    elif [[ -n "${WAYLAND_DISPLAY:-}" ]]; then
        ok "WAYLAND_DISPLAY=$WAYLAND_DISPLAY"
    else
        fail "No display (\$DISPLAY and \$WAYLAND_DISPLAY unset) — GUI will not work"
    fi
else
    ok "Non-Linux — display check skipped"
fi

# ── Python ───────────────────────────────────────────────────
hdr "Python"
if command -v python3 &>/dev/null; then
    PY_VER=$(python3 -c 'import sys; print(sys.version)')
    PY_SHORT=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    ok "python3 $PY_VER"
    PY_MAJOR=$(python3 -c 'import sys; print(sys.version_info.major)')
    PY_MINOR=$(python3 -c 'import sys; print(sys.version_info.minor)')
    if [[ "$PY_MAJOR" -lt 3 || ( "$PY_MAJOR" -eq 3 && "$PY_MINOR" -lt 10 ) ]]; then
        fail "Python 3.10+ required (found $PY_SHORT)"
    else
        ok "Version $PY_SHORT meets minimum (3.10+)"
    fi
else
    fail "python3 not found — install Python 3.10+"
fi

# ── tkinter ──────────────────────────────────────────────────
hdr "tkinter"
if python3 -c "import tkinter" &>/dev/null; then
    TK_VER=$(python3 -c "import tkinter; print(tkinter.TkVersion)" 2>/dev/null || echo "unknown")
    ok "tkinter available (Tk $TK_VER)"
else
    fail "tkinter not available"
    if [[ "$OS" == "Linux" ]]; then
        warn "  Fix: sudo apt-get install -y python3-tk"
    elif [[ "$OS" == "Darwin" ]]; then
        warn "  Fix: brew install python-tk"
    fi
fi

# ── Virtual environment ──────────────────────────────────────
hdr "Virtual environment"
if [[ -d "$VENV" ]]; then
    ok ".venv found: $VENV"
    VENV_PYTHON="$VENV/bin/python3"
    if [[ -x "$VENV_PYTHON" ]]; then
        VENV_VER=$("$VENV_PYTHON" -c 'import sys; print(sys.version)' 2>/dev/null)
        ok "venv Python: $VENV_VER"
    else
        fail "venv Python binary not found/executable"
    fi
else
    fail ".venv not found at $VENV — run: bash install.sh"
fi

# ── Key Python imports ────────────────────────────────────────
hdr "Python package imports"
if [[ -d "$VENV" ]]; then
    ACTIVATE="$VENV/bin/activate"
    # shellcheck source=/dev/null
    source "$ACTIVATE" 2>/dev/null || true

    check_import() {
        local module="$1" label="${2:-$1}"
        if python3 -c "import $module" &>/dev/null; then
            ok "$label"
        else
            case "$module" in
                llama_cpp) warn "$label — optional (AI model loading disabled)" ;;
                pyaudio)   warn "$label — optional (voice input disabled)" ;;
                gputil)    warn "$label — optional (GPU monitor disabled)" ;;
                *)         fail "$label — required; re-run install.sh" ;;
            esac
        fi
    }

    check_import customtkinter "customtkinter"
    check_import tkinter       "tkinter (in venv)"
    check_import PIL           "Pillow"
    check_import psutil        "psutil"
    check_import requests      "requests"
    check_import cryptography  "cryptography"
    check_import speech_recognition "SpeechRecognition"
    check_import pyttsx3       "pyttsx3"
    check_import pyaudio       "pyaudio (optional)"
    check_import llama_cpp     "llama-cpp-python (optional)"
    check_import gputil        "gputil (optional)"
else
    warn "Skipping import checks — .venv not found"
fi

# ── System libraries ─────────────────────────────────────────
if [[ "$OS" == "Linux" ]] && command -v dpkg &>/dev/null; then
    hdr "System libraries (Debian/Ubuntu/Mint)"
    for pkg in python3-tk portaudio19-dev build-essential libssl-dev libffi-dev; do
        if dpkg -s "$pkg" &>/dev/null; then
            ok "$pkg"
        else
            warn "$pkg not installed"
        fi
    done
fi

# ── Crash reports ─────────────────────────────────────────────
hdr "Crash reports"
CRASH_DIR="$APP_DIR/crash_reports"
if [[ -d "$CRASH_DIR" ]]; then
    mapfile -t CRASH_FILES < <(find "$CRASH_DIR" -maxdepth 1 -type f)
    COUNT="${#CRASH_FILES[@]}"
    if [[ "$COUNT" -eq 0 ]]; then
        ok "No crash reports found"
    else
        warn "$COUNT file(s) in $CRASH_DIR (latest below)"
        LATEST=$(ls -t "$CRASH_DIR" 2>/dev/null | head -1)
        [[ -n "$LATEST" ]] && info "  $CRASH_DIR/$LATEST"
    fi
else
    ok "crash_reports directory not yet created"
fi

# ── Summary ───────────────────────────────────────────────────
echo
echo "  ─────────────────────────────────────────────────"
if [[ "$FAIL" -eq 0 ]]; then
    echo -e "  ${GREEN}${BOLD}All checks passed. You're good to go!${RESET}"
    echo -e "  ${CYAN}  bash launch.sh${RESET}"
else
    echo -e "  ${RED}${BOLD}Some checks failed — fix the issues above, then re-run:${RESET}"
    echo -e "  ${CYAN}  bash install.sh${RESET}"
fi
echo "  ─────────────────────────────────────────────────"
echo

exit "$FAIL"
