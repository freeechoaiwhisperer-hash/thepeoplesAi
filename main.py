#!/usr/bin/env python3
"""
The People's AI — main entry point
Fully local desktop app. No cloud.
"""

import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Install crash handler as early as possible — before any external-package imports
try:
    from core import crash_reporter as _crash_reporter
    _crash_reporter.install_handler()
except Exception:
    pass

# Friendly early check for required GUI packages
_REQUIRED_PACKAGES = [
    ("customtkinter", "customtkinter>=5.2.0"),
    ("PIL",           "Pillow>=10.0.0"),
    ("psutil",        "psutil>=5.9.0"),
    ("requests",      "requests>=2.28.0"),
]
_missing = []
for _mod, _pkg in _REQUIRED_PACKAGES:
    try:
        __import__(_mod)
    except ImportError:
        _missing.append(_pkg)
if _missing:
    print("\n\u274c  Missing required packages. Please run:  bash install.sh\n")
    print("   Missing:")
    for _p in _missing:
        print(f"     \u2022 {_p}")
    print()
    sys.exit(1)

from core import config, logger
from utils.paths import ensure_dirs


def main():
    logger.init()
    logger.info("=== The People's AI starting ===")

    ensure_dirs()
    config.load_config()

    # Deferred import — crash handler is already active by this point
    from ui.app import App

    # Patch tkinter's silent exception handler to log crashes to app.log
    import traceback as _tb

    def _log_tk_error(exc, val, tb):
        logger.error("Tkinter callback exception:\n" + "".join(_tb.format_exception(exc, val, tb)))

    # Launch the GUI
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.report_callback_exception = _log_tk_error
    app.mainloop()


if __name__ == "__main__":
    main()
