from ..command_tree.arguments import SelectorArgument
from ..command_tree.builder import literal, argument
from ..command_tree.dispatcher import dispatcher
from ..context import ExecutionContext


def kill_cmd(ctx: ExecutionContext, target: list, **kwargs):
    count = 0
    for t in target:
        entity = next((e for e in ctx.world.entities if e.uuid == t or e.name == t), None)
        if entity:
            ctx.world.remove_entity(entity)
            count += 1
    print(f"Killed {count} entities")
    return count


dispatcher.register(literal("kill").then(argument("target", SelectorArgument()).executes(kill_cmd)))
