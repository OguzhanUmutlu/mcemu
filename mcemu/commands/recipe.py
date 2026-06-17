from ..command_tree.arguments import *
from ..command_tree.dispatcher import dispatcher
from ..command_tree.nodes import LiteralNode, ArgumentNode
from ..context import ExecutionContext, get_entities_from_target_strings

def exec_recipe(ctx: ExecutionContext, target: list, action: str, recipe: str) -> int:
    return 1

cmd = LiteralNode("recipe")
r_action = ArgumentNode("action", WordArgument())
r_target = ArgumentNode("target", SelectorArgument())
r_name = ArgumentNode("recipe", WordArgument())
r_name.executes(exec_recipe)
r_target.then(r_name)
r_action.then(r_target)
cmd.then(r_action)
dispatcher.register(cmd)
