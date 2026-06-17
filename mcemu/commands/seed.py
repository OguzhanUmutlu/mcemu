from ..command_tree.dispatcher import dispatcher
from ..command_tree.nodes import LiteralNode
from ..context import ExecutionContext


def exec_seed(ctx: ExecutionContext) -> int:
    return ctx.world.seed


cmd = LiteralNode("seed")
cmd.executes(exec_seed)
dispatcher.register(cmd)
