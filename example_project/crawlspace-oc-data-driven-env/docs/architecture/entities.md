# Entity System

Manages all living things (players, monsters, creatures) - stats, body parts, injuries, and hidden consciousness bars.

---

## Overview

Every entity in the game has a body, stats, and injuries. Health is not a single bar but emerges from body part conditions and hidden resource bars (blood, fatigue, sustenance).

---

## Stats

Data-driven in `data/stats.json`:

```json
{
  "stats": {
    "strength": {"min": 1, "max": 10, "default": 5},
    "constitution": {"min": 1, "max": 10, "default": 5},
    "dexterity": {"min": 1, "max": 10, "default": 5},
    "intelligence": {"min": 1, "max": 10, "default": 5},
    "willpower": {"min": 1, "max": 10, "default": 5},
    "intuition": {"min": 1, "max": 10, "default": 5}
  }
}
```

---

## Body Parts

Parts organized in chains (parent → child). If a part in a chain is lost, all attached parts are also lost.

### Part Chain Example (Human)
```
Torso
├── Neck
│   └── Head
│       ├── Eye (left)
│       └── Eye (right)
├── Arm (left)
│   └── Hand
│       └── Finger...
└── Arm (right)
    └── Hand
        └── Finger...
└── Leg (left)
    └── Foot
└── Leg (right)
    └── Foot
```

### Body Part Structure
```json
{
  "body_templates": {
    "human": {
      "torso": {
        "type": "torso",
        "attached": ["neck", "arm_left", "arm_right", "leg_left", "leg_right"],
        "quality": 1.0
      },
      "neck": {
        "type": "neck",
        "attached": ["head"],
        "quality": 1.0
      },
      "head": {
        "type": "head",
        "attached": ["eye_left", "eye_right"],
        "has_injury_slots": true,
        "quality": 1.0
      }
    }
  }
}
```

### Body Part Class
```python
@dataclass
class BodyPart:
    type: str                  # Part type (eye, leg, arm, etc.)
    quality: float             # 0.0-1.0, reduced by injuries
    lost: bool                 # True = severed, cannot heal naturally
    injuries: list[str]        # Applied injury IDs
    attached: list[str]        # Child part IDs
```

### Quality Calculation

All actions are multiplied by involved body part quality. Each part contributes its quality divided by the number of involved parts.

```python
# Walking with two healthy legs:
walk_quality = 1.0/2 + 1.0/2 = 1.0 (100%)

# Walking with one lost leg:
walk_quality = 0.0/2 + 1.0/2 = 0.5 (50%)

# Walking with one broken leg (quality=0.7):
walk_quality = 0.7/2 + 1.0/2 = 0.85 (85%)

# Eyes when neck is lost (neck->head->eyes):
eye_quality = 0 (ancestor lost, child doesn't exist)

# Eyes when neck is broken (quality=0.7):
eye_quality = 1.0 (only eyes count, ancestor injury doesn't affect them)
```

### Key Rules
1. **Lost parts**: If `lost=True`, the part doesn't exist → contributes 0
2. **Injured parts**: Still exist, contribute their reduced quality
3. **Chain rule**: If an ancestor is lost, child parts also don't exist
4. **Denominator**: ALL involved parts count (even lost ones)

---

## Consciousness (Hidden Bars)

Beyond body parts, entities have hidden resource bars that multiply all actions:

- **Blood** (0-1): Health resource, multiplies all actions
- **Fatigue** (0-1): Energy, decreases action quality
- **Sustenance** (0-1): Food/drink, required for healing

```python
consciousness = (blood * (1 - fatigue) * min(1.0, 0.2 + sustenance * 2)) / 3
action_quality = stat * body_part_quality * consciousness
```

---

## Injuries

Defined in `data/injuries.json`:

```json
{
  "injuries": [{
    "id": "broken",
    "target_types": ["leg", "arm"],
    "quality_deficit": 0.3,
    "healable": true,
    "healing_threshold": 50,
    "healing_speed": 0.8,
    "relieve_factor": 1.0,
    "followup_injury": null,
    "stackable": true,
    "severity": 3,
    "template_singular": "has a fractured bone",
    "template_plural": "have fractured bones",
    "inspect_description": "Detailed for 'look [body_part]'"
  }]
}
```

### Key Fields
- `description`: Brief description for listings
- `inspect_description`: Detailed description for `look [body_part]` command

### Injury Mechanics

**Application:**
```python
part.quality -= quality_deficit  # Minimum 0
```

**Healing** (checked after each turn):
```python
healing = constitution * blood * min(1, sustenance * 2)
healing_threshold += healing * healing_speed * max(0.8, willpower * 2)
sustenance -= healing * 0.1

# When healing_threshold >= 100:
part.quality += original_deficit * relieve_factor
# Replace with followup_injury if set
```

### Severity Hierarchy
```
1 = destroyed (instant death)
2 = severed (permanent loss)
3 = broken (serious)
4 = crushed/burned/frozen
5 = cut/punctured/infected
6 = bruised (minor)
```

---

## Entity Class

```python
@dataclass
class Entity:
    template: str               # Body template name
    stats: dict[str, int]       # Current stat values
    body_parts: dict[str, BodyPart]
    blood: float                # 0-1
    fatigue: float              # 0-1
    sustenance: float           # 0-1
    inventory: list             # Carried items

    def get_quality(self, part_ids: list[str]) -> float:
        """Calculate combined quality for involved parts."""
        pass

    def apply_injury(self, injury_id: str, part_id: str) -> None:
        """Apply injury to a body part."""
        pass

    def heal(self) -> None:
        """Attempt to heal all healable injuries."""
        pass
```

---

## Dependencies

| System | How it's used |
|--------|---------------|
| Inventory System | Carried weight affects fatigue |
| Combat System | Injuries applied during combat |
| Narrative System | Injury descriptions for output |
| Sense System | Body part quality affects sense checks |
