from ..command_tree.arguments import ResourceLocationArgument, TimeArgument
from ..command_tree.builder import literal, argument
from ..command_tree.dispatcher import dispatcher
from ..context import ExecutionContext


def schedule_function_cmd(ctx: ExecutionContext, path: str, time: int, mode: str = "replace", **kwargs):
    target_tick = ctx.world.current_tick + time

    if mode == "replace":
        ctx.world.scheduled_tasks = [t for t in ctx.world.scheduled_tasks if t["path"] != path]

    ctx.world.scheduled_tasks.append({"tick": target_tick, "path": path, "ctx": ctx.clone(), "mode": mode})
    print(f"Scheduled {path} to run at tick {target_tick}")
    return target_tick


def schedule_clear_cmd(ctx: ExecutionContext, path: str, **kwargs):
    initial_len = len(ctx.world.scheduled_tasks)
    ctx.world.scheduled_tasks = [t for t in ctx.world.scheduled_tasks if t["path"] != path]
    removed = initial_len - len(ctx.world.scheduled_tasks)
    print(f"Cleared {removed} scheduled tasks for {path}")
    return removed


dispatcher.register(literal("schedule").then(literal("function").then(argument("path", ResourceLocationArgument()).then(
    argument("time", TimeArgument()).executes(
        lambda ctx, path, time: schedule_function_cmd(ctx, path, time, "replace")).then(
        literal("append").executes(lambda ctx, path, time: schedule_function_cmd(ctx, path, time, "append"))).then(
        literal("replace").executes(lambda ctx, path, time: schedule_function_cmd(ctx, path, time, "replace")))))).then(
    literal("clear").then(argument("path", ResourceLocationArgument()).executes(schedule_clear_cmd))))
