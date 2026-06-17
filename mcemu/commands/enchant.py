from ..command_tree.arguments import SelectorArgument, WordArgument, IntArgument
from ..command_tree.dispatcher import dispatcher
from ..command_tree.nodes import LiteralNode, ArgumentNode
from ..context import ExecutionContext, get_entities_from_target_strings

def exec_enchant(ctx: ExecutionContext, target: list, enchantment: str, level: int = 1) -> int:
    count = 0
    entities = get_entities_from_target_strings(ctx, target)
    for entity in entities:
        if "weapon.mainhand" in entity.inventory:
            item = entity.inventory["weapon.mainhand"]
            if "Enchantments" not in item:
                item["Enchantments"] = {}
            item["Enchantments"][enchantment] = level
            count += 1
    return count

enchant_cmd = LiteralNode("enchant")
target_node = ArgumentNode("target", SelectorArgument())
enchantment_node = ArgumentNode("enchantment", WordArgument())
enchantment_node.executes(exec_enchant)
level_node = ArgumentNode("level", IntArgument())
level_node.executes(exec_enchant)

enchantment_node.then(level_node)
target_node.then(enchantment_node)
enchant_cmd.then(target_node)
dispatcher.register(enchant_cmd)
