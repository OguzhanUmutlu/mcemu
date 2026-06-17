from ..command_tree.arguments import *
from ..command_tree.dispatcher import dispatcher
from ..command_tree.nodes import LiteralNode, ArgumentNode
from ..context import ExecutionContext, get_entities_from_target_strings

def exec_fill(ctx: ExecutionContext, pos1: tuple, pos2: tuple, block: BlockStateData) -> int:
    x1, y1, z1 = int(pos1[0].resolve(ctx.position[0])), int(pos1[1].resolve(ctx.position[1])), int(pos1[2].resolve(ctx.position[2]))
    x2, y2, z2 = int(pos2[0].resolve(ctx.position[0])), int(pos2[1].resolve(ctx.position[1])), int(pos2[2].resolve(ctx.position[2]))
    min_x, max_x = min(x1, x2), max(x1, x2)
    min_y, max_y = min(y1, y2), max(y1, y2)
    min_z, max_z = min(z1, z2), max(z1, z2)
    
    count = 0
    if ctx.world.track_blocks:
        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                for z in range(min_z, max_z + 1):
                    ctx.world.blocks[(x, y, z)] = block.block_id
                    count += 1
    else:
        count = (max_x - min_x + 1) * (max_y - min_y + 1) * (max_z - min_z + 1)
    return count

cmd = LiteralNode("fill")
pos1_node = ArgumentNode("pos1", BlockPosArgument())
pos2_node = ArgumentNode("pos2", BlockPosArgument())
fill_block_node = ArgumentNode("block", BlockStateArgument())
fill_block_node.executes(exec_fill)
pos2_node.then(fill_block_node)
pos1_node.then(pos2_node)
cmd.then(pos1_node)
dispatcher.register(cmd)
