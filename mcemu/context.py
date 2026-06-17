from typing import List

from .command_tree.arguments import TargetSelectorData
from .entity import ExecutionContext, Player


def resolve_target_selector(selector: TargetSelectorData, ctx: ExecutionContext) -> List[str]:
    if not isinstance(selector, TargetSelectorData):
        return []

    if selector.arguments is None:
        return [selector.base]

    targets = []

    candidates = []
    if selector.base == "a":
        candidates = [e for e in ctx.world.entities if isinstance(e, Player)]
    elif selector.base == "e":
        candidates = ctx.world.entities[:]
    elif selector.base == "p":
        if isinstance(ctx.executor, Player):
            candidates = [ctx.executor]
        else:
            players = [e for e in ctx.world.entities if isinstance(e, Player)]
            if players:
                candidates = [players[0]]
    elif selector.base == "s":
        if ctx.executor:
            candidates = [ctx.executor]
    elif selector.base == "r":
        import random
        if ctx.world.entities:
            candidates = [random.choice(ctx.world.entities)]

    for entity in candidates:
        valid = True
        if selector.arguments:
            for key, val in selector.arguments.items():
                if key == "type":
                    if val.startswith("!"):
                        if entity.type == val[1:]:
                            valid = False
                    elif entity.type != val and entity.type != f"minecraft:{val}":
                        valid = False
                elif key == "tag":
                    if val.startswith("!"):
                        if val[1:] in entity.tags:
                            valid = False
                    elif val not in entity.tags:
                        valid = False
        if valid:
            target_str = entity.name if entity.name else entity.uuid
            targets.append(target_str)

    if selector.arguments and "limit" in selector.arguments:
        limit = int(selector.arguments["limit"])
        targets = targets[:limit]

    return targets


def resolve_single_target(selector: TargetSelectorData, ctx: ExecutionContext) -> str:
    targets = resolve_target_selector(selector, ctx)
    if not targets:
        return ""
    return targets[0]
