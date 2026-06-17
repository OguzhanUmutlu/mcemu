from ..command_tree.arguments import *
from ..command_tree.dispatcher import dispatcher
from ..command_tree.nodes import LiteralNode, ArgumentNode
from ..context import ExecutionContext, get_entities_from_target_strings

def exec_gamemode(ctx: ExecutionContext, mode: str, target: list = None) -> int:
    if target is None:
        if ctx.executor:
            ctx.executor.gamemode = mode
            return 1
        return 0
    entities = get_entities_from_target_strings(ctx, target)
    count = 0
    for entity in entities:
        entity.gamemode = mode
        count += 1
    return count

cmd = LiteralNode("gamemode")
gm_mode = ArgumentNode("mode", WordArgument())
gm_mode.executes(exec_gamemode)
gm_target = ArgumentNode("target", SelectorArgument())
gm_target.executes(exec_gamemode)
gm_mode.then(gm_target)
cmd.then(gm_mode)
dispatcher.register(cmd)
