# MVP Plan

MVP Goal: A playable prototype with all core systems implemented and functional, featuring a 6-room environment to move through, combat testing, and narrative descriptions. The systems don't need to be fleshed out but must be functional and extensible for future development.

---

## MVP Requirements

1. All systems implemented and working
2. 6-room environment to navigate
3. Combat testable (monsters don't need full AI yet)
4. Core commands: move, look, interact, fight
5. Narrative descriptions for all actions
6. Injury system functional

---

## Implementation Phases

### Phase 1: Foundation
- [ ] Refactor `state.py` to support room tracking, discovery history, flags
- [ ] Refactor `commands.py` to work with new state structure
- [ ] Update `main.py` UI to handle new output format

### Phase 2: Room System
- [ ] Create `rooms.py` with Room, Exit, RoomObject classes
- [ ] Create RoomRegistry with JSON loading
- [ ] Create `data/rooms.json` with 6 rooms
- [ ] Implement `look` command (narrative room description)
- [ ] Implement `move` command (navigate between rooms)

### Phase 3: Narrative System
- [ ] Create `narrative.py` with NarrativeBuilder base class
- [ ] Implement RoomNarrativeBuilder
- [ ] Implement fragment + sentence template system
- [ ] Integrate with look/move commands
- [ ] Add placeholder variable substitution

### Phase 4: Sense System
- [ ] Implement detection rules for objects/exits
- [ ] Add discovery persistence tracking
- [ ] Implement `has_light` context variable
- [ ] Integrate with narrative system

### Phase 5: Entity System
- [ ] Create `entities.py` with Entity, BodyPart classes
- [ ] Load body templates from `data/body_templates.json`
- [ ] Load stats from `data/stats.json`
- [ ] Implement quality calculation
- [ ] Implement injury application
- [ ] Create `data/injuries.json`

### Phase 6: Combat System
- [ ] Implement stance system (standing, crawling, lying)
- [ ] Implement action quality calculation
- [ ] Implement deterministic hit/damage
- [ ] Add `attack` command
- [ ] Add `stance` command
- [ ] Connect injuries to combat

### Phase 7: AI System (Minimal)
- [ ] Implement basic monster behavior (no full AI needed)
- [ ] Monsters attack player when in same room
- [ ] Deterministic targeting (e.g., always target torso)
- [ ] Monster turn execution

### Phase 8: Inventory System (Minimal)
- [ ] Implement basic inventory on Entity
- [ ] Add `pickup` command
- [ ] Add `inventory` command
- [ ] Weight-based fatigue calculation

### Phase 9: Integration & Polish
- [ ] Wire all systems together through commands
- [ ] Ensure narrative descriptions work for all actions
- [ ] Test move → look → fight → injury flow
- [ ] Fix UI issues
- [ ] Update documentation

---

## 6-Room Layout (MVP)

```
1. Dungeon Entrance → 2. Dark Corridor → 3. Guard Room
                                              ↓
6. Exit Tunnel ← 5. Treasure Vault ← 4. Spider Nest
```

| Room | Features |
|------|----------|
| 1. Dungeon Entrance | Torch, basic description, exit north |
| 2. Dark Corridor | No light, requires feel sense, exit north |
| 3. Guard Room | Zombie enemy, locked door east |
| 4. Spider Nest | Spider enemy, web objects, exit south |
| 5. Treasure Vault | Pickup items, chest object |
| 6. Exit Tunnel | Escape room, game win condition |

---

## MVP Command List

| Command | Description |
|---------|-------------|
| `hello` | Greet player |
| `help` | List commands |
| `move [direction]` | Move to adjacent room |
| `look [target]` | Describe room or object |
| `attack [target]` | Attack monster or body part |
| `stance [name]` | Change stance (standing/crawling/lying) |
| `pickup [item]` | Pick up object from room |
| `inventory` | List carried items |

---

## Extensibility Considerations

All systems should be designed so that MVP implementation can be extended to full functionality without major rewrites:

- **Commands**: Registry pattern allows adding commands without modifying existing code
- **Rooms**: JSON-driven, adding rooms requires only data changes
- **Narrative**: Template system allows adding descriptions without code changes
- **Combat**: Deterministic calculation allows adding stances/actions later
- **Entities**: Data-driven stats/injuries allow content expansion
- **AI**: Behavior type enum allows adding new behaviors later
