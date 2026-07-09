"""Peer list widget."""

from textual.widgets import ListView, ListItem, Label
from textual.containers import Vertical
from rich.text import Text

from core.user import User


class PeerListItem(ListItem):
    """Custom list item for displaying peer information."""

    def __init__(self, user: User) -> None:
        """Initialize peer list item.

        Args:
            user: User information
        """
        super().__init__()
        self.user = user
        self._update_content()

    def _update_content(self) -> None:
        """Update the displayed content."""
        # Status indicator
        status = "●" if self.user.is_online else "○"
        status_class = "status-online" if self.user.is_online else "status-offline"

        # Create rich text
        text = Text()
        text.append(f"{status} ", style=status_class)
        text.append(self.user.username, style="bold")

        # Set as renderable
        self.set_renderable(text)

    def update_status(self, is_online: bool) -> None:
        """Update online status.

        Args:
            is_online: Whether user is online
        """
        self.user.is_online = is_online
        self._update_content()


class PeerList(Vertical):
    """Widget displaying list of available peers."""

    DEFAULT_CSS = """
    PeerList {
        width: 30;
        height: 100%;
        border-right: solid $border;
    }

    PeerList > Label {
        width: 100%;
        height: 3;
        content-align: center middle;
        text-style: bold;
        color: $primary;
        background: #252332;
    }

    PeerList > ListView {
        height: 1fr;
    }
    """

    def __init__(self) -> None:
        """Initialize peer list."""
        super().__init__()
        self.peers: dict[str, PeerListItem] = {}  # user_id -> PeerListItem

    def compose(self):
        """Compose peer list widgets."""
        yield Label("Online Peers")
        yield ListView()

    def add_peer(self, user: User) -> None:
        """Add a peer to the list.

        Args:
            user: User to add
        """
        if user.user_id in self.peers:
            # Update existing
            self.peers[user.user_id].user = user
            self.peers[user.user_id]._update_content()
            return

        # Create new item
        item = PeerListItem(user)
        self.peers[user.user_id] = item

        # Add to list view
        list_view = self.query_one(ListView)
        list_view.append(item)

    def remove_peer(self, user_id: str) -> None:
        """Remove a peer from the list.

        Args:
            user_id: User ID to remove
        """
        if user_id in self.peers:
            item = self.peers[user_id]
            item.remove()
            del self.peers[user_id]

    def update_peer_status(self, user_id: str, is_online: bool) -> None:
        """Update peer online status.

        Args:
            user_id: User ID
            is_online: Whether user is online
        """
        if user_id in self.peers:
            self.peers[user_id].update_status(is_online)

    def get_selected_peer(self) -> User | None:
        """Get currently selected peer.

        Returns:
            Selected user or None
        """
        list_view = self.query_one(ListView)
        if list_view.index is not None and list_view.index >= 0:
            item = list(self.peers.values())[list_view.index]
            return item.user
        return None

    def clear(self) -> None:
        """Clear all peers."""
        list_view = self.query_one(ListView)
        list_view.clear()
        self.peers.clear()
