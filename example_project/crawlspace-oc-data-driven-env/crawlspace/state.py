"""
Game State Module

Manages the overall game state for Crawlspace.
This module provides the foundation for tracking player progress,
inventory, location, and other transient game data.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PlayerState:
    """Represents the player's current state."""

    name: str = "Player"
    health: int = 100
    max_health: int = 100
    gold: int = 0
    room_id: str = "start"  # Current room the player is in


@dataclass
class GameState:
    """
    Main game state container.

    Holds all transient data that represents the current state of the game,
    including player stats, world state, and any runtime flags.
    """

    player: PlayerState = field(default_factory=PlayerState)
    turn: int = 0
    game_over: bool = False

    def get_current_room_id(self) -> str:
        """Get the current room ID."""
        return self.player.room_id

    def set_current_room(self, room_id: str) -> None:
        """Set the current room."""
        self.player.room_id = room_id

    def reset(self) -> None:
        """Reset the game state to initial values."""
        self.player = PlayerState()
        self.turn = 0
        self.game_over = False