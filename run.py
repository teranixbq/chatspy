#!/usr/bin/env python3
"""ChatSpy standalone entry point for PyInstaller."""

import sys
import os
from pathlib import Path

# Setup Python path for imports
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    base_path = Path(sys._MEIPASS)
    sys.path.insert(0, str(base_path / 'src'))
else:
    # Running in development
    base_path = Path(__file__).parent
    sys.path.insert(0, str(base_path / 'src'))

# Import and run
from ui.app import run_app

if __name__ == "__main__":
    run_app()
