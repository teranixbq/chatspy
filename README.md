# ChatSpy 🔐

**Secure peer-to-peer chat for local networks with end-to-end encryption.**

ChatSpy is a terminal-based chat application that allows you to communicate securely with others on your local network (WiFi or Ethernet). All messages are encrypted end-to-end using RSA-2048 and AES-256-GCM.

![ChatSpy with Aura Theme](assets/screenshot.png)

## Features

- ✅ **End-to-End Encryption**: RSA-2048 for key exchange, AES-256-GCM for messages
- ✅ **Auto-Discovery**: Automatically finds peers on your local network via mDNS
- ✅ **No Server Required**: Pure P2P communication, no central server
- ✅ **Modern Terminal UI**: Beautiful interface with Aura color theme
- ✅ **Cross-Platform**: Works on Linux and Windows
- ✅ **Desktop Notifications**: Get notified of new messages
- ✅ **Privacy-Focused**: No message history stored, realtime only
- ✅ **Single Executable**: No Python installation required (when built)

## Security Features

- **RSA-2048** keypair for identity and key exchange
- **AES-256-GCM** for message encryption
- **HMAC-SHA256** for message authentication
- **Replay protection** via nonces and timestamps
- **Trust-on-First-Use (TOFU)** security model
- Keys stored encrypted on disk

## Installation

### From Source (Development)

```bash
# Clone repository
cd /path/to/chatspy

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run ChatSpy
python -m src
```

### From Binary (Coming Soon)

Download the latest release for your platform:
- Linux: `chatspy-linux-x86_64`
- Windows: `chatspy-windows-x64.exe`

No installation required, just run the executable.

## Usage

### First Run

1. Launch ChatSpy: `python -m src`
2. Enter your username when prompted
3. ChatSpy will generate your encryption keys automatically

### Chatting

1. ChatSpy will automatically discover peers on your local network
2. Select a peer from the left panel (use arrow keys or mouse)
3. Press `Enter` to connect
4. Type your message and press `Enter` to send
5. All messages are automatically encrypted!

### Keyboard Shortcuts

**Global:**
- `Ctrl+C` / `q` - Quit application
- `Ctrl+H` / `?` - Show help screen
- `Tab` - Switch focus between panels

**Peer List:**
- `↑` / `k` - Move up
- `↓` / `j` - Move down
- `Enter` - Select peer and focus chat

**Chat:**
- `i` - Focus input box
- `↑` / `k` - Scroll up
- `↓` / `j` - Scroll down
- `Ctrl+U` - Page up
- `Ctrl+D` - Page down

**Input Box:**
- `Enter` - Send message
- `Esc` - Unfocus input
- `Ctrl+U` - Clear input

## Configuration

Configuration is stored in `~/.config/chatspy/config.toml`:

```toml
[user]
username = "your_username"
user_id = "uuid"

[network]
discovery_port = 5000
listen_port = 5001
broadcast_interval = 5

[ui]
theme = "aura"
notification_enabled = true
sound_enabled = false

[security]
auto_accept_peers = true
key_rotation_days = 0
```

### Encryption Keys

Your RSA keypair is stored in `~/.config/chatspy/keys/`:
- `private_key.pem` - Your private key (keep secret!)
- `public_key.pem` - Your public key (shared with peers)

## Network Requirements

- **Local Network**: All users must be on the same LAN (WiFi or Ethernet)
- **Ports**: ChatSpy uses ports 5000 (discovery) and 5001 (P2P chat)
- **Firewall**: Ensure these ports are allowed in your firewall
- **mDNS**: Requires mDNS/Bonjour support (built into most systems)

## Building from Source

```bash
# Install build dependencies
pip install -r requirements-dev.txt

# Build executable
pyinstaller pyinstaller.spec

# Output: dist/chatspy (Linux) or dist/chatspy.exe (Windows)
```

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint
flake8 src/ tests/

# Type checking
mypy src/
```

## Architecture

```
┌─────────────────────────────────────────────────┐
│                  ChatSpy App                    │
├─────────────────────────────────────────────────┤
│  UI Layer (Textual)                             │
│  - Setup Screen                                 │
│  - Lobby Screen (Peer List + Chat)              │
│  - Aura Theme                                   │
├─────────────────────────────────────────────────┤
│  Network Layer                                  │
│  - mDNS Discovery (Zeroconf)                    │
│  - Async TCP Transport                          │
│  - Peer Connection Management                   │
│  - Message Protocol (msgpack)                   │
├─────────────────────────────────────────────────┤
│  Crypto Layer                                   │
│  - RSA-2048 Key Management                      │
│  - AES-256-GCM Encryption                       │
│  - Secure Key Exchange                          │
│  - HMAC Authentication                          │
├─────────────────────────────────────────────────┤
│  Core                                           │
│  - User Models                                  │
│  - Message Models                               │
│  - Configuration (Pydantic)                     │
└─────────────────────────────────────────────────┘
```

## Technology Stack

- **Python 3.10+**
- **Textual** - Modern TUI framework
- **cryptography** - RSA & AES encryption
- **Zeroconf** - mDNS service discovery
- **msgpack** - Binary message serialization
- **plyer** - Cross-platform notifications
- **Pydantic** - Data validation & settings

## Security Considerations

### What ChatSpy Protects Against

✅ **Network eavesdropping**: All messages encrypted end-to-end  
✅ **Message tampering**: HMAC signatures verify integrity  
✅ **Replay attacks**: Timestamps and nonces prevent replay  

### Limitations

⚠️ **Not anonymous**: IP addresses visible on LAN  
⚠️ **No forward secrecy**: Session keys not rotated (yet)  
⚠️ **Trust-on-First-Use**: First connection auto-trusted  
⚠️ **Local device security**: If your device is compromised, keys are accessible  

### Best Practices

- Use ChatSpy only on trusted local networks
- Keep your device secure with disk encryption
- Don't share your private key file
- Verify peer identity out-of-band for sensitive communications

## Troubleshooting

### Peers not showing up

- Ensure all devices are on the same network
- Check firewall allows ports 5000 and 5001
- Verify mDNS is not blocked by your router

### Connection failed

- Check the peer's firewall settings
- Ensure port 5001 is not used by another application
- Try restarting ChatSpy on both devices

### Messages not decrypting

- This indicates a key exchange failure
- Disconnect and reconnect to the peer
- Check the logs in `chatspy.log`

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Ensure all tests pass: `pytest tests/ -v`
6. Format code: `black src/ tests/`
7. Submit a pull request

## License

MIT License - see LICENSE file for details

## Roadmap

- [ ] Group chat support
- [ ] File transfer (encrypted)
- [ ] Perfect forward secrecy (key rotation)
- [ ] Optional peer fingerprint verification
- [ ] Custom emoji support
- [ ] Read receipts
- [ ] Typing indicators
- [ ] Sound notifications
- [ ] Multiple theme support
- [ ] Windows build and testing

## Credits

Built with:
- [Textual](https://textual.textualize.io/) - Amazing TUI framework
- [cryptography](https://cryptography.io/) - Secure crypto primitives
- [Aura Theme](https://github.com/daltonmenezes/aura-theme) - Beautiful color scheme

---

**ChatSpy** - Secure chat for paranoid developers 🔐
