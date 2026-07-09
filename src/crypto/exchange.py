"""Secure key exchange protocol between peers."""

import base64
import os
from typing import Optional

from crypto.keys import KeyManager
from crypto.encryption import MessageEncryption


class KeyExchange:
    """Manages secure session key exchange between peers."""

    def __init__(self, key_manager: KeyManager):
        """Initialize key exchange.

        Args:
            key_manager: KeyManager instance for RSA operations
        """
        self.key_manager = key_manager
        self.session_keys: dict[str, MessageEncryption] = {}  # peer_id -> MessageEncryption

    def create_key_exchange_request(self, peer_public_key_b64: str) -> tuple[bytes, str]:
        """Create a key exchange request with encrypted session key.

        Args:
            peer_public_key_b64: Peer's RSA public key (base64)

        Returns:
            Tuple of (session_key_bytes, encrypted_session_key_b64)
        """
        # Generate new AES session key
        session_key = MessageEncryption.generate_session_key()

        # Encrypt session key with peer's public key
        encrypted_key = self.key_manager.encrypt_with_public_key(
            session_key,
            peer_public_key_b64
        )

        # Encode to base64 for transmission
        encrypted_key_b64 = base64.b64encode(encrypted_key).decode('utf-8')

        return session_key, encrypted_key_b64

    def generate_nonce(self) -> str:
        """Generate a random nonce for replay protection.

        Returns:
            Base64 encoded 16-byte nonce
        """
        nonce = os.urandom(16)
        return base64.b64encode(nonce).decode('utf-8')

    def process_key_exchange_response(self, encrypted_session_key_b64: str) -> bytes:
        """Process incoming key exchange and decrypt session key.

        Args:
            encrypted_session_key_b64: Encrypted session key (base64)

        Returns:
            Decrypted session key bytes
        """
        # Decode from base64
        encrypted_key = base64.b64decode(encrypted_session_key_b64)

        # Decrypt with our private key
        session_key = self.key_manager.decrypt_with_private_key(encrypted_key)

        return session_key

    def establish_session(self, peer_id: str, session_key: bytes) -> MessageEncryption:
        """Establish an encryption session with a peer.

        Args:
            peer_id: Peer's user ID
            session_key: 32-byte AES session key

        Returns:
            MessageEncryption instance for this session
        """
        encryption = MessageEncryption(session_key)
        self.session_keys[peer_id] = encryption
        return encryption

    def get_session(self, peer_id: str) -> Optional[MessageEncryption]:
        """Get existing encryption session with a peer.

        Args:
            peer_id: Peer's user ID

        Returns:
            MessageEncryption instance or None if no session exists
        """
        return self.session_keys.get(peer_id)

    def has_session(self, peer_id: str) -> bool:
        """Check if session exists with peer.

        Args:
            peer_id: Peer's user ID

        Returns:
            True if session established
        """
        return peer_id in self.session_keys

    def remove_session(self, peer_id: str) -> None:
        """Remove session with peer (on disconnect).

        Args:
            peer_id: Peer's user ID
        """
        if peer_id in self.session_keys:
            del self.session_keys[peer_id]
