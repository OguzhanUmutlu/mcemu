from typing import List, Dict, Callable, Any, Tuple

from .arguments import ArgumentType, CommandSyntaxError


class CommandNode:
    def __init__(self):
        self.children: Dict[str, "CommandNode"] = {}
        self.executable: Callable = None
        self.redirect: "CommandNode" = None
        self.modifier: Any = None

    def then(self, node: "CommandNode") -> "CommandNode":
        self.children[node.get_name()] = node
        return self

    def executes(self, func: Callable) -> "CommandNode":
        self.executable = func
        return self

    def forks(self, node: "CommandNode", modifier: Any = None) -> "CommandNode":
        self.redirect = node
        self.modifier = modifier
        return self

    def parse(self, tokens: List[Any], pos: int) -> Tuple[Any, int]:
        raise NotImplementedError()

    def get_name(self) -> str:
        raise NotImplementedError()

    def get_usage(self) -> str:
        raise NotImplementedError()


class LiteralNode(CommandNode):
    def __init__(self, literal: str):
        super().__init__()
        self.literal = literal

    def parse(self, tokens: List[Any], pos: int) -> Tuple[Any, int]:
        if pos >= len(tokens):
            raise CommandSyntaxError(f"Expected '{self.literal}'")
        if tokens[pos].value == self.literal:
            return self.literal, pos + 1
        raise CommandSyntaxError(f"Expected '{self.literal}', got '{tokens[pos].value}'")

    def get_name(self) -> str:
        return self.literal

    def get_usage(self) -> str:
        return self.literal


class ArgumentNode(CommandNode):
    def __init__(self, name: str, arg_type: ArgumentType):
        super().__init__()
        self.name = name
        self.arg_type = arg_type

    def parse(self, tokens: List[Any], pos: int) -> Tuple[Any, int]:
        return self.arg_type.parse(tokens, pos)

    def get_name(self) -> str:
        return self.name

    def get_usage(self) -> str:
        return f"<{self.name}: {self.arg_type.get_name()}>"
