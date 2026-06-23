from ..command_tree.arguments import ResourceLocationArgument, NBTArgument, PathArgument
from ..command_tree.builder import literal, argument
from ..command_tree.dispatcher import dispatcher
from ..context import ExecutionContext
from .data import _build_target_branch, _get_target_leaf, _get_target_dicts, _traverse_nbt, NBTPath


def function_cmd(ctx: ExecutionContext, path: str, nbt: dict = None, **kwargs):
    if not ctx.emulator:
        print("No emulator attached to context, cannot run file.")
        return 0
    return ctx.emulator.execute_function(path, ctx.clone(), macro_args=nbt)


def function_with_cmd(ctx: ExecutionContext, path: str, target_type: str, **kwargs):
    if not ctx.emulator:
        print("No emulator attached to context, cannot run file.")
        return 0

    dicts = _get_target_dicts(ctx, target_type, kwargs)
    if not dicts:
        return 0

    nbt_path_str = kwargs.get("data_path")
    if nbt_path_str:
        _, _, macro_args = _traverse_nbt(dicts[0], NBTPath(nbt_path_str))
    else:
        macro_args = dicts[0]

    if not isinstance(macro_args, dict):
        return 0

    return ctx.emulator.execute_function(path, ctx.clone(), macro_args=macro_args)


path_arg = argument("path", ResourceLocationArgument())
path_arg.executes(function_cmd)
path_arg.then(argument("nbt", NBTArgument()).executes(function_cmd))

with_node = literal("with")
for t_type in ("block", "entity", "storage"):
    t_node = _build_target_branch(t_type)
    leaf = _get_target_leaf(t_node)

    leaf.executes(lambda ctx, t=t_type, **k: function_with_cmd(ctx, target_type=t, **k))
    leaf.then(argument("data_path", PathArgument()).executes(
        lambda ctx, t=t_type, **k: function_with_cmd(ctx, target_type=t, **k)))
    with_node.then(t_node)

path_arg.then(with_node)

func_node = literal("function").then(path_arg)
dispatcher.register(func_node)
