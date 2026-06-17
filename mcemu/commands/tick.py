from ..command_tree.arguments import TimeArgument
from ..command_tree.builder import literal, argument
from ..command_tree.dispatcher import dispatcher
from ..context import ExecutionContext


def tick_query_cmd(ctx: ExecutionContext, **kwargs):
    print(f"Current tick: {ctx.world.current_tick}")
    return ctx.world.current_tick


def tick_step_cmd(ctx: ExecutionContext, time: int, **kwargs):
    if not ctx.emulator:
        return 0
    print(f"Stepping {time} ticks...")
    for _ in range(time):
        ctx.emulator.tick()
    return time


def tick_freeze_cmd(ctx: ExecutionContext, **kwargs):
    print("Tick loop frozen (manual REPL mode).")
    return 1


def tick_unfreeze_cmd(ctx: ExecutionContext, **kwargs):
    print("Tick loop unfrozen.")
    return 1


dispatcher.register(literal("tick").then(literal("query").executes(tick_query_cmd)).then(
    literal("step").then(argument("time", TimeArgument()).executes(tick_step_cmd))).then(
    literal("freeze").executes(tick_freeze_cmd)).then(literal("unfreeze").executes(tick_unfreeze_cmd)))
