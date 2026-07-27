# System Requirements

This document tracks all internal game systems, their responsibilities, and inter-system dependencies.

---

## Systems Overview

| System           | Purpose                                                                   |
|------------------|---------------------------------------------------------------------------|
| Room System      | Manage room definitions, exits, objects, creatures, and runtime instances |
| Entity System    | Manage stats, body parts, injuries, and inventory for all entities        |
| Command System   | Parse and execute player commands via extensible registry pattern         |
| Narrative System | Build sentences and fill fragments with data; ensures grammar and variety |
| Combat System    | Deterministic turn-based combat with body part targeting and stances      |
| Inventory System | Volume-based inventory with weight, hand slots, and backpacks             |
| State System     | Track game state including room instances, discovered objects, flags      |
| AI System        | Deterministic monster behavior scripts                                    |
| Sense System     | Visibility/detectability based on senses (sight, hearing, touch)          |

---

## System Details

### Room System

**Purpose:** Define and manage game locations (rooms), their connections (exits), contents (objects, creatures), and runtime instances.

**Data Structure (JSON template):**
- `id`: Unique identifier
- `name`: Display name
- `fragments`: Sense-based description fragments with placeholder variables (see Narrative System for format)
- `exits`: Array of connected exits ids
- `objects`: Array of contained objects ids
- `creatures`: Array of contained creatures ids

**Exit Structure:**
- `name`: Name (e.g., "door to cellar", "trapdoor")
- `fragments`: Same sense-based fragment pattern as rooms
- `destination`: Target room ID
- `locked`: Boolean, whether exit requires unlocking
- `enter_requirements`: Requirements to use (key, stat check, etc.)
- `sense_requirements`: Visibility rules (requires light, darkness, etc.)

**Objects Structure:**
- `name`: Display name
- `fragments`: Sense-based description fragments
- `senses`: Array of sense types required to detect (see, hear, feel)
- `conditions`: Environmental requirements for detection (light, darkness, stat check)

**Runtime Behavior:**
- Rooms are **templates** loaded from JSON
- **GameState** holds runtime room instances (what's currently in each room)
- Objects/creatures can be added or removed at runtime
- Exits are monodirectional by default, can be bidirectional if both rooms reference each other

**Dependencies:**
- Narrative System: Calls narrative builder for descriptions
- Sense System: Uses sense rules to determine what's detectable
- State System: Tracks runtime room state, discovered objects, flags

---

### Sense System

**Purpose:** Determine what entities can perceive based on senses (sight, hearing, smell, touch), environmental conditions, stats, and sense propagation through exits.

**Senses:**
- `see`: Vision-based detection. Requires light for most objects. Can pass through exits that are "see-through" (max one room away).
- `hear`: Audio-based detection. Works in darkness. Propagates through exits with intensity decay.
- `smell`: Odor-based detection. Propagates through exits with intensity decay. Works in darkness.
- `feel`: Touch-based detection. Requires physical proximity or action. Does not propagate through exits.

**Exit Permeability:**
Each exit has permeability values for sight, sound, and smell:
```json
{
  "name": "north",
  "permeability": {
    "see_through": 1.0,// if 0.0 you can't see into the other room, otherwise, the see roll is multiplied by this value to see into that exits room
    "sound_cost": 0.5, // reduces the intensity of the sound when passing through
    "smell_cost": 0.8  // reduces the intensity of the smell when passing through
  }
}
```
- `see_through`: multiplies the see-skill to see into this room
- `sound_cost`: Intensity reduction for sound per exit traversed
- `smell_cost`: Intensity reduction for smell per exit traversed

**Intensity Propagation:**
- Sound and smell start with an intensity value at their source
- When passing through an exit: `intensity -= exit_cost`
- When intensity reaches 0 or below, the sense cannot propagate further
- Example: A smell with intensity 4 passing through 3 exits with `smell_cost: 1` has intensity 1 remaining when it reaches the third room
- Sight only reaches directly adjacent rooms (one exit away) if `see_through` is true

**Detection Difficulty:**
- Determined by remaining intensity after propagation
- Higher remaining intensity = easier to detect
- Detection check: `sense_quality = intuition * body_part_quality * consciousness * remaining_intensity`
- If `sense_quality` meets or exceeds the object's detection difficulty, it is detected

**Detection Rules:**
- Each object/exit/creature has `senses` defining which senses can detect it
- Objects have an `intensity` value for sound/smell they produce
- Detection may have `conditions` (e.g., `requires_light`, `stat_check: {stat: "intuition", difficulty: 15}`)
- Once detected, object is **persistently known** by the player (tracked in State System)
- Previously detected objects that have changed since last detection are described differently

**Opposed Checks:**
- Stealth vs perception: Player hiding vs monster sensing
- Both sides use same calculation: stats × body part quality × consciousness × intensity
- Higher value wins

**Dependencies:**
- Entity System: Player/monster stats and body part quality for checks
- State System: Discovery tracking, sense propagation context
- Room System: Exit permeability values, object intensity values

---

### Narrative System

**Purpose:** The central text generator. Contains ALL sentence building parts and formulations. Rooms and objects only provide tiny fragments. The narrative system constructs complete, grammatically correct, varied prose by combining stance phrases, sense context, condition descriptions, and data fragments.

**Core Concept - Narrative System Owns Sentences, Data Owns Fragments:**
- **Fragments** (from JSON data): Tiny descriptive phrases only
  - Examples: `"narrow hallway"`, `"walls out of rough hewn stone"`, `"faint dripping sound"`
- **Sentence builders** (in Narrative System): Complete sentence structures, stance phrases, connectors, and formulations
  - All grammar, variety, and sentence alignment happens here

**Fragment Structure (JSON):**
```json
{
  "fragments": {
    "see": ["narrow hallway", "walls out of rough hewn stone", "faint light from above"],
    "hear": ["distant dripping sound", "echo of footsteps"],
    "smell": ["damp stone", "rotting wood"],
    "feel": ["rough carved grooves", "cold metal surface"]
  }
}
```

**Sentence Builders (Narrative System):**
The narrative system contains:

1. **Stance phrases**:
   - `"You stand"`, `"You crawl"`, `"You lie on the ground"`, `"You pull yourself forward with your leftover arm"`

2. **Sense introduction phrases** (variations for each sense):
   - See: `"You look around and see..."`, `"Your eyes catch..."`, `"Before you lies..."`
   - Hear: `"The sound of..."`, `"You hear..."`, `"Echoes reach you - ..."`
   - Smell: `"The air carries..."`, `"You catch the smell of..."`, `"... drifts through the air"`
   - Feel: `"Your fingers find..."`, `"You feel..."`, `"Touch reveals..."`

3. **Sense-unavailable formulations**:
   - When sight is blocked: `"As you crawl, the sound of your body moving across the floor echoes from {hear_fragment}. With your fingers you feel {feel_fragment}. You seem to be in {inferred_description}."`

4. **Condition/state integration**:
   - `"Standing exhausted and bleeding..."`, `"Crawling across the floor, pulling yourself forward..."`
   - Uses entity state (injuries, fatigue, body parts) to color descriptions

5. **Sentence alignment/combining**:
   - Multiple fragments woven into single flowing sentences
   - Random selection from variations to avoid repetition
   - Example: `"You look around as you crawl into a {room_fragment}, you see {object_fragment}."`

**Output Examples:**

*Full sight available, standing:*
> "You stand in a narrow hallway. You look around and see walls out of rough hewn stone. A faint light from above catches your eye."

*No sight, crawling, one arm:*
> "Crawling across the floor, pulling yourself forward with your leftover arm... The sound of your body moving echoes from narrow walls. With your fingers you feel rough carved grooves. You seem to be in a narrow hallway."

*Exhausted, bleeding, entering new room:*
> "Standing exhausted and bleeding, you look around. The damp stone air fills your lungs. Walls out of rough hewn stone surround you."

**Description Types:**
- **Primary descriptions**: First encounter. Full sensory detail based on available senses.
- **Secondary descriptions**: Re-encounter. Familiarity assumed, shorter formulations.

**Output Rules:**
- Multiple object descriptions woven into flowing paragraphs, not listed
- Brief mention when looking at room; full description with `look [object]`
- Previously detected objects acknowledged: `"the rune you felt earlier"`
- Changed objects described with contrast: `"the chest you saw before is now open"`
- Grammar and variety ensured entirely by narrative system, not data
- Player state (injuries, stance, consciousness) integrated into descriptions

---

### Entity System

**Purpose:** Manage all living things - stats, body parts, injuries, consciousness.

**Stats:**
- `strength`, `constitution`, `dexterity`, `intelligence`, `willpower`, `intuition`
- Data-driven from `data/stats.json` (min, max, default)

**Body Parts:**
- Organized in chains (parent → child)
- If a part is lost, all attached parts are also lost
- `quality`: 0.0-1.0 (reduced by injuries, can heal)
- `lost`: bool (physically severed, cannot heal naturally)

**Quality Calculation:**
```
involved_quality = sum(part.quality for part in involved_parts) / len(involved_parts)
```
- Lost parts contribute 0 but count in denominator
- Ancestor lost → child doesn't exist → contributes 0

**Consciousness (hidden bars):**
- `blood`: 0-1, health resource, multiplies all actions
- `fatigue`: 0-1, energy, decreases action quality
- `sustenance`: 0-1, food/drink, required for healing
```
consciousness = (blood * (1 - fatigue) * min(1.0, 0.2 + sustenance * 2)) / 3
```

**Injuries:**
- Reduce body part quality by `quality_deficit`
- `healable`: bool
- `healing_threshold`: progress toward healing (100 to heal)
- `healing_speed`: multiplier on healing progress
- `relieve_factor`: how much quality is restored when healed
- `followup_injury`: what injury replaces this when healed
- `stackable`: can multiple of same injury apply
- `severity`: for sorting (1 = worst)
- Healing check after each action

**Dependencies:**
- Inventory System: Carried weight affects fatigue
- Combat System: Injuries applied during combat
- Narrative System: Injury descriptions for output

---

### Combat System

**Purpose:** Deterministic turn-based combat with body part targeting, stances, and equipment.

**Core Mechanics:**
- **Deterministic**: No RNG. Outcomes calculated from stats, body quality, equipment, stance
- **Stances**: standing, crawling, lying - chosen by player, affected by body condition
  - Missing legs → cannot stand
  - Stances affect available actions and targetability
- **Actions**: Derived from available body parts + equipped items
  - Have teeth → can bite
  - Have arm → can hit
  - Have sword → can pierce or slash
- **Body part targeting**: Optional. Default targeting is abstract but deterministic
- **Action Quality**:
  ```
  action_quality = stat * body_part_quality * consciousness
  ```
  - Check against required quality for success

**Monster AI:**
- Deterministic behavior defined by behavior type
- Behavior types (enum): `aggressive`, `passive`, `fearsome`
  - `aggressive`: Seeks and attacks player
  - `passive`: Defends only, acts passively or flees
  - `fearsome`: Aggressive but retreats when injured
- Behavior code coupled to enum, can be JSON-driven or Python-based
- Monsters have same capabilities as player (stats, body, senses)

**Dependencies:**
- Entity System: Stats, body parts, injuries, consciousness
- Inventory System: Equipped weapons determine actions
- State System: Combat state tracking
- AI System: Monster behavior scripts

---

### Inventory System

**Purpose:** Volume-based inventory management with weight tracking.

**Mechanics:**
- **Hands**: Each hand has volume threshold for held items
- **Backpacks**: Additional volume without blocking hands
- **Weight**: Sum of all carried items
- **Fatigue from weight**: If `weight >= strength * 100`:
  ```
  fatigue_per_action = (weight - strength * 100) / 100
  ```
- **Sustenance from weight**: Weight affects sustenance consumption per turn/movement

**Functions:**
- `apply_inventory_sustenance_and_fatigue(entity)`: Auto-calculate effects

**Dependencies:**
- Entity System: Entity stats (strength), body parts (hands)

---

### State System

**Purpose:** Track all runtime game state across systems.

**Tracked Data:**
- Current room ID
- Room instances (runtime objects/creatures per room)
- Discovery tracking: what the player has sensed in each room
- Flags: `visited`, `has_light`, etc.
- Player entity state
- Game turn counter
- Game over state

**Discovery Tracking:**
- Persisted across room visits
- Stores: object ID, room ID, last known state
- Used by narrative system to generate "already known" descriptions
- Detects changes since last discovery

**Dependencies:**
- All systems read/write to State System

---

### Command System

**Purpose:** Parse and execute player commands via extensible registry pattern.

**Base Structure:**
```
Command (ABC)
├── name: str
├── aliases: list[str]
├── execute(state, args) -> CommandResult
└── help() -> str
```

**Built-in Commands:**
- `hello`: Greet player
- `help`: List commands or describe specific command
- `move [direction]`: Move to adjacent room (no args = list exits)
- `look [target]`: Describe room or specific object

**Dependencies:**
- State System: Reads/writes game state
- Room System: Move, look at rooms/exits/objects
- Entity System: Look at body parts, inventory
- Narrative System: Generate descriptive output
- Combat System: Combat commands
- Inventory System: Inventory commands

---

### AI System

**Purpose:** Deterministic monster behavior scripts.

**Behavior Types:**
- `aggressive`: Seeks and attacks player
- `passive`: Defends only, flees or stays still
- `fearsome`: Aggressive but retreats when injured

**Implementation:**
- Python code coupled to enum values
- Scripts define: action to take, target to aim for, conditions
- Can be JSON-driven for simple behaviors, Python for complex ones

**Monster Capabilities:**
- Same as player: stats, body, senses, inventory
- Use same check calculations as player

**Dependencies:**
- Entity System: Monster stats and body
- Combat System: Combat actions
- Sense System: Monster perception

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
