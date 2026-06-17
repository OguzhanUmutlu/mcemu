from typing import List, Any, Tuple

from .nodes import CommandNode
from ..tokenizer import Token


class ExecuteNode(CommandNode):
    def get_name(self) -> str:
        return "execute"

    def get_usage(self) -> str:
        return "execute <subcommands> run <command>"

    def parse(self, tokens: List[Token], pos: int) -> Tuple[Any, int]:
        pass
