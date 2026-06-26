from ..command_tree.arguments import (
    WordArgument, IntArgument, SelectorArgument, ComponentArgument, CommandSyntaxError
)
from ..command_tree.builder import literal, argument
from ..command_tree.dispatcher import dispatcher
from ..context import ExecutionContext, resolve_target_selector

VALID_COLORS = {"blue", "green", "pink", "purple", "red", "white", "yellow"}
VALID_STYLES = {"notched_6", "notched_10", "notched_12", "notched_20", "progress"}


def _normalize_id(bossbar_id: str) -> str:
    if ":" not in bossbar_id:
        return f"minecraft:{bossbar_id}"
    return bossbar_id


def _get_bossbar(ctx: ExecutionContext, bossbar_id: str) -> dict:
    bar = ctx.world.server.bossbars.get(bossbar_id)
    if bar is None:
        raise CommandSyntaxError(f"No bossbar exists with the ID '{bossbar_id}'")
    return bar


def bossbar_add(ctx: ExecutionContext, id: str, name: str, **kwargs) -> int:
    bossbar_id = _normalize_id(id)
    if bossbar_id in ctx.world.server.bossbars:
        raise CommandSyntaxError(f"A bossbar with the ID '{bossbar_id}' already exists")
    ctx.world.server.bossbars[bossbar_id] = {
        "id": bossbar_id,
        "name": name,
        "max": 100,
        "value": 0,
        "color": "white",
        "style": "progress",
        "visible": True,
        "players": [],
    }
    print(f"Custom bossbar [{bossbar_id}] {name} has been created")
    return 1


def bossbar_remove(ctx: ExecutionContext, id: str, **kwargs) -> int:
    bossbar_id = _normalize_id(id)
    _get_bossbar(ctx, bossbar_id)
    del ctx.world.server.bossbars[bossbar_id]
    print(f"Removed custom bossbar [{bossbar_id}]")
    return 1


def bossbar_list(ctx: ExecutionContext, **kwargs) -> int:
    bars = ctx.world.server.bossbars
    count = len(bars)
    if count == 0:
        print("There are no custom bossbars active")
    else:
        ids = ", ".join(bars.keys())
        print(f"There are {count} custom bossbars: {ids}")
    return count


def bossbar_get(ctx: ExecutionContext, id: str, property: str, **kwargs) -> int:
    bossbar_id = _normalize_id(id)
    bar = _get_bossbar(ctx, bossbar_id)
    prop = property.lower()
    if prop == "max":
        val = bar["max"]
        print(f"Custom bossbar [{bossbar_id}] has a maximum of {val}")
        return val
    elif prop == "value":
        val = bar["value"]
        print(f"Custom bossbar [{bossbar_id}] has a value of {val}")
        return val
    elif prop == "visible":
        val = bar["visible"]
        print(f"Custom bossbar [{bossbar_id}] is {'visible' if val else 'hidden'}")
        return 1 if val else 0
    elif prop == "players":
        players = bar["players"]
        count = len(players)
        if count == 0:
            print(f"Custom bossbar [{bossbar_id}] has no players currently online")
        else:
            print(f"Custom bossbar [{bossbar_id}] is visible to {count} player(s): {', '.join(players)}")
        return count
    else:
        raise CommandSyntaxError(f"Invalid bossbar property '{property}'")


def bossbar_set_color(ctx: ExecutionContext, id: str, color: str, **kwargs) -> int:
    bossbar_id = _normalize_id(id)
    bar = _get_bossbar(ctx, bossbar_id)
    if color not in VALID_COLORS:
        raise CommandSyntaxError(f"Unknown color '{color}'. Valid colors: {', '.join(sorted(VALID_COLORS))}")
    if bar["color"] == color:
        return 0
    bar["color"] = color
    return 1


def bossbar_set_style(ctx: ExecutionContext, id: str, style: str, **kwargs) -> int:
    bossbar_id = _normalize_id(id)
    bar = _get_bossbar(ctx, bossbar_id)
    if style not in VALID_STYLES:
        raise CommandSyntaxError(f"Unknown style '{style}'. Valid styles: {', '.join(sorted(VALID_STYLES))}")
    if bar["style"] == style:
        return 0
    bar["style"] = style
    return 1


def bossbar_set_max(ctx: ExecutionContext, id: str, max: int, **kwargs) -> int:
    bossbar_id = _normalize_id(id)
    bar = _get_bossbar(ctx, bossbar_id)
    if max < 1:
        raise CommandSyntaxError(f"Max must be at least 1")
    if bar["max"] == max:
        return 0
    bar["max"] = max
    bar["value"] = min(bar["value"], max)
    return 1


def bossbar_set_value(ctx: ExecutionContext, id: str, value: int, **kwargs) -> int:
    bossbar_id = _normalize_id(id)
    bar = _get_bossbar(ctx, bossbar_id)
    clamped = max(0, min(value, bar["max"]))
    if bar["value"] == clamped:
        return 0
    bar["value"] = clamped
    return 1


def bossbar_set_visible(ctx: ExecutionContext, id: str, visible: str, **kwargs) -> int:
    bossbar_id = _normalize_id(id)
    bar = _get_bossbar(ctx, bossbar_id)
    if visible.lower() == "true":
        new_vis = True
    elif visible.lower() == "false":
        new_vis = False
    else:
        raise CommandSyntaxError(f"Expected 'true' or 'false', got '{visible}'")
    if bar["visible"] == new_vis:
        return 0
    bar["visible"] = new_vis
    return 1


def bossbar_set_name(ctx: ExecutionContext, id: str, name: str, **kwargs) -> int:
    bossbar_id = _normalize_id(id)
    bar = _get_bossbar(ctx, bossbar_id)
    bar["name"] = name
    return 1


def bossbar_set_players(ctx: ExecutionContext, id: str, targets=None, **kwargs) -> int:
    bossbar_id = _normalize_id(id)
    bar = _get_bossbar(ctx, bossbar_id)
    if targets is None:
        if bar["players"]:
            bar["players"] = []
            return 1
        return 0
    resolved = resolve_target_selector(targets, ctx)
    old = set(bar["players"])
    new = set(resolved)
    if old == new:
        return 0
    bar["players"] = resolved
    return 1


bossbar_root = literal("bossbar")

bossbar_root.then(
    literal("add").then(
        argument("id", WordArgument()).then(
            argument("name", ComponentArgument()).executes(bossbar_add)
        )
    )
)

bossbar_root.then(
    literal("remove").then(
        argument("id", WordArgument()).executes(bossbar_remove)
    )
)

bossbar_root.then(literal("list").executes(bossbar_list))

bossbar_root.then(
    literal("get").then(
        argument("id", WordArgument()).then(
            literal("max").executes(lambda ctx, **k: bossbar_get(ctx, property="max", **k)).then(
                argument("id", WordArgument())
            )
        )
    )
)

_get_node = argument("id", WordArgument())
for _prop in ("max", "players", "value", "visible"):
    _p = _prop
    _get_node.then(
        literal(_prop).executes(lambda ctx, prop=_p, **k: bossbar_get(ctx, property=prop, **k))
    )

bossbar_root_get = literal("get").then(_get_node)

_set_id = argument("id", WordArgument())

_set_id.then(literal("color").then(argument("color", WordArgument()).executes(bossbar_set_color)))
_set_id.then(literal("style").then(argument("style", WordArgument()).executes(bossbar_set_style)))
_set_id.then(literal("max").then(argument("max", IntArgument()).executes(bossbar_set_max)))
_set_id.then(literal("value").then(argument("value", IntArgument()).executes(bossbar_set_value)))
_set_id.then(literal("visible").then(argument("visible", WordArgument()).executes(bossbar_set_visible)))
_set_id.then(literal("name").then(argument("name", ComponentArgument()).executes(bossbar_set_name)))
_set_id.then(
    literal("players").executes(lambda ctx, **k: bossbar_set_players(ctx, **k)).then(
        argument("targets", SelectorArgument()).executes(bossbar_set_players)
    )
)

bossbar_root_set = literal("set").then(_set_id)

bossbar_cmd = literal("bossbar")
bossbar_cmd.then(literal("add").then(
    argument("id", WordArgument()).then(
        argument("name", ComponentArgument()).executes(bossbar_add)
    )
))
bossbar_cmd.then(literal("remove").then(
    argument("id", WordArgument()).executes(bossbar_remove)
))
bossbar_cmd.then(literal("list").executes(bossbar_list))
bossbar_cmd.then(bossbar_root_get)
bossbar_cmd.then(bossbar_root_set)

dispatcher.register(bossbar_cmd)
