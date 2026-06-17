from ..command_tree.arguments import *
from ..command_tree.dispatcher import dispatcher
from ..command_tree.nodes import LiteralNode, ArgumentNode
from ..context import ExecutionContext


def exec_simple(ctx: ExecutionContext, *args) -> int:
    return 1


cmd = LiteralNode("save-off")
args = ArgumentNode("args", GreedyStringArgument())
args.executes(exec_simple)
cmd.executes(exec_simple)
cmd.then(args)
dispatcher.register(cmd)
