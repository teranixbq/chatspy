# ChatSpy v1.0.0

Secure peer-to-peer terminal chat for local networks with end-to-end encryption.

## Download

| Platform | File |
|----------|------|
| Linux x86_64 | `chatspy-linux-x86_64` |
| Windows x64 | `chatspy-windows-x64.exe` |

## Quick Start

### Linux
```bash
chmod +x chatspy-linux-x86_64
./chatspy-linux-x86_64
```

### Windows
```powershell
.\chatspy-windows-x64.exe
```

## Features

- End-to-End Encryption (RSA-2048 + AES-256-GCM)
- Auto-Discovery via mDNS (no configuration needed)
- Modern terminal UI with Aura theme
- Desktop notifications
- No server required - fully peer-to-peer
- Zero message history for privacy

## Requirements

- Linux: x86_64 architecture
- Windows: x64 architecture, Windows 10 or later
- Ports 5000-5001 must be open in firewall
- All peers must be on the same local network (LAN)

## Technical Details

- **Encryption**: RSA-2048 for key exchange, AES-256-GCM for message encryption
- **Discovery**: mDNS/Zeroconf for automatic peer discovery
- **Protocol**: Custom binary protocol over TCP with msgpack serialization
- **Trust Model**: TOFU (Trust On First Use) - no manual fingerprint verification

## Known Limitations

- No message history persistence
- No support for file transfers
- No group chat support (one-on-one only)
- Requires LAN connectivity (no internet relay)

## Support

Report issues at: https://github.com/teranixbq/chatspy/issues
