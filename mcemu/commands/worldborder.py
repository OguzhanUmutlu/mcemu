from ..command_tree.arguments import *
from ..command_tree.dispatcher import dispatcher
from ..command_tree.nodes import LiteralNode, ArgumentNode
from ..context import ExecutionContext


def exec_worldborder_set(ctx: ExecutionContext, distance: float, time: int = 0) -> int:
    ctx.world.worldborder["size"] = distance
    return 1


cmd = LiteralNode("worldborder")
wb_set = LiteralNode("set")
wb_dist = ArgumentNode("distance", FloatArgument())
wb_dist.executes(exec_worldborder_set)
wb_time = ArgumentNode("time", IntArgument())
wb_time.executes(exec_worldborder_set)
wb_dist.then(wb_time)
wb_set.then(wb_dist)
cmd.then(wb_set)
dispatcher.register(cmd)
