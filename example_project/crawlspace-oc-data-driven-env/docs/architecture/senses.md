# Sense System

Determines what entities can perceive based on senses, environmental conditions, stats, and sense propagation through exits.

---

## Overview

Every object, exit, and creature in the game has detectability rules. Senses can propagate through exits, allowing both the player and monsters to detect things beyond their current room. Detection difficulty is determined by remaining intensity after propagation.

---

## Senses

| Sense | Propagates Through Exits | Notes |
|-------|--------------------------|-------|
| see | Yes (adjacent rooms only) | Requires light for most objects. Exit must have `see_through: true` |
| hear | Yes (intensity decay) | Works in darkness. Intensity reduced per exit traversed |
| smell | Yes (intensity decay) | Works in darkness. Intensity reduced per exit traversed |
| feel | No | Requires physical proximity or action |

---

## Exit Permeability

Each exit defines how well each sense can pass through it:

```json
{
  "name": "north",
  "permeability": {
    "see_through": true,
    "see_cost": 1.0,
    "sound_cost": 0.5,
    "smell_cost": 0.8
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `see_through` | bool | Whether vision can pass through this exit |
| `see_cost` | float | Intensity reduction for sight (always 1.0 if see_through is true, since sight only reaches adjacent rooms) |
| `sound_cost` | float | Intensity reduction for sound per exit traversed |
| `smell_cost` | float | Intensity reduction for smell per exit traversed |

---

## Intensity Propagation

Sound and smell start with an **intensity** value at their source. When propagating through exits:

```
remaining_intensity = source_intensity - sum(exit_cost for each exit traversed)
```

### Example: Sound Propagation
```
Room A (monster growling, sound_intensity=4)
  └── exit (sound_cost=0.5)
       └── Room B (player here, remaining_intensity=3.5)
            └── exit (sound_cost=1.2)
                 └── Room C (remaining_intensity=2.3)
                      └── exit (sound_cost=1.5)
                           └── Room D (remaining_intensity=0.8)
                                └── exit (sound_cost=1.0)
                                     └── Room E (remaining_intensity=-0.2 → not audible)
```

### Example: Smell Propagation
```
Room A (rotting corpse, smell_intensity=4)
  └── exit (smell_cost=0.8)
       └── Room B (player here, remaining_intensity=3.2)
            └── exit (smell_cost=0.8)
                 └── Room C (remaining_intensity=2.4)
                      └── exit (smell_cost=0.8)
                           └── Room D (remaining_intensity=1.6)
```

### Sight Propagation
- Sight only reaches **directly adjacent rooms** (one exit away)
- If exit has `see_through: true`, the player can see into that room
- Objects in adjacent rooms can be seen if remaining intensity allows detection
- Sight does not chain through multiple rooms

---

## Detection Rules

Each detectable entity (object, exit, creature) defines:

```python
@dataclass
class DetectionRule:
    senses: list[str]           # Which senses can detect this
    base_intensity: float       # Intensity at source for sound/smell
    conditions: list[Condition] # Environmental/stat requirements
```

### Conditions
- `requires_light`: Only detectable if light is present
- `requires_darkness`: Only detectable in darkness
- `stat_check`: Check against a stat (e.g., intuition >= 15)
- `distance`: Maximum propagation distance for sound/smell

### Detection Difficulty
Determined by remaining intensity after propagation:
```python
sense_quality = intuition * body_part_quality * consciousness * remaining_intensity
if sense_quality >= detection_difficulty:
    detected = True
```

Higher remaining intensity = easier to detect.

---

## Discovery Persistence

Once detected, an object is **persistently known** by the player:
- Tracked in State System per room
- Survives room exits and re-entries
- Narrative system uses this for "already known" descriptions
- Changes since last detection are noted in descriptions

---

## Opposed Checks

Used for stealth vs perception scenarios:

```python
# Player hiding
hide_quality = dexterity * body_part_quality * consciousness

# Monster perceiving (with propagation)
perceive_quality = intuition * body_part_quality * consciousness * remaining_intensity

if perceive_quality > hide_quality:
    monster_detects_player()
```

Both sides use the same calculation. Higher value wins.

---

## Context Variables

The sense system provides context to the narrative system:
- `has_light`: Whether current room has light source
- `light_source`: Description of active light source
- `active_senses`: Which senses are currently effective
- `discovered`: What has been discovered in current room
- `propagated_sounds`: Sounds heard from adjacent rooms
- `propagated_smells`: Smells detected from nearby rooms

---

## Dependencies

| System | How it's used |
|--------|---------------|
| Entity System | Stats and body part quality for checks |
| State System | Discovery tracking, sense propagation context |
| Narrative System | Provides sense context for description selection |
| Room System | Provides exit permeability, object intensity values |
| AI System | Monster perception of player through propagation |
