"""
Room System Module

Provides an extensible room framework for the dungeon crawler.
Rooms are the fundamental building blocks of the game environment.

Usage:
    - Define rooms by subclassing Room
    - Add exits to connect rooms
    - Rooms can contain creatures and objects
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Exit:
    """Represents an exit from a room to another room."""

    name: str
    description: str
    destination: str  # Room ID
    aliases: list[str] = field(default_factory=list)


@dataclass
class RoomObject:
    """An object that can be found in a room."""

    name: str
    description: str
    aliases: list[str] = field(default_factory=list)


@dataclass
class Room:
    """
    Base class for all rooms in the game.

    Each room has:
    - id: unique identifier
    - name: display name
    - description: general visual description
    - exits: dict of exits (exit_name -> Exit)
    - objects: list of objects in the room
    - creatures: list of creatures in the room
    """

    id: str
    name: str
    description: str
    exits: dict[str, Exit] = field(default_factory=dict)
    objects: list[RoomObject] = field(default_factory=list)
    creatures: list[str] = field(default_factory=list)

    def get_exit(self, direction: str) -> Optional[Exit]:
        """Get exit by name or alias."""
        direction_lower = direction.lower()
        if direction_lower in self.exits:
            return self.exits[direction_lower]
        for exit in self.exits.values():
            if direction_lower in exit.aliases:
                return exit
        return None

    def get_object(self, name: str) -> Optional[RoomObject]:
        """Get object by name or alias."""
        name_lower = name.lower()
        for obj in self.objects:
            if obj.name.lower() == name_lower or name_lower in obj.aliases:
                return obj
        return None

    def list_exits(self) -> list[str]:
        """List all available exits."""
        return list(self.exits.keys())


class RoomRegistry:
    """
    Registry for managing all rooms in the game.

    Provides methods to register, lookup, and navigate between rooms.
    """

    def __init__(self):
        self._rooms: dict[str, Room] = {}

    def register(self, room: Room) -> None:
        """Register a room."""
        self._rooms[room.id] = room

    def get(self, room_id: str) -> Optional[Room]:
        """Get a room by ID."""
        return self._rooms.get(room_id)

    def get_all(self) -> dict[str, Room]:
        """Get all registered rooms."""
        return self._rooms.copy()


_global_registry: Optional[RoomRegistry] = None


def get_room_registry() -> RoomRegistry:
    """Get the global room registry (lazy initialization)."""
    global _global_registry
    if _global_registry is None:
        _global_registry = RoomRegistry()
        _initialize_default_rooms()
    return _global_registry


def _initialize_default_rooms() -> None:
    """Initialize rooms from the rooms.json data file."""
    import json
    import os

    registry = _global_registry

    data_dir = os.path.join(os.path.dirname(__file__), "data")
    rooms_file = os.path.join(data_dir, "rooms.json")

    if not os.path.exists(rooms_file):
        return

    with open(rooms_file, "r") as f:
        data = json.load(f)

    for room_data in data.get("rooms", []):
        exits = {}
        for exit_data in room_data.get("exits", []):
            exit_obj = Exit(
                name=exit_data["name"],
                description=exit_data.get("description", ""),
                destination=exit_data.get("destination", ""),
                aliases=exit_data.get("aliases", []),
            )
            exits[exit_data["name"].lower()] = exit_obj

        objects = []
        for obj_data in room_data.get("objects", []):
            objects.append(RoomObject(
                name=obj_data["name"],
                description=obj_data.get("description", ""),
                aliases=obj_data.get("aliases", []),
            ))

        room = Room(
            id=room_data["id"],
            name=room_data.get("name", ""),
            description=room_data.get("description", ""),
            exits=exits,
            objects=objects,
            creatures=room_data.get("creatures", []),
        )
        registry.register(room)
