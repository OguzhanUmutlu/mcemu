from ..command_tree.arguments import *
from ..command_tree.dispatcher import dispatcher
from ..command_tree.nodes import LiteralNode, ArgumentNode
from ..context import ExecutionContext, get_entities_from_target_strings

cmd = LiteralNode("locate")
loc_args = ArgumentNode("args", GreedyStringArgument())
loc_args.executes(lambda ctx, args: 1)
cmd.then(loc_args)
dispatcher.register(cmd)
