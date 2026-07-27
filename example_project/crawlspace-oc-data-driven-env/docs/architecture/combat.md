# Combat System

Deterministic turn-based combat with body part targeting, stances, and equipment-driven actions.

---

## Overview

Combat is fully deterministic - no RNG. Outcomes are calculated from stats, body part quality, equipment, and stance. Both players and monsters use the same combat rules.

---

## Stances

Stances represent the entity's physical position. Affects available actions and targetability.

| Stance | Available Actions | Notes |
|--------|-------------------|-------|
| standing | All melee, ranged, movement | Default stance |
| crawling | Low attacks, stealth, movement | Harder to hit, slower |
| lying | Defensive, minimal attacks | Cannot move, hard to hit |

### Stance Restrictions
Body condition restricts available stances:
- Missing legs → cannot stand
- Injured arms → stance may force lying down
- Severe fatigue → may collapse to lying

---

## Actions

Actions derived from available body parts + equipped items:

| Body Part/Item | Available Actions |
|----------------|-------------------|
| Teeth | bite |
| Arm (unarmed) | hit, grab, push |
| Sword | pierce, slash, thrust |
| Legs | kick, stomp |

Action quality calculation:
```python
action_quality = stat * body_part_quality * consciousness
```

Actions succeed if `action_quality` meets or exceeds required quality for the target.

---

## Targeting

- **Body part targeting**: Optional. Player can specify target body part.
- **Default targeting**: Abstract but deterministic (based on stance, distance, AI behavior).
- **Monster targeting**: Determined by AI behavior scripts.

---

## Damage Application

1. Action quality determines hit success
2. Hit success determines damage amount
3. Damage applied as injury to target body part
4. Injury reduces body part quality
5. If quality reaches 0 and injury is severe enough, part may be lost

```python
def apply_damage(attacker: Entity, defender: Entity, target_part: str, action: str) -> CombatResult:
    action_quality = attacker.stats[stat] * attacker.body_parts[part].quality * attacker.consciousness
    defense_quality = defender.stats[stat] * defender.body_parts[part].quality * defender.consciousness

    if action_quality >= defense_quality:
        injury = select_injury(action, action_quality)
        defender.apply_injury(injury, target_part)
        return CombatResult(hit=True, damage=action_quality)
    return CombatResult(hit=False)
```

---

## Deterministic Nature

- No RNG in any combat calculation
- Same inputs always produce same outputs
- Injury selection is deterministic (based on action type, target part)
- Monster behavior is scripted, not random

---

## Dependencies

| System | How it's used |
|--------|---------------|
| Entity System | Stats, body parts, injuries, consciousness for calculations |
| Inventory System | Equipped weapons determine available actions |
| State System | Combat state tracking, turn order |
| AI System | Monster behavior scripts determine actions |
