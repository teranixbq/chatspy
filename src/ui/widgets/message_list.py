"""Message list widget for displaying chat messages."""

from datetime import datetime
from textual.widgets import RichLog
from textual.containers import Vertical
from rich.text import Text


class MessageList(Vertical):
    """Widget for displaying chat messages."""

    DEFAULT_CSS = """
    MessageList {
        width: 1fr;
        height: 1fr;
    }

    MessageList > RichLog {
        height: 100%;
        background: $background;
        border: solid $border;
    }
    """

    def __init__(self) -> None:
        """Initialize message list."""
        super().__init__()

    def compose(self):
        """Compose message list widgets."""
        yield RichLog(highlight=True, markup=True)

    def add_message(self, sender: str, content: str, timestamp: datetime | None = None) -> None:
        """Add a chat message.

        Args:
            sender: Message sender username
            content: Message content
            timestamp: Message timestamp (defaults to now)
        """
        if timestamp is None:
            timestamp = datetime.now()

        # Format timestamp
        time_str = timestamp.strftime("%H:%M:%S")

        # Create rich text
        text = Text()
        text.append(f"[{time_str}] ", style="dim")
        text.append(sender, style="bold #a277ff")
        text.append(": ", style="dim")
        text.append(content, style="#edecee")

        # Add to log
        log = self.query_one(RichLog)
        log.write(text)

    def add_system_message(self, content: str, level: str = "info") -> None:
        """Add a system message.

        Args:
            content: Message content
            level: Message level (info, warning, error)
        """
        timestamp = datetime.now()
        time_str = timestamp.strftime("%H:%M:%S")

        # Style based on level
        style_map = {
            "info": "#61ffca",
            "warning": "#ffca85",
            "error": "#ff6767",
        }
        style = style_map.get(level, "#61ffca")

        # Create rich text
        text = Text()
        text.append(f"[{time_str}] ", style="dim")
        text.append("● ", style=style)
        text.append(content, style=f"italic {style}")

        # Add to log
        log = self.query_one(RichLog)
        log.write(text)

    def clear(self) -> None:
        """Clear all messages."""
        log = self.query_one(RichLog)
        log.clear()
