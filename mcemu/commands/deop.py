from ..command_tree.arguments import *
from ..command_tree.dispatcher import dispatcher
from ..command_tree.nodes import LiteralNode, ArgumentNode
from ..context import ExecutionContext, get_entities_from_target_strings

def exec_deop(ctx: ExecutionContext, target: list) -> int:
    entities = get_entities_from_target_strings(ctx, target)
    count = 0
    for entity in entities:
        if entity.uuid in ctx.world.server.opped:
            ctx.world.server.opped.remove(entity.uuid)
            count += 1
    return count

cmd = LiteralNode("deop")
deop_t = ArgumentNode("target", SelectorArgument())
deop_t.executes(exec_deop)
cmd.then(deop_t)
dispatcher.register(cmd)
