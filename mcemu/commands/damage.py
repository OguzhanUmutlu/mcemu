from ..command_tree.arguments import *
from ..command_tree.dispatcher import dispatcher
from ..command_tree.nodes import LiteralNode, ArgumentNode
from ..context import ExecutionContext, get_entities_from_target_strings

def exec_damage(ctx: ExecutionContext, target: list, amount: float, type: str = "generic") -> int:
    entities = get_entities_from_target_strings(ctx, target)
    count = 0
    for entity in entities:
        if entity.gamemode in ("creative", "spectator"):
            continue
        entity.health -= amount
        if entity.health <= 0:
            entity.health = 0
            entity.is_dead = True
        count += 1
    return count

cmd = LiteralNode("damage")
d_target = ArgumentNode("target", SelectorArgument())
d_amount = ArgumentNode("amount", FloatArgument())
d_amount.executes(exec_damage)
d_type = ArgumentNode("type", WordArgument())
d_type.executes(exec_damage)
d_amount.then(d_type)
d_target.then(d_amount)
cmd.then(d_target)
dispatcher.register(cmd)
