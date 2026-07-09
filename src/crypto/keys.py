"""RSA key generation and management."""

import base64
from pathlib import Path
from typing import Tuple, Optional

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend


class KeyManager:
    """Manages RSA keypairs for user identity and encryption."""

    def __init__(self, keys_dir: Path):
        """Initialize key manager.

        Args:
            keys_dir: Directory to store key files
        """
        self.keys_dir = keys_dir
        self.private_key_path = keys_dir / "private_key.pem"
        self.public_key_path = keys_dir / "public_key.pem"
        self._private_key = None
        self._public_key = None

    def generate_keypair(self) -> Tuple[str, str]:
        """Generate a new RSA keypair.

        Returns:
            Tuple of (private_key_pem, public_key_pem) as base64 strings
        """
        # Generate 2048-bit RSA key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public_key = private_key.public_key()

        # Serialize to PEM format
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        self._private_key = private_key
        self._public_key = public_key

        return (
            base64.b64encode(private_pem).decode('utf-8'),
            base64.b64encode(public_pem).decode('utf-8')
        )

    def save_keypair(self, private_key_b64: str, public_key_b64: str) -> None:
        """Save keypair to disk.

        Args:
            private_key_b64: Base64 encoded private key PEM
            public_key_b64: Base64 encoded public key PEM
        """
        self.keys_dir.mkdir(parents=True, exist_ok=True)

        # Decode from base64
        private_pem = base64.b64decode(private_key_b64)
        public_pem = base64.b64decode(public_key_b64)

        # Write to files with restricted permissions
        self.private_key_path.write_bytes(private_pem)
        self.private_key_path.chmod(0o600)  # Read/write for owner only

        self.public_key_path.write_bytes(public_pem)
        self.public_key_path.chmod(0o644)  # Read for all, write for owner

    def load_keypair(self) -> Tuple[str, str]:
        """Load keypair from disk.

        Returns:
            Tuple of (private_key_b64, public_key_b64)

        Raises:
            FileNotFoundError: If keys don't exist
        """
        if not self.private_key_path.exists() or not self.public_key_path.exists():
            raise FileNotFoundError("Keys not found. Generate new keys first.")

        private_pem = self.private_key_path.read_bytes()
        public_pem = self.public_key_path.read_bytes()

        # Load keys into memory
        self._private_key = serialization.load_pem_private_key(
            private_pem,
            password=None,
            backend=default_backend()
        )
        self._public_key = serialization.load_pem_public_key(
            public_pem,
            backend=default_backend()
        )

        return (
            base64.b64encode(private_pem).decode('utf-8'),
            base64.b64encode(public_pem).decode('utf-8')
        )

    def keys_exist(self) -> bool:
        """Check if keypair files exist.

        Returns:
            True if both keys exist
        """
        return self.private_key_path.exists() and self.public_key_path.exists()

    def encrypt_with_public_key(self, data: bytes, public_key_b64: str) -> bytes:
        """Encrypt data with a public key (for key exchange).

        Args:
            data: Data to encrypt
            public_key_b64: Base64 encoded public key PEM

        Returns:
            Encrypted data
        """
        public_pem = base64.b64decode(public_key_b64)
        public_key = serialization.load_pem_public_key(
            public_pem,
            backend=default_backend()
        )

        encrypted = public_key.encrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return encrypted

    def decrypt_with_private_key(self, encrypted_data: bytes) -> bytes:
        """Decrypt data with private key.

        Args:
            encrypted_data: Encrypted data

        Returns:
            Decrypted data

        Raises:
            ValueError: If private key not loaded
        """
        if self._private_key is None:
            raise ValueError("Private key not loaded. Call load_keypair() first.")

        decrypted = self._private_key.decrypt(
            encrypted_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return decrypted

    def get_fingerprint(self, public_key_b64: str) -> str:
        """Generate a fingerprint from a public key.

        Args:
            public_key_b64: Base64 encoded public key PEM

        Returns:
            Fingerprint as hex string (e.g., "A7:3F:2D:8B...")
        """
        public_pem = base64.b64decode(public_key_b64)
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(public_pem)
        hash_bytes = digest.finalize()

        # Take first 16 bytes and format as hex with colons
        fingerprint = ':'.join(f'{b:02X}' for b in hash_bytes[:16])
        return fingerprint
