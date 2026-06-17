from ..command_tree.arguments import *
from ..command_tree.dispatcher import dispatcher
from ..command_tree.nodes import LiteralNode, ArgumentNode
from ..context import ExecutionContext, get_entities_from_target_strings

def exec_ban(ctx: ExecutionContext, target: list, reason: str = "") -> int:
    entities = get_entities_from_target_strings(ctx, target)
    count = 0
    for entity in entities:
        ctx.world.banned.add(entity.uuid)
        count += 1
    return count

cmd = LiteralNode("ban")
ban_t = ArgumentNode("target", SelectorArgument())
ban_reason = ArgumentNode("reason", GreedyStringArgument())
ban_reason.executes(exec_ban)
ban_t.executes(exec_ban)
ban_t.then(ban_reason)
cmd.then(ban_t)
dispatcher.register(cmd)
