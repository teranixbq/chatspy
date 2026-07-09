"""Status bar widget."""

from textual.widgets import Static
from textual.containers import Horizontal
from rich.text import Text


class StatusBar(Horizontal):
    """Widget for displaying status information."""

    DEFAULT_CSS = """
    StatusBar {
        width: 100%;
        height: 1;
        dock: top;
        background: #252332;
    }

    StatusBar > Static {
        width: 1fr;
        padding: 0 1;
    }

    #status-left {
        text-align: left;
    }

    #status-center {
        text-align: center;
    }

    #status-right {
        text-align: right;
    }
    """

    def __init__(self) -> None:
        """Initialize status bar."""
        super().__init__()
        self._username = ""
        self._connection_status = "Disconnected"
        self._peer_count = 0

    def compose(self):
        """Compose status bar widgets."""
        yield Static("", id="status-left")
        yield Static("", id="status-center")
        yield Static("", id="status-right")

    def on_mount(self) -> None:
        """Handle mount event."""
        self._update_display()

    def set_username(self, username: str) -> None:
        """Set current username.

        Args:
            username: Username to display
        """
        self._username = username
        self._update_display()

    def set_connection_status(self, status: str) -> None:
        """Set connection status.

        Args:
            status: Status text (e.g., "Connected", "Connecting", "Disconnected")
        """
        self._connection_status = status
        self._update_display()

    def set_peer_count(self, count: int) -> None:
        """Set peer count.

        Args:
            count: Number of online peers
        """
        self._peer_count = count
        self._update_display()

    def _update_display(self) -> None:
        """Update the status bar display."""
        # Left: Username
        left_text = Text()
        left_text.append("User: ", style="dim")
        left_text.append(self._username, style="bold #a277ff")
        self.query_one("#status-left", Static).update(left_text)

        # Center: Connection status
        center_text = Text()
        status_style = {
            "Connected": "#29d398",
            "Connecting": "#ffca85",
            "Disconnected": "#6d6d6d",
        }.get(self._connection_status, "#6d6d6d")
        center_text.append("● ", style=status_style)
        center_text.append(self._connection_status, style=status_style)
        self.query_one("#status-center", Static).update(center_text)

        # Right: Peer count
        right_text = Text()
        right_text.append(f"Peers: {self._peer_count}", style="#61ffca")
        self.query_one("#status-right", Static).update(right_text)
