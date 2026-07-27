"""
Narrative System Module

This module provides the narrative description system for Crawlspace.
It transforms raw game data (injuries, rooms, objects) into flowing, story-like descriptions
that adapt to the player's senses, body condition, and environment.

Core Components:
- SenseManager: Tracks player senses and enables/disables based on body parts
- NumberWordConverter: Converts counts to narrative words (2 -> "two")
- NarrativeBuilder: Abstract base for building descriptions
- InjuryNarrativeBuilder: Builds injury descriptions
- RoomNarrativeBuilder: Builds room descriptions
- StatefulObject: Base for objects that change state

Usage:
    from crawlspace.narrative import InjuryNarrativeBuilder
    builder = InjuryNarrativeBuilder()
    desc = builder.describe_part_injuries(entity.get_part("hand_left"))
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional
import os
import json


# ============================================================================
# SENSE MANAGER
# ============================================================================

@dataclass
class Senses:
    """
    Represents the player's senses and their effectiveness.

    Each sense is a float from 0.0 to 1.0:
    - 1.0 = fully functional
    - 0.0 = completely disabled

    The senses are derived from the player's body parts:
    - sight: Eyes
    - hearing: Ears
    - feeling: Skin/nerve endings
    - smell: Nose
    - taste: Tongue
    """

    sight: float = 1.0
    hearing: float = 1.0
    feeling: float = 1.0
    smell: float = 1.0
    taste: float = 1.0

    def get_active_senses(self) -> list[tuple[str, float]]:
        """Returns senses sorted by priority (sight > hearing > feeling > smell > taste)."""
        senses = [
            ("sight", self.sight),
            ("hearing", self.hearing),
            ("feeling", self.feeling),
            ("smell", self.smell),
            ("taste", self.taste),
        ]
        return [(name, value) for name, value in senses if value > 0]

    def get_top_senses(self, count: int = 2) -> list[tuple[str, float]]:
        """Returns the top N active senses."""
        active = self.get_active_senses()
        return active[:count]

    def is_sense_active(self, sense_name: str) -> bool:
        """Check if a specific sense is active."""
        return getattr(self, sense_name, 0.0) > 0


class SenseManager:
    """
    Manages the player's senses based on body condition.

    Automatically updates sense effectiveness based on injuries to body parts.
    """

    @staticmethod
    def update_from_entity(entity) -> Senses:
        """
        Update senses based on an entity's body parts.

        If eyes are lost/damaged -> sight reduced
        If ears are lost/damaged -> hearing reduced
        etc.
        """
        senses = Senses()

        # Check sight (eyes)
        eye_left = entity.get_part("eye_left")
        eye_right = entity.get_part("eye_right")

        if eye_left and eye_right:
            senses.sight = (eye_left.quality + eye_right.quality) / 2
            if entity.is_part_lost("eye_left") or entity.is_part_lost("eye_right"):
                senses.sight = 0.0

        # Check hearing (ears)
        ear_left = entity.get_part("ear_left")
        ear_right = entity.get_part("ear_right")

        if ear_left and ear_right:
            senses.hearing = (ear_left.quality + ear_right.quality) / 2
            if entity.is_part_lost("ear_left") or entity.is_part_lost("ear_right"):
                senses.hearing = 0.0

        # Check feeling (skin - using torso as proxy)
        torso = entity.get_part("torso")
        if torso:
            senses.feeling = torso.quality

        # Check smell (nose)
        nose = entity.get_part("nose")
        if nose:
            senses.smell = nose.quality
            if entity.is_part_lost("nose"):
                senses.smell = 0.0

        # Check taste (tongue)
        tongue = entity.get_part("tongue")
        if tongue:
            senses.taste = tongue.quality
            if entity.is_part_lost("tongue"):
                senses.taste = 0.0

        return senses


# ============================================================================
# NUMBER WORD CONVERTER
# ============================================================================

class NumberWordConverter:
    """
    Converts numeric counts to narrative words.

    Used to make descriptions feel more story-like:
    - 1 -> "one"
    - 2 -> "two"
    - 3 -> "a few"
    - 4 -> "several"
    - 5+ -> "numerous"
    """

    WORD_MAP = {
        0: "no",
        1: "one",
        2: "two",
        3: "a few",
        4: "several",
        5: "numerous",
    }

    @classmethod
    def convert(cls, count: int) -> str:
        """Convert an integer to a narrative word."""
        if count <= 0:
            return cls.WORD_MAP[0]
        if count >= 5:
            return cls.WORD_MAP[5]
        return cls.WORD_MAP.get(count, str(count))


# ============================================================================
# NARRATIVE BUILDERS
# ============================================================================

class NarrativeBuilder(ABC):
    """Abstract base class for narrative builders."""

    @abstractmethod
    def build_description(self, *args, **kwargs) -> str:
        """Build a narrative description."""
        pass


# ============================================================================
# INJURY NARRATIVE BUILDER
# ============================================================================

class InjuryNarrativeBuilder(NarrativeBuilder):
    """
    Builds injury descriptions that read like story paragraphs.

    Features:
    - Groups injuries by part and type
    - Aggregates counts (two broken fingers, not broken + broken)
    - Applies severity hierarchy (destroyed > severed > broken > crushed > cut > bruised)
    - Connects clauses with narrative flow
    - Limits to top 3 severity types

    Example Input:
        - finger_left_a: broken
        - finger_left_b: broken
        - hand_left: bruised
        - arm_left: bruised
        - arm_left: cut

    Example Output:
        "On your left hand, two fingers are badly fractured.
        Your palm is bruised and swollen.
        Additionally, there are a few bruises and cuts running up your left arm."
    """

    # Severity hierarchy (lower number = more severe)
    SEVERITY_ORDER = {
        "destroyed": 1,
        "severed": 2,
        "broken": 3,
        "crushed": 4,
        "cut": 5,
        "bruised": 6,
    }

    def build_description(self, *args, **kwargs) -> str:
        return self.describe_injuries(*args, **kwargs)

    def describe_injuries(self, injuries: list) -> str:
        """Build a description from a list of injuries on a part."""
        if not injuries:
            return ""

        # Group by severity
        grouped = self._group_by_severity(injuries)

        # Build narrative
        return self._build_narrative(grouped)

    def describe_part_injuries(self, part, entity=None) -> str:
        """
        Describe injuries on a specific body part.

        Args:
            part: BodyPart object
            entity: Entity (optional, for context)
        """
        if not part or not part.injuries:
            return ""

        injury_registry = self._get_injury_registry()
        injury_data = []

        for injury_id in part.injuries:
            injury = injury_registry.get(injury_id)
            if injury:
                injury_data.append({
                    "id": injury_id,
                    "type": injury.get("id", injury_id),
                    "severity": injury.get("severity", 5),
                    "description": injury.get("description", ""),
                    "inspect_description": injury.get("inspect_description", ""),
                    "template_singular": injury.get("template_singular", ""),
                    "template_plural": injury.get("template_plural", ""),
                })

        if not injury_data:
            return ""

        # Also check child parts (attached)
        if entity and part.attached:
            for child_id in part.attached:
                child = entity.get_part(child_id)
                if child and child.injuries:
                    for injury_id in child.injuries:
                        injury = injury_registry.get(injury_id)
                        if injury:
                            injury_data.append({
                                "id": injury_id,
                                "type": injury.get("id", injury_id),
                                "severity": injury.get("severity", 5),
                                "description": injury.get("description", ""),
                                "inspect_description": injury.get("inspect_description", ""),
                                "template_singular": injury.get("template_singular", ""),
                                "template_plural": injury.get("template_plural", ""),
                                "part_type": child.type,
                            })

        # Group by severity
        grouped = self._group_by_severity(injury_data)

        # Build narrative
        return self._build_narrative(grouped, part.type)

    def describe_full_body(self, entity) -> str:
        """Describe all injuries on the entire body as a narrative."""
        all_parts = entity.get_all_parts()

        injury_registry = self._get_injury_registry()
        all_injuries = []

        for part_id, part in all_parts.items():
            if not part.injuries:
                continue

            # Check if parent is lost
            if entity.is_part_lost(part_id):
                continue

            for injury_id in part.injuries:
                injury = injury_registry.get(injury_id)
                if injury:
                    all_injuries.append({
                        "id": injury_id,
                        "type": injury.get("id", injury_id),
                        "severity": injury.get("severity", 5),
                        "description": injury.get("description", ""),
                        "inspect_description": injury.get("inspect_description", ""),
                        "part_id": part_id,
                        "part_type": part.type,
                    })

        if not all_injuries:
            return ""

        # Group by severity
        grouped = self._group_by_severity(all_injuries)

        return self._build_full_narrative(grouped)

    def _group_by_severity(self, injuries: list) -> dict:
        """Group injuries by severity and aggregate counts."""
        grouped = {}

        for injury in injuries:
            severity = injury.get("severity", 5)
            injury_type = injury.get("type", injury.get("id", ""))
            part_type = injury.get("part_type", "")

            key = (severity, injury_type, part_type)

            if key not in grouped:
                grouped[key] = {
                    "severity": severity,
                    "type": injury_type,
                    "part_type": part_type,
                    "description": injury.get("description", ""),
                    "inspect_description": injury.get("inspect_description", ""),
                    "template_singular": injury.get("template_singular", ""),
                    "template_plural": injury.get("template_plural", ""),
                    "count": 0,
                }

            grouped[key]["count"] += 1

        return grouped

    def _build_narrative(self, grouped: dict, base_part_type: str = "") -> str:
        """Build a narrative paragraph from grouped injuries."""
        if not grouped:
            return ""

        # Sort by severity (worst first)
        sorted_groups = sorted(grouped.values(), key=lambda x: x["severity"])

        # Take top 3 severity types
        top_groups = sorted_groups[:3]

        sentences = []

        for group in top_groups:
            count = group["count"]
            injury_type = group["type"]
            description = group.get("description", "")
            template_singular = group.get("template_singular", "")
            template_plural = group.get("template_plural", "")
            # Use the explicitly set part_type, or fall back to base_part_type
            part_type = group.get("part_type", "") or base_part_type

            if not part_type:
                continue

            # Convert count to word
            count_word = NumberWordConverter.convert(count)

            # Build sentence
            sentence = self._build_injury_sentence(
                count_word, injury_type, description, part_type,
                template_singular, template_plural
            )
            sentences.append(sentence)

        # Connect sentences with narrative flow
        return self._connect_sentences(sentences)

    def _build_full_narrative(self, grouped: dict) -> str:
        """Build narrative for full body description."""
        if not grouped:
            return ""

        sorted_groups = sorted(grouped.values(), key=lambda x: x["severity"])
        top_groups = sorted_groups[:5]  # More for full body

        sentences = []
        current_part = None

        for group in top_groups:
            count = group["count"]
            injury_type = group["type"]
            part_type = group.get("part_type", "")
            description = group["description"]

            # Group by body part
            if part_type != current_part:
                if sentences:
                    sentences.append("")
                current_part = part_type

            count_word = NumberWordConverter.convert(count)
            sentence = self._build_injury_sentence(
                count_word, injury_type, description, part_type
            )
            sentences.append(sentence)

        return self._connect_sentences(sentences)

    def _build_injury_sentence(self, count_word: str, injury_type: str,
                            description: str, part_type: str,
                            template_singular: str = "", template_plural: str = "") -> str:
        """Build a single injury sentence with proper story grammar."""
        if count_word == "no" or count_word == "" or not part_type:
            return ""

        is_plural = count_word != "one"
        part = self._make_plural(part_type, is_plural)

        # Use template if available, otherwise fall back to description
        if is_plural and template_plural:
            template = template_plural
        elif template_singular:
            template = template_singular
        else:
            # Fallback
            desc = description.strip()
            if "-" in desc:
                desc = desc.split("-")[-1].strip()
            if count_word == "one":
                return f"your {part} {desc}"
            else:
                return f"{count_word} of your {part} {desc}"
            return ""

        # Build sentence with template
        if count_word == "one":
            return f"your {part} {template}"
        else:
            return f"{count_word} of your {part} {template}"

    def _make_plural(self, part_type: str, is_plural: bool) -> str:
        """Make part name plural if needed."""
        if not is_plural:
            return part_type

        irregular = {
            "foot": "feet",
            "tooth": "teeth",
            "hand": "hands",
            "finger": "fingers",
            "toe": "toes",
            "leg": "legs",
            "arm": "arms",
            "ear": "ears",
            "eye": "eyes",
            "neck": "necks",
            "head": "heads",
        }
        return irregular.get(part_type, part_type + "s")

    def _connect_sentences(self, sentences: list) -> str:
        """Connect sentences with narrative flow, not as a list."""
        if not sentences:
            return ""

        # Remove empty/None
        sentences = [s for s in sentences if s]

        if not sentences:
            return ""

        if len(sentences) == 1:
            return sentences[0].capitalize() + "."

        # Build natural paragraph flow
        result = sentences[0].capitalize() + "."

        for i, sentence in enumerate(sentences[1:-1], 1):
            if sentence:
                result += " " + sentence + "."

        if sentences[-1]:
            result += " Additionally, " + sentences[-1] + "."

        return result

    def _get_injury_registry(self):
        """Get the injury registry."""
        from crawlspace.entities import get_injury_registry
        return get_injury_registry()


# ============================================================================
# ROOM NARRATIVE BUILDER
# ============================================================================

class RoomNarrativeBuilder(NarrativeBuilder):
    """
    Builds room descriptions that adapt to player senses and object states.

    Features:
    - Uses player's senses to filter what can be described
    - Includes object states in descriptions
    - Mentions creatures present
    - Describes available exits
    """

    def build_description(self, room, senses: Senses = None, entity=None) -> str:
        """
        Build a narrative description of a room as a flowing paragraph.

        Args:
            room: Room object
            senses: Player's Senses (optional)
            entity: Player entity for context
        """
        if senses is None:
            senses = Senses()

        parts = []

        # Start with room name/description
        parts.append(room.name + ".\n" + room.description)

        # Describe what's in the room based on senses
        if room.objects:
            obj_desc = self._describe_objects(room.objects, senses)
            if obj_desc:
                parts.append(obj_desc)

        # Describe creatures
        if room.creatures:
            creature_desc = self._describe_creatures(room.creatures, senses)
            if creature_desc:
                parts.append(creature_desc)

        # Describe exits naturally
        exit_desc = self._describe_exits(room.exits, senses)
        if exit_desc:
            parts.append(exit_desc)

        return " ".join(parts)

    def _describe_objects(self, objects: list, senses: Senses) -> str:
        """Describe objects in the room in a natural way."""
        if not objects:
            return ""

        names = [obj.name for obj in objects if obj.name]
        if not names:
            return ""

        # Add green color markup to each object name
        colored_names = []
        for name in names:
            colored_names.append(f"[green]{name}[/green]")

        obj_list = self._oxford_list(colored_names)

        if senses.sight > 0.5:
            return f"Among the objects here, you spot {obj_list}."
        elif senses.hearing > 0:
            return f"You hear mention of {obj_list} in the room."
        elif senses.feeling > 0:
            return f"Your hands find {obj_list} nearby."

        return f"You sense {obj_list} here."

    def _describe_creatures(self, creatures: list, senses: Senses) -> str:
        """Describe creatures in the room naturally."""
        if not creatures:
            return ""

        # Add red color markup to each creature name
        colored_creatures = []
        for c in creatures:
            colored_creatures.append(f"[red]{c}[/red]")

        creature_list = self._oxford_list(colored_creatures)

        if senses.sight > 0.5:
            return f"A {creature_list} {self._plural_verb(creatures, 'is', 'are')} here, watching you with hungry eyes."
        elif senses.hearing > 0:
            return f"You hear movement from a {creature_list} lurking nearby."
        elif senses.feeling > 0:
            return f"You sense a {creature_list} presence in the darkness."

        return f"A {creature_list} {self._plural_verb(creatures, 'is', 'are')} here."

    def _describe_exits(self, exits: dict, senses: Senses) -> str:
        """Describe available exits naturally."""
        if not exits:
            return "There are no exits leading out of this place."

        # Add cyan color markup to each exit name
        exit_names = []
        for name in exits.keys():
            exit_names.append(f"[cyan]{name}[/cyan]")

        exit_list = self._oxford_list(exit_names)

        return f"Passages lead {exit_list}."

    def _oxford_list(self, items: list) -> str:
        """Format a list with Oxford comma."""
        if not items:
            return ""
        if len(items) == 1:
            return items[0]
        if len(items) == 2:
            return f"{items[0]} and {items[1]}"
        return ", ".join(items[:-1]) + f", and {items[-1]}"

    def _plural_verb(self, items: list, singular: str, plural: str) -> str:
        """Choose correct verb form."""
        return plural if len(items) != 1 else singular


# ============================================================================
# STATEFUL OBJECT
# ============================================================================

@dataclass
class ObjectState:
    """Represents a state for a stateful object."""
    id: str
    name: str
    description: str = ""


class StatefulObject(ABC):
    """
    Base class for objects that can change state.

    Use cases:
    - Exits: "default" -> "locked" -> "broken"
    - Objects: "lit" -> "unlit" -> "broken"
    - Containers: "closed" -> "open" -> "empty"
    """

    def __init__(self):
        self._states: dict[str, str] = {}
        self.current_state: str = "default"

    def get_description(self) -> str:
        """Get description for current state."""
        return self._states.get(self.current_state, "")

    def set_state(self, new_state: str) -> bool:
        """Change state. Returns True if successful."""
        if new_state in self._states:
            self.current_state = new_state
            return True
        return False

    def get_state(self) -> str:
        """Get current state."""
        return self.current_state


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

def create_injury_narrative_builder() -> InjuryNarrativeBuilder:
    """Create an InjuryNarrativeBuilder instance."""
    return InjuryNarrativeBuilder()


def create_room_narrative_builder() -> RoomNarrativeBuilder:
    """Create a RoomNarrativeBuilder instance."""
    return RoomNarrativeBuilder()


def get_player_senses(entity) -> Senses:
    """Get senses for a player entity."""
    return SenseManager.update_from_entity(entity)