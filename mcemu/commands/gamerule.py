from ..command_tree.arguments import *
from ..command_tree.dispatcher import dispatcher
from ..command_tree.nodes import LiteralNode, ArgumentNode
from ..context import ExecutionContext, get_entities_from_target_strings

def exec_gamerule(ctx: ExecutionContext, rule: str, value: str = None) -> int:
    if value is not None:
        ctx.world.gamerules[rule] = value
        return 1
    return 1 if rule in ctx.world.gamerules else 0

cmd = LiteralNode("gamerule")
gr_rule = ArgumentNode("rule", WordArgument())
gr_rule.executes(exec_gamerule)
gr_val = ArgumentNode("value", WordArgument())
gr_val.executes(exec_gamerule)
gr_rule.then(gr_val)
cmd.then(gr_rule)
dispatcher.register(cmd)
