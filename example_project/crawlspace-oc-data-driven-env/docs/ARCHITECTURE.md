# Crawlspace Architecture

This document describes the architecture of the Crawlspace dungeon crawler game at a high level. Each system has its own detailed documentation in the `architecture/` subdirectory.

---

## Overview

Crawlspace is a CLI-based dungeon crawler built with Python and Textual. The game uses a data-driven architecture where game content is defined in JSON files and loaded at runtime. The core philosophy is **narrative-first** - all game events are expressed through flowing, story-like descriptions rather than stats and lists.

### Data Flow

```
JSON Data → Commands → Narrative Builders → Narrative Output → UI
                   ↑
             (senses, context)
```

---

## Core Systems

### 1. Room System
Manages all game locations defined in JSON. Rooms are templates loaded at runtime with exits, objects, and creatures.
- **Details:** [`architecture/rooms.md`](architecture/rooms.md)

### 2. Narrative System
The central text generator. Builds grammatically correct sentences by filling data fragments with context variables and selecting from multiple sentence templates for variety.
- **Details:** [`architecture/narrative.md`](architecture/narrative.md)

### 3. Sense System
Determines what the player can perceive based on senses (sight, hearing, touch), environmental conditions, and stats. Supports opposed checks for stealth vs perception.
- **Details:** [`architecture/senses.md`](architecture/senses.md)

### 4. Entity System
Manages all living things - stats, body parts organized in chains, injuries, and hidden consciousness bars (blood, fatigue, sustenance).
- **Details:** [`architecture/entities.md`](architecture/entities.md)

### 5. Combat System
Deterministic turn-based combat with body part targeting, stances (standing/crawlying/lying), and equipment-driven actions.
- **Details:** [`architecture/combat.md`](architecture/combat.md)

### 6. AI System
Deterministic monster behavior scripts coupled to behavior types (aggressive, passive, fearsome). Monsters have same capabilities as players.
- **Details:** [`architecture/ai.md`](architecture/ai.md)

### 7. Inventory System
Volume-based inventory with hand slots, backpacks, and weight-based fatigue/sustenance effects.
- **Details:** [`architecture/inventory.md`](architecture/inventory.md)

### 8. Command System
Extensible registry pattern for parsing and executing player commands.
- **Details:** [`architecture/commands.md`](architecture/commands.md)

### 9. State System
Tracks all runtime game state - room instances, discovery history, flags, entities, turn counter.
- **Details:** [See SYSTEM_REQUIREMENTS.md](../SYSTEM_REQUIREMENTS.md)

---

## Inter-System Dependency Map

```
                    ┌─────────────┐
                    │ State System │
                    └──────┬──────┘
                           │ (all systems read/write)
                           ▼
┌──────────┐    ┌─────────────┐    ┌─────────────┐
│ Room Sys │───▶│ Narrative   │◀───│  Sense Sys  │
└──────────┘    │    System   │    └──────┬──────┘
                └──────┬──────┘           │
                       │                  │
┌──────────┐    ┌──────▼──────┐    ┌──────┴──────┐
│Inventory │◀───│ Entity Sys  │───▶│ Combat Sys  │
└──────────┘    └─────────────┘    └──────┬──────┘
                       ▲                  │
                       │            ┌─────▼─────┐
                       └────────────│   AI Sys  │
                                    └───────────┘

┌──────────────┐
│ Command Sys  │ (orchestrates all systems)
└──────┬───────┘
       │ calls
       ▼
  All Systems
```

---

## File Organization

```
docs/
├── ARCHITECTURE.md              # This file - high-level overview
├── SYSTEM_REQUIREMENTS.md       # System requirements & dependencies
├── architecture/
│   ├── rooms.md                 # Room system deep-dive
│   ├── entities.md              # Entity system deep-dive
│   ├── narrative.md             # Narrative system deep-dive
│   ├── combat.md                # Combat system deep-dive
│   ├── ai.md                    # AI system deep-dive
│   ├── commands.md              # Command system deep-dive
│   ├── senses.md                # Sense system deep-dive
│   └── inventory.md             # Inventory system deep-dive
└── MVP_PLAN.md                  # MVP implementation plan

crawlspace/
├── __init__.py
├── main.py              # Textual UI entry point
├── state.py            # Game state management
├── commands.py          # Command system
├── rooms.py            # Room system
├── entities.py         # Entity system (body parts, injuries)
├── narrative.py        # Narrative system
├── data/
│   ├── rooms.json      # Room definitions
│   ├── stats.json      # Stat definitions
│   ├── injuries.json   # Injury definitions
│   ├── body_templates.json # Body part templates
│   ├── creatures.json  # Creature definitions
│   └── items.json      # Item definitions
```

---

## Best Practices

1. **Data-driven**: Define content in JSON, not Python code
2. **Atomic commits**: Each feature system in its own commit
3. **Narrative-first**: Descriptions read like story, not lists
4. **Template system**: Use fragments + sentence templates for grammar and variety
5. **Extensible APIs**: Use registries and base classes
6. **Test incrementally**: Test each command/registry before moving on
