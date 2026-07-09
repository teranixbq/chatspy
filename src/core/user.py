"""User and identity models."""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class User(BaseModel):
    """Represents a ChatSpy user."""

    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique user identifier")
    username: str = Field(..., min_length=1, max_length=50, description="Display name")
    public_key: Optional[str] = Field(default=None, description="Base64 encoded RSA public key")
    ip_address: Optional[str] = Field(default=None, description="Last known IP address")
    port: int = Field(default=5001, description="P2P listening port")
    last_seen: datetime = Field(default_factory=datetime.now, description="Last activity timestamp")
    is_online: bool = Field(default=False, description="Current online status")

    def __str__(self) -> str:
        return f"{self.username} ({self.user_id[:8]})"

    def __repr__(self) -> str:
        return f"User(id={self.user_id[:8]}, username={self.username}, online={self.is_online})"


class LocalUser(User):
    """Represents the local user with private key information."""

    private_key: Optional[str] = Field(default=None, description="Base64 encoded RSA private key")

    def to_user(self) -> User:
        """Convert to regular User (without private key)."""
        return User(
            user_id=self.user_id,
            username=self.username,
            public_key=self.public_key,
            ip_address=self.ip_address,
            port=self.port,
            last_seen=self.last_seen,
            is_online=self.is_online,
        )
