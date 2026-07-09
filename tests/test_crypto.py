"""Tests for cryptography modules."""

import pytest
from pathlib import Path

from src.crypto.keys import KeyManager
from src.crypto.encryption import MessageEncryption
from src.crypto.exchange import KeyExchange


class TestKeyManager:
    """Tests for RSA key management."""

    def test_generate_keypair(self, temp_config_dir):
        """Test RSA keypair generation."""
        keys_dir = temp_config_dir / "keys"
        keys_dir.mkdir()
        km = KeyManager(keys_dir)

        private_b64, public_b64 = km.generate_keypair()

        assert private_b64
        assert public_b64
        assert len(private_b64) > 0
        assert len(public_b64) > 0

    def test_save_and_load_keypair(self, temp_config_dir):
        """Test saving and loading keys from disk."""
        keys_dir = temp_config_dir / "keys"
        keys_dir.mkdir()
        km = KeyManager(keys_dir)

        # Generate and save
        private_b64, public_b64 = km.generate_keypair()
        km.save_keypair(private_b64, public_b64)

        # Load
        loaded_private, loaded_public = km.load_keypair()

        assert loaded_private == private_b64
        assert loaded_public == public_b64

    def test_keys_exist(self, temp_config_dir):
        """Test checking if keys exist."""
        keys_dir = temp_config_dir / "keys"
        keys_dir.mkdir()
        km = KeyManager(keys_dir)

        assert not km.keys_exist()

        private_b64, public_b64 = km.generate_keypair()
        km.save_keypair(private_b64, public_b64)

        assert km.keys_exist()

    def test_encrypt_decrypt_with_keypair(self, temp_config_dir):
        """Test RSA encryption and decryption."""
        keys_dir = temp_config_dir / "keys"
        keys_dir.mkdir()
        km = KeyManager(keys_dir)

        private_b64, public_b64 = km.generate_keypair()
        km.save_keypair(private_b64, public_b64)
        km.load_keypair()  # Load into memory

        # Test data
        test_data = b"Hello, this is a test message!"

        # Encrypt with public key
        encrypted = km.encrypt_with_public_key(test_data, public_b64)
        assert encrypted != test_data

        # Decrypt with private key
        decrypted = km.decrypt_with_private_key(encrypted)
        assert decrypted == test_data

    def test_fingerprint_generation(self, temp_config_dir):
        """Test public key fingerprint generation."""
        keys_dir = temp_config_dir / "keys"
        keys_dir.mkdir()
        km = KeyManager(keys_dir)

        _, public_b64 = km.generate_keypair()
        fingerprint = km.get_fingerprint(public_b64)

        # Should be formatted as hex with colons
        assert ':' in fingerprint
        assert len(fingerprint.split(':')) == 16


class TestMessageEncryption:
    """Tests for AES message encryption."""

    def test_generate_session_key(self):
        """Test session key generation."""
        key = MessageEncryption.generate_session_key()
        assert len(key) == 32  # 256 bits

    def test_encrypt_decrypt(self):
        """Test AES encryption and decryption."""
        session_key = MessageEncryption.generate_session_key()
        enc = MessageEncryption(session_key)

        plaintext = "This is a secret message!"
        encrypted_b64, iv_b64, signature_b64 = enc.encrypt(plaintext)

        assert encrypted_b64
        assert iv_b64
        assert signature_b64

        # Decrypt
        decrypted = enc.decrypt(encrypted_b64, iv_b64, signature_b64)
        assert decrypted == plaintext

    def test_encryption_produces_different_ciphertext(self):
        """Test that same plaintext produces different ciphertext (random IV)."""
        session_key = MessageEncryption.generate_session_key()
        enc = MessageEncryption(session_key)

        plaintext = "Same message"
        encrypted1, _, _ = enc.encrypt(plaintext)
        encrypted2, _, _ = enc.encrypt(plaintext)

        # Should be different due to random IV
        assert encrypted1 != encrypted2

    def test_tampered_message_fails_verification(self):
        """Test that tampered messages fail HMAC verification."""
        session_key = MessageEncryption.generate_session_key()
        enc = MessageEncryption(session_key)

        plaintext = "Original message"
        encrypted_b64, iv_b64, signature_b64 = enc.encrypt(plaintext)

        # Tamper with encrypted data
        import base64
        encrypted_bytes = base64.b64decode(encrypted_b64)
        tampered_bytes = bytes([b ^ 1 for b in encrypted_bytes[:10]]) + encrypted_bytes[10:]
        tampered_b64 = base64.b64encode(tampered_bytes).decode('utf-8')

        # Should fail verification
        with pytest.raises(ValueError, match="HMAC signature verification failed"):
            enc.decrypt(tampered_b64, iv_b64, signature_b64)

    def test_wrong_key_fails_decryption(self):
        """Test that wrong key fails decryption."""
        session_key1 = MessageEncryption.generate_session_key()
        session_key2 = MessageEncryption.generate_session_key()

        enc1 = MessageEncryption(session_key1)
        enc2 = MessageEncryption(session_key2)

        plaintext = "Secret message"
        encrypted_b64, iv_b64, signature_b64 = enc1.encrypt(plaintext)

        # Try to decrypt with wrong key
        with pytest.raises(ValueError):
            enc2.decrypt(encrypted_b64, iv_b64, signature_b64)


class TestKeyExchange:
    """Tests for key exchange protocol."""

    def test_full_key_exchange(self, temp_config_dir):
        """Test complete key exchange between two peers."""
        # Setup two key managers (two peers)
        keys_dir1 = temp_config_dir / "peer1" / "keys"
        keys_dir2 = temp_config_dir / "peer2" / "keys"
        keys_dir1.mkdir(parents=True)
        keys_dir2.mkdir(parents=True)

        km1 = KeyManager(keys_dir1)
        km2 = KeyManager(keys_dir2)

        private1_b64, public1_b64 = km1.generate_keypair()
        private2_b64, public2_b64 = km2.generate_keypair()

        km1.save_keypair(private1_b64, public1_b64)
        km2.save_keypair(private2_b64, public2_b64)

        km1.load_keypair()
        km2.load_keypair()

        # Create key exchange instances
        kx1 = KeyExchange(km1)
        kx2 = KeyExchange(km2)

        # Peer 1 initiates key exchange with Peer 2's public key
        session_key, encrypted_key_b64 = kx1.create_key_exchange_request(public2_b64)

        # Peer 2 receives and decrypts session key
        received_key = kx2.process_key_exchange_response(encrypted_key_b64)

        # Both should have same session key
        assert session_key == received_key

        # Establish sessions
        enc1 = kx1.establish_session("peer2", session_key)
        enc2 = kx2.establish_session("peer1", received_key)

        # Test encryption/decryption with established session
        message = "Hello from peer 1!"
        encrypted_b64, iv_b64, sig_b64 = enc1.encrypt(message)
        decrypted = enc2.decrypt(encrypted_b64, iv_b64, sig_b64)

        assert decrypted == message

    def test_nonce_generation(self, temp_config_dir):
        """Test nonce generation for replay protection."""
        keys_dir = temp_config_dir / "keys"
        keys_dir.mkdir()
        km = KeyManager(keys_dir)
        kx = KeyExchange(km)

        nonce1 = kx.generate_nonce()
        nonce2 = kx.generate_nonce()

        # Should be different
        assert nonce1 != nonce2
        # Should be base64
        import base64
        decoded = base64.b64decode(nonce1)
        assert len(decoded) == 16

    def test_session_management(self, temp_config_dir):
        """Test session creation and retrieval."""
        keys_dir = temp_config_dir / "keys"
        keys_dir.mkdir()
        km = KeyManager(keys_dir)
        kx = KeyExchange(km)

        session_key = MessageEncryption.generate_session_key()
        peer_id = "test-peer-123"

        # No session initially
        assert not kx.has_session(peer_id)
        assert kx.get_session(peer_id) is None

        # Establish session
        enc = kx.establish_session(peer_id, session_key)
        assert kx.has_session(peer_id)
        assert kx.get_session(peer_id) is enc

        # Remove session
        kx.remove_session(peer_id)
        assert not kx.has_session(peer_id)
