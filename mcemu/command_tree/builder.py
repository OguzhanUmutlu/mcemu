from .arguments import ArgumentType
from .nodes import LiteralNode, ArgumentNode


def literal(name: str) -> LiteralNode:
    return LiteralNode(name)


def argument(name: str, arg_type: ArgumentType) -> ArgumentNode:
    return ArgumentNode(name, arg_type)
