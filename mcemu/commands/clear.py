from ..command_tree.arguments import SelectorArgument, ItemArgument, IntArgument, ItemData
from ..command_tree.dispatcher import dispatcher
from ..command_tree.nodes import LiteralNode, ArgumentNode
from ..context import ExecutionContext, get_entities_from_target_strings


def exec_clear(ctx: ExecutionContext, target: list, item: ItemData = None, maxCount: int = -1) -> int:
    cleared = 0
    entities = get_entities_from_target_strings(ctx, target)
    for entity in entities:
        slots_to_delete = []
        for slot, slot_item in entity.inventory.items():
            if item is None or slot_item["id"] == item.item_id:
                amount_to_clear = slot_item["count"]
                if maxCount != -1:
                    amount_to_clear = min(amount_to_clear, maxCount)
                    maxCount -= amount_to_clear

                slot_item["count"] -= amount_to_clear
                cleared += amount_to_clear

                if slot_item["count"] <= 0:
                    slots_to_delete.append(slot)

                if maxCount == 0:
                    break

        for s in slots_to_delete:
            del entity.inventory[s]

    return cleared


clear_cmd = LiteralNode("clear")
clear_cmd.executes(exec_clear)
target_node = ArgumentNode("target", SelectorArgument())
target_node.executes(exec_clear)
item_node = ArgumentNode("item", ItemArgument())
item_node.executes(exec_clear)
count_node = ArgumentNode("maxCount", IntArgument())
count_node.executes(exec_clear)

item_node.then(count_node)
target_node.then(item_node)
clear_cmd.then(target_node)
dispatcher.register(clear_cmd)
