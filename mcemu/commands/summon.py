from ..command_tree.arguments import WordArgument, GreedyStringArgument
from ..command_tree.builder import literal, argument
from ..command_tree.dispatcher import dispatcher
from ..context import ExecutionContext
from ..entity import Entity


def summon_cmd(ctx: ExecutionContext, entity_type: str, pos_x: str = "~", pos_y: str = "~", pos_z: str = "~",
               nbt: str = "{}", **kwargs):
    if ":" not in entity_type:
        entity_type = f"minecraft:{entity_type}"

    pos = ctx.position
    try:
        pos = (float(pos_x.replace("~", "") or 0) + (ctx.position[0] if "~" in pos_x else 0),
               float(pos_y.replace("~", "") or 0) + (ctx.position[1] if "~" in pos_y else 0),
               float(pos_z.replace("~", "") or 0) + (ctx.position[2] if "~" in pos_z else 0))
    except:
        pass

    entity = Entity(entity_type, pos=pos)
    import json
    try:
        parsed_nbt = json.loads(nbt)
        entity.nbt.update(parsed_nbt)
        if "Tags" in parsed_nbt:
            entity.tags.update(parsed_nbt["Tags"])
    except:
        pass

    ctx.world.add_entity(entity)
    print(f"Summoned {entity.type} at {entity.pos}")
    return 1


dispatcher.register(literal("summon").then(argument("entity_type", WordArgument()).executes(summon_cmd).then(
    argument("pos_x", WordArgument()).then(argument("pos_y", WordArgument()).then(
        argument("pos_z", WordArgument()).executes(summon_cmd).then(
            argument("nbt", GreedyStringArgument()).executes(summon_cmd)))))))
