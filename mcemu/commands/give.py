from ..command_tree.arguments import SelectorArgument, ItemArgument, IntArgument, ItemData
from ..command_tree.dispatcher import dispatcher
from ..command_tree.nodes import LiteralNode, ArgumentNode
from ..context import ExecutionContext, get_entities_from_target_strings

def exec_give(ctx: ExecutionContext, target: list, item: ItemData, count: int = 1) -> int:
    total_given = 0
    entities = get_entities_from_target_strings(ctx, target)
    for entity in entities:
        found = False
        for i in range(36):
            slot_name = f"inventory.{i}"
            if slot_name not in entity.inventory:
                entity.inventory[slot_name] = {"id": item.item_id, "count": count, "nbt": item.nbt}
                total_given += count
                found = True
                break
        if not found:
            entity.inventory["inventory.overflow"] = {"id": item.item_id, "count": count, "nbt": item.nbt}
            total_given += count
    return total_given

give_cmd = LiteralNode("give")
target_node = ArgumentNode("target", SelectorArgument())
item_node = ArgumentNode("item", ItemArgument())
item_node.executes(exec_give)
count_node = ArgumentNode("count", IntArgument())
count_node.executes(exec_give)

item_node.then(count_node)
target_node.then(item_node)
give_cmd.then(target_node)
dispatcher.register(give_cmd)
