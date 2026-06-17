from ..command_tree.arguments import *
from ..command_tree.dispatcher import dispatcher
from ..command_tree.nodes import LiteralNode, ArgumentNode
from ..context import ExecutionContext, get_entities_from_target_strings

def exec_pardon(ctx: ExecutionContext, target: list) -> int:
    entities = get_entities_from_target_strings(ctx, target)
    count = 0
    for entity in entities:
        if entity.uuid in ctx.world.banned:
            ctx.world.banned.remove(entity.uuid)
            count += 1
    return count

cmd = LiteralNode("pardon")
pardon_t = ArgumentNode("target", SelectorArgument())
pardon_t.executes(exec_pardon)
cmd.then(pardon_t)
dispatcher.register(cmd)
