# Room System

Manages all game locations (rooms), their connections (exits), contents (objects, creatures), and runtime instances.

---

## Overview

Rooms are defined in `data/rooms.json` as templates and loaded by `RoomRegistry` at runtime. Rooms are **static templates** - runtime state (what objects exist, what's been discovered) is tracked in the State System.

---

## JSON Schema

```json
{
  "rooms": [
    {
      "id": "entrance",
      "name": "Dungeon Entrance",
      "fragments": {
        "see": ["dark stone entrance", "cracks in the walls"],
        "hear": ["footsteps echo against stone"],
        "smell": ["stale air"],
        "feel": ["rough stone surface"]
      },
      "exits": [
        {
          "name": "north",
          "fragments": {
            "see": ["dark passage leading north"],
            "hear": ["draft whistling northward"]
          },
          "destination": "hallway",
          "locked": false,
          "conditions": [],
          "permeability": {
            "see_through": true,
            "see_cost": 1.0,
            "sound_cost": 0.5,
            "smell_cost": 0.8
          }
        }
      ],
      "objects": [
        {
          "name": "torch",
          "fragments": {
            "see": ["flickering flame on the wall"],
            "smell": ["burning pitch"],
            "feel": ["warm metal handle"]
          },
          "senses": ["see", "smell", "feel"],
          "conditions": []
        }
      ],
      "creatures": ["giant spider"]
    }
  ]
}
```

---

## Room Class

```python
@dataclass
class Room:
    id: str                    # Unique identifier
    name: str                 # Display name
    fragments: dict           # Sense-based description fragments
    exits: dict[str, Exit]    # name -> Exit mapping
    objects: list[RoomObject] # Interactive objects
    creatures: list[str]      # Creature IDs present
```

---

## Exit Class

```python
@dataclass
class Exit:
    name: str                 # Direction or label
    fragments: dict           # Sense-based description fragments
    destination: str          # Target room ID
    locked: bool              # Requires unlocking
    conditions: list          # Requirements to use
    senses: list[str]         # Senses that can detect this exit
    permeability: Permeability  # How well senses pass through
```

```python
@dataclass
class Permeability:
    see_through: bool         # Whether vision can pass through
    see_cost: float           # Intensity reduction for sight (always 1.0 if see_through)
    sound_cost: float         # Intensity reduction for sound per exit
    smell_cost: float         # Intensity reduction for smell per exit
```

### Exit JSON Example
```json
{
  "name": "north",
  "fragments": { ... },
  "destination": "hallway",
  "locked": false,
  "conditions": [],
  "permeability": {
    "see_through": true,
    "see_cost": 1.0,
    "sound_cost": 0.5,
    "smell_cost": 0.8
  }
}
```

---

## RoomObject Class

```python
@dataclass
class RoomObject:
    name: str                 # Display name
    fragments: dict           # Sense-based description fragments (simple arrays)
    senses: list[str]         # Senses that can detect this object
    conditions: list          # Detection conditions
    base_intensity: float     # Intensity at source for sound/smell (default 0)
```

---

## RoomRegistry API

```python
registry = get_room_registry()
room = registry.get("room_id")           # Get room by ID
all_rooms = registry.get_all()            # Get all rooms
registry.load_from_json("path")          # Load from JSON
registry.register(Room(...))             # Add room programmatically
```

---

## Runtime Behavior

- Rooms are **templates** loaded from JSON at startup
- **GameState** holds runtime room instances (what's currently in each room)
- Objects and creatures can be added or removed at runtime
- Exits are monodirectional by default; bidirectional only if both rooms reference each other
- Discovery of objects/exits is tracked in State System, not on the room itself

---

## Dependencies

| System | How it's used |
|--------|---------------|
| Narrative System | Calls narrative builder for descriptions using fragments |
| Sense System | Uses sense rules to determine what's detectable in a room |
| State System | Tracks runtime room state, discovered objects, visitation flags |

---

## Extending Rooms

### Option A: Add in JSON
Add entries to `data/rooms.json`.

### Option B: Programmatically
```python
from crawlspace.rooms import RoomRegistry, Room, Exit

registry = get_room_registry()
new_room = Room(
    id="treasury",
    name="Treasury",
    fragments={...},
    exits={},
    objects=[],
    creatures=[]
)
registry.register(new_room)
```
