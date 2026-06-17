from ..command_tree.arguments import SelectorArgument, WordArgument
from ..command_tree.builder import literal, argument
from ..command_tree.dispatcher import dispatcher
from ..context import ExecutionContext


def tp_destination_cmd(ctx: ExecutionContext, target: list, destination: list, **kwargs):
    if not target or not destination:
        return 0

    dest_entity = next((e for e in ctx.world.entities if e.uuid == destination[0] or e.name == destination[0]), None)
    if not dest_entity:
        return 0

    count = 0
    for t in target:
        entity = next((e for e in ctx.world.entities if e.uuid == t or e.name == t), None)
        if entity:
            entity.pos = dest_entity.pos
            count += 1
    print(f"Teleported {count} entities to {dest_entity.pos}")
    return count


def tp_pos_cmd(ctx: ExecutionContext, target: list, pos_x: str, pos_y: str, pos_z: str, **kwargs):
    if not target:
        return 0

    try:
        pos = (float(pos_x.replace("~", "") or 0) + (ctx.position[0] if "~" in pos_x else 0),
               float(pos_y.replace("~", "") or 0) + (ctx.position[1] if "~" in pos_y else 0),
               float(pos_z.replace("~", "") or 0) + (ctx.position[2] if "~" in pos_z else 0))
    except:
        pos = ctx.position

    count = 0
    for t in target:
        entity = next((e for e in ctx.world.entities if e.uuid == t or e.name == t), None)
        if entity:
            entity.pos = pos
            count += 1
    print(f"Teleported {count} entities to {pos}")
    return count


tp_target = argument("target", SelectorArgument())
tp_target.then(argument("destination", SelectorArgument()).executes(tp_destination_cmd))
tp_target.then(argument("pos_x", WordArgument()).then(
    argument("pos_y", WordArgument()).then(argument("pos_z", WordArgument()).executes(tp_pos_cmd))))

dispatcher.register(literal("tp").then(tp_target))
dispatcher.register(literal("teleport").then(tp_target))
