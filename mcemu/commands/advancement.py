from ..command_tree.arguments import *
from ..command_tree.dispatcher import dispatcher
from ..command_tree.nodes import LiteralNode, ArgumentNode
from ..context import ExecutionContext, get_entities_from_target_strings

def exec_advancement(ctx: ExecutionContext, target: list, action: str, adv: str) -> int:
    entities = get_entities_from_target_strings(ctx, target)
    count = 0
    for entity in entities:
        if action == "grant":
            entity.advancements.add(adv)
            count += 1
        elif action == "revoke":
            if adv in entity.advancements:
                entity.advancements.remove(adv)
                count += 1
    return count

cmd = LiteralNode("advancement")
adv_action = ArgumentNode("action", WordArgument())
adv_target = ArgumentNode("target", SelectorArgument())
adv_name = ArgumentNode("advancement", WordArgument())
adv_name.executes(exec_advancement)
adv_target.then(adv_name)
adv_action.then(adv_target)
cmd.then(adv_action)
dispatcher.register(cmd)
