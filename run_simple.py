#!/usr/bin/env python3
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Now import works without relative imports
if __name__ == '__main__':
    from ui.app import run_app
    run_app()
