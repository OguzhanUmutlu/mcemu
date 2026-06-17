from ..command_tree.arguments import SelectorArgument, ItemArgument, IntArgument, SlotArgument, ItemData
from ..command_tree.dispatcher import dispatcher
from ..command_tree.nodes import LiteralNode, ArgumentNode
from ..context import ExecutionContext, get_entities_from_target_strings

def exec_item_replace_entity(ctx: ExecutionContext, target: list, slot: str, item: ItemData, count: int = 1) -> int:
    changed = 0
    entities = get_entities_from_target_strings(ctx, target)
    for entity in entities:
        entity.inventory[slot] = {"id": item.item_id, "count": count, "nbt": item.nbt}
        changed += 1
    return changed

item_cmd = LiteralNode("item")
replace_node = LiteralNode("replace")
entity_node = LiteralNode("entity")

target_node = ArgumentNode("target", SelectorArgument())
slot_node = ArgumentNode("slot", SlotArgument())
with_node = LiteralNode("with")
item_arg_node = ArgumentNode("item", ItemArgument())
item_arg_node.executes(exec_item_replace_entity)
count_node = ArgumentNode("count", IntArgument())
count_node.executes(exec_item_replace_entity)

item_arg_node.then(count_node)
with_node.then(item_arg_node)
slot_node.then(with_node)
target_node.then(slot_node)
entity_node.then(target_node)
replace_node.then(entity_node)
item_cmd.then(replace_node)
dispatcher.register(item_cmd)
