from ..command_tree.arguments import SelectorArgument, WordArgument, IntArgument
from ..command_tree.dispatcher import dispatcher
from ..command_tree.nodes import LiteralNode, ArgumentNode
from ..context import ExecutionContext, get_entities_from_target_strings

def exec_effect_clear(ctx: ExecutionContext, target: list, effect: str = None) -> int:
    count = 0
    entities = get_entities_from_target_strings(ctx, target)
    for entity in entities:
        if effect is None:
            if entity.effects:
                count += len(entity.effects)
                entity.effects.clear()
        else:
            if effect in entity.effects:
                del entity.effects[effect]
                count += 1
    return count

def exec_effect_give(ctx: ExecutionContext, target: list, effect: str, seconds: int = 30, amplifier: int = 0, hideParticles: str = "false") -> int:
    count = 0
    entities = get_entities_from_target_strings(ctx, target)
    for entity in entities:
        entity.effects[effect] = {
            "duration": seconds * 20,
            "amplifier": amplifier,
            "hideParticles": hideParticles.lower() == "true"
        }
        count += 1
    return count

effect_cmd = LiteralNode("effect")
clear_node = LiteralNode("clear")
give_node = LiteralNode("give")

target_node_clear = ArgumentNode("target", SelectorArgument())
target_node_clear.executes(exec_effect_clear)
effect_node_clear = ArgumentNode("effect", WordArgument())
effect_node_clear.executes(exec_effect_clear)
target_node_clear.then(effect_node_clear)
clear_node.then(target_node_clear)

target_node_give = ArgumentNode("target", SelectorArgument())
effect_node_give = ArgumentNode("effect", WordArgument())
effect_node_give.executes(exec_effect_give)
seconds_node = ArgumentNode("seconds", IntArgument())
seconds_node.executes(exec_effect_give)
amp_node = ArgumentNode("amplifier", IntArgument())
amp_node.executes(exec_effect_give)
hide_node = ArgumentNode("hideParticles", WordArgument())
hide_node.executes(exec_effect_give)

amp_node.then(hide_node)
seconds_node.then(amp_node)
effect_node_give.then(seconds_node)
target_node_give.then(effect_node_give)
give_node.then(target_node_give)

effect_cmd.then(clear_node).then(give_node)
dispatcher.register(effect_cmd)
