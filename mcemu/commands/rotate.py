from ..command_tree.arguments import *
from ..command_tree.dispatcher import dispatcher
from ..command_tree.nodes import LiteralNode, ArgumentNode
from ..context import ExecutionContext, get_entities_from_target_strings

cmd = LiteralNode("rotate")
rot_args = ArgumentNode("args", GreedyStringArgument())
rot_args.executes(lambda ctx, args: 1)
cmd.then(rot_args)
dispatcher.register(cmd)
