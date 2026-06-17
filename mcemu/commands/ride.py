from ..command_tree.arguments import *
from ..command_tree.dispatcher import dispatcher
from ..command_tree.nodes import LiteralNode, ArgumentNode
from ..context import ExecutionContext, get_entities_from_target_strings

def exec_ride_mount(ctx: ExecutionContext, target: list, vehicle: list) -> int:
    return 1

def exec_ride_dismount(ctx: ExecutionContext, target: list) -> int:
    return 1

cmd = LiteralNode("ride")
r_target = ArgumentNode("target", SelectorArgument())
r_mount = LiteralNode("mount")
r_vehicle = ArgumentNode("vehicle", SelectorArgument())
r_vehicle.executes(exec_ride_mount)
r_mount.then(r_vehicle)
r_dismount = LiteralNode("dismount")
r_dismount.executes(exec_ride_dismount)
r_target.then(r_mount)
r_target.then(r_dismount)
cmd.then(r_target)
dispatcher.register(cmd)
