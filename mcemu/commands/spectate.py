from ..command_tree.arguments import *
from ..command_tree.dispatcher import dispatcher
from ..command_tree.nodes import LiteralNode, ArgumentNode
from ..context import ExecutionContext


def exec_spectate(ctx: ExecutionContext, target: list, player: list = None) -> int:
    return 1


cmd = LiteralNode("spectate")
spec_t = ArgumentNode("target", SelectorArgument())
spec_p = ArgumentNode("player", SelectorArgument())
spec_p.executes(exec_spectate)
spec_t.executes(exec_spectate)
spec_t.then(spec_p)
cmd.then(spec_t)
dispatcher.register(cmd)
