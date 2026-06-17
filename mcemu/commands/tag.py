from ..command_tree.arguments import SelectorArgument, WordArgument
from ..command_tree.builder import literal, argument
from ..command_tree.dispatcher import dispatcher
from ..context import ExecutionContext


def tag_cmd(ctx: ExecutionContext, target: list, action: str, tag: str = None, **kwargs):
    count = 0
    for t in target:
        entity = next((e for e in ctx.world.entities if e.uuid == t or e.name == t), None)
        if entity:
            if action == "add" and tag:
                entity.tags.add(tag)
            elif action == "remove" and tag:
                if tag in entity.tags:
                    entity.tags.remove(tag)
            elif action == "list":
                print(f"Entity {t} tags: {entity.tags}")
            count += 1
    return count


dispatcher.register(literal("tag").then(argument("target", SelectorArgument()).then(literal("add").then(
    argument("tag", WordArgument()).executes(lambda ctx, target, tag: tag_cmd(ctx, target, "add", tag)))).then(
    literal("remove").then(
        argument("tag", WordArgument()).executes(lambda ctx, target, tag: tag_cmd(ctx, target, "remove", tag)))).then(
    literal("list").executes(lambda ctx, target: tag_cmd(ctx, target, "list")))))
