import json

from ..command_tree.arguments import GreedyStringArgument, PseudoSelectorArgument, WordArgument
from ..command_tree.builder import literal, argument
from ..command_tree.dispatcher import dispatcher
from ..context import ExecutionContext


def set_nested_dict(d: dict, path: str, value: any):
    keys = path.split(".")
    for key in keys[:-1]:
        d = d.setdefault(key, {})
    d[keys[-1]] = value


def get_nested_dict(d: dict, path: str) -> any:
    keys = path.split(".")
    for key in keys[:-1]:
        if key not in d:
            return 0
        d = d[key]
    return d.get(keys[-1], 0)


def data_modify_set_value(ctx: ExecutionContext, target_type: str, target: list, path: str, value: str, **kwargs):
    if not target:
        return 0
    if "NBTType" in target_type:
        target_type = target_type.split(".")[-1].lower()

    res = 0
    for t in target:
        target_key = f"{target_type}:{t}"
        if target_key not in ctx.world.nbt_storage:
            ctx.world.nbt_storage[target_key] = {}

        val = value
        try:
            if "." in val:
                val = float(val)
            else:
                val = int(val)
        except ValueError:
            pass

        set_nested_dict(ctx.world.nbt_storage[target_key], path, val)
        res = 1
    return res


def data_modify_set_from(ctx: ExecutionContext, target_type: str, target: list, path: str, source_target_type: str,
                         source_target: list, source_path: str, **kwargs):
    if not target or not source_target:
        return 0

    if "NBTType" in target_type:
        target_type = target_type.split(".")[-1].lower()
    if "NBTType" in source_target_type:
        source_target_type = source_target_type.split(".")[-1].lower()

    src_key = f"{source_target_type}:{source_target[0]}"
    src_val = get_nested_dict(ctx.world.nbt_storage.get(src_key, {}), source_path)

    res = 0
    for t in target:
        target_key = f"{target_type}:{t}"
        if target_key not in ctx.world.nbt_storage:
            ctx.world.nbt_storage[target_key] = {}
        set_nested_dict(ctx.world.nbt_storage[target_key], path, src_val)
        res = 1
    return res


def data_modify_merge(ctx: ExecutionContext, target_type: str, target: list, path: str, value: str, **kwargs):
    if not target:
        return 0

    if "NBTType" in target_type:
        target_type = target_type.split(".")[-1].lower()

    try:
        val = json.loads(value)
    except:
        val = value

    res = 0
    for t in target:
        target_key = f"{target_type}:{t}"
        if target_key not in ctx.world.nbt_storage:
            ctx.world.nbt_storage[target_key] = {}
        set_nested_dict(ctx.world.nbt_storage[target_key], path, val)
        res = 1
    return res


def data_get(ctx: ExecutionContext, target_type: str, target: list, path: str, **kwargs):
    if not target:
        return 0
    if "NBTType" in target_type:
        target_type = target_type.split(".")[-1].lower()

    target_key = f"{target_type}:{target[0]}"
    val = get_nested_dict(ctx.world.nbt_storage.get(target_key, {}), path)
    if isinstance(val, (int, float)):
        return int(val)
    return 1 if val else 0


data_target_node = argument("target_type", WordArgument()).then(argument("target", PseudoSelectorArgument()).then(
    argument("path", WordArgument()).then(literal("set").then(
        literal("value").then(argument("value", WordArgument()).executes(data_modify_set_value))).then(
        literal("from").then(argument("source_target_type", WordArgument()).then(
            argument("source_target", PseudoSelectorArgument()).then(
                argument("source_path", WordArgument()).executes(data_modify_set_from)))))).then(
        literal("merge").then(literal("value").then(

            argument("value", GreedyStringArgument()).executes(data_modify_merge))))))

nbt_workaround_node = argument("nbt_type", WordArgument()).then(data_target_node)

dispatcher.register(literal("data").then(literal("modify").then(data_target_node).then(nbt_workaround_node)).then(
    literal("get").then(argument("target_type", WordArgument()).then(
        argument("target", PseudoSelectorArgument()).then(argument("path", WordArgument()).executes(data_get)))).then(

        argument("nbt_type", WordArgument()).then(argument("target_type", WordArgument()).then(
            argument("target", PseudoSelectorArgument()).then(argument("path", WordArgument()).executes(data_get)))))))
