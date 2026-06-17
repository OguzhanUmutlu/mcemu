from ..command_tree.arguments import *
from ..command_tree.dispatcher import dispatcher
from ..command_tree.nodes import LiteralNode, ArgumentNode
from ..context import ExecutionContext, get_entities_from_target_strings


def exec_whitelist(ctx: ExecutionContext, action: str, target: list = None) -> int:
    if action == "add" and target:
        entities = get_entities_from_target_strings(ctx, target)
        for e in entities:
            ctx.world.whitelisted.add(e.uuid)
        return len(entities)
    elif action == "remove" and target:
        entities = get_entities_from_target_strings(ctx, target)
        count = 0
        for e in entities:
            if e.uuid in ctx.world.whitelisted:
                ctx.world.whitelisted.remove(e.uuid)
                count += 1
        return count
    return 1


cmd = LiteralNode("whitelist")
wl_action = ArgumentNode("action", WordArgument())
wl_action.executes(exec_whitelist)
wl_t = ArgumentNode("target", SelectorArgument())
wl_t.executes(exec_whitelist)
wl_action.then(wl_t)
cmd.then(wl_action)
dispatcher.register(cmd)
