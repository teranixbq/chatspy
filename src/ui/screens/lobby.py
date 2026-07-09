"""Main lobby screen with peer list and chat."""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Horizontal, Vertical
from textual.binding import Binding

from ui.widgets.peer_list import PeerList
from ui.widgets.message_list import MessageList
from ui.widgets.input_box import MessageInput
from ui.widgets.status_bar import StatusBar
from core.user import User


class LobbyScreen(Screen):
    """Main screen with peer list and chat interface."""

    BINDINGS = [
        Binding("ctrl+h", "show_help", "Help", show=True),
        Binding("?", "show_help", "Help", show=False),
        Binding("tab", "focus_next", "Next Panel", show=True),
        Binding("i", "focus_input", "Focus Input", show=False),
        Binding("q", "quit", "Quit", show=True),
    ]

    CSS = """
    LobbyScreen {
        background: $background;
    }

    #main-container {
        width: 100%;
        height: 100%;
    }

    #chat-container {
        width: 1fr;
        height: 100%;
    }
    """

    def __init__(self, username: str) -> None:
        """Initialize lobby screen.

        Args:
            username: Current user's username
        """
        super().__init__()
        self.username = username
        self.current_peer: User | None = None
        self.on_message_send = None
        self.on_peer_selected = None

    def compose(self) -> ComposeResult:
        """Compose the lobby screen layout."""
        yield StatusBar()
        with Horizontal(id="main-container"):
            yield PeerList()
            with Vertical(id="chat-container"):
                yield MessageList()
                yield MessageInput()

    def on_mount(self) -> None:
        """Handle screen mount."""
        # Setup status bar
        status_bar = self.query_one(StatusBar)
        status_bar.set_username(self.username)
        status_bar.set_connection_status("Connecting")

        # Setup message input callback
        input_box = self.query_one(MessageInput)
        input_box.set_on_submit(self._on_message_submitted)

    def _on_message_submitted(self, message: str) -> None:
        """Handle message submission.

        Args:
            message: Message text
        """
        if not self.current_peer:
            msg_list = self.query_one(MessageList)
            msg_list.add_system_message("No peer selected", "warning")
            return

        # Add to message list
        msg_list = self.query_one(MessageList)
        msg_list.add_message(self.username, message)

        # Call callback
        if self.on_message_send:
            self.on_message_send(self.current_peer.user_id, message)

    def action_show_help(self) -> None:
        """Show help screen."""
        from .help import HelpScreen
        self.app.push_screen(HelpScreen())

    def action_focus_input(self) -> None:
        """Focus the message input."""
        input_box = self.query_one(MessageInput)
        input_box.focus_input()

    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()

    # Public methods for external control

    def add_peer(self, user: User) -> None:
        """Add a peer to the list.

        Args:
            user: User to add
        """
        peer_list = self.query_one(PeerList)
        peer_list.add_peer(user)
        self._update_peer_count()

    def remove_peer(self, user_id: str) -> None:
        """Remove a peer from the list.

        Args:
            user_id: User ID to remove
        """
        peer_list = self.query_one(PeerList)
        peer_list.remove_peer(user_id)
        self._update_peer_count()

        # Clear chat if this was current peer
        if self.current_peer and self.current_peer.user_id == user_id:
            self.current_peer = None
            msg_list = self.query_one(MessageList)
            msg_list.add_system_message("Peer disconnected", "warning")

    def update_peer_status(self, user_id: str, is_online: bool) -> None:
        """Update peer online status.

        Args:
            user_id: User ID
            is_online: Whether user is online
        """
        peer_list = self.query_one(PeerList)
        peer_list.update_peer_status(user_id, is_online)

    def select_peer(self, user: User) -> None:
        """Select a peer for chatting.

        Args:
            user: User to select
        """
        self.current_peer = user
        msg_list = self.query_one(MessageList)
        msg_list.clear()
        msg_list.add_system_message(f"Connected to {user.username}", "info")

        # Call callback
        if self.on_peer_selected:
            self.on_peer_selected(user)

    def add_received_message(self, sender: str, content: str) -> None:
        """Add a received message to the chat.

        Args:
            sender: Message sender
            content: Message content
        """
        msg_list = self.query_one(MessageList)
        msg_list.add_message(sender, content)

    def add_system_message(self, content: str, level: str = "info") -> None:
        """Add a system message.

        Args:
            content: Message content
            level: Message level
        """
        msg_list = self.query_one(MessageList)
        msg_list.add_system_message(content, level)

    def set_connection_status(self, status: str) -> None:
        """Set connection status.

        Args:
            status: Status text
        """
        status_bar = self.query_one(StatusBar)
        status_bar.set_connection_status(status)

    def _update_peer_count(self) -> None:
        """Update peer count in status bar."""
        peer_list = self.query_one(PeerList)
        count = len(peer_list.peers)
        status_bar = self.query_one(StatusBar)
        status_bar.set_peer_count(count)

    def on_list_view_selected(self, event) -> None:
        """Handle peer selection from list.

        Args:
            event: ListView selected event
        """
        peer_list = self.query_one(PeerList)
        selected_peer = peer_list.get_selected_peer()
        if selected_peer:
            self.select_peer(selected_peer)
