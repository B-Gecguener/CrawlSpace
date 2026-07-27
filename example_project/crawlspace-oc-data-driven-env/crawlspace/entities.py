"""
Entity System Module

Provides the entity system for Crawlspace including:
- Stats (strength, constitution, dexterity, etc.)
- Body parts with chain relationships
- Injuries and their effects
- Consciousness calculations

Usage:
    - Create entities with templates from data files
    - Apply injuries and track body part quality
    - Calculate action quality based on body state
"""

import json
import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class BodyPart:
    """A single body part with quality and injury tracking."""

    id: str
    type: str
    attached: list[str]  # IDs of attached parts (children in chain)
    quality: float = 1.0
    lost: bool = False  # Part is physically gone (severed), different from quality 0
    can_be_broken: bool = True
    can_be_cut: bool = True
    can_be_bruised: bool = True
    is_critical: bool = False
    injuries: list[str] = field(default_factory=list)


@dataclass
class EntityStats:
    """Stats for an entity."""

    strength: int = 5
    constitution: int = 5
    dexterity: int = 5
    intelligence: int = 5
    willpower: int = 5
    intuition: int = 5

    def get(self, stat_name: str) -> int:
        """Get a stat value."""
        return getattr(self, stat_name, 5)

    def to_dict(self) -> dict:
        return {
            "strength": self.strength,
            "constitution": self.constitution,
            "dexterity": self.dexterity,
            "intelligence": self.intelligence,
            "willpower": self.willpower,
            "intuition": self.intuition,
        }


@dataclass
class Entity:
    """
    An entity in the game (player, creature).

    Contains stats, body parts, and vital resources.
    """

    id: str
    name: str
    template: str
    body_parts: dict[str, BodyPart] = field(default_factory=dict)
    stats: EntityStats = field(default_factory=EntityStats)

    blood: float = 1.0
    fatigue: float = 0.0
    sustenance: float = 1.0
    consciousness: float = 1.0
    alive: bool = True

    def get_part(self, part_id: str) -> Optional[BodyPart]:
        """Get a body part by ID."""
        return self.body_parts.get(part_id)

    def get_all_parts(self) -> dict[str, BodyPart]:
        """Get all body parts."""
        return self.body_parts.copy()

    def get_parts_by_type(self, part_type: str) -> list[BodyPart]:
        """Get all parts of a specific type."""
        return [p for p in self.body_parts.values() if p.type == part_type]

    def _find_part_in_chain(self, part_id: str) -> Optional[str]:
        """Find a part ID in the chain (returns ancestor or self)."""
        for pid, part in self.body_parts.items():
            if pid == part_id:
                return pid
            if part_id in part.attached:
                return pid
        return None

    def is_part_in_chain(self, part_id: str) -> bool:
        """Check if a part is part of this entity's body."""
        return part_id in self.body_parts

    def get_chain_quality(self, part_ids: list[str]) -> float:
        """
        Calculate quality for a list of part IDs.

        Key rules:
        - Lost parts (severed): The part doesn't exist = contributes 0
        - Injured parts: Quality reduced, still contributes their quality
        - Chain: If a parent is lost (not quality 0), children don't exist either
        - Each part contributes part.quality / num_parts (lost or not lost)

        Example: Walking with two legs (one lost)
        - leg_left lost=True, leg_right lost=False (quality 1.0)
        - walk_quality = 0.0 / 2 + 1.0 / 2 = 0.5

        Example: Walking with broken leg
        - leg_left quality=0.7, leg_right quality=1.0
        - walk_quality = 0.7 / 2 + 1.0 / 2 = 0.85

        Returns quality between 0.0 and 1.0.
        """
        if not part_ids:
            return 0.0

        num_parts = len(part_ids)
        total_contribution = 0.0

        for part_id in part_ids:
            part = self.body_parts.get(part_id)
            if part is None:
                continue

            if self.is_part_lost(part_id):
                continue  # Part doesn't exist

            total_contribution += part.quality / num_parts

        return total_contribution

    def is_part_lost(self, part_id: str) -> bool:
        """
        Check if a part is physically lost (severed).

        If any ancestor in the chain is lost, this part doesn't exist either.
        Quality 0 means the part is useless but NOT lost (can heal).
        """
        part = self.body_parts.get(part_id)
        if part is None:
            return False

        if part.lost:
            return True

        return self._is_ancestor_lost(part_id)

    def _is_ancestor_lost(self, part_id: str) -> bool:
        """Check if any ancestor in the chain is lost."""
        parent_map = self._build_parent_map()
        current = parent_map.get(part_id)

        while current:
            parent_part = self.body_parts.get(current)
            if parent_part and parent_part.lost:
                return True
            current = parent_map.get(current)

        return False

    def _build_parent_map(self) -> dict[str, str]:
        """Build a map of child_id -> parent_id for the whole body."""
        parent_map = {}
        for pid, part in self.body_parts.items():
            for child_id in part.attached:
                parent_map[child_id] = pid
        return parent_map

    def calculate_consciousness(self) -> float:
        """
        Calculate consciousness based on blood, fatigue, and sustenance.

        Formula from GDD:
        consciousness = (blood * (1-fatigue) * min(1, 0.2 + sustenance*2)) / 3
        """
        blood_factor = self.blood
        fatigue_factor = 1.0 - self.fatigue
        sust_factor = min(1.0, 0.2 + self.sustenance * 2.0)

        self.consciousness = (blood_factor * fatigue_factor * sust_factor) / 3.0
        return self.consciousness

    def get_action_quality(self, part_ids: list[str], stat_name: str = "strength") -> float:
        """
        Calculate quality for an action involving body parts and a stat.

        Formula from GDD:
        action_quality = stat * body_part_quality * consciousness
        """
        body_quality = self.get_chain_quality(part_ids)
        stat_value = self.stats.get(stat_name) / 10.0  # Normalize to 0-1
        consciousness = self.calculate_consciousness()

        return stat_value * body_quality * consciousness

    def apply_injury(self, injury_id: str, part_id: str) -> bool:
        """
        Apply an injury to a body part.

        Returns True if injury was applied, False if invalid.
        """
        if self.is_part_lost(part_id):
            return False

        part = self.body_parts.get(part_id)
        if part is None:
            return False

        injury = get_injury_registry().get(injury_id)
        if injury is None:
            return False

        if injury["id"] == "severed":
            part.lost = True
            part.quality = 0.0
        else:
            deficit = injury.get("quality_deficit", 0.1)
            part.quality = max(0.0, part.quality - deficit)

        if injury_id not in part.injuries:
            part.injuries.append(injury_id)

        self._check_death()
        return True

    def get_part_injuries(self, part_id: str) -> list[dict]:
        """Get detailed info about injuries on a body part."""
        part = self.body_parts.get(part_id)
        if part is None:
            return []

        injury_registry = get_injury_registry()
        injuries = []
        for injury_id in part.injuries:
            injury = injury_registry.get(injury_id)
            if injury:
                injuries.append(injury)
        return injuries

    def describe_part(self, part_id: str) -> str:
        """Get a description of a body part including injuries."""
        part = self.body_parts.get(part_id)
        if part is None:
            return "You don't have that part."

        if self.is_part_lost(part_id):
            return f"Your {part.type} is missing. It was lost."

        desc = f"Your {part.type} is at {int(part.quality * 100)}% quality."

        injuries = self.get_part_injuries(part_id)
        if injuries:
            desc += "\n\nInjuries:"
            for injury in injuries:
                desc += f"\n- {injury.get('description', injury['id'])}"
                inspect_desc = injury.get('inspect_description', '')
                if inspect_desc:
                    desc += f"\n  {inspect_desc}"

        return desc

    def _check_death(self) -> bool:
        """Check if entity should be dead based on critical injuries."""
        for part in self.body_parts.values():
            if part.is_critical and part.quality <= 0:
                self.alive = False
                self.consciousness = 0.0
                return True

        if self.blood <= 0:
            self.alive = False
            self.consciousness = 0.0
            return True

        if self.calculate_consciousness() <= 0:
            self.alive = False
            self.consciousness = 0.0
            return True

        return False

    def tick(self) -> None:
        """Process end-of-turn updates (healing, resource consumption)."""
        if not self.alive:
            return

        self.calculate_consciousness()
        self._process_healing()

    def _process_healing(self) -> None:
        """Process natural healing based on stats and resources."""
        for part in self.body_parts.values():
            if part.quality >= 1.0:
                continue

            for injury_id in part.injuries:
                injury = get_injury_registry().get(injury_id)
                if injury is None or not injury.get("healable", False):
                    continue

                healing_threshold = injury.get("healing_threshold", 0)
                healing_speed = injury.get("healing_speed", 1.0)

                if healing_threshold >= 100:
                    relieve_factor = injury.get("relieve_factor", 1.0)
                    original_deficit = injury.get("quality_deficit", 0.1)
                    part.quality = min(1.0, part.quality + original_deficit * relieve_factor)
                    if part.quality >= 1.0:
                        part.injuries.remove(injury_id)
                    continue

                healing = (
                    self.stats.constitution
                    * self.blood
                    * min(1.0, self.sustenance * 2.0)
                )
                healing_threshold += healing * healing_speed * max(0.8, self.stats.willpower / 5.0)
                self.sustenance = max(0.0, self.sustenance - healing * 0.01)


class InjuryRegistry:
    """Registry for injury definitions."""

    def __init__(self):
        self._injuries: dict = {}

    def load_from_json(self, json_path: str) -> None:
        with open(json_path, 'r') as f:
            data = json.load(f)
        for injury in data.get('injuries', []):
            self._injuries[injury['id']] = injury

    def get(self, injury_id: str) -> Optional[dict]:
        return self._injuries.get(injury_id)

    def get_all(self) -> dict:
        return self._injuries.copy()


class BodyTemplateRegistry:
    """Registry for body part templates."""

    def __init__(self):
        self._templates: dict = {}

    def load_from_json(self, json_path: str) -> None:
        with open(json_path, 'r') as f:
            data = json.load(f)
        self._templates = data.get('templates', {})

    def get(self, template_name: str) -> Optional[dict]:
        return self._templates.get(template_name)

    def get_all(self) -> dict:
        return self._templates.copy()


class StatsRegistry:
    """Registry for stat definitions."""

    def __init__(self):
        self._stats: dict = {}

    def load_from_json(self, json_path: str) -> None:
        with open(json_path, 'r') as f:
            data = json.load(f)
        self._stats = data.get('stats', {})

    def get(self, stat_name: str) -> Optional[dict]:
        return self._stats.get(stat_name)

    def get_all(self) -> dict:
        return self._stats.copy()

    def get_default(self, stat_name: str) -> int:
        stat = self._stats.get(stat_name, {})
        return stat.get('default', 5)


class EntityFactory:
    """Factory for creating entities from templates."""

    @staticmethod
    def create(template_name: str, entity_id: str, name: str) -> Entity:
        """Create an entity from a template."""
        body_registry = get_body_template_registry()
        template = body_registry.get(template_name)

        if template is None:
            raise ValueError(f"Unknown template: {template_name}")

        body_parts = {}
        for part_id, part_data in template.items():
            body_parts[part_id] = BodyPart(
                id=part_id,
                type=part_data.get('type', part_id),
                attached=part_data.get('attached', []),
                quality=part_data.get('quality', 1.0),
                can_be_broken=part_data.get('can_be_broken', True),
                can_be_cut=part_data.get('can_be_cut', True),
                can_be_bruised=part_data.get('can_be_bruised', True),
                is_critical=part_data.get('critical', False),
            )

        return Entity(
            id=entity_id,
            name=name,
            template=template_name,
            body_parts=body_parts,
            stats=EntityStats(),
        )


_injury_registry: Optional[InjuryRegistry] = None
_body_template_registry: Optional[BodyTemplateRegistry] = None
_stats_registry: Optional[StatsRegistry] = None


def get_injury_registry() -> InjuryRegistry:
    """Get the injury registry (lazy initialization)."""
    global _injury_registry
    if _injury_registry is None:
        _injury_registry = InjuryRegistry()
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        path = os.path.join(data_dir, 'injuries.json')
        if os.path.exists(path):
            _injury_registry.load_from_json(path)
    return _injury_registry


def get_body_template_registry() -> BodyTemplateRegistry:
    """Get the body template registry (lazy initialization)."""
    global _body_template_registry
    if _body_template_registry is None:
        _body_template_registry = BodyTemplateRegistry()
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        path = os.path.join(data_dir, 'body_templates.json')
        if os.path.exists(path):
            _body_template_registry.load_from_json(path)
    return _body_template_registry


def get_stats_registry() -> StatsRegistry:
    """Get the stats registry (lazy initialization)."""
    global _stats_registry
    if _stats_registry is None:
        _stats_registry = StatsRegistry()
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        path = os.path.join(data_dir, 'stats.json')
        if os.path.exists(path):
            _stats_registry.load_from_json(path)
    return _stats_registry


def create_entity(template: str, entity_id: str, name: str) -> Entity:
    """Create an entity from a template."""
    return EntityFactory.create(template, entity_id, name)