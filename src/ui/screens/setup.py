"""First-run setup screen for username configuration."""

from textual.app import ComposeResult
from textual.containers import Container, Vertical, Center
from textual.screen import Screen
from textual.widgets import Input, Button, Label, Static
from textual.validation import Length


class SetupScreen(Screen):
    """Screen for first-time username setup."""

    CSS = """
    SetupScreen {
        align: center middle;
    }

    #setup-container {
        width: 60;
        height: auto;
        background: $surface;
        border: solid $border;
        padding: 2;
    }

    #title {
        width: 100%;
        content-align: center middle;
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }

    #subtitle {
        width: 100%;
        content-align: center middle;
        color: $text-muted;
        margin-bottom: 2;
    }

    #username-input {
        width: 100%;
        margin-bottom: 1;
    }

    #button-container {
        width: 100%;
        height: auto;
        align: center middle;
    }

    #continue-button {
        width: 20;
    }

    .error {
        color: $error;
        margin-top: 1;
    }
    """

    def __init__(self, on_setup_complete: callable) -> None:
        """Initialize setup screen.

        Args:
            on_setup_complete: Callback function(username: str) when setup is done
        """
        super().__init__()
        self.on_setup_complete = on_setup_complete

    def compose(self) -> ComposeResult:
        """Compose the setup screen layout."""
        with Container(id="setup-container"):
            yield Static("Welcome to ChatSpy", id="title")
            yield Static("Secure P2P chat for your local network", id="subtitle")
            yield Label("Choose your username:")
            yield Input(
                placeholder="Enter username (3-50 characters)",
                id="username-input",
                validators=[Length(minimum=3, maximum=50)],
            )
            with Center(id="button-container"):
                yield Button("Continue", variant="primary", id="continue-button")

    def on_mount(self) -> None:
        """Handle screen mount."""
        # Focus the input field
        self.query_one("#username-input", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press.

        Args:
            event: Button press event
        """
        if event.button.id == "continue-button":
            self._submit_username()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission (Enter key).

        Args:
            event: Input submitted event
        """
        if event.input.id == "username-input":
            self._submit_username()

    def _submit_username(self) -> None:
        """Validate and submit username."""
        username_input = self.query_one("#username-input", Input)
        username = username_input.value.strip()

        # Validate
        if not username:
            self._show_error("Username cannot be empty")
            return

        if len(username) < 3:
            self._show_error("Username must be at least 3 characters")
            return

        if len(username) > 50:
            self._show_error("Username must be at most 50 characters")
            return

        # Call callback
        self.on_setup_complete(username)

    def _show_error(self, message: str) -> None:
        """Show error message.

        Args:
            message: Error message to display
        """
        # Remove existing error if any
        existing_error = self.query(".error")
        for widget in existing_error:
            widget.remove()

        # Add new error
        container = self.query_one("#setup-container")
        container.mount(Static(message, classes="error"))
