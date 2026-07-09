"""Async TCP socket transport layer."""

import asyncio
import logging
from typing import Optional, Callable, Awaitable

from network.protocol import Protocol
from core.message import Message

logger = logging.getLogger(__name__)


class Connection:
    """Represents a TCP connection to a peer."""

    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Initialize connection.

        Args:
            reader: Stream reader
            writer: Stream writer
        """
        self.reader = reader
        self.writer = writer
        self.closed = False

    async def send(self, message: Message) -> None:
        """Send a message over the connection.

        Args:
            message: Message to send

        Raises:
            ConnectionError: If connection is closed or send fails
        """
        if self.closed:
            raise ConnectionError("Connection is closed")

        try:
            # Serialize message
            data = Protocol.serialize(message)

            # Send length prefix (4 bytes, big-endian)
            length = len(data)
            self.writer.write(length.to_bytes(4, byteorder='big'))

            # Send message data
            self.writer.write(data)
            await self.writer.drain()

            logger.debug(f"Sent message type={message.type}, size={length} bytes")

        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            await self.close()
            raise ConnectionError(f"Send failed: {e}")

    async def receive(self) -> Optional[Message]:
        """Receive a message from the connection.

        Returns:
            Received message or None if connection closed

        Raises:
            ConnectionError: If receive fails
        """
        if self.closed:
            return None

        try:
            # Read length prefix (4 bytes)
            length_bytes = await self.reader.readexactly(4)
            length = int.from_bytes(length_bytes, byteorder='big')

            # Validate length (max 10MB)
            if length > 10 * 1024 * 1024:
                raise ValueError(f"Message too large: {length} bytes")

            # Read message data
            data = await self.reader.readexactly(length)

            # Deserialize message
            message = Protocol.deserialize(data)

            logger.debug(f"Received message type={message.type}, size={length} bytes")
            return message

        except asyncio.IncompleteReadError:
            # Connection closed by peer
            logger.debug("Connection closed by peer")
            await self.close()
            return None

        except Exception as e:
            logger.error(f"Failed to receive message: {e}")
            await self.close()
            raise ConnectionError(f"Receive failed: {e}")

    async def close(self) -> None:
        """Close the connection."""
        if not self.closed:
            self.closed = True
            try:
                self.writer.close()
                await self.writer.wait_closed()
                logger.debug("Connection closed")
            except Exception as e:
                logger.error(f"Error closing connection: {e}")

    def get_peer_address(self) -> tuple[str, int]:
        """Get peer's address.

        Returns:
            Tuple of (host, port)
        """
        return self.writer.get_extra_info('peername')


class TransportServer:
    """Async TCP server for incoming connections."""

    def __init__(self, host: str, port: int, on_connection: Callable[[Connection], Awaitable[None]]):
        """Initialize transport server.

        Args:
            host: Host to bind to (e.g., '0.0.0.0')
            port: Port to listen on
            on_connection: Async callback for new connections
        """
        self.host = host
        self.port = port
        self.on_connection = on_connection
        self.server: Optional[asyncio.Server] = None

    async def start(self) -> None:
        """Start the server."""
        self.server = await asyncio.start_server(
            self._handle_client,
            self.host,
            self.port,
        )
        logger.info(f"Server listening on {self.host}:{self.port}")

    async def _handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        """Handle incoming client connection.

        Args:
            reader: Stream reader
            writer: Stream writer
        """
        connection = Connection(reader, writer)
        peer_addr = connection.get_peer_address()
        logger.info(f"New connection from {peer_addr}")

        try:
            await self.on_connection(connection)
        except Exception as e:
            logger.error(f"Error handling connection from {peer_addr}: {e}")
        finally:
            await connection.close()

    async def stop(self) -> None:
        """Stop the server."""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            logger.info("Server stopped")


class TransportClient:
    """Async TCP client for outgoing connections."""

    @staticmethod
    async def connect(host: str, port: int, timeout: float = 5.0) -> Connection:
        """Connect to a remote peer.

        Args:
            host: Remote host
            port: Remote port
            timeout: Connection timeout in seconds

        Returns:
            Connection object

        Raises:
            ConnectionError: If connection fails
        """
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port),
                timeout=timeout,
            )
            logger.info(f"Connected to {host}:{port}")
            return Connection(reader, writer)

        except asyncio.TimeoutError:
            raise ConnectionError(f"Connection timeout to {host}:{port}")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to {host}:{port}: {e}")
