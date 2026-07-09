# ChatSpy

Secure P2P terminal chat for local networks with end-to-end encryption.

## Features

- End-to-end encryption (RSA-2048 + AES-256-GCM)
- Auto-discovery via mDNS
- No server required
- Modern terminal UI
- Desktop notifications
- No message history

## Installation

```bash
# Clone repository
git clone https://github.com/teranixbq/chatspy.git
cd chatspy

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run ChatSpy
python -m src
```

## Usage

1. Launch ChatSpy and enter your username
2. Peers on your LAN will appear automatically
3. Select a peer and press Enter to connect
4. Type messages and press Enter to send

**Keyboard shortcuts:**
- `Ctrl+C` / `q` - Quit
- `Tab` - Switch focus
- `↑↓` or `jk` - Navigate

## Requirements

- Same local network (LAN)
- Ports 5000-5001 open in firewall
- Linux x86_64 or Windows x64

## Building Executable (Optional)

```bash
# Install build dependencies
pip install pyinstaller

# Build single executable
pyinstaller pyinstaller.spec

# Output: dist/chatspy (Linux) or dist/chatspy.exe (Windows)
```

## Development

```bash
# Run tests
pytest tests/ -v

# Format code
black src/ tests/
```

## License

MIT
