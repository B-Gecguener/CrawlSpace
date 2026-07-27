# Narrative System

The central text generator. Contains ALL sentence building parts and formulations. Rooms and objects only provide tiny fragments. The narrative system constructs complete, grammatically correct, varied prose.

---

## Overview

The narrative system transforms raw game data into flowing, story-like descriptions. It owns all sentence structure, grammar, variety, and alignment. Data files (rooms, objects, creatures) only provide small descriptive fragments.

### Core Philosophy

**Narrative System owns sentences. Data owns fragments.**

- **Fragments** (from JSON data): Tiny descriptive phrases only
  - Examples: `"narrow hallway"`, `"walls out of rough hewn stone"`, `"faint dripping sound"`
- **Sentence builders** (in Narrative System): All sentence structure, stance phrases, connectors, formulations
  - Grammar, variety, and sentence alignment happen entirely here

---

## Fragment Structure (JSON)

Rooms and objects provide minimal fragments:

```json
{
  "id": "corridor",
  "name": "Dark Corridor",
  "fragments": {
    "see": ["narrow hallway", "walls out of rough hewn stone", "faint light from above"],
    "hear": ["distant dripping sound", "echo of footsteps"],
    "smell": ["damp stone", "rotting wood"],
    "feel": ["rough carved grooves", "cold metal surface"]
  }
}
```

Fragments are small phrases without sentence structure. They describe what is present, not how to say it.

---

## Sentence Builders (Narrative System)

The narrative system contains all sentence construction logic:

### 1. Stance Phrases

Context-aware phrases based on player stance:

```python
STANCE_PHRASES = {
    "standing": [
        "You stand",
        "You are on your feet",
        "Standing upright"
    ],
    "crawling": [
        "You crawl",
        "You move on hands and knees",
        "Crawling forward"
    ],
    "lying": [
        "You lie on the ground",
        "You rest on the floor",
        "Lying flat"
    ]
}
```

### 2. Sense Introduction Phrases

Multiple variations per sense, randomly selected:

```python
SENSE_INTRODUCTIONS = {
    "see_first": [
        "You look around and see {fragment}.",
        "Your eyes catch {fragment}.",
        "Before you lies {fragment}.",
        "{fragment} catches your attention."
    ],
    "see_known": [
        "You see {fragment} again.",
        "{fragment} remains where you left it."
    ],
    "hear_first": [
        "You hear {fragment}.",
        "Sound reaches you - {fragment}.",
        "The {fragment} echoes around you."
    ],
    "hear_known": [
        "The familiar sound of {fragment}.",
        "{fragment} echoes once more."
    ],
    "smell_first": [
        "The air carries {fragment}.",
        "You catch the smell of {fragment}.",
        "{fragment} drifts through the air."
    ],
    "smell_known": [
        "The familiar scent of {fragment}.",
        "{fragment} still lingers."
    ],
    "feel_first": [
        "Your fingers find {fragment}.",
        "You feel {fragment}.",
        "Touch reveals {fragment}."
    ],
    "feel_known": [
        "{fragment} greets your touch again.",
        "You recognize {fragment} by touch."
    ]
}
```

### 3. Sense-Unavailable Formulations

When a sense is blocked, the narrative system constructs descriptions that explain how the player infers their surroundings:

```python
SENSE_UNAVAILABLE = {
    "no_sight": [
        "As you {stance}, the sound of {body_sound} {hear_fragment}. "
        "With your fingers you feel {feel_fragment}. "
        "You seem to be in a {inferred_description}.",
        "{stance} in darkness. {hear_fragment} echoes around you. "
        "Your touch finds {feel_fragment}. "
        "This feels like {inferred_description}."
    ]
}
```

### 4. Condition/State Integration

Player state (injuries, fatigue, body parts) is woven into descriptions:

```python
CONDITION_PHRASES = {
    "exhausted": [
        "Standing exhausted, you look around.",
        "Bleary-eyed and tired, you notice..."
    ],
    "bleeding": [
        "Standing exhausted and bleeding, you look around.",
        "Blood dripping, you manage to see..."
    ],
    "one_arm": [
        "Crawling across the floor, pulling yourself forward with your leftover arm...",
        "Dragging yourself with one arm, you feel..."
    ],
    "missing_legs": [
        "Pulling your torso across the stone floor...",
        "Without legs to stand, you drag yourself forward..."
    ]
}
```

### 5. Sentence Alignment/Combining

Multiple fragments are woven into single flowing sentences:

```python
# Instead of separate sentences for each fragment:
# "You see a narrow hallway. You see walls out of rough hewn stone."

# The narrative system combines them:
COMBINE_PATTERNS = [
    "You {stance} into a {fragment1}, you see {fragment2}.",
    "{stance_phrase}, {sense_intro} {fragment1} and {fragment2}.",
    "{condition_phrase}. {sense_intro} {fragment1}. {sense_intro2} {fragment2}."
]
```

---

## Output Examples

### Full sight available, standing:
> "You stand in a narrow hallway. You look around and see walls out of rough hewn stone. A faint light from above catches your eye."

### No sight, crawling, one arm:
> "Crawling across the floor, pulling yourself forward with your leftover arm... The sound of your body moving echoes from narrow walls. With your fingers you feel rough carved grooves. You seem to be in a narrow hallway."

### Exhausted, bleeding, entering new room:
> "Standing exhausted and bleeding, you look around. The damp stone air fills your lungs. Walls out of rough hewn stone surround you."

### Adjacent room sound/smell propagation:
> "You hear a distant growling sound from the passage north. The smell of rotting flesh drifts through the air."

---

## Description Types

### Primary Descriptions
First encounter with a room or object. Full sensory detail based on available senses.
- All available senses contribute to the description
- Detailed and immersive
- Selects from `first` variation pools

### Secondary Descriptions
Re-encounter. Familiarity assumed, shorter formulations.
- Acknowledges prior discovery
- More concise
- Selects from `known` variation pools

---

## Output Rules

1. **No labels**: Never "You see:" or "Exits:" - descriptions flow naturally
2. **Objects in rooms**: Briefly mentioned when looking at room; full description with `look [object]`
3. **Previously detected objects**: Acknowledged - `"the rune you felt earlier"`
4. **Changed objects**: Described with contrast - `"the chest you saw before is now open"`
5. **Grammar**: Ensured entirely by narrative system, not data
6. **Variety**: Multiple templates selected to prevent repetition
7. **Player state**: Injuries, stance, and consciousness integrated into descriptions
8. **Sense context**: Descriptions change based on which senses are available

---

## NarrativeBuilder Classes

```python
class NarrativeBuilder(ABC):
    """Base class for all narrative builders."""

    @abstractmethod
    def build(self, context: dict) -> str:
        """Build narrative text from context data."""
        pass

    def fill_variables(self, template: str, variables: dict) -> str:
        """Replace placeholder variables in a template."""
        result = template
        for key, value in variables.items():
            result = result.replace("{" + key + "}", str(value))
        return result
```

### RoomNarrativeBuilder
Builds room descriptions by:
1. Determining visitation state (first vs known)
2. Checking which senses are active
3. Selecting matching fragments from room data
4. Choosing stance and condition phrases from entity state
5. Wrapping fragments in sentence templates
6. Combining into flowing paragraphs

### InjuryNarrativeBuilder
Builds injury descriptions using templates from `data/injuries.json`:
- `template_singular` for count = 1
- `template_plural` for count > 1
- Connected with "Additionally," for multiple injuries

---

## Dependencies

| System | How it's used |
|--------|---------------|
| State System | Flags, discovery history, previous states, context variables |
| Room System | Fragment definitions from rooms, exits, objects |
| Entity System | Stance, injuries, body parts, consciousness for condition phrases |
| Sense System | Determines which senses are active and available for descriptions |
