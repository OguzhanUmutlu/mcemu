from ..command_tree.arguments import PathArgument, NBTArgument
from ..command_tree.builder import literal, argument
from ..command_tree.dispatcher import dispatcher
from ..context import ExecutionContext


def function_cmd(ctx: ExecutionContext, path: str, nbt: dict = None, **kwargs):
    if not ctx.emulator:
        print("No emulator attached to context, cannot run file.")
        return 0
    return ctx.emulator.execute_function(path, ctx.clone(), macro_args=nbt)


func_node = literal("function").then(argument("path", PathArgument()).executes(function_cmd).then(argument("nbt", NBTArgument()).executes(function_cmd)))
dispatcher.register(func_node)
