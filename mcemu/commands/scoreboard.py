from ..command_tree.arguments import IntArgument, ObjectiveArgument, PseudoSelectorArgument, WordArgument
from ..command_tree.builder import literal, argument
from ..command_tree.dispatcher import dispatcher
from ..context import ExecutionContext


def scoreboard_objectives_add(ctx: ExecutionContext, objective: str, criteria: str, **kwargs):
    ctx.world.objectives[objective] = {"criteria": criteria, "displayname": objective}
    return 1


def scoreboard_objectives_remove(ctx: ExecutionContext, objective: str, **kwargs):
    if objective in ctx.world.objectives:
        del ctx.world.objectives[objective]
    if objective in ctx.world.scoreboards:
        del ctx.world.scoreboards[objective]
    return 1


def scoreboard_players_set(ctx: ExecutionContext, target: list, objective: str, value: int, **kwargs):
    res = 0
    for t in target:
        ctx.world.set_score(t, objective, value)
        res = value
    return res


def scoreboard_players_add(ctx: ExecutionContext, target: list, objective: str, value: int, **kwargs):
    res = 0
    for t in target:
        val = ctx.world.get_score(t, objective) + value
        ctx.world.set_score(t, objective, val)
        res = val
    return res


def scoreboard_players_remove(ctx: ExecutionContext, target: list, objective: str, value: int, **kwargs):
    res = 0
    for t in target:
        val = ctx.world.get_score(t, objective) - value
        ctx.world.set_score(t, objective, val)
        res = val
    return res


def scoreboard_players_get(ctx: ExecutionContext, target: list, objective: str, **kwargs):
    if not target:
        return 0
    return ctx.world.get_score(target[0], objective)


def scoreboard_players_operation(ctx: ExecutionContext, target: list, objective: str, op: str, source: list,
                                 source_obj: str, **kwargs):
    if not source:
        return 0

    res = 0
    for t in target:
        src_val = ctx.world.get_score(source[0], source_obj)
        val = ctx.world.get_score(t, objective)

        if op == "=":
            val = src_val
        elif op == "+=":
            val += src_val
        elif op == "-=":
            val -= src_val
        elif op == "*=":
            val *= src_val
        elif op == "/=":
            if src_val != 0:
                val = int(val / src_val)
            else:
                raise ZeroDivisionError("Scoreboard division by zero")
        elif op == "%=":
            if src_val != 0:
                val %= src_val
            else:
                raise ZeroDivisionError("Scoreboard modulo by zero")
        elif op == "<":
            val = min(val, src_val)
        elif op == ">":
            val = max(val, src_val)
        elif op == "><":
            ctx.world.set_score(source[0], source_obj, val)
            val = src_val

        ctx.world.set_score(t, objective, int(val))
        res = int(val)
    return res


dispatcher.register(literal("scoreboard").then(literal("objectives").then(literal("add").then(
    argument("objective", ObjectiveArgument()).then(
        argument("criteria", WordArgument()).executes(scoreboard_objectives_add)))).then(
    literal("remove").then(argument("objective", ObjectiveArgument()).executes(scoreboard_objectives_remove)))).then(
    literal("players").then(literal("set").then(argument("target", PseudoSelectorArgument()).then(
        argument("objective", ObjectiveArgument()).then(
            argument("value", IntArgument()).executes(scoreboard_players_set))))).then(literal("add").then(
        argument("target", PseudoSelectorArgument()).then(argument("objective", ObjectiveArgument()).then(
            argument("value", IntArgument()).executes(scoreboard_players_add))))).then(literal("remove").then(
        argument("target", PseudoSelectorArgument()).then(argument("objective", ObjectiveArgument()).then(
            argument("value", IntArgument()).executes(scoreboard_players_remove))))).then(literal("get").then(
        argument("target", PseudoSelectorArgument()).then(
            argument("objective", ObjectiveArgument()).executes(scoreboard_players_get)))).then(
        literal("operation").then(argument("target", PseudoSelectorArgument()).then(
            argument("objective", ObjectiveArgument()).then(argument("op", WordArgument()).then(
                argument("source", PseudoSelectorArgument()).then(
                    argument("source_obj", ObjectiveArgument()).executes(scoreboard_players_operation)))))))))
