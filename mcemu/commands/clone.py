from ..command_tree.arguments import *
from ..command_tree.dispatcher import dispatcher
from ..command_tree.nodes import LiteralNode, ArgumentNode
from ..context import ExecutionContext, get_entities_from_target_strings

def exec_clone(ctx: ExecutionContext, pos1: tuple, pos2: tuple, dest: tuple) -> int:
    x1, y1, z1 = int(pos1[0].resolve(ctx.position[0])), int(pos1[1].resolve(ctx.position[1])), int(pos1[2].resolve(ctx.position[2]))
    x2, y2, z2 = int(pos2[0].resolve(ctx.position[0])), int(pos2[1].resolve(ctx.position[1])), int(pos2[2].resolve(ctx.position[2]))
    dx, dy, dz = int(dest[0].resolve(ctx.position[0])), int(dest[1].resolve(ctx.position[1])), int(dest[2].resolve(ctx.position[2]))
    
    min_x, max_x = min(x1, x2), max(x1, x2)
    min_y, max_y = min(y1, y2), max(y1, y2)
    min_z, max_z = min(z1, z2), max(z1, z2)
    
    count = 0
    if ctx.world.track_blocks:
        cloned_blocks = {}
        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                for z in range(min_z, max_z + 1):
                    b = ctx.world.blocks.get((x, y, z), "minecraft:air")
                    cloned_blocks[(dx + (x - min_x), dy + (y - min_y), dz + (z - min_z))] = b
                    count += 1
        ctx.world.blocks.update(cloned_blocks)
    else:
        count = (max_x - min_x + 1) * (max_y - min_y + 1) * (max_z - min_z + 1)
    return count

cmd = LiteralNode("clone")
cpos1 = ArgumentNode("pos1", BlockPosArgument())
cpos2 = ArgumentNode("pos2", BlockPosArgument())
dest_pos = ArgumentNode("dest", BlockPosArgument())
dest_pos.executes(exec_clone)
cpos2.then(dest_pos)
cpos1.then(cpos2)
cmd.then(cpos1)
dispatcher.register(cmd)
