from ..command_tree.arguments import *
from ..command_tree.dispatcher import dispatcher
from ..command_tree.nodes import LiteralNode, ArgumentNode
from ..context import ExecutionContext


def exec_time_set(ctx: ExecutionContext, value: int) -> int:
    ctx.world.time = value
    return value


def exec_time_add(ctx: ExecutionContext, value: int) -> int:
    ctx.world.time += value
    return ctx.world.time


cmd = LiteralNode("time")
t_set = LiteralNode("set")
t_add = LiteralNode("add")
t_val1 = ArgumentNode("value", IntArgument())
t_val2 = ArgumentNode("value", IntArgument())
t_val1.executes(exec_time_set)
t_val2.executes(exec_time_add)
t_set.then(t_val1)
t_add.then(t_val2)
cmd.then(t_set).then(t_add)
dispatcher.register(cmd)
