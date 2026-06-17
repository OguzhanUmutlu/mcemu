from ..command_tree.arguments import *
from ..command_tree.dispatcher import dispatcher
from ..command_tree.nodes import LiteralNode, ArgumentNode

cmd = LiteralNode("spreadplayers")
spr_args = ArgumentNode("args", GreedyStringArgument())
spr_args.executes(lambda ctx, args: 1)
cmd.then(spr_args)
dispatcher.register(cmd)
