#!/usr/bin/env python3
"""
The People's AI — main entry point
Fully local desktop app. No cloud.
"""

import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from ui.app import App
from core import config, logger
from utils.paths import ensure_dirs

def main():
    logger.init()
    logger.info("=== The People's AI starting ===")

    ensure_dirs()
    config.load_config()

    # Launch the GUI
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()

if __name__ == "__main__":
    main()
