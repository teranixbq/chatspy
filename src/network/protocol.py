"""Message serialization and protocol handling."""

import msgpack
from typing import Any, Dict, Optional
from datetime import datetime

from core.message import (
    Message,
    MessageType,
    DiscoveryMessage,
    KeyExchangeMessage,
    ChatMessage,
    ChatPayload,
    PingMessage,
    PongMessage,
)


class Protocol:
    """Handles message serialization/deserialization with msgpack."""

    @staticmethod
    def serialize(message: Message) -> bytes:
        """Serialize a message to bytes using msgpack.

        Args:
            message: Message object to serialize

        Returns:
            Serialized message bytes
        """
        # Convert Pydantic model to dict
        data = message.model_dump(mode='json')
        
        # Encode with msgpack
        return msgpack.packb(data, use_bin_type=True)

    @staticmethod
    def deserialize(data: bytes) -> Message:
        """Deserialize bytes to a message object.

        Args:
            data: Serialized message bytes

        Returns:
            Message object

        Raises:
            ValueError: If message type is unknown or deserialization fails
        """
        try:
            # Decode with msgpack
            raw_data = msgpack.unpackb(data, raw=False)
            
            # Get message type
            msg_type = raw_data.get('type')
            
            if not msg_type:
                raise ValueError("Message missing 'type' field")
            
            # Map to appropriate message class
            message_classes = {
                MessageType.DISCOVER: DiscoveryMessage,
                MessageType.KEY_EXCHANGE: KeyExchangeMessage,
                MessageType.CHAT: ChatMessage,
                MessageType.PING: PingMessage,
                MessageType.PONG: PongMessage,
            }
            
            message_class = message_classes.get(msg_type)
            if not message_class:
                raise ValueError(f"Unknown message type: {msg_type}")
            
            # Create message instance from dict
            return message_class(**raw_data)
            
        except Exception as e:
            raise ValueError(f"Failed to deserialize message: {e}")

    @staticmethod
    def serialize_payload(payload: ChatPayload) -> bytes:
        """Serialize chat payload for encryption.

        Args:
            payload: ChatPayload to serialize

        Returns:
            Serialized payload bytes
        """
        data = payload.model_dump(mode='json')
        return msgpack.packb(data, use_bin_type=True)

    @staticmethod
    def deserialize_payload(data: bytes) -> ChatPayload:
        """Deserialize bytes to chat payload.

        Args:
            data: Serialized payload bytes

        Returns:
            ChatPayload object
        """
        raw_data = msgpack.unpackb(data, raw=False)
        return ChatPayload(**raw_data)


class MessageBuilder:
    """Helper class to build various message types."""

    @staticmethod
    def discovery(user_id: str, username: str, public_key: str, port: int = 5001) -> DiscoveryMessage:
        """Build a discovery message.

        Args:
            user_id: User's unique ID
            username: User's display name
            public_key: Base64 RSA public key
            port: P2P listening port

        Returns:
            DiscoveryMessage
        """
        return DiscoveryMessage(
            user_id=user_id,
            username=username,
            public_key=public_key,
            port=port,
        )

    @staticmethod
    def key_exchange(session_key: str, nonce: str, sender_id: str) -> KeyExchangeMessage:
        """Build a key exchange message.

        Args:
            session_key: Base64 encrypted session key
            nonce: Base64 nonce for replay protection
            sender_id: Sender's user ID

        Returns:
            KeyExchangeMessage
        """
        return KeyExchangeMessage(
            session_key=session_key,
            nonce=nonce,
            sender_id=sender_id,
        )

    @staticmethod
    def chat(sender_id: str, encrypted_payload: str, iv: str, signature: str) -> ChatMessage:
        """Build a chat message.

        Args:
            sender_id: Sender's user ID
            encrypted_payload: Base64 encrypted message content
            iv: Base64 initialization vector
            signature: Base64 HMAC signature

        Returns:
            ChatMessage
        """
        return ChatMessage(
            sender_id=sender_id,
            encrypted_payload=encrypted_payload,
            iv=iv,
            signature=signature,
        )

    @staticmethod
    def chat_payload(sender: str, content: str, msg_id: Optional[str] = None) -> ChatPayload:
        """Build a chat payload (to be encrypted).

        Args:
            sender: Sender's username
            content: Message text
            msg_id: Optional message ID (auto-generated if not provided)

        Returns:
            ChatPayload
        """
        if msg_id:
            return ChatPayload(sender=sender, content=content, msg_id=msg_id)
        return ChatPayload(sender=sender, content=content)

    @staticmethod
    def ping(sender_id: str) -> PingMessage:
        """Build a ping message.

        Args:
            sender_id: Sender's user ID

        Returns:
            PingMessage
        """
        return PingMessage(sender_id=sender_id)

    @staticmethod
    def pong(sender_id: str) -> PongMessage:
        """Build a pong message.

        Args:
            sender_id: Sender's user ID

        Returns:
            PongMessage
        """
        return PongMessage(sender_id=sender_id)
