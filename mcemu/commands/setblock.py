from ..command_tree.arguments import *
from ..command_tree.dispatcher import dispatcher
from ..command_tree.nodes import LiteralNode, ArgumentNode
from ..context import ExecutionContext


def exec_setblock(ctx: ExecutionContext, pos: tuple, block: BlockStateData) -> int:
    x, y, z = pos
    x = int(x.resolve(ctx.position[0]))
    y = int(y.resolve(ctx.position[1]))
    z = int(z.resolve(ctx.position[2]))
    if ctx.world.track_blocks:
        ctx.world.blocks[(x, y, z)] = block.block_id
    return 1


cmd = LiteralNode("setblock")
pos_node = ArgumentNode("pos", BlockPosArgument())
block_node = ArgumentNode("block", BlockStateArgument())
block_node.executes(exec_setblock)
pos_node.then(block_node)
cmd.then(pos_node)
dispatcher.register(cmd)
