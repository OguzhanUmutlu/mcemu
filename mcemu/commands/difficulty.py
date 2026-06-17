from ..command_tree.arguments import *
from ..command_tree.dispatcher import dispatcher
from ..command_tree.nodes import LiteralNode, ArgumentNode
from ..context import ExecutionContext, get_entities_from_target_strings

def exec_difficulty(ctx: ExecutionContext, level: str) -> int:
    ctx.world.difficulty = level
    return 1

cmd = LiteralNode("difficulty")
diff_level = ArgumentNode("level", WordArgument())
diff_level.executes(exec_difficulty)
cmd.then(diff_level)
dispatcher.register(cmd)
