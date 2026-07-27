"""
Crawlspace - Main Module

Entry point for the terminal dungeon crawler game.
Uses Textual framework for terminal UI.
"""

import asyncio
from textual.app import App, ComposeResult
from textual.widgets import Input, Static
from textual.containers import Container, VerticalScroll
from textual.binding import Binding

from crawlspace.state import GameState
from crawlspace.commands import get_registry


class GameScreen(App):
    """Main game application."""

    CSS = """
    Screen {
        background: $surface 0%;
    }
    #game-container {
        width:100%;
        height:100%;
    }
    #output-area {
        height:85%;
        border:solid $primary;
        padding:0;
    }
    #output-scroller {
        height:85%;
        width:100%;
    }
    #output-text {
        width:100%;
    }
    #input-area {
        height:15%;
        dock:bottom;
        background:$panel 0%;
    }
    #cmd-input {
        width:100%;
    }
    .input-field {
        border:solid $primary;
    }
    """

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", priority=True),
    ]

    def __init__(self):
        super().__init__()
        self.game_state = GameState()
        self.command_history = []
        self.output_lines = []

    def compose(self) -> ComposeResult:
        """Create the UI components."""
        with Container(id="game-container"):
            with Container(id="output-area"):
                with VerticalScroll(id="output-scroller"):
                    yield Static(
                        "[bold cyan]Welcome to Crawlspace![/]\n\n"
                        "You wake up in a dark dungeon. Your head throbs.\n"
                        "Type [bold]look[/] to see your surroundings.\n"
                        "Type [bold]help[/] to see available commands.\n",
                        id="output-text"
                    )
            with Container(id="input-area"):
                yield Input(
                    placeholder="Enter command...",
                    id="cmd-input",
                    classes="input-field"
                )

    def on_mount(self) -> None:
        """Handle mount event."""
        input_widget = self.query_one("#cmd-input", Input)
        input_widget.focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle command input submission."""
        command_str = event.value.strip()
        if not command_str:
            return

        # Clear input immediately
        event.input.value = ""

        self.command_history.append(command_str)
        self.game_state.turn += 1

        registry = get_registry()
        result = registry.execute(self.game_state, command_str)

        output = self.query_one("#output-text", Static)
        
        # Get current content
        try:
            current = str(output.renderable)
        except:
            current = ""

        # Response already has color markup from narrative builder
        styled_response = result.message
        
        if not result.success:
            styled_response = f"[bold red]Error:[/] {styled_response}"

        # Append as chat: command then response
        new_output = current + f"\n\n[bold cyan]> {command_str}[/]\n{styled_response}\n[dim]{'-' * 30}[/]"

        output.update(new_output)

        # Scroll to bottom
        try:
            scroller = self.query_one("#output-scroller", VerticalScroll)
            scroller.scroll_end()
        except:
            pass

    def action_quit(self) -> None:
        """Quit the game."""
        self.exit()


def run():
    """Entry point function."""
    app = GameScreen()
    app.run()


if __name__ == "__main__":
    run()