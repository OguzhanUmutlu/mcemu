from ..command_tree.arguments import *
from ..command_tree.dispatcher import dispatcher
from ..command_tree.nodes import LiteralNode, ArgumentNode
from ..context import ExecutionContext, get_entities_from_target_strings

def exec_attribute_base_set(ctx: ExecutionContext, target: list, attribute: str, value: float) -> int:
    entities = get_entities_from_target_strings(ctx, target)
    count = 0
    for entity in entities:
        entity.attributes[attribute] = value
        count += 1
    return count

cmd = LiteralNode("attribute")
a_target = ArgumentNode("target", SelectorArgument())
a_attr = ArgumentNode("attribute", WordArgument())
a_base = LiteralNode("base")
a_set = LiteralNode("set")
a_val = ArgumentNode("value", FloatArgument())
a_val.executes(exec_attribute_base_set)
a_set.then(a_val)
a_base.then(a_set)
a_attr.then(a_base)
a_target.then(a_attr)
cmd.then(a_target)
dispatcher.register(cmd)
