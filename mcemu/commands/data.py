import copy
import json
import re
from typing import Any, List, Tuple

from ..command_tree.arguments import WordArgument, BlockPosArgument, NBTArgument, IntArgument, \
    FloatArgument, PathArgument, ArgumentType, CommandSyntaxError, SingleEntitySelectorArgument
from ..command_tree.builder import literal, argument
from ..command_tree.dispatcher import dispatcher
from ..context import ExecutionContext, resolve_target_selector, get_entities_from_target_strings


class NBTByte(int):
    def __str__(self): return f"{int(self)}b"

    def __repr__(self): return f"{int(self)}b"


class NBTShort(int):
    def __str__(self): return f"{int(self)}s"

    def __repr__(self): return f"{int(self)}s"


class NBTInt(int):
    def __str__(self): return str(int(self))

    def __repr__(self): return str(int(self))


class NBTLong(int):
    def __str__(self): return f"{int(self)}l"

    def __repr__(self): return f"{int(self)}l"


class NBTFloat(float):
    def __str__(self): return f"{float(self)}f"

    def __repr__(self): return f"{float(self)}f"


class NBTDouble(float):
    def __str__(self): return f"{float(self)}d"

    def __repr__(self): return f"{float(self)}d"


class NBTByteArray(list):
    pass


class NBTIntArray(list):
    pass


class NBTLongArray(list):
    pass


def to_snbt(val: Any) -> str:
    if isinstance(val, dict):
        parts = []
        for k, v in val.items():
            k_str = str(k) if re.match(r"^[a-zA-Z0-9_\-\.\+]+$", str(k)) else f'"{k}"'
            parts.append(f"{k_str}:{to_snbt(v)}")
        return "{" + ",".join(parts) + "}"
    elif isinstance(val, NBTByteArray):
        return "[B;" + ",".join(to_snbt(NBTByte(v)) for v in val) + "]"
    elif isinstance(val, NBTIntArray):
        return "[I;" + ",".join(to_snbt(NBTInt(v)) for v in val) + "]"
    elif isinstance(val, NBTLongArray):
        return "[L;" + ",".join(to_snbt(NBTLong(v)) for v in val) + "]"
    elif isinstance(val, list):
        return "[" + ",".join(to_snbt(v) for v in val) + "]"
    elif isinstance(val, str):
        val_escaped = val.replace('\\', '\\\\').replace('"', '\\"')
        return f'"{val_escaped}"'
    elif isinstance(val, bool):
        return "1b" if val else "0b"
    elif hasattr(val, "__class__") and val.__class__.__name__.startswith("NBT"):
        return str(val)
    elif isinstance(val, float):
        return f"{val}d"
    else:
        return str(val)


class DataValueArgument(ArgumentType):
    def parse(self, tokens, pos: int):
        if pos >= len(tokens):
            raise CommandSyntaxError("Expected NBT value")

        val = tokens[pos].value
        if val in ("{", "["):
            return NBTArgument().parse(tokens, pos)

        if tokens[pos].type == "STRING":
            return tokens[pos].value, pos + 1

        val_str = ""
        while pos < len(tokens):
            val_str += tokens[pos].value + " "
            pos += 1

        val_str = val_str.strip()
        parsed = val_str
        if val_str.lower() in ("true", "1b"):
            parsed = NBTByte(1)
        elif val_str.lower() in ("false", "0b"):
            parsed = NBTByte(0)
        else:
            try:
                if "f" in val_str.lower():
                    parsed = NBTFloat(float(val_str.rstrip("fdFD")))
                elif "d" in val_str.lower() or "." in val_str:
                    parsed = NBTDouble(float(val_str.rstrip("fdFD")))
                elif "b" in val_str.lower():
                    parsed = NBTByte(int(val_str.rstrip("bBsSlL")))
                elif "s" in val_str.lower():
                    parsed = NBTShort(int(val_str.rstrip("bBsSlL")))
                elif "l" in val_str.lower():
                    parsed = NBTLong(int(val_str.rstrip("bBsSlL")))
                else:
                    parsed = NBTInt(int(val_str.rstrip("bBsSlL")))
            except:
                pass

        return parsed, pos


class NBTPath:
    def __init__(self, path: str):
        self.raw_path = path
        self.segments = []
        self._parse()

    def _parse(self):
        s = self.raw_path
        i = 0
        n = len(s)

        while i < n:
            key_start = i
            depth = 0
            while i < n and not (s[i] == "." and depth == 0) and not (s[i] == "[" and depth == 0):
                if s[i] in ("{", "["):
                    depth += 1
                elif s[i] in ("}", "]"):
                    depth -= 1
                i += 1
            key = s[key_start:i]
            if key:
                self.segments.append(key)

            if i < n and s[i] == ".":
                i += 1
                continue

            while i < n and s[i] == "[":
                i += 1
                depth = 1
                start = i
                while i < n and depth > 0:
                    if s[i] == "[":
                        depth += 1
                    elif s[i] == "]":
                        depth -= 1
                    i += 1
                inner = s[start:i - 1]
                try:
                    self.segments.append(int(inner))
                except ValueError:
                    if inner == "":
                        self.segments.append(None)
                    else:
                        try:
                            self.segments.append(json.loads(inner))
                        except Exception:
                            self.segments.append(f'[{inner}]')

            if i < n and s[i] == ".":
                i += 1


def _get_target_dicts(ctx: ExecutionContext, target_type: str, args: dict) -> List[dict]:
    if target_type == "block":
        pos_arg = args.get("pos")
        if pos_arg and isinstance(pos_arg, tuple) and len(pos_arg) == 3:
            px = int(pos_arg[0].resolve(ctx.position[0]))
            py = int(pos_arg[1].resolve(ctx.position[1]))
            pz = int(pos_arg[2].resolve(ctx.position[2]))
            pos = (px, py, pz)
        else:
            pos = pos_arg
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
        if storage_id not in ctx.emulator.server.nbt_storage:
            ctx.emulator.server.nbt_storage[storage_id] = {}
        return [ctx.emulator.server.nbt_storage[storage_id]]
    return []


def _match_filter(item, filt):
    if filt is None:
        return True
    if isinstance(filt, dict):
        if not isinstance(item, dict):
            return False
        for k, v in filt.items():
            if item.get(k) != v:
                return False
        return True
    return False


def _traverse_nbt(nbt_dict: dict, path: NBTPath, create_missing: bool = False) -> Tuple[Any, Any, Any]:
    current = nbt_dict
    parent = None
    last_key = None

    for i, seg in enumerate(path.segments):
        parent = current
        last_key = seg

        if isinstance(current, dict):
            if isinstance(seg, (int, dict)) or seg is None:
                return None, None, None
            if seg not in current:
                if not create_missing:
                    return None, None, None
                next_seg = path.segments[i + 1] if i + 1 < len(path.segments) else None
                current[seg] = [] if isinstance(next_seg, int) else {}
            current = current[seg]

        elif isinstance(current, list):
            if isinstance(seg, int):
                idx = seg
                if idx < 0:
                    idx = len(current) + idx
                if idx < 0 or idx >= len(current):
                    if not create_missing:
                        return None, None, None
                    if idx == len(current):
                        next_seg = path.segments[i + 1] if i + 1 < len(path.segments) else None
                        current.append([] if isinstance(next_seg, int) else {})
                    else:
                        return None, None, None
                current = current[idx]
                last_key = idx
            elif isinstance(seg, dict) or seg is None:
                match_idx = None
                for j, item in enumerate(current):
                    if _match_filter(item, seg):
                        match_idx = j
                        break
                if match_idx is None:
                    return None, None, None
                last_key = match_idx
                current = current[match_idx]
            else:
                return None, None, None
        else:
            return None, None, None

    return parent, last_key, current


def _parse_nbt_value(val_str: str) -> Any:
    try:
        return json.loads(val_str)
    except:
        pass
    if val_str.lower() in ("true", "1b"): return NBTByte(1)
    if val_str.lower() in ("false", "0b"): return NBTByte(0)
    try:
        if "f" in val_str.lower():
            return NBTFloat(float(val_str.rstrip("fdFD")))
        elif "d" in val_str.lower() or "." in val_str:
            return NBTDouble(float(val_str.rstrip("fdFD")))
        elif "b" in val_str.lower():
            return NBTByte(int(val_str.rstrip("bBsSlL")))
        elif "s" in val_str.lower():
            return NBTShort(int(val_str.rstrip("bBsSlL")))
        elif "l" in val_str.lower():
            return NBTLong(int(val_str.rstrip("bBsSlL")))
        else:
            return NBTInt(int(val_str.rstrip("bBsSlL")))
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
        raise CommandSyntaxError("Can only merge a compound tag")

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
    elif source_type in ("from", "string"):
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

        if source_type == "string":
            if source_val is None:
                return 0

            s_val = to_snbt(source_val)
            if isinstance(source_val, str):
                s_val = source_val
            elif hasattr(source_val, "__class__") and source_val.__class__.__name__.startswith(
                    "NBT") and not isinstance(source_val, (int, float)):
                s_val = str(source_val)

            start = kwargs.get("start")
            end = kwargs.get("end")

            if start is not None:
                if end is not None:
                    s_val = s_val[start:end]
                else:
                    s_val = s_val[start:]

            source_val = s_val

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
            if not isinstance(val, dict):
                raise CommandSyntaxError("Target must be a compound tag to merge")
            if not isinstance(source_val, dict):
                raise CommandSyntaxError("Source must be a compound tag to merge")

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
        return node.then(argument("target", SingleEntitySelectorArgument()))
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
            t_node.then(argument("source_target", SingleEntitySelectorArgument()).executes(
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


def _build_string_branch(target_type: str, modify_op: str):
    node = literal("string")

    for t_type in ("block", "entity", "storage"):
        t_node = literal(t_type)
        if t_type == "block":
            t_node.then(argument("source_pos", BlockPosArgument()).then(
                argument("source_path", PathArgument()).executes(
                    lambda ctx, t=target_type, op=modify_op, **k: data_modify(ctx, target_type=t, modify_op=op,
                                                                              source_type="string",
                                                                              source_target_type="block", **k)).then(
                    argument("start", IntArgument()).executes(
                        lambda ctx, t=target_type, op=modify_op, **k: data_modify(ctx, target_type=t, modify_op=op,
                                                                                  source_type="string",
                                                                                  source_target_type="block",
                                                                                  **k)).then(
                        argument("end", IntArgument()).executes(
                            lambda ctx, t=target_type, op=modify_op, **k: data_modify(ctx, target_type=t, modify_op=op,
                                                                                      source_type="string",
                                                                                      source_target_type="block", **k))
                    )
                )
            ))
        elif t_type == "entity":
            t_node.then(argument("source_target", SingleEntitySelectorArgument()).then(
                argument("source_path", PathArgument()).executes(
                    lambda ctx, t=target_type, op=modify_op, **k: data_modify(ctx, target_type=t, modify_op=op,
                                                                              source_type="string",
                                                                              source_target_type="entity", **k)).then(
                    argument("start", IntArgument()).executes(
                        lambda ctx, t=target_type, op=modify_op, **k: data_modify(ctx, target_type=t, modify_op=op,
                                                                                  source_type="string",
                                                                                  source_target_type="entity",
                                                                                  **k)).then(
                        argument("end", IntArgument()).executes(
                            lambda ctx, t=target_type, op=modify_op, **k: data_modify(ctx, target_type=t, modify_op=op,
                                                                                      source_type="string",
                                                                                      source_target_type="entity", **k))
                    )
                )
            ))
        elif t_type == "storage":
            t_node.then(argument("source_id", WordArgument()).then(
                argument("source_path", PathArgument()).executes(
                    lambda ctx, t=target_type, op=modify_op, **k: data_modify(ctx, target_type=t, modify_op=op,
                                                                              source_type="string",
                                                                              source_target_type="storage", **k)).then(
                    argument("start", IntArgument()).executes(
                        lambda ctx, t=target_type, op=modify_op, **k: data_modify(ctx, target_type=t, modify_op=op,
                                                                                  source_type="string",
                                                                                  source_target_type="storage",
                                                                                  **k)).then(
                        argument("end", IntArgument()).executes(
                            lambda ctx, t=target_type, op=modify_op, **k: data_modify(ctx, target_type=t, modify_op=op,
                                                                                      source_type="string",
                                                                                      source_target_type="storage",
                                                                                      **k))
                    )
                )
            ))
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
    leaf.then(_build_string_branch(target_type, op))
    return node


def _get_target_leaf(node):
    if "pos" in node.children: return node.children["pos"]
    if "target" in node.children: return node.children["target"]
    if "id" in node.children: return node.children["id"]
    return node


data_root = literal("data")
get_node = literal("get")
merge_node = literal("merge")
remove_node = literal("remove")
modify_node = literal("modify")

data_root.then(get_node)
data_root.then(merge_node)
data_root.then(remove_node)
data_root.then(modify_node)

for target_type in ("block", "entity", "storage"):
    target_node_get = _build_target_branch(target_type)
    leaf_get = _get_target_leaf(target_node_get)
    leaf_get.executes(lambda ctx, t=target_type, **k: data_get(ctx, target_type=t, **k)).then(
        argument("path", PathArgument()).executes(
            lambda ctx, t=target_type, **k: data_get(ctx, target_type=t, **k)).then(
            argument("scale", FloatArgument()).executes(
                lambda ctx, t=target_type, **k: data_get(ctx, target_type=t, **k))))
    get_node.then(target_node_get)

    target_node_merge = _build_target_branch(target_type)
    leaf_merge = _get_target_leaf(target_node_merge)
    leaf_merge.then(
        argument("nbt", NBTArgument()).executes(lambda ctx, t=target_type, **k: data_merge(ctx, target_type=t, **k)))
    merge_node.then(target_node_merge)

    target_node_remove = _build_target_branch(target_type)
    leaf_remove = _get_target_leaf(target_node_remove)
    leaf_remove.then(
        argument("path", PathArgument()).executes(lambda ctx, t=target_type, **k: data_remove(ctx, target_type=t, **k)))
    remove_node.then(target_node_remove)

    target_node_modify = _build_target_branch(target_type)
    leaf_modify = _get_target_leaf(target_node_modify)

    path_node = argument("path", PathArgument())
    leaf_modify.then(path_node)

    modify_node.then(target_node_modify)

    for op in ("append", "insert", "merge", "prepend", "set"):
        path_node.then(_build_modify_op(op, target_type))

dispatcher.register(data_root)
