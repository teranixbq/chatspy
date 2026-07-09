"""Message models for ChatSpy."""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class MessageType(str, Enum):
    """Types of messages in the protocol."""

    DISCOVER = "discover"  # mDNS discovery broadcast
    KEY_EXCHANGE = "key_exchange"  # Secure key exchange
    CHAT = "message"  # Encrypted chat message
    SYSTEM = "system"  # System notification
    PING = "ping"  # Keep-alive
    PONG = "pong"  # Keep-alive response


class Message(BaseModel):
    """Base message model."""

    msg_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique message ID")
    type: MessageType = Field(..., description="Message type")
    timestamp: datetime = Field(default_factory=datetime.now, description="Message timestamp")


class DiscoveryMessage(Message):
    """mDNS discovery broadcast message."""

    type: MessageType = Field(default=MessageType.DISCOVER, frozen=True)
    user_id: str = Field(..., description="Sender's user ID")
    username: str = Field(..., description="Sender's username")
    public_key: str = Field(..., description="Base64 RSA public key")
    port: int = Field(default=5001, description="P2P listening port")


class KeyExchangeMessage(Message):
    """Secure session key exchange message."""

    type: MessageType = Field(default=MessageType.KEY_EXCHANGE, frozen=True)
    session_key: str = Field(..., description="Base64 AES session key (RSA encrypted)")
    nonce: str = Field(..., description="Random nonce for replay protection")
    sender_id: str = Field(..., description="Sender's user ID")


class ChatMessage(Message):
    """Encrypted chat message."""

    type: MessageType = Field(default=MessageType.CHAT, frozen=True)
    sender_id: str = Field(..., description="Sender's user ID")
    encrypted_payload: str = Field(..., description="Base64 encrypted message content")
    iv: str = Field(..., description="Base64 initialization vector for AES")
    signature: str = Field(..., description="Base64 HMAC signature")


class ChatPayload(BaseModel):
    """Decrypted chat message payload."""

    sender: str = Field(..., description="Sender's username")
    content: str = Field(..., description="Message text content")
    msg_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Message ID")


class SystemMessage(Message):
    """System notification message (local only, not sent over network)."""

    type: MessageType = Field(default=MessageType.SYSTEM, frozen=True)
    content: str = Field(..., description="System message content")
    level: str = Field(default="info", description="Message level: info, warning, error")


class PingMessage(Message):
    """Keep-alive ping message."""

    type: MessageType = Field(default=MessageType.PING, frozen=True)
    sender_id: str = Field(..., description="Sender's user ID")


class PongMessage(Message):
    """Keep-alive pong response."""

    type: MessageType = Field(default=MessageType.PONG, frozen=True)
    sender_id: str = Field(..., description="Sender's user ID")
