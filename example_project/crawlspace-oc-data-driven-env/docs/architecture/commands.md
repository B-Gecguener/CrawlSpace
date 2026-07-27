# Command System

Extensible registry pattern for parsing and executing player commands.

---

## Overview

All player interactions flow through commands. The command system uses a registry pattern where commands are registered and looked up by name.

---

## Command Base Class

```python
class Command(ABC):
    """Base class for all game commands."""

    name: str = ""                # Primary command name
    aliases: list[str] = []       # Alternative names

    @abstractmethod
    def execute(self, state: GameState, args: str) -> CommandResult:
        """Execute the command with the given game state and arguments."""
        pass

    def help(self) -> str:
        """Return help text for this command."""
        return "No help available."
```

---

## CommandResult

```python
@dataclass
class CommandResult:
    success: bool                 # Whether command executed successfully
    message: str                  # Output message
    state: Optional[GameState]    # Updated state (if modified)
```

---

## CommandRegistry

```python
class CommandRegistry:
    def register(self, command: Command) -> None:
        """Register a command."""
        pass

    def get(self, name: str) -> Optional[Command]:
        """Get a command by name or alias."""
        pass

    def execute(self, state: GameState, input_str: str) -> CommandResult:
        """Parse and execute a command string."""
        pass

    def list_commands(self) -> list[str]:
        """List all available commands."""
        pass
```

---

## Built-in Commands

### hello
Greet the player.
```
hello -> "hello Player"
```

### help
List all commands or describe a specific command.
```
help -> Lists all commands
help hello -> "hello - Greet the player"
```

### move
Move to an adjacent room via an exit.
```
move north -> Moves player to the north exit's destination
move -> Lists all known exits in current room
```

### look
Describe the room or a specific object.
```
look -> Describes current room (all sensed objects mentioned)
look torch -> Describes the torch in detail
look head -> Describes own head body part
```

---

## Creating a New Command

```python
class MyCommand(Command):
    name = "mycommand"
    aliases = ["mc", "my"]

    def execute(self, state: GameState, args: str) -> CommandResult:
        # Implementation
        return CommandResult(success=True, message="Result message")

    def help(self) -> str:
        return "mycommand - Description of what it does"

# Register it
registry = get_registry()
registry.register(MyCommand())
```

---

## Dependencies

| System | How it's used |
|--------|---------------|
| State System | Reads/writes game state |
| Room System | Move, look at rooms/exits/objects |
| Entity System | Look at body parts, inventory commands |
| Narrative System | Generate descriptive output |
| Combat System | Combat-related commands |
| Inventory System | Inventory commands |
