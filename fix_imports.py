#!/usr/bin/env python3
"""Fix all import paths to work with both dev mode and PyInstaller."""

import os
import re
from pathlib import Path

def fix_file(filepath):
    """Fix imports in a single file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    original = content
    
    # For files in ui/widgets and ui/screens: use ../../ for core/crypto/network
    if '/ui/widgets/' in str(filepath) or '/ui/screens/' in str(filepath):
        content = re.sub(r'^from \.core\.', 'from ...core.', content, flags=re.MULTILINE)
        content = re.sub(r'^from \.\.\.core\.', 'from ...core.', content, flags=re.MULTILINE)
    
    # For files in ui/: use ../ for core/crypto/network  
    elif '/ui/' in str(filepath) and '/ui/widgets/' not in str(filepath) and '/ui/screens/' not in str(filepath):
        content = re.sub(r'^from core\.', 'from ..core.', content, flags=re.MULTILINE)
        content = re.sub(r'^from crypto\.', 'from ..crypto.', content, flags=re.MULTILINE)
        content = re.sub(r'^from network\.', 'from ..network.', content, flags=re.MULTILINE)
        content = re.sub(r'^from \.\.\.core\.', 'from ..core.', content, flags=re.MULTILINE)
        content = re.sub(r'^from \.\.\.crypto\.', 'from ..crypto.', content, flags=re.MULTILINE)
        content = re.sub(r'^from \.\.\.network\.', 'from ..network.', content, flags=re.MULTILINE)
    
    # For files in network/: use ../ for core/crypto
    elif '/network/' in str(filepath):
        content = re.sub(r'^from core\.', 'from ..core.', content, flags=re.MULTILINE)
        content = re.sub(r'^from crypto\.', 'from ..crypto.', content, flags=re.MULTILINE)
    
    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Fixed: {filepath}")
    
if __name__ == '__main__':
    src_dir = Path('src')
    for py_file in src_dir.rglob('*.py'):
        if '__pycache__' not in str(py_file):
            fix_file(py_file)
    print("\nDone!")
