# Inventory System

Volume-based inventory management with weight tracking.

---

## Overview

Inventory is volume-based, not slot-based. What can be carried is determined by available volume in hands and backpacks. Weight affects fatigue and sustenance consumption.

---

## Mechanics

### Volume
- **Hands**: Each hand has a volume threshold for held items
- **Backpacks**: Provide additional volume without blocking hands
- Items have a `volume` property

### Weight
- Sum of all carried items' weights
- Affects fatigue and sustenance

### Fatigue from Weight
```python
if weight >= strength * 100:
    fatigue_per_action = (weight - strength * 100) / 100
```

### Sustenance from Weight
Weight increases sustenance consumption per turn/movement action.

---

## Item Structure

```json
{
  "id": "iron_sword",
  "name": "Iron Sword",
  "description": "A heavy iron blade.",
  "volume": 3,
  "weight": 50,
  "type": "weapon",
  "hand_slots": 1,
  "actions": ["pierce", "slash"]
}
```

---

## Entity Inventory

```python
@dataclass
class Inventory:
    items: list[Item]            # All carried items
    backpack_volume: int         # Extra volume from backpacks
    hand_volume: int             # Total hand volume (based on hands)

    def can_carry(self, item: Item) -> bool:
        """Check if item fits in available volume."""
        pass

    def add_item(self, item: Item) -> bool:
        """Add item to inventory. Returns False if can't carry."""
        pass

    def total_weight(self) -> float:
        """Sum of all item weights."""
        pass

    def apply_effects(self, entity: Entity) -> None:
        """Apply fatigue and sustenance effects based on weight."""
        pass
```

---

## Functions

### apply_inventory_sustenance_and_fatigue
```python
def apply_inventory_sustenance_and_fatigue(entity: Entity) -> None:
    """Calculate and apply fatigue and sustenance effects from carried weight."""
    weight = entity.inventory.total_weight()
    strength = entity.stats["strength"]

    if weight >= strength * 100:
        entity.fatigue += (weight - strength * 100) / 100

    entity.sustenance -= weight * 0.001  # Scale factor
```

---

## Dependencies

| System | How it's used |
|--------|---------------|
| Entity System | Entity stats (strength), body parts (hands) |
| Combat System | Equipped weapons determine available actions |
