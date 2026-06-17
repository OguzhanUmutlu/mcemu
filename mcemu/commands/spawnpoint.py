from ..command_tree.arguments import *
from ..command_tree.dispatcher import dispatcher
from ..command_tree.nodes import LiteralNode, ArgumentNode
from ..context import ExecutionContext, get_entities_from_target_strings


def exec_spawnpoint(ctx: ExecutionContext, target: list, pos: tuple = None) -> int:
    entities = get_entities_from_target_strings(ctx, target)
    count = 0
    for entity in entities:
        count += 1
    return count


cmd = LiteralNode("spawnpoint")
sp_t = ArgumentNode("target", SelectorArgument())
sp_p = ArgumentNode("pos", BlockPosArgument())
sp_p.executes(exec_spawnpoint)
sp_t.executes(exec_spawnpoint)
cmd.executes(lambda ctx: 1)
sp_t.then(sp_p)
cmd.then(sp_t)
dispatcher.register(cmd)
