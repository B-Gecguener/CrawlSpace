"""
Command System Module

Provides an extensible command framework for parsing and executing player commands.
This module defines the base command interface and a registry for handling
various game commands that can be extended with new functionality.

Usage:
    - Register new commands by subclassing Command
    - Use CommandRegistry to parse and execute commands
"""

from abc import ABC, abstractmethod
from typing import Optional
from dataclasses import dataclass

from crawlspace.state import GameState
from crawlspace.rooms import get_room_registry, Room, RoomObject
from crawlspace.narrative import RoomNarrativeBuilder, create_room_narrative_builder


@dataclass
class CommandResult:
    """Result of executing a command."""

    success: bool
    message: str
    state: Optional["GameState"] = None


class Command(ABC):
    """Base class for all game commands."""

    name: str = ""
    aliases: list[str] = []

    @abstractmethod
    def execute(self, state: GameState, args: str) -> CommandResult:
        """Execute the command with the given game state and arguments."""
        pass

    def help(self) -> str:
        """Return help text for this command."""
        return "No help available."


class CommandRegistry:
    """
    Registry for managing and executing commands.

    Maintains a mapping of command names to Command objects and provides
    methods for registering, looking up, and executing commands.
    """

    def __init__(self):
        self._commands: dict[str, Command] = {}

    def register(self, command: Command) -> None:
        """Register a command."""
        self._commands[command.name] = command
        for alias in command.aliases:
            self._commands[alias] = command

    def get(self, name: str) -> Optional[Command]:
        """Get a command by name or alias."""
        return self._commands.get(name)

    def execute(self, state: GameState, input_str: str) -> CommandResult:
        """Parse and execute a command string."""
        parts = input_str.strip().split(maxsplit=1)
        if not parts:
            return CommandResult(success=False, message="No command entered.")

        cmd_name = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        cmd = self.get(cmd_name)
        if cmd is None:
            msg = "Unknown command: " + cmd_name
            return CommandResult(success=False, message=msg)

        return cmd.execute(state, args)

    def list_commands(self) -> list[str]:
        """List all available commands."""
        return list(self._commands.keys())


class HelloCommand(Command):
    """Command to test basic functionality - echoes back 'hello player'."""

    name = "hello"
    aliases = []

    def execute(self, state: GameState, args: str) -> CommandResult:
        """Execute the hello command."""
        return CommandResult(success=True, message="hello " + state.player.name)

    def help(self) -> str:
        """Return help text."""
        return "hello - Returns a greeting to the player."


class HelpCommand(Command):
    """Help command - shows available commands or help for a specific command."""

    name = "help"
    aliases = ["h", "?"]

    def execute(self, state: GameState, args: str) -> CommandResult:
        """Execute the help command."""
        registry = get_registry()

        if args.strip():
            # Show help for specific command
            cmd = registry.get(args.strip().lower())
            if cmd:
                return CommandResult(success=True, message=cmd.help())
            return CommandResult(success=False, message=f"No help available for '{args}'. Type 'help' to see all commands.")

        # Show all available commands
        commands = registry.list_commands()
        cmd_list = ", ".join(sorted(commands))
        message = f"Available commands:\n{cmd_list}\n\nType 'help <command>' for details on a specific command."
        return CommandResult(success=True, message=message)

    def help(self) -> str:
        """Return help text."""
        return "help [command] - Show all commands or help for a specific command."


class LookCommand(Command):
    """Look around the current room or examine a specific object."""

    name = "look"
    aliases = ["l", "examine", "inspect"]

    def execute(self, state: GameState, args: str) -> CommandResult:
        """Execute the look command."""
        room_registry = get_room_registry()
        current_room_id = state.get_current_room_id()
        room = room_registry.get(current_room_id)

        if room is None:
            return CommandResult(success=False, message="You are in a void. Something is wrong.")

        if not args.strip():
            # Use narrative builder for room description
            builder = create_room_narrative_builder()
            output = builder.build_description(room)
            return CommandResult(success=True, message=output)

        # Check if looking at an exit
        target = args.strip().lower()
        exit_info = room.get_exit(target)
        if exit_info:
            return CommandResult(success=True, message=exit_info.description)

        # Check objects in room
        obj = room.get_object(target)
        if obj:
            return CommandResult(success=True, message=obj.description)

        # Provide descriptive error with available options
        available_exits = list(room.exits.keys())
        available_objects = [o.name for o in room.objects]
        available = []
        
        if available_exits:
            available.append(f"exits: {', '.join(available_exits)}")
        if available_objects:
            available.append(f"objects: {', '.join(available_objects)}")
        if room.creatures:
            available.append(f"creatures: {', '.join(room.creatures)}")
        
        if available:
            return CommandResult(success=False, message=f"You don't see '{target}' here. You can make out {', '.join(available)}.")
        return CommandResult(success=False, message=f"You don't see '{target}' here.")

    def help(self) -> str:
        """Return help text."""
        return "look [object] - Look around the room or examine a specific object."


class MoveCommand(Command):
    """Move to another room through an exit."""

    name = "move"
    aliases = ["go", "walk", "m"]

    def execute(self, state: GameState, args: str) -> CommandResult:
        """Execute the move command."""
        room_registry = get_room_registry()
        current_room_id = state.get_current_room_id()
        room = room_registry.get(current_room_id)

        if room is None:
            return CommandResult(success=False, message="You are in a void. Something is wrong.")

        if not args.strip():
            # Show available exits with narrative
            exits = room.list_exits()
            if exits:
                return CommandResult(success=True, message=f"You can go {self._format_list_names(exits)} from here.")
            return CommandResult(success=False, message="There are no exits from here.")

        exit_info = room.get_exit(args)
        if exit_info is None:
            available_exits = list(room.exits.keys())
            if available_exits:
                return CommandResult(success=False, message=f"You can't go {args}. Paths lead {self._format_list(room.exits)}.")
            return CommandResult(success=False, message="You can't go that way. There are no exits.")

        dest_room = room_registry.get(exit_info.destination)
        if dest_room is None:
            return CommandResult(success=False, message="The path leads nowhere.")

        state.set_current_room(exit_info.destination)

        # Move through exit with narrative
        builder = create_room_narrative_builder()
        output = f"You go {args}, heading toward the {dest_room.name}.\n\n"
        output += builder.build_description(dest_room)

        return CommandResult(success=True, message=output)

    def _format_list(self, exits: dict) -> str:
        """Format exits as oxford list (for dict input)."""
        names = list(exits.keys())
        if not names:
            return ""
        if len(names) == 1:
            return names[0]
        if len(names) == 2:
            return f"{names[0]} and {names[1]}"
        return ", ".join(names[:-1]) + f", and {names[-1]}"

    def _format_list_names(self, exits: list) -> str:
        """Format exit names as oxford list (for list input)."""
        if not exits:
            return ""
        if len(exits) == 1:
            return exits[0]
        if len(exits) == 2:
            return f"{exits[0]} and {exits[1]}"
        return ", ".join(exits[:-1]) + f", and {exits[-1]}"

    def help(self) -> str:
        """Return help text."""
        return "move <direction> - Move through an exit to another room."


_global_registry: Optional[CommandRegistry] = None


def get_registry() -> CommandRegistry:
    """Get the global command registry (lazy initialization)."""
    global _global_registry
    if _global_registry is None:
        _global_registry = CommandRegistry()
        _global_registry.register(HelloCommand())
        _global_registry.register(LookCommand())
        _global_registry.register(MoveCommand())
        _global_registry.register(HelpCommand())
    return _global_registry