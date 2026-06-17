from ..command_tree.arguments import *
from ..command_tree.dispatcher import dispatcher
from ..command_tree.nodes import LiteralNode, ArgumentNode
from ..context import ExecutionContext


def exec_weather(ctx: ExecutionContext, type: str, duration: int = -1) -> int:
    ctx.world.weather = type
    return 1


cmd = LiteralNode("weather")
w_type = ArgumentNode("type", WordArgument())
w_type.executes(exec_weather)
w_dur = ArgumentNode("duration", IntArgument())
w_dur.executes(exec_weather)
w_type.then(w_dur)
cmd.then(w_type)
dispatcher.register(cmd)
