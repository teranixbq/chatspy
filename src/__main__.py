"""ChatSpy entry point."""

import sys
import os

# Fix import paths for PyInstaller
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    import pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).parent))

try:
    from ui.app import run_app
except ImportError:
    from .ui.app import run_app

if __name__ == "__main__":
    run_app()
