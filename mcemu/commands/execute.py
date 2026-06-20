from ..command_tree.arguments import SelectorArgument, ObjectiveArgument, WordArgument, FloatArgument, BlockPosArgument, BlockStateArgument, CoordinateArgument, IntRangeArgument, PathArgument
from ..command_tree.builder import literal, argument
from ..command_tree.dispatcher import dispatcher
from ..command_tree.execute_modifiers import *
from ..command_tree.nodes import CommandNode

class DummyNode(CommandNode):
    def get_name(self): return "__subcommand__"
    def get_usage(self): return ""

execute_root = literal("execute")
execute_subcommand = DummyNode()
execute_root.then(execute_subcommand)

execute_run = literal("run").forks(dispatcher.root)
execute_subcommand.then(execute_run)

# as/at
execute_subcommand.then(literal("as").then(argument("target", SelectorArgument()).forks(execute_subcommand, ExecuteAsModifier())))
execute_subcommand.then(literal("at").then(argument("target", SelectorArgument()).forks(execute_subcommand, ExecuteAtModifier())))

# store
execute_store_score = literal("score").then(argument("store_target", SelectorArgument()).then(
    argument("store_objective", ObjectiveArgument()).forks(execute_subcommand, ExecuteStoreScoreModifier())))

execute_store_result_type = argument("store_type", WordArgument()).then(
    argument("store_target", SelectorArgument()).then(argument("store_path", PathArgument()).then(
        argument("store_datatype", WordArgument()).then(
            argument("store_multiplier", FloatArgument()).forks(execute_subcommand, ExecuteStoreResultModifier())))))

execute_store_result_nbt = argument("store_nbttype", WordArgument()).then(execute_store_result_type)
execute_store = literal("store").then(
    literal("result").then(execute_store_score).then(execute_store_result_type).then(execute_store_result_nbt))
execute_subcommand.then(execute_store)

# positioned
execute_subcommand.then(
    literal("positioned").then(
        literal("as").then(argument("target", SelectorArgument()).forks(execute_subcommand, ExecutePositionedAsModifier()))
    ).then(
        argument("pos", BlockPosArgument()).forks(execute_subcommand, ExecutePositionedModifier())
    )
)

# aligned
execute_subcommand.then(literal("aligned").then(argument("axes", WordArgument()).forks(execute_subcommand, ExecuteAlignedModifier())))

# facing
execute_subcommand.then(
    literal("facing").then(
        literal("entity").then(argument("target", SelectorArgument()).then(argument("anchor", WordArgument()).forks(execute_subcommand, ExecuteFacingEntityModifier())))
    ).then(
        argument("pos", BlockPosArgument()).forks(execute_subcommand, ExecuteFacingModifier())
    )
)

# rotated
execute_subcommand.then(
    literal("rotated").then(
        literal("as").then(argument("target", SelectorArgument()).forks(execute_subcommand, ExecuteRotatedAsModifier()))
    ).then(
        argument("yaw", CoordinateArgument()).then(argument("pitch", CoordinateArgument()).forks(execute_subcommand, ExecuteRotatedModifier()))
    )
)

# anchored
execute_subcommand.then(literal("anchored").then(argument("anchor", WordArgument()).forks(execute_subcommand, ExecuteAnchoredModifier())))

# in
execute_subcommand.then(literal("in").then(argument("dimension", WordArgument()).forks(execute_subcommand, ExecuteInModifier())))

# on
execute_subcommand.then(literal("on").then(argument("relation", WordArgument()).forks(execute_subcommand, ExecuteOnModifier())))

# summon
execute_subcommand.then(literal("summon").then(argument("entity_type", WordArgument()).forks(execute_subcommand, ExecuteSummonModifier())))

# if / unless
for condition_mode in ["if", "unless"]:
    invert = (condition_mode == "unless")
    condition_node = literal(condition_mode)
    
    # block
    condition_node.then(
        literal("block").then(argument("pos", BlockPosArgument()).then(argument("block", BlockStateArgument()).forks(execute_subcommand, ExecuteIfBlockModifier(invert))))
    )
    # blocks
    condition_node.then(
        literal("blocks").then(argument("start", BlockPosArgument()).then(argument("end", BlockPosArgument()).then(
            argument("destination", BlockPosArgument()).then(argument("scan_mode", WordArgument()).forks(execute_subcommand, ExecuteIfBlocksModifier(invert)))
        )))
    )
    # data
    condition_node.then(
        literal("data").then(argument("data_type", WordArgument()).then(argument("source", WordArgument()).then(
            argument("path", PathArgument()).forks(execute_subcommand, ExecuteIfDataModifier(invert))
        )))
    )
    # entity
    condition_node.then(
        literal("entity").then(argument("target", SelectorArgument()).forks(execute_subcommand, ExecuteIfEntityModifier(invert)))
    )
    # score
    target_obj_node = argument("target_obj", ObjectiveArgument())
    score_node = literal("score").then(argument("target", SelectorArgument()).then(target_obj_node))
    target_obj_node.then(
        literal("matches").then(argument("range", IntRangeArgument()).forks(execute_subcommand, ExecuteIfScoreMatchesModifier(invert)))
    )
    target_obj_node.then(
        argument("op", WordArgument()).then(argument("source", SelectorArgument()).then(argument("source_obj", ObjectiveArgument()).forks(execute_subcommand, ExecuteIfScoreModifier(invert))))
    )
    condition_node.then(score_node)
    
    execute_subcommand.then(condition_node)

dispatcher.register(execute_root)
