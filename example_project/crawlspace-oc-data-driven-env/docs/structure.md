# Crawlspace Project Structure

```
crawlspace/
├── crawlspace.toml          # Project package metadata
├── pyproject.toml           # Python package configuration
├── readme.md                # Main readme
├── docs/
│   └── structure.md          # This file
└── crawlspace/
    ├── __init__.py          # Package root
    ├── state.py             # Game state management
    ├── commands.py          # Command system
    └── main.py              # Main application entry point
```

## Module Overview

### state.py
Manages the game state using dataclasses:
- `PlayerState`: Tracks player data (name, health, gold, location)
- `GameState`: Main container for all game state

### commands.py
Extensible command framework:
- `Command`: Abstract base class for commands
- `CommandRegistry`: Maps command names to Command objects
- `CommandResult`: Result wrapper for command execution

### main.py
Textual-based terminal UI:
- `GameScreen`: Main App class with input/output widgets

## Extending Commands

To add new commands, create a new Command subclass:

```python
class MoveCommand(Command):
    name = "move"
    aliases = ["go", "walk"]

    def execute(self, state: GameState, args: str) -> CommandResult:
        # Implementation here
        return CommandResult(success=True, message="You move...")

# Register it
registry = get_registry()
registry.register(MoveCommand())
```