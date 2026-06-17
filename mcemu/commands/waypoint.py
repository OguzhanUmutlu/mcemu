from ..command_tree.arguments import *
from ..command_tree.dispatcher import dispatcher
from ..command_tree.nodes import LiteralNode, ArgumentNode

cmd = LiteralNode("waypoint")
wp_args = ArgumentNode("args", GreedyStringArgument())
wp_args.executes(lambda ctx, args: 1)
cmd.then(wp_args)
dispatcher.register(cmd)
