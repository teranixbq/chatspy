"""Peer connection management."""

import asyncio
import logging
from typing import Optional, Callable, Awaitable
from datetime import datetime

from network.transport import Connection, TransportClient
from network.protocol import Protocol, MessageBuilder
from core.user import User
from core.message import Message, MessageType, ChatMessage, KeyExchangeMessage
from crypto.exchange import KeyExchange

logger = logging.getLogger(__name__)


class PeerConnection:
    """Manages connection and communication with a single peer."""

    def __init__(
        self,
        peer: User,
        connection: Connection,
        key_exchange: KeyExchange,
        local_user_id: str,
    ):
        """Initialize peer connection.

        Args:
            peer: Peer user information
            connection: TCP connection to peer
            key_exchange: Key exchange handler
            local_user_id: Local user's ID
        """
        self.peer = peer
        self.connection = connection
        self.key_exchange = key_exchange
        self.local_user_id = local_user_id
        self.session_established = False
        self._receive_task: Optional[asyncio.Task] = None
        self._ping_task: Optional[asyncio.Task] = None
        self.on_message: Optional[Callable[[str, str], Awaitable[None]]] = None
        self.on_disconnect: Optional[Callable[[], Awaitable[None]]] = None

    async def start(self) -> None:
        """Start peer connection (initiate key exchange and message loop)."""
        try:
            # Initiate key exchange
            await self._initiate_key_exchange()

            # Start receive loop
            self._receive_task = asyncio.create_task(self._receive_loop())

            # Start ping loop (keep-alive)
            self._ping_task = asyncio.create_task(self._ping_loop())

            logger.info(f"Started connection with {self.peer.username}")

        except Exception as e:
            logger.error(f"Failed to start connection with {self.peer.username}: {e}")
            await self.disconnect()

    async def _initiate_key_exchange(self) -> None:
        """Initiate secure key exchange with peer."""
        # Create session key and encrypt with peer's public key
        session_key, encrypted_key_b64 = self.key_exchange.create_key_exchange_request(
            self.peer.public_key
        )

        # Generate nonce
        nonce = self.key_exchange.generate_nonce()

        # Build key exchange message
        msg = MessageBuilder.key_exchange(
            session_key=encrypted_key_b64,
            nonce=nonce,
            sender_id=self.local_user_id,
        )

        # Send to peer
        await self.connection.send(msg)

        # Establish local session
        self.key_exchange.establish_session(self.peer.user_id, session_key)
        self.session_established = True

        logger.info(f"Key exchange initiated with {self.peer.username}")

    async def _receive_loop(self) -> None:
        """Receive and process messages from peer."""
        while not self.connection.closed:
            try:
                message = await self.connection.receive()
                if message is None:
                    # Connection closed
                    break

                await self._handle_message(message)

            except Exception as e:
                logger.error(f"Error in receive loop: {e}")
                break

        # Connection closed
        await self.disconnect()

    async def _handle_message(self, message: Message) -> None:
        """Handle incoming message.

        Args:
            message: Received message
        """
        if message.type == MessageType.KEY_EXCHANGE:
            await self._handle_key_exchange(message)

        elif message.type == MessageType.CHAT:
            await self._handle_chat_message(message)

        elif message.type == MessageType.PING:
            await self._handle_ping()

        elif message.type == MessageType.PONG:
            # Update last seen
            self.peer.last_seen = datetime.now()

    async def _handle_key_exchange(self, message: KeyExchangeMessage) -> None:
        """Handle incoming key exchange.

        Args:
            message: Key exchange message
        """
        try:
            # Decrypt session key with our private key
            session_key = self.key_exchange.process_key_exchange_response(
                message.session_key
            )

            # Establish session
            self.key_exchange.establish_session(message.sender_id, session_key)
            self.session_established = True

            logger.info(f"Key exchange completed with {self.peer.username}")

        except Exception as e:
            logger.error(f"Key exchange failed: {e}")
            await self.disconnect()

    async def _handle_chat_message(self, message: ChatMessage) -> None:
        """Handle incoming chat message.

        Args:
            message: Chat message
        """
        if not self.session_established:
            logger.warning("Received chat message before session established")
            return

        try:
            # Get encryption session
            encryption = self.key_exchange.get_session(message.sender_id)
            if not encryption:
                logger.error("No encryption session found")
                return

            # Decrypt message
            decrypted_json = encryption.decrypt(
                message.encrypted_payload,
                message.iv,
                message.signature,
            )

            # Deserialize payload
            payload = Protocol.deserialize_payload(decrypted_json.encode('utf-8'))

            logger.debug(f"Received message from {payload.sender}: {payload.content}")

            # Call callback if set
            if self.on_message:
                await self.on_message(payload.sender, payload.content)

        except Exception as e:
            logger.error(f"Failed to decrypt message: {e}")

    async def _handle_ping(self) -> None:
        """Handle ping message (send pong response)."""
        pong = MessageBuilder.pong(self.local_user_id)
        await self.connection.send(pong)
        self.peer.last_seen = datetime.now()

    async def _ping_loop(self) -> None:
        """Send periodic ping messages for keep-alive."""
        while not self.connection.closed:
            await asyncio.sleep(30)  # Ping every 30 seconds
            try:
                ping = MessageBuilder.ping(self.local_user_id)
                await self.connection.send(ping)
            except Exception as e:
                logger.error(f"Failed to send ping: {e}")
                break

    async def send_message(self, sender_username: str, content: str) -> None:
        """Send an encrypted chat message to peer.

        Args:
            sender_username: Sender's username
            content: Message content

        Raises:
            RuntimeError: If session not established
        """
        if not self.session_established:
            raise RuntimeError("Session not established, cannot send message")

        # Get encryption session
        encryption = self.key_exchange.get_session(self.peer.user_id)
        if not encryption:
            raise RuntimeError("No encryption session found")

        # Create payload
        payload = MessageBuilder.chat_payload(sender_username, content)

        # Serialize payload
        payload_bytes = Protocol.serialize_payload(payload)

        # Encrypt
        encrypted_b64, iv_b64, signature_b64 = encryption.encrypt(payload_bytes.decode('utf-8'))

        # Build chat message
        msg = MessageBuilder.chat(
            sender_id=self.local_user_id,
            encrypted_payload=encrypted_b64,
            iv=iv_b64,
            signature=signature_b64,
        )

        # Send
        await self.connection.send(msg)
        logger.debug(f"Sent message to {self.peer.username}")

    async def disconnect(self) -> None:
        """Disconnect from peer."""
        if self._receive_task and not self._receive_task.done():
            self._receive_task.cancel()

        if self._ping_task and not self._ping_task.done():
            self._ping_task.cancel()

        await self.connection.close()

        # Remove session
        self.key_exchange.remove_session(self.peer.user_id)

        logger.info(f"Disconnected from {self.peer.username}")

        # Call callback
        if self.on_disconnect:
            await self.on_disconnect()


class PeerManager:
    """Manages multiple peer connections."""

    def __init__(self, key_exchange: KeyExchange, local_user_id: str):
        """Initialize peer manager.

        Args:
            key_exchange: Key exchange handler
            local_user_id: Local user's ID
        """
        self.key_exchange = key_exchange
        self.local_user_id = local_user_id
        self.peers: dict[str, PeerConnection] = {}  # user_id -> PeerConnection

    async def connect_to_peer(self, peer: User) -> PeerConnection:
        """Connect to a peer.

        Args:
            peer: Peer information

        Returns:
            PeerConnection instance

        Raises:
            ConnectionError: If connection fails
        """
        if peer.user_id in self.peers:
            logger.warning(f"Already connected to {peer.username}")
            return self.peers[peer.user_id]

        try:
            # Establish TCP connection
            connection = await TransportClient.connect(peer.ip_address, peer.port)

            # Create peer connection
            peer_conn = PeerConnection(
                peer=peer,
                connection=connection,
                key_exchange=self.key_exchange,
                local_user_id=self.local_user_id,
            )

            # Setup disconnect callback
            async def on_disconnect():
                if peer.user_id in self.peers:
                    del self.peers[peer.user_id]

            peer_conn.on_disconnect = on_disconnect

            # Start connection
            await peer_conn.start()

            # Store
            self.peers[peer.user_id] = peer_conn

            logger.info(f"Connected to peer: {peer.username}")
            return peer_conn

        except Exception as e:
            logger.error(f"Failed to connect to {peer.username}: {e}")
            raise

    async def handle_incoming_connection(self, connection: Connection, peer: User) -> None:
        """Handle incoming connection from peer.

        Args:
            connection: Established connection
            peer: Peer information
        """
        if peer.user_id in self.peers:
            logger.warning(f"Already connected to {peer.username}")
            await connection.close()
            return

        # Create peer connection
        peer_conn = PeerConnection(
            peer=peer,
            connection=connection,
            key_exchange=self.key_exchange,
            local_user_id=self.local_user_id,
        )

        # Setup disconnect callback
        async def on_disconnect():
            if peer.user_id in self.peers:
                del self.peers[peer.user_id]

        peer_conn.on_disconnect = on_disconnect

        # Store
        self.peers[peer.user_id] = peer_conn

        # Start receive loop (key exchange will be initiated by remote peer)
        peer_conn._receive_task = asyncio.create_task(peer_conn._receive_loop())
        peer_conn._ping_task = asyncio.create_task(peer_conn._ping_loop())

        logger.info(f"Accepted connection from {peer.username}")

    def get_peer_connection(self, user_id: str) -> Optional[PeerConnection]:
        """Get connection to peer.

        Args:
            user_id: Peer's user ID

        Returns:
            PeerConnection or None
        """
        return self.peers.get(user_id)

    async def disconnect_peer(self, user_id: str) -> None:
        """Disconnect from peer.

        Args:
            user_id: Peer's user ID
        """
        peer_conn = self.peers.get(user_id)
        if peer_conn:
            await peer_conn.disconnect()

    async def disconnect_all(self) -> None:
        """Disconnect from all peers."""
        tasks = [peer.disconnect() for peer in self.peers.values()]
        await asyncio.gather(*tasks, return_exceptions=True)
        self.peers.clear()
