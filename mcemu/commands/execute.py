from ..command_tree.arguments import SelectorArgument, ObjectiveArgument, WordArgument, FloatArgument
from ..command_tree.builder import literal, argument
from ..command_tree.dispatcher import dispatcher
from ..command_tree.execute_modifiers import ExecuteAsModifier, ExecuteAtModifier, ExecuteStoreScoreModifier, \
    ExecuteStoreResultModifier
from ..command_tree.nodes import CommandNode


class DummyNode(CommandNode):
    def get_name(self): return "__subcommand__"

    def get_usage(self): return ""


execute_root = literal("execute")
execute_subcommand = DummyNode()
execute_root.then(execute_subcommand)

execute_run = literal("run").forks(dispatcher.root)

execute_as = literal("as").then(argument("target", SelectorArgument()).forks(execute_subcommand, ExecuteAsModifier()))

execute_at = literal("at").then(argument("target", SelectorArgument()).forks(execute_subcommand, ExecuteAtModifier()))

execute_store_score = literal("score").then(argument("store_target", SelectorArgument()).then(
    argument("store_objective", ObjectiveArgument()).forks(execute_subcommand, ExecuteStoreScoreModifier())))

execute_store_result_type = argument("store_type", WordArgument()).then(
    argument("store_target", SelectorArgument()).then(argument("store_path", WordArgument()).then(
        argument("store_datatype", WordArgument()).then(
            argument("store_multiplier", FloatArgument()).forks(execute_subcommand, ExecuteStoreResultModifier())))))

execute_store_result_nbt = argument("store_nbttype", WordArgument()).then(execute_store_result_type)

execute_store = literal("store").then(
    literal("result").then(execute_store_score).then(execute_store_result_type).then(execute_store_result_nbt))

execute_subcommand.then(execute_as)
execute_subcommand.then(execute_at)
execute_subcommand.then(execute_store)
execute_subcommand.then(execute_run)

dispatcher.register(execute_root)
