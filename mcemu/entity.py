import uuid
from typing import Dict, Any, Set, List, Tuple


class Entity:
    def __init__(self, entity_type: str, pos: Tuple[float, float, float] = (0.0, 0.0, 0.0)):
        self.uuid = str(uuid.uuid4())
        self.type = entity_type
        self.name = ""
        self.pos = pos
        self.rotation = (0.0, 0.0)

        self.tags: Set[str] = set()
        self.scores: Dict[str, int] = {}
        self.nbt: Dict[str, Any] = {}
        self.team: str = None

        self.is_dead = False

    def __repr__(self):
        return f"Entity(type={self.type}, uuid={self.uuid[:8]})"


class Player(Entity):
    def __init__(self, name: str, pos: Tuple[float, float, float] = (0.0, 0.0, 0.0)):
        super().__init__("minecraft:player", pos)
        self.name = name
        self.gamemode = "survival"
        self.uuid = name


class World:
    def __init__(self):
        self.entities: List[Entity] = []
        self.scoreboards: Dict[str, Dict[str, int]] = {}
        self.objectives: Dict[str, Dict[str, str]] = {}
        self.nbt_storage: Dict[str, Dict[str, Any]] = {}
        self.current_tick: int = 0
        self.scheduled_tasks: List[Dict[str, Any]] = []

    def add_entity(self, entity: Entity):
        self.entities.append(entity)

    def remove_entity(self, entity: Entity):
        entity.is_dead = True
        if entity in self.entities:
            self.entities.remove(entity)

    def get_score(self, target_str: str, objective: str) -> int:
        if objective == "__flare__constant__":
            try:
                return int(target_str.split("_")[0])
            except:
                pass
        if objective not in self.objectives:
            raise RuntimeError(f"Objective '{objective}' does not exist")
        return self.scoreboards.get(objective, {}).get(target_str, 0)

    def set_score(self, target_str: str, objective: str, value: int):
        if objective not in self.objectives:
            raise RuntimeError(f"Objective '{objective}' does not exist")
        if objective not in self.scoreboards:
            self.scoreboards[objective] = {}
        self.scoreboards[objective][target_str] = value


class ExecutionContext:
    def __init__(self, world: World, executor: Entity = None, position: Tuple[float, float, float] = (0.0, 0.0, 0.0),
                 emulator=None):
        self.world = world
        self.executor = executor
        self.position = position
        self.emulator = emulator

    def clone(self):
        return ExecutionContext(self.world, self.executor, self.position, self.emulator)
