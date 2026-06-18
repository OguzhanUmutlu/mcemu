import copy
import json
import re
from typing import Any, List, Tuple

from ..command_tree.arguments import WordArgument, BlockPosArgument, SelectorArgument, \
    NBTArgument, IntArgument, FloatArgument, PathArgument, ArgumentType, CommandSyntaxError
from ..command_tree.builder import literal, argument
from ..command_tree.dispatcher import dispatcher
from ..context import ExecutionContext, resolve_target_selector, get_entities_from_target_strings


class DataValueArgument(ArgumentType):
    def parse(self, tokens, pos: int):
        if pos >= len(tokens):
            raise CommandSyntaxError("Expected NBT value")

        val = tokens[pos].value
        if val in ("{", "["):
            return NBTArgument().parse(tokens, pos)

        val_str = ""
        while pos < len(tokens):
            if tokens[pos].type == "STRING":
                val_str += f'"{tokens[pos].value}" '
            else:
                val_str += tokens[pos].value + " "
            pos += 1

        val_str = val_str.strip()
        parsed = val_str
        if val_str.lower() in ("true", "1b"):
            parsed = True
        elif val_str.lower() in ("false", "0b"):
            parsed = False
        else:
            try:
                if "." in val_str or "f" in val_str.lower() or "d" in val_str.lower():
                    parsed = float(val_str.rstrip("fdFD"))
                else:
                    parsed = int(val_str.rstrip("bBsSlL"))
            except:
                pass

        return parsed, pos


class NBTPath:
    def __init__(self, path: str):
        self.raw_path = path
        self.segments = []
        self._parse()

    def _parse(self):
        parts = self.raw_path.split(".")
        for part in parts:
            if not part:
                continue
            m = re.match(r"^([^\[]+)(?:\[(.*?)\])?$", part)
            if m:
                key = m.group(1)
                idx = m.group(2)
                self.segments.append(key)
                if idx is not None:
                    try:
                        self.segments.append(int(idx))
                    except ValueError:
                        self.segments.append(f"[{idx}]")
            else:
                self.segments.append(part)


def _get_target_dicts(ctx: ExecutionContext, target_type: str, args: dict) -> List[dict]:
    if target_type == "block":
        pos = args.get("pos")
        if pos not in ctx.world.block_nbt:
            ctx.world.block_nbt[pos] = {}
        return [ctx.world.block_nbt[pos]]
    elif target_type == "entity":
        target_selector = args.get("target")
        target_strs = resolve_target_selector(target_selector, ctx)
        entities = get_entities_from_target_strings(ctx, target_strs)
        return [e.nbt for e in entities]
    elif target_type == "storage":
        storage_id = args.get("id")
        if storage_id not in ctx.world.nbt_storage:
            ctx.world.nbt_storage[storage_id] = {}
        return [ctx.world.nbt_storage[storage_id]]
    return []


def _traverse_nbt(nbt_dict: dict, path: NBTPath, create_missing: bool = False) -> Tuple[Any, Any, Any]:
    current = nbt_dict
    parent = None
    last_key = None

    for i, seg in enumerate(path.segments):
        parent = current
        last_key = seg

        if isinstance(current, dict):
            if seg not in current:
                if not create_missing:
                    return None, None, None
                if i + 1 < len(path.segments) and isinstance(path.segments[i + 1], int):
                    current[seg] = []
                else:
                    current[seg] = {}
            current = current[seg]
        elif isinstance(current, list):
            if not isinstance(seg, int):
                return None, None, None
            if seg < 0:
                seg = len(current) + seg
            if seg < 0 or seg >= len(current):
                if not create_missing:
                    return None, None, None
                if seg == len(current):
                    if i + 1 < len(path.segments) and isinstance(path.segments[i + 1], int):
                        current.append([])
                    else:
                        current.append({})
                else:
                    return None, None, None
            current = current[seg]
            last_key = seg
        else:
            return None, None, None

    return parent, last_key, current


def _parse_nbt_value(val_str: str) -> Any:
    try:
        return json.loads(val_str)
    except:
        pass
    if val_str.lower() in ("true", "1b"): return True
    if val_str.lower() in ("false", "0b"): return False
    try:
        if "." in val_str or "f" in val_str.lower() or "d" in val_str.lower():
            return float(val_str.rstrip("fdFD"))
        else:
            return int(val_str.rstrip("bBsSlL"))
    except:
        return val_str


def data_get(ctx: ExecutionContext, target_type: str, **kwargs):
    dicts = _get_target_dicts(ctx, target_type, kwargs)
    if not dicts: return 0
    path_str = kwargs.get("path")
    if not path_str:
        return 1

    scale = kwargs.get("scale", 1.0)

    parent, last_key, val = _traverse_nbt(dicts[0], NBTPath(path_str))
    if val is None:
        return 0

    if isinstance(val, (int, float)):
        return int(val * scale)
    elif isinstance(val, list):
        return len(val)
    elif isinstance(val, dict):
        return len(val.keys())
    elif isinstance(val, str):
        return len(val)
    return 1


def data_merge(ctx: ExecutionContext, target_type: str, **kwargs):
    dicts = _get_target_dicts(ctx, target_type, kwargs)
    if not dicts: return 0

    val_dict = kwargs.get("nbt", {})
    if not isinstance(val_dict, dict):
        return 0

    res = 0
    for d in dicts:
        d.update(val_dict)
        res = 1
    return res


def data_remove(ctx: ExecutionContext, target_type: str, **kwargs):
    dicts = _get_target_dicts(ctx, target_type, kwargs)
    if not dicts: return 0

    path = NBTPath(kwargs.get("path"))
    res = 0
    for d in dicts:
        parent, last_key, val = _traverse_nbt(d, path)
        if parent is not None and last_key is not None:
            try:
                del parent[last_key]
                res = 1
            except:
                pass
    return res


def data_modify(ctx: ExecutionContext, target_type: str, modify_op: str, source_type: str, **kwargs):
    dicts = _get_target_dicts(ctx, target_type, kwargs)
    if not dicts: return 0

    path = NBTPath(kwargs.get("path"))

    source_val = None
    if source_type == "value":
        source_val = kwargs.get("value")
    elif source_type == "from":
        src_target_type = kwargs.get("source_target_type")
        src_dicts = _get_target_dicts(ctx, src_target_type,
                                      {"pos": kwargs.get("source_pos"), "target": kwargs.get("source_target"),
                                          "id": kwargs.get("source_id")})
        if src_dicts:
            src_path_str = kwargs.get("source_path")
            if src_path_str:
                _, _, source_val = _traverse_nbt(src_dicts[0], NBTPath(src_path_str))
            else:
                source_val = src_dicts[0]

    if source_val is None:
        return 0

    source_val = copy.deepcopy(source_val)

    res = 0
    for d in dicts:
        parent, last_key, val = _traverse_nbt(d, path, create_missing=True)
        if parent is None or last_key is None:
            continue

        if modify_op == "set":
            parent[last_key] = source_val
            res = 1
        elif modify_op == "merge":
            if isinstance(val, dict) and isinstance(source_val, dict):
                val.update(source_val)
                res = 1
        elif modify_op in ("append", "prepend", "insert"):
            if not isinstance(val, list):
                val = []
                parent[last_key] = val

            if modify_op == "append":
                val.append(source_val)
            elif modify_op == "prepend":
                val.insert(0, source_val)
            elif modify_op == "insert":
                idx = kwargs.get("index", 0)
                val.insert(idx, source_val)
            res = 1

    return res


def _build_target_branch(name: str):
    node = literal(name)
    if name == "block":
        return node.then(argument("pos", BlockPosArgument()))
    elif name == "entity":
        return node.then(argument("target", SelectorArgument()))
    elif name == "storage":
        return node.then(argument("id", WordArgument()))
    return node


def _build_source_branch(target_type: str, modify_op: str):
    node = literal("from")

    for t_type in ("block", "entity", "storage"):
        t_node = literal(t_type)
        if t_type == "block":
            t_node.then(argument("source_pos", BlockPosArgument()).executes(
                lambda ctx, t=target_type, op=modify_op, **k: data_modify(ctx, target_type=t, modify_op=op,
                                                                          source_type="from",
                                                                          source_target_type="block", **k)).then(
                argument("source_path", PathArgument()).executes(
                    lambda ctx, t=target_type, op=modify_op, **k: data_modify(ctx, target_type=t, modify_op=op,
                                                                              source_type="from",
                                                                              source_target_type="block", **k))))
        elif t_type == "entity":
            t_node.then(argument("source_target", SelectorArgument()).executes(
                lambda ctx, t=target_type, op=modify_op, **k: data_modify(ctx, target_type=t, modify_op=op,
                                                                          source_type="from",
                                                                          source_target_type="entity", **k)).then(
                argument("source_path", PathArgument()).executes(
                    lambda ctx, t=target_type, op=modify_op, **k: data_modify(ctx, target_type=t, modify_op=op,
                                                                              source_type="from",
                                                                              source_target_type="entity", **k))))
        elif t_type == "storage":
            t_node.then(argument("source_id", WordArgument()).executes(
                lambda ctx, t=target_type, op=modify_op, **k: data_modify(ctx, target_type=t, modify_op=op,
                                                                          source_type="from",
                                                                          source_target_type="storage", **k)).then(
                argument("source_path", PathArgument()).executes(
                    lambda ctx, t=target_type, op=modify_op, **k: data_modify(ctx, target_type=t, modify_op=op,
                                                                              source_type="from",
                                                                              source_target_type="storage", **k))))
        node.then(t_node)

    return node


def _build_modify_op(op: str, target_type: str):
    node = literal(op)

    leaf = node
    if op == "insert":
        idx_node = argument("index", IntArgument())
        node.then(idx_node)
        leaf = idx_node

    val_node = literal("value").then(argument("value", DataValueArgument()).executes(
        lambda ctx, t=target_type, **k: data_modify(ctx, target_type=t, modify_op=op, source_type="value", **k)))
    leaf.then(val_node)

    leaf.then(_build_source_branch(target_type, op))
    return node


def _get_target_leaf(node):
    if "pos" in node.children: return node.children["pos"]
    if "target" in node.children: return node.children["target"]
    if "id" in node.children: return node.children["id"]
    return node


data_root = literal("data")

for target_type in ("block", "entity", "storage"):
    get_node = literal("get")
    target_node_get = _build_target_branch(target_type)
    leaf_get = _get_target_leaf(target_node_get)
    leaf_get.executes(lambda ctx, t=target_type, **k: data_get(ctx, target_type=t, **k)).then(
        argument("path", PathArgument()).executes(
            lambda ctx, t=target_type, **k: data_get(ctx, target_type=t, **k)).then(
            argument("scale", FloatArgument()).executes(
                lambda ctx, t=target_type, **k: data_get(ctx, target_type=t, **k))))
    get_node.then(target_node_get)
    data_root.then(get_node)

    merge_node = literal("merge")
    target_node_merge = _build_target_branch(target_type)
    leaf_merge = _get_target_leaf(target_node_merge)
    leaf_merge.then(
        argument("nbt", NBTArgument()).executes(lambda ctx, t=target_type, **k: data_merge(ctx, target_type=t, **k)))
    merge_node.then(target_node_merge)
    data_root.then(merge_node)

    remove_node = literal("remove")
    target_node_remove = _build_target_branch(target_type)
    leaf_remove = _get_target_leaf(target_node_remove)
    leaf_remove.then(
        argument("path", PathArgument()).executes(lambda ctx, t=target_type, **k: data_remove(ctx, target_type=t, **k)))
    remove_node.then(target_node_remove)
    data_root.then(remove_node)

    modify_node = literal("modify")
    target_node_modify = _build_target_branch(target_type)
    leaf_modify = _get_target_leaf(target_node_modify)

    path_node = argument("path", PathArgument())
    leaf_modify.then(path_node)

    modify_node.then(target_node_modify)

    for op in ("append", "insert", "merge", "prepend", "set"):
        path_node.then(_build_modify_op(op, target_type))

    data_root.then(modify_node)

dispatcher.register(data_root)
