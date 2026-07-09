"""Message input widget."""

from textual.widgets import Input
from textual.containers import Horizontal
from textual.binding import Binding


class MessageInput(Horizontal):
    """Widget for message input."""

    DEFAULT_CSS = """
    MessageInput {
        width: 100%;
        height: 3;
        dock: bottom;
        background: #252332;
    }

    MessageInput > Input {
        width: 1fr;
    }
    """

    BINDINGS = [
        Binding("escape", "blur", "Unfocus", show=False),
        Binding("ctrl+u", "clear", "Clear", show=False),
    ]

    def __init__(self) -> None:
        """Initialize message input."""
        super().__init__()
        self.on_submit_callback = None

    def compose(self):
        """Compose input widgets."""
        yield Input(placeholder="Type a message... (Enter to send, Esc to unfocus)")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission.

        Args:
            event: Input submitted event
        """
        message = event.value.strip()
        if message and self.on_submit_callback:
            self.on_submit_callback(message)
            # Clear input
            event.input.value = ""

    def action_blur(self) -> None:
        """Unfocus the input."""
        input_widget = self.query_one(Input)
        input_widget.blur()

    def action_clear(self) -> None:
        """Clear the input."""
        input_widget = self.query_one(Input)
        input_widget.value = ""

    def focus_input(self) -> None:
        """Focus the input field."""
        input_widget = self.query_one(Input)
        input_widget.focus()

    def set_on_submit(self, callback: callable) -> None:
        """Set callback for message submission.

        Args:
            callback: Function to call with message text
        """
        self.on_submit_callback = callback
