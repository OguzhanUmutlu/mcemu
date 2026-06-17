from ..command_tree.arguments import PathArgument, IntArgument, GreedyStringArgument
from ..command_tree.builder import literal, argument
from ..command_tree.dispatcher import dispatcher
from ..context import ExecutionContext
from ..exceptions import CommandReturn


def function_cmd(ctx: ExecutionContext, path: str, **kwargs):
    if not ctx.emulator:
        print("No emulator attached to context, cannot run file.")
        return 0
    return ctx.emulator.execute_file(path, ctx.clone())


def return_value_cmd(ctx: ExecutionContext, value: int, **kwargs):
    raise CommandReturn(value)


def return_fail_cmd(ctx: ExecutionContext, **kwargs):
    raise CommandReturn(0)


def return_run_cmd(ctx: ExecutionContext, command: str, **kwargs):
    if not ctx.emulator:
        return 0
    result = ctx.emulator.execute_command(command, ctx)
    raise CommandReturn(result)


dispatcher.register(literal("function").then(argument("path", PathArgument()).executes(function_cmd)))

dispatcher.register(literal("return").then(argument("value", IntArgument()).executes(return_value_cmd)).then(
    literal("fail").executes(return_fail_cmd)).then(
    literal("run").then(argument("command", GreedyStringArgument()).executes(return_run_cmd))))
