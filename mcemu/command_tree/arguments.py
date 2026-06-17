class CommandSyntaxError(Exception):
    pass


class ArgumentType:
    def get_name(self) -> str:
        return self.__class__.__name__

    def parse(self, tokens, pos: int):
        raise NotImplementedError()


class IntArgument(ArgumentType):
    def parse(self, tokens, pos: int):
        if pos >= len(tokens):
            raise CommandSyntaxError("Expected integer")
        t = tokens[pos]
        try:
            return int(t.value), pos + 1
        except ValueError:
            raise CommandSyntaxError(f"Expected integer, got '{t.value}'")


class FloatArgument(ArgumentType):
    def parse(self, tokens, pos: int):
        if pos >= len(tokens):
            raise CommandSyntaxError("Expected float")
        t = tokens[pos]
        try:
            return float(t.value), pos + 1
        except ValueError:
            raise CommandSyntaxError(f"Expected float, got '{t.value}'")


class StringArgument(ArgumentType):
    def parse(self, tokens, pos: int):
        if pos >= len(tokens):
            raise CommandSyntaxError("Expected string")
        t = tokens[pos]
        return t.value, pos + 1


class GreedyStringArgument(ArgumentType):
    def parse(self, tokens, pos: int):
        if pos >= len(tokens):
            raise CommandSyntaxError("Expected string")
        val = ""
        while pos < len(tokens):
            val += tokens[pos].value + " "
            pos += 1
        return val.strip(), pos


class PathArgument(ArgumentType):
    def parse(self, tokens, pos: int):
        if pos >= len(tokens):
            raise CommandSyntaxError("Expected path")

        val = ""
        if tokens[pos].type == "WORD":
            val += tokens[pos].value
            pos += 1

        while pos < len(tokens):
            t = tokens[pos]
            if t.value in ("/", "-", "_", ":", ".", "\\"):
                val += t.value
                pos += 1
                if pos < len(tokens) and tokens[pos].type == "WORD":
                    val += tokens[pos].value
                    pos += 1
            else:
                break

        if not val:
            raise CommandSyntaxError("Expected path")
        return val, pos


class TimeArgument(ArgumentType):
    def parse(self, tokens, pos: int):
        if pos >= len(tokens):
            raise CommandSyntaxError("Expected time")

        t = tokens[pos]
        val = t.value
        pos += 1

        multiplier = 1
        if val.endswith("t"):
            val = val[:-1]
        elif val.endswith("s"):
            val = val[:-1]
            multiplier = 20
        elif val.endswith("d"):
            val = val[:-1]
            multiplier = 24000

        try:
            return int(val) * multiplier, pos
        except ValueError:
            raise CommandSyntaxError(f"Expected time, got '{t.value}'")


class WordArgument(ArgumentType):
    def parse(self, tokens, pos: int):
        if pos >= len(tokens):
            raise CommandSyntaxError("Expected word")

        val = tokens[pos].value
        pos += 1

        while pos < len(tokens):
            t = tokens[pos]
            if t.value in (":", "."):
                val += t.value
                pos += 1
                if pos < len(tokens) and tokens[pos].type == "WORD":
                    val += tokens[pos].value
                    pos += 1
            else:
                break
        return val, pos


class ObjectiveArgument(WordArgument):
    def get_name(self) -> str:
        return "objective"


class TargetSelectorData:
    def __init__(self, base: str, arguments: dict = None, is_pseudo: bool = False):
        self.base = base
        self.arguments = arguments
        self.is_pseudo = is_pseudo


class PseudoSelectorArgument(ArgumentType):
    def get_name(self) -> str:
        return "pseudo_target"

    def parse(self, tokens, pos: int):
        if pos >= len(tokens):
            raise CommandSyntaxError("Expected target selector or name")

        t = tokens[pos]
        if t.value == "@":
            pos += 1
            if pos >= len(tokens):
                raise CommandSyntaxError("Incomplete target selector")
            base = tokens[pos].value
            pos += 1
            args = {}
            if pos < len(tokens) and tokens[pos].value == "[":
                pos += 1
                while pos < len(tokens) and tokens[pos].value != "]":
                    key_val, pos = WordArgument().parse(tokens, pos)
                    if pos >= len(tokens) or tokens[pos].value != "=":
                        raise CommandSyntaxError("Expected '=' in selector")
                    pos += 1
                    val, pos = WordArgument().parse(tokens, pos)
                    args[key_val] = val
                    if pos < len(tokens) and tokens[pos].value == ",":
                        pos += 1
                if pos >= len(tokens) or tokens[pos].value != "]":
                    raise CommandSyntaxError("Expected ']'")
                pos += 1
            return TargetSelectorData(base, args, is_pseudo=False), pos
        else:
            val, pos = WordArgument().parse(tokens, pos)
            return TargetSelectorData(val, None, is_pseudo=True), pos


class SelectorArgument(PseudoSelectorArgument):
    def get_name(self) -> str:
        return "target"


class ItemData:
    def __init__(self, item_id: str, nbt: str = ""):
        self.item_id = item_id
        self.nbt = nbt


class ItemArgument(ArgumentType):
    def get_name(self) -> str:
        return "item"

    def parse(self, tokens, pos: int):
        if pos >= len(tokens):
            raise CommandSyntaxError("Expected item")

        item_id, pos = WordArgument().parse(tokens, pos)

        if ":" not in item_id:
            item_id = f"minecraft:{item_id}"

        nbt = ""
        if pos < len(tokens) and tokens[pos].value in ("{", "["):
            open_bracket = tokens[pos].value
            close_bracket = "}" if open_bracket == "{" else "]"
            depth = 0

            while pos < len(tokens):
                val = tokens[pos].value
                if val in ("{", "["):
                    depth += 1
                elif val in ("}", "]"):
                    depth -= 1

                nbt += val if tokens[pos].type != "STRING" else f"'{val}'"
                pos += 1

                if depth == 0:
                    break

            if depth > 0:
                raise CommandSyntaxError("Unbalanced brackets in item components/NBT")

        return ItemData(item_id, nbt), pos


class SlotArgument(WordArgument):
    def get_name(self) -> str:
        return "slot"
