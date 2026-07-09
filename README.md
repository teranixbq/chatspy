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

Download from [Releases](https://github.com/teranixbq/chatspy/releases):

**Linux:**
```bash
chmod +x chatspy-linux-x86_64
./chatspy-linux-x86_64
```

**Windows:**
```powershell
.\chatspy-windows-x64.exe
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

## Development

```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run
python -m src

# Test
pytest tests/ -v

# Build
pyinstaller pyinstaller.spec
```

## License

MIT
