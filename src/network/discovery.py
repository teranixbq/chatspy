"""mDNS service discovery using Zeroconf."""

import asyncio
import logging
import socket
from typing import Callable, Optional
from zeroconf import ServiceBrowser, ServiceInfo, Zeroconf
from zeroconf.asyncio import AsyncZeroconf, AsyncServiceBrowser

from core.user import User

logger = logging.getLogger(__name__)

SERVICE_TYPE = "_chatspy._tcp.local."


class DiscoveryService:
    """Handles peer discovery via mDNS/Zeroconf."""

    def __init__(
        self,
        user_id: str,
        username: str,
        public_key: str,
        port: int,
        on_peer_discovered: Callable[[User], None],
        on_peer_lost: Callable[[str], None],
    ):
        """Initialize discovery service.

        Args:
            user_id: Local user's ID
            username: Local user's display name
            public_key: Local user's public key (base64)
            port: P2P listening port
            on_peer_discovered: Callback when peer is discovered
            on_peer_lost: Callback when peer is lost (receives user_id)
        """
        self.user_id = user_id
        self.username = username
        self.public_key = public_key
        self.port = port
        self.on_peer_discovered = on_peer_discovered
        self.on_peer_lost = on_peer_lost

        self.zeroconf: Optional[AsyncZeroconf] = None
        self.browser: Optional[AsyncServiceBrowser] = None
        self.service_info: Optional[ServiceInfo] = None
        self.discovered_peers: dict[str, User] = {}  # service_name -> User

    async def start(self) -> None:
        """Start discovery service (broadcast and listen)."""
        self.zeroconf = AsyncZeroconf()

        # Register our service
        await self._register_service()

        # Start browsing for peers
        self.browser = AsyncServiceBrowser(
            self.zeroconf.zeroconf,
            SERVICE_TYPE,
            handlers=[self._on_service_state_change],
        )

        logger.info(f"Discovery service started for {self.username} ({self.user_id[:8]})")

    async def _register_service(self) -> None:
        """Register this instance as a service."""
        # Get local IP address
        local_ip = self._get_local_ip()

        # Create service name: username.user_id._chatspy._tcp.local.
        service_name = f"{self.username}.{self.user_id[:8]}.{SERVICE_TYPE}"

        # Service properties (key-value pairs)
        # Note: mDNS properties have max 255 bytes per value
        # Public key is too large, so we don't include it here
        # Peers will exchange keys via TCP after connection
        properties = {
            b"user_id": self.user_id.encode('utf-8'),
            b"username": self.username.encode('utf-8'),
        }

        # Create service info
        self.service_info = ServiceInfo(
            SERVICE_TYPE,
            service_name,
            addresses=[socket.inet_aton(local_ip)],
            port=self.port,
            properties=properties,
        )

        # Register service
        await self.zeroconf.async_register_service(self.service_info)
        logger.info(f"Registered service: {service_name} at {local_ip}:{self.port}")

    def _on_service_state_change(
        self,
        zeroconf: Zeroconf,
        service_type: str,
        name: str,
        state_change,
    ) -> None:
        """Handle service state changes.

        Args:
            zeroconf: Zeroconf instance
            service_type: Service type
            name: Service name
            state_change: State change enum
        """
        from zeroconf import ServiceStateChange

        if state_change is ServiceStateChange.Added:
            asyncio.create_task(self._handle_service_added(zeroconf, service_type, name))
        elif state_change is ServiceStateChange.Removed:
            self._handle_service_removed(name)

    async def _handle_service_added(self, zeroconf: Zeroconf, service_type: str, name: str) -> None:
        """Handle discovered service.

        Args:
            zeroconf: Zeroconf instance
            service_type: Service type
            name: Service name
        """
        # Get service info
        info = zeroconf.get_service_info(service_type, name)
        if not info:
            logger.warning(f"Could not get info for service: {name}")
            return

        # Extract properties
        props = info.properties
        user_id = props.get(b"user_id", b"").decode('utf-8')
        username = props.get(b"username", b"").decode('utf-8')
        # Public key will be exchanged via TCP, not mDNS
        public_key = ""  # Placeholder, will be filled during key exchange

        # Ignore our own service
        if user_id == self.user_id:
            return

        # Get IP address
        if info.addresses:
            ip_address = socket.inet_ntoa(info.addresses[0])
        else:
            logger.warning(f"No address for service: {name}")
            return

        # Create User object
        user = User(
            user_id=user_id,
            username=username,
            public_key=public_key,
            ip_address=ip_address,
            port=info.port,
            is_online=True,
        )

        # Store and notify
        self.discovered_peers[name] = user
        logger.info(f"Discovered peer: {username} ({user_id[:8]}) at {ip_address}:{info.port}")

        # Call callback
        self.on_peer_discovered(user)

    def _handle_service_removed(self, name: str) -> None:
        """Handle service removal.

        Args:
            name: Service name
        """
        if name in self.discovered_peers:
            user = self.discovered_peers[name]
            logger.info(f"Peer lost: {user.username} ({user.user_id[:8]})")
            del self.discovered_peers[name]

            # Call callback
            self.on_peer_lost(user.user_id)

    async def stop(self) -> None:
        """Stop discovery service."""
        if self.browser:
            await self.browser.async_cancel()

        if self.service_info and self.zeroconf:
            await self.zeroconf.async_unregister_service(self.service_info)

        if self.zeroconf:
            await self.zeroconf.async_close()

        logger.info("Discovery service stopped")

    @staticmethod
    def _get_local_ip() -> str:
        """Get local IP address.

        Returns:
            Local IP address as string
        """
        try:
            # Create a socket to determine the local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception:
            # Fallback to localhost
            return "127.0.0.1"
