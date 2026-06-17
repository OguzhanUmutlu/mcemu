from ..command_tree.arguments import *
from ..command_tree.dispatcher import dispatcher
from ..command_tree.nodes import LiteralNode, ArgumentNode
from ..context import ExecutionContext, get_entities_from_target_strings

def exec_op(ctx: ExecutionContext, target: list) -> int:
    entities = get_entities_from_target_strings(ctx, target)
    count = 0
    for entity in entities:
        ctx.world.opped.add(entity.uuid)
        count += 1
    return count

cmd = LiteralNode("op")
op_t = ArgumentNode("target", SelectorArgument())
op_t.executes(exec_op)
cmd.then(op_t)
dispatcher.register(cmd)
