"""AES encryption and HMAC for message security."""

import base64
import hmac
import hashlib
import os
from typing import Tuple

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


class MessageEncryption:
    """Handles AES-256-GCM encryption for chat messages."""

    def __init__(self, session_key: bytes):
        """Initialize encryption with session key.

        Args:
            session_key: 32-byte AES-256 key
        """
        if len(session_key) != 32:
            raise ValueError("Session key must be 32 bytes for AES-256")
        self.session_key = session_key

    @staticmethod
    def generate_session_key() -> bytes:
        """Generate a random 32-byte AES-256 session key.

        Returns:
            32-byte random key
        """
        return os.urandom(32)

    def encrypt(self, plaintext: str) -> Tuple[str, str, str]:
        """Encrypt a message with AES-256-GCM.

        Args:
            plaintext: Message to encrypt

        Returns:
            Tuple of (encrypted_b64, iv_b64, signature_b64)
        """
        # Generate random 16-byte IV
        iv = os.urandom(16)

        # Convert plaintext to bytes
        plaintext_bytes = plaintext.encode('utf-8')

        # Create AES-GCM cipher
        cipher = Cipher(
            algorithms.AES(self.session_key),
            modes.GCM(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()

        # Encrypt
        ciphertext = encryptor.update(plaintext_bytes) + encryptor.finalize()

        # Get authentication tag from GCM
        tag = encryptor.tag

        # Combine ciphertext + tag
        encrypted_data = ciphertext + tag

        # Generate HMAC signature for additional integrity
        signature = self._generate_hmac(encrypted_data, iv)

        # Encode to base64
        encrypted_b64 = base64.b64encode(encrypted_data).decode('utf-8')
        iv_b64 = base64.b64encode(iv).decode('utf-8')
        signature_b64 = base64.b64encode(signature).decode('utf-8')

        return encrypted_b64, iv_b64, signature_b64

    def decrypt(self, encrypted_b64: str, iv_b64: str, signature_b64: str) -> str:
        """Decrypt a message with AES-256-GCM.

        Args:
            encrypted_b64: Base64 encrypted data (ciphertext + tag)
            iv_b64: Base64 initialization vector
            signature_b64: Base64 HMAC signature

        Returns:
            Decrypted plaintext

        Raises:
            ValueError: If signature verification fails
        """
        # Decode from base64
        encrypted_data = base64.b64decode(encrypted_b64)
        iv = base64.b64decode(iv_b64)
        signature = base64.b64decode(signature_b64)

        # Verify HMAC signature
        if not self._verify_hmac(encrypted_data, iv, signature):
            raise ValueError("HMAC signature verification failed - message may be tampered")

        # Split ciphertext and tag (GCM tag is 16 bytes)
        ciphertext = encrypted_data[:-16]
        tag = encrypted_data[-16:]

        # Create AES-GCM cipher
        cipher = Cipher(
            algorithms.AES(self.session_key),
            modes.GCM(iv, tag),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()

        # Decrypt
        try:
            plaintext_bytes = decryptor.update(ciphertext) + decryptor.finalize()
            return plaintext_bytes.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Decryption failed: {e}")

    def _generate_hmac(self, data: bytes, iv: bytes) -> bytes:
        """Generate HMAC-SHA256 signature.

        Args:
            data: Data to sign
            iv: Initialization vector

        Returns:
            HMAC signature
        """
        h = hmac.new(self.session_key, digestmod=hashlib.sha256)
        h.update(iv)
        h.update(data)
        return h.digest()

    def _verify_hmac(self, data: bytes, iv: bytes, signature: bytes) -> bool:
        """Verify HMAC-SHA256 signature.

        Args:
            data: Data to verify
            iv: Initialization vector
            signature: HMAC signature to verify

        Returns:
            True if signature is valid
        """
        expected_signature = self._generate_hmac(data, iv)
        return hmac.compare_digest(expected_signature, signature)
