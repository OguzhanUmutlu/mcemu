from ..command_tree.arguments import *
from ..command_tree.dispatcher import dispatcher
from ..command_tree.nodes import LiteralNode, ArgumentNode
from ..context import ExecutionContext, get_entities_from_target_strings

from .xp import exec_xp

cmd = LiteralNode("experience")
x_target = ArgumentNode("target", SelectorArgument())
x_amount = ArgumentNode("amount", IntArgument())
x_type = ArgumentNode("type", WordArgument())
x_amount.executes(exec_xp)
x_type.executes(exec_xp)
x_amount.then(x_type)
x_target.then(x_amount)
cmd.then(x_target)
dispatcher.register(cmd)
