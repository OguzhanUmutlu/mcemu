from ..command_tree.arguments import *
from ..command_tree.dispatcher import dispatcher
from ..command_tree.nodes import LiteralNode, ArgumentNode
from ..context import ExecutionContext, get_entities_from_target_strings

def exec_defaultgamemode(ctx: ExecutionContext, mode: str) -> int:
    return 1

cmd = LiteralNode("defaultgamemode")
dgm_mode = ArgumentNode("mode", WordArgument())
dgm_mode.executes(exec_defaultgamemode)
cmd.then(dgm_mode)
dispatcher.register(cmd)
