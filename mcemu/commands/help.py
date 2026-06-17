from ..command_tree.arguments import GreedyStringArgument
from ..command_tree.dispatcher import dispatcher
from ..command_tree.nodes import LiteralNode, ArgumentNode
from ..context import ExecutionContext

def exec_help(ctx: ExecutionContext, args: str = "") -> int:
    paths = dispatcher.get_valid_paths(dispatcher.root)
    print("\033[96mAvailable commands:\033[0m")
    for p in sorted(paths):
        print(f"  \033[92m- {p}\033[0m")
    return 1

cmd = LiteralNode("help")
args = ArgumentNode("args", GreedyStringArgument())
args.executes(exec_help)
cmd.executes(exec_help)
cmd.then(args)
dispatcher.register(cmd)
