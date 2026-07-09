"""Help screen showing keyboard shortcuts."""

from textual.app import ComposeResult
from textual.containers import Container, VerticalScroll
from textual.screen import Screen
from textual.widgets import Static, Button


class HelpScreen(Screen):
    """Help screen with keyboard shortcuts."""

    CSS = """
    HelpScreen {
        align: center middle;
    }

    #help-container {
        width: 70;
        height: auto;
        max-height: 80%;
        background: $surface;
        border: solid $border;
        padding: 2;
    }

    #title {
        width: 100%;
        content-align: center middle;
        text-style: bold;
        color: $primary;
        margin-bottom: 2;
    }

    .section-title {
        text-style: bold;
        color: $secondary;
        margin-top: 1;
        margin-bottom: 1;
    }

    .shortcut {
        margin-left: 2;
        margin-bottom: 1;
    }

    .key {
        color: $accent;
        text-style: bold;
    }

    #close-button {
        width: 20;
        margin-top: 2;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose the help screen."""
        with Container(id="help-container"):
            yield Static("ChatSpy - Keyboard Shortcuts", id="title")

            with VerticalScroll():
                yield Static("Global", classes="section-title")
                yield Static("[key]Ctrl+C[/key] / [key]q[/key] - Quit application", classes="shortcut", markup=True)
                yield Static("[key]Ctrl+H[/key] / [key]?[/key] - Show this help screen", classes="shortcut", markup=True)
                yield Static("[key]Tab[/key] - Switch focus between panels", classes="shortcut", markup=True)
                yield Static("[key]Esc[/key] - Close dialog or unfocus input", classes="shortcut", markup=True)

                yield Static("Peer List (when focused)", classes="section-title")
                yield Static("[key]↑[/key] / [key]k[/key] - Move up", classes="shortcut", markup=True)
                yield Static("[key]↓[/key] / [key]j[/key] - Move down", classes="shortcut", markup=True)
                yield Static("[key]Enter[/key] - Select peer and focus chat", classes="shortcut", markup=True)
                yield Static("[key]/[/key] - Search peers", classes="shortcut", markup=True)

                yield Static("Chat (when focused)", classes="section-title")
                yield Static("[key]↑[/key] / [key]k[/key] - Scroll up", classes="shortcut", markup=True)
                yield Static("[key]↓[/key] / [key]j[/key] - Scroll down", classes="shortcut", markup=True)
                yield Static("[key]Ctrl+U[/key] - Page up", classes="shortcut", markup=True)
                yield Static("[key]Ctrl+D[/key] - Page down", classes="shortcut", markup=True)
                yield Static("[key]i[/key] - Focus input box", classes="shortcut", markup=True)

                yield Static("Input Box (when focused)", classes="section-title")
                yield Static("[key]Enter[/key] - Send message", classes="shortcut", markup=True)
                yield Static("[key]Esc[/key] - Cancel and unfocus", classes="shortcut", markup=True)
                yield Static("[key]Ctrl+U[/key] - Clear input", classes="shortcut", markup=True)

            yield Button("Close", variant="primary", id="close-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        self.dismiss()
