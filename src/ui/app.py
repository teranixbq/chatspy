"""Main ChatSpy Textual application."""

import asyncio
import logging
from textual.app import App

from ui.theme import get_aura_theme
from ui.screens.setup import SetupScreen
from ui.screens.lobby import LobbyScreen
from core.config import get_config, set_config
from core.user import LocalUser, User
from crypto.keys import KeyManager
from crypto.exchange import KeyExchange
from network.discovery import DiscoveryService
from network.transport import TransportServer
from network.peer import PeerManager
from network.protocol import MessageBuilder

logger = logging.getLogger(__name__)


class ChatSpyApp(App):
    """ChatSpy main application."""

    CSS = get_aura_theme()

    def __init__(self):
        """Initialize the application."""
        super().__init__()
        self.config = get_config()
        self.local_user: LocalUser | None = None
        self.key_manager: KeyManager | None = None
        self.key_exchange: KeyExchange | None = None
        self.peer_manager: PeerManager | None = None
        self.discovery_service: DiscoveryService | None = None
        self.transport_server: TransportServer | None = None
        self.lobby_screen: LobbyScreen | None = None

    async def on_mount(self) -> None:
        """Handle app mount - show setup or lobby."""
        # Check if user is configured
        if not self.config.username or not self.config.user_id:
            # Show setup screen
            await self.push_screen(SetupScreen(self._on_setup_complete))
        else:
            # Load existing user
            await self._initialize_user()
            await self._start_services()
            await self._show_lobby()

    def _on_setup_complete(self, username: str) -> None:
        """Handle setup completion.

        Args:
            username: Chosen username
        """
        import uuid

        # Generate user ID
        user_id = str(uuid.uuid4())

        # Update config
        self.config.username = username
        self.config.user_id = user_id
        self.config.save_to_file()
        set_config(self.config)

        # Close setup screen and initialize
        self.pop_screen()
        asyncio.create_task(self._initialize_and_start())

    async def _initialize_and_start(self) -> None:
        """Initialize user and start services."""
        await self._initialize_user()
        await self._start_services()
        await self._show_lobby()

    async def _initialize_user(self) -> None:
        """Initialize local user and crypto."""
        # Initialize key manager
        self.key_manager = KeyManager(self.config.keys_dir)

        # Load or generate keys
        if self.key_manager.keys_exist():
            private_b64, public_b64 = self.key_manager.load_keypair()
            logger.info("Loaded existing keypair")
        else:
            private_b64, public_b64 = self.key_manager.generate_keypair()
            self.key_manager.save_keypair(private_b64, public_b64)
            logger.info("Generated new keypair")

        # Create local user
        self.local_user = LocalUser(
            user_id=self.config.user_id,
            username=self.config.username,
            public_key=public_b64,
            private_key=private_b64,
            port=self.config.listen_port,
            is_online=True,
        )

        # Initialize key exchange
        self.key_exchange = KeyExchange(self.key_manager)

        # Initialize peer manager
        self.peer_manager = PeerManager(self.key_exchange, self.local_user.user_id)

        logger.info(f"Initialized user: {self.local_user.username} ({self.local_user.user_id[:8]})")

    async def _start_services(self) -> None:
        """Start network services."""
        # Start transport server for incoming connections
        self.transport_server = TransportServer(
            host="0.0.0.0",
            port=self.config.listen_port,
            on_connection=self._handle_incoming_connection,
        )
        await self.transport_server.start()

        # Start discovery service
        self.discovery_service = DiscoveryService(
            user_id=self.local_user.user_id,
            username=self.local_user.username,
            public_key=self.local_user.public_key,
            port=self.config.listen_port,
            on_peer_discovered=self._on_peer_discovered,
            on_peer_lost=self._on_peer_lost,
        )
        await self.discovery_service.start()

        logger.info("Network services started")

    async def _show_lobby(self) -> None:
        """Show the main lobby screen."""
        self.lobby_screen = LobbyScreen(self.local_user.username)
        self.lobby_screen.on_message_send = self._on_message_send
        self.lobby_screen.on_peer_selected = self._on_peer_selected
        await self.push_screen(self.lobby_screen)
        self.lobby_screen.set_connection_status("Connected")

    async def _handle_incoming_connection(self, connection) -> None:
        """Handle incoming P2P connection.

        Args:
            connection: Incoming connection
        """
        # We need to wait for peer identification via message
        # For now, just handle it in peer manager
        # In a real implementation, first message should be peer info
        logger.info("Incoming connection received")

    def _on_peer_discovered(self, user: User) -> None:
        """Handle peer discovery.

        Args:
            user: Discovered peer
        """
        logger.info(f"Peer discovered: {user.username}")
        if self.lobby_screen:
            self.lobby_screen.add_peer(user)
            self.lobby_screen.add_system_message(f"{user.username} is online", "info")

    def _on_peer_lost(self, user_id: str) -> None:
        """Handle peer loss.

        Args:
            user_id: Lost peer's user ID
        """
        logger.info(f"Peer lost: {user_id[:8]}")
        if self.lobby_screen:
            self.lobby_screen.remove_peer(user_id)

    async def _on_peer_selected(self, user: User) -> None:
        """Handle peer selection.

        Args:
            user: Selected peer
        """
        try:
            # Connect to peer
            peer_conn = await self.peer_manager.connect_to_peer(user)

            # Setup message callback
            async def on_message(sender: str, content: str):
                if self.lobby_screen:
                    self.lobby_screen.add_received_message(sender, content)

            peer_conn.on_message = on_message

            if self.lobby_screen:
                self.lobby_screen.add_system_message(f"Encrypted connection established with {user.username}", "info")

        except Exception as e:
            logger.error(f"Failed to connect to peer: {e}")
            if self.lobby_screen:
                self.lobby_screen.add_system_message(f"Failed to connect: {e}", "error")

    async def _on_message_send(self, peer_id: str, message: str) -> None:
        """Handle message send.

        Args:
            peer_id: Target peer ID
            message: Message content
        """
        peer_conn = self.peer_manager.get_peer_connection(peer_id)
        if not peer_conn:
            if self.lobby_screen:
                self.lobby_screen.add_system_message("Not connected to peer", "error")
            return

        try:
            await peer_conn.send_message(self.local_user.username, message)
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            if self.lobby_screen:
                self.lobby_screen.add_system_message(f"Failed to send message: {e}", "error")

    async def on_unmount(self) -> None:
        """Handle app shutdown."""
        logger.info("Shutting down...")

        # Stop services
        if self.discovery_service:
            await self.discovery_service.stop()

        if self.transport_server:
            await self.transport_server.stop()

        if self.peer_manager:
            await self.peer_manager.disconnect_all()

        logger.info("Shutdown complete")


def run_app() -> None:
    """Run the ChatSpy application."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        filename="chatspy.log",
    )

    # Run app
    app = ChatSpyApp()
    app.run()
