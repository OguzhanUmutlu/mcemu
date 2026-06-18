from mcemu.commands.data import _traverse_nbt, NBTPath
from ..command_tree.arguments import GreedyStringArgument, SelectorArgument, NBTArgument, ComponentArgument
from ..command_tree.dispatcher import dispatcher
from ..command_tree.nodes import LiteralNode, ArgumentNode
from ..context import ExecutionContext, get_entities_from_target_strings


def format_text_component(comp, ctx: ExecutionContext = None) -> str:
    if isinstance(comp, str):
        return comp
    if isinstance(comp, list):
        return "".join(format_text_component(c, ctx) for c in comp)
    if isinstance(comp, dict):
        text = comp.get("text", "")

        if "score" in comp and ctx:
            score_data = comp["score"]
            try:
                val = ctx.world.get_score(score_data.get("name", ""), score_data.get("objective", ""))
                text += str(val) if val is not None else ""
            except RuntimeError:
                pass

        if "nbt" in comp and ctx:
            path = comp["nbt"]
            if "storage" in comp:
                target_key = comp['storage']
                d = ctx.world.nbt_storage.get(target_key, {})
                parent, last_key, val = _traverse_nbt(d, NBTPath(path))
                if val is not None:
                    text += str(val)

        if "extra" in comp:
            text += "".join(format_text_component(c, ctx) for c in comp["extra"])

        color_map = {"black": "30", "dark_blue": "34", "dark_green": "32", "dark_aqua": "36", "dark_red": "31",
                     "dark_purple": "35", "gold": "33", "gray": "37", "dark_gray": "90", "blue": "94", "green": "92",
                     "aqua": "96", "red": "91", "light_purple": "95", "yellow": "93", "white": "97"}
        color_code = color_map.get(comp.get("color", ""), "")

        formats = []
        if comp.get("bold"): formats.append("1")
        if comp.get("italic"): formats.append("3")
        if comp.get("underline"): formats.append("4")
        if comp.get("strikethrough"): formats.append("9")

        codes = []
        if color_code: codes.append(color_code)
        codes.extend(formats)

        if not codes:
            return text

        code_str = ";".join(codes)
        return f"\033[{code_str}m{text}\033[0m"
    return ""


def exec_print(ctx: ExecutionContext, message: str) -> int:
    name = "Server"
    if ctx.executor:
        name = ctx.executor.name if ctx.executor.name else ctx.executor.uuid
    print(f"\033[95m[{name}] {message}\033[0m")
    return 1


def exec_tellraw(ctx: ExecutionContext, target: list, message: dict) -> int:
    entities = get_entities_from_target_strings(ctx, target)
    formatted = format_text_component(message, ctx)
    print(formatted)
    return len(entities)


def exec_simple(ctx: ExecutionContext, *args) -> int:
    return 1


for name in ["say", "tell", "msg", "w", "me", "teammsg"]:
    cmd = LiteralNode(name)
    msg = ArgumentNode("message", GreedyStringArgument())
    msg.executes(exec_print)
    cmd.then(msg)
    dispatcher.register(cmd)

tellraw_cmd = LiteralNode("tellraw")
tr_target = ArgumentNode("target", SelectorArgument())
tr_msg = ArgumentNode("message", ComponentArgument())
tr_msg.executes(exec_tellraw)
tr_target.then(tr_msg)
tellraw_cmd.then(tr_target)
dispatcher.register(tellraw_cmd)

for name in ["title", "tm", "bossbar", "particle", "playsound", "stopsound", "dialog", "forceload", "list", "transfer",
             "team", "setidletimeout"]:
    cmd = LiteralNode(name)
    args = ArgumentNode("args", GreedyStringArgument())
    args.executes(exec_simple)
    cmd.executes(exec_simple)
    cmd.then(args)
    dispatcher.register(cmd)
