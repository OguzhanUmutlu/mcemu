from ..command_tree.arguments import PathArgument, WordArgument
from ..command_tree.builder import literal, argument
from ..command_tree.dispatcher import dispatcher
from ..context import ExecutionContext

def exec_datapack_load(ctx: ExecutionContext, path: str, **kwargs) -> int:
    if not ctx.emulator:
        return 0
    return ctx.emulator.load_datapack(path)

def exec_datapack_simple(ctx: ExecutionContext, **kwargs) -> int:
    return 1

dp_node = literal("datapack").then(
    literal("load").then(argument("path", PathArgument()).executes(exec_datapack_load))
).then(
    literal("enable").then(argument("name", WordArgument()).executes(exec_datapack_simple))
).then(
    literal("disable").then(argument("name", WordArgument()).executes(exec_datapack_simple))
)

dispatcher.register(dp_node)
