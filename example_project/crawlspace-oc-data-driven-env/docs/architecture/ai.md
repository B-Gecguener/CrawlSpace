# AI System

Deterministic monster behavior scripts coupled to behavior types.

---

## Overview

Monsters have the same capabilities as players (stats, body, senses, inventory). Their behavior is fully deterministic - defined by behavior type and scripts, not RNG.

---

## Behavior Types

```python
class BehaviorType(enum.Enum):
    AGGRESSIVE = "aggressive"   # Seeks and attacks player
    PASSIVE = "passive"         # Defends only, flees or stays still
    FEARSOME = "fearsome"       # Aggressive but retreats when injured
```

### Aggressive
- Actively seeks player when in sense range
- Attacks on sight
- Targets based on deterministic rules (e.g., lowest health body part)

### Passive
- Does not initiate attacks
- Defends if attacked
- May flee when injured or threatened

### Fearsome
- Aggressive when player is not threatening
- Retreats when entity is injured below threshold
- Prioritizes quick attacks

---

## Behavior Scripts

Scripts define monster actions per situation:

```python
@dataclass
class BehaviorScript:
    behavior_type: BehaviorType
    target_preference: str       # e.g., "head", "legs", "random_deterministic"
    flee_threshold: float        # Blood/fatigue level at which to flee
    sense_range: int             # How far monster can detect player

    def decide_action(self, monster: Entity, player: Entity, context: CombatContext) -> Action:
        """Determine next action based on current situation."""
        pass
```

### Implementation Options
1. **JSON-driven**: Simple behaviors defined in data files
2. **Python scripts**: Complex behaviors with full logic access

---

## Monster Capabilities

Monsters have:
- Stats (same 6 as player)
- Body parts (from template)
- Senses (same detection rules as player)
- Inventory (items they carry/drop)

All checks use the same calculation as player:
```python
check_quality = stat * body_part_quality * consciousness
```

---

## Dependencies

| System | How it's used |
|--------|---------------|
| Entity System | Monster stats, body parts, injuries |
| Combat System | Combat actions and damage |
| Sense System | Monster perception of player |
| State System | Current room, player position |
