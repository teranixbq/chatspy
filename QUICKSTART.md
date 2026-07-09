# ChatSpy - Quick Start Guide

## 🚀 Start Chatting in 3 Steps

### Step 1: Run ChatSpy
```bash
cd /home/nodenix/Documents/chatspy
source venv/bin/activate
python -m src
```

### Step 2: Enter Your Username
When prompted, type your username (3-50 characters) and press Enter.

### Step 3: Start Chatting!
- Peers on your network appear in the left panel
- Select a peer and press Enter to connect
- Type your message and press Enter to send

That's it! All messages are automatically encrypted. 🔐

---

## 🎮 Keyboard Shortcuts

### Quick Reference
```
Ctrl+H  - Help screen
Ctrl+C  - Quit
Tab     - Switch panels
i       - Focus input
Esc     - Unfocus input
Enter   - Send message
↑/↓ or j/k - Navigate
```

---

## 🧪 Test with 2 Instances (Same Machine)

### Terminal 1:
```bash
python -m src
# Username: Alice
```

### Terminal 2:
```bash
python -m src
# Username: Bob
```

They should discover each other automatically!

---

## 🔧 Troubleshooting

### "No peers showing up"
- Check: Same network? ✓
- Check: Firewall allows ports 5000-5001? ✓
- Try: Restart ChatSpy

### "Connection failed"
- Check: Peer's firewall settings
- Try: Both restart ChatSpy

### "Messages not decrypting"
- Try: Disconnect and reconnect
- Check: Logs in `chatspy.log`

---

## 📁 Important Files

```
~/.config/chatspy/
├── config.toml           # Your settings
└── keys/
    ├── private_key.pem   # Keep secret!
    └── public_key.pem    # Shared with peers
```

---

## 🏗️ Build Executable (Optional)

```bash
venv/bin/pyinstaller pyinstaller.spec

# Result:
dist/chatspy  # ~30-40MB, ready to share!
```

No Python needed to run the built version!

---

## 📊 What's Happening Under the Hood?

1. **Discovery**: ChatSpy broadcasts via mDNS (port 5000)
2. **Connection**: Peers connect via TCP (port 5001)
3. **Key Exchange**: RSA-2048 secures AES-256 session key
4. **Encryption**: All messages encrypted with AES-256-GCM
5. **Delivery**: Messages sent peer-to-peer, no server

---

## 💡 Pro Tips

1. **Private chat**: Only works on local network (by design)
2. **No history**: Messages disappear when you close (privacy!)
3. **Desktop alerts**: You get notified even when unfocused
4. **Security**: First connection auto-trusted (TOFU model)
5. **Ports**: If 5000/5001 are taken, edit `~/.config/chatspy/config.toml`

---

## ❓ Need Help?

- Press `Ctrl+H` in ChatSpy for help
- Check README.md for detailed docs
- Check chatspy.log for error messages

---

**Enjoy secure chatting!** 🎉🔐
