from ..command_tree.arguments import *
from ..command_tree.dispatcher import dispatcher
from ..command_tree.nodes import LiteralNode, ArgumentNode
from ..context import ExecutionContext


def exec_setworldspawn(ctx: ExecutionContext, pos: tuple = None) -> int:
    return 1


cmd = LiteralNode("setworldspawn")
sws_p = ArgumentNode("pos", BlockPosArgument())
sws_p.executes(exec_setworldspawn)
cmd.executes(lambda ctx: 1)
cmd.then(sws_p)
dispatcher.register(cmd)
