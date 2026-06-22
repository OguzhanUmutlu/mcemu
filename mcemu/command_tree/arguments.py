import json
import re


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


class IntRangeArgument(ArgumentType):
    def get_name(self) -> str:
        return "int_range"

    def parse(self, tokens, pos: int):
        if pos >= len(tokens):
            raise CommandSyntaxError("Expected integer range")

        val = ""
        start_pos = pos
        while pos < len(tokens):
            t = tokens[pos]
            if ".." in t.value:
                val += t.value
                pos += 1
            elif t.value in ("..", "-") or t.value.isdigit() or (t.value.startswith("-") and t.value[1:].isdigit()):
                val += t.value
                pos += 1
            else:
                break

        if not val:
            raise CommandSyntaxError("Expected integer range")

        min_val = None
        max_val = None

        if ".." in val:
            parts = val.split("..", 1)
            if parts[0]:
                min_val = int(parts[0])
            if parts[1]:
                max_val = int(parts[1])
        else:
            min_val = int(val)
            max_val = min_val

        return (min_val, max_val), pos


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


class NBTArgument(ArgumentType):
    def get_name(self) -> str:
        return "nbt"

    def parse(self, tokens, pos: int):
        if pos >= len(tokens):
            raise CommandSyntaxError("Expected NBT")

        nbt_str = ""
        if tokens[pos].value not in ("{", "["):
            raise CommandSyntaxError("Expected '{' or '[' for NBT compound/array")

        depth = 0
        while pos < len(tokens):
            val = tokens[pos].value
            if val in ("{", "["):
                depth += 1
            elif val in ("}", "]"):
                depth -= 1

            nbt_str += val if tokens[pos].type != "STRING" else f'"{val}"'
            pos += 1

            if depth == 0:
                break

        if depth > 0:
            raise CommandSyntaxError("Unbalanced braces/brackets in NBT")

        dict_str = nbt_str
        dict_str = re.sub(r'(?<!["\'\w])([a-zA-Z0-9_]+)\s*:', r'"\1":', dict_str)
        dict_str = re.sub(r'\[\s*[a-zA-Z]\s*;\s*', '[', dict_str)
        try:
            nbt_dict = json.loads(dict_str)
            return nbt_dict, pos
        except Exception:
            return {} if nbt_str.startswith("{") else [], pos


class ComponentArgument(ArgumentType):
    def get_name(self) -> str:
        return "component"

    def parse(self, tokens, pos: int):
        if pos >= len(tokens):
            raise CommandSyntaxError("Expected JSON component")

        val = tokens[pos].value
        if val in ("{", "["):
            return NBTArgument().parse(tokens, pos)
        elif tokens[pos].type == "STRING":
            return tokens[pos].value, pos + 1
        elif val.isdigit() or (val.startswith("-") and val[1:].isdigit()):
            return val, pos + 1
        elif val.lower() in ("true", "false"):
            return val.lower() == "true", pos + 1
        else:
            raise CommandSyntaxError("Expected JSON text component")


class ResourceLocationArgument(ArgumentType):
    def parse(self, tokens, pos: int):
        if pos >= len(tokens):
            raise CommandSyntaxError("Expected resource location")

        val = ""
        while pos < len(tokens):
            t = tokens[pos]
            if t.type == "WORD":
                val += t.value
                pos += 1
            elif t.value in (":", "/", "-", "_", "."):
                val += t.value
                pos += 1
            else:
                break

        if not val:
            raise CommandSyntaxError("Expected resource location")

        return val, pos


class PathArgument(ArgumentType):
    def parse(self, tokens, pos: int):
        if pos >= len(tokens):
            raise CommandSyntaxError("Expected path")

        val = ""
        t = tokens[pos]
        if t.type in ("WORD", "STRING"):
            val += t.value if t.type == "WORD" else f'"{t.value}"'
            pos += 1
        elif t.value == "[":
            pass
        else:
            raise CommandSyntaxError("Expected path")

        while pos < len(tokens):
            t = tokens[pos]
            if t.value == ".":
                val += "."
                pos += 1
                if pos < len(tokens) and tokens[pos].type in ("WORD", "STRING"):
                    val += tokens[pos].value if tokens[pos].type == "WORD" else f'"{tokens[pos].value}"'
                    pos += 1
            elif t.value == "[":
                val += "["
                pos += 1
                depth = 1
                while pos < len(tokens) and depth > 0:
                    inner_t = tokens[pos]
                    if inner_t.value == "[":
                        depth += 1
                    elif inner_t.value == "]":
                        depth -= 1

                    if inner_t.type == "STRING":
                        val += f'"{inner_t.value}"'
                    else:
                        val += inner_t.value
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
        if t.value.startswith("@"):
            if len(t.value) == 1:
                pos += 1
                if pos >= len(tokens):
                    raise CommandSyntaxError("Incomplete target selector")
                base = tokens[pos].value
                pos += 1
            else:
                base = t.value[1:]
                pos += 1
            args = {}
            if pos < len(tokens) and tokens[pos].value == "[":
                is_selector_args = False
                if pos + 1 < len(tokens) and tokens[pos + 1].value == "]":
                    is_selector_args = True
                elif pos + 2 < len(tokens) and tokens[pos + 2].value == "=":
                    is_selector_args = True

                if is_selector_args:
                    pos += 1
                    while pos < len(tokens) and tokens[pos].value != "]":
                        key_val, pos = WordArgument().parse(tokens, pos)
                        if pos >= len(tokens) or tokens[pos].value != "=":
                            raise CommandSyntaxError("Expected '=' in selector")
                        pos += 1
                        val, pos = WordArgument().parse(tokens, pos)

                        if key_val == "type":
                            if val.startswith("!") and ":" not in val:
                                val = f"!minecraft:{val[1:]}"
                            elif not val.startswith("!") and ":" not in val:
                                val = f"minecraft:{val}"

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


class CoordinateData:
    def __init__(self, value: float, is_relative: bool, is_local: bool):
        self.value = value
        self.is_relative = is_relative
        self.is_local = is_local

    def resolve(self, base: float) -> float:
        if self.is_relative or self.is_local:
            return base + self.value
        return self.value


class CoordinateArgument(ArgumentType):
    def get_name(self) -> str:
        return "coordinate"

    def parse(self, tokens, pos: int):
        if pos >= len(tokens):
            raise CommandSyntaxError("Expected coordinate")

        t = tokens[pos].value
        is_rel = False
        is_loc = False
        val_str = t

        if t.startswith("~"):
            is_rel = True
            val_str = t[1:]
        elif t.startswith("^"):
            is_loc = True
            val_str = t[1:]

        val = 0.0
        if val_str:
            try:
                val = float(val_str)
            except ValueError:
                raise CommandSyntaxError(f"Invalid coordinate: {t}")

        return CoordinateData(val, is_rel, is_loc), pos + 1


class BlockPosArgument(ArgumentType):
    def get_name(self) -> str:
        return "block_pos"

    def parse(self, tokens, pos: int):
        x, pos = CoordinateArgument().parse(tokens, pos)
        y, pos = CoordinateArgument().parse(tokens, pos)
        z, pos = CoordinateArgument().parse(tokens, pos)
        return (x, y, z), pos


class BlockStateData:
    def __init__(self, block_id: str, state: str = "", nbt: str = ""):
        self.block_id = block_id
        self.state = state
        self.nbt = nbt


class BlockStateArgument(ArgumentType):
    def get_name(self) -> str:
        return "block_state"

    def parse(self, tokens, pos: int):
        if pos >= len(tokens):
            raise CommandSyntaxError("Expected block state")

        block_id, pos = WordArgument().parse(tokens, pos)
        if ":" not in block_id:
            block_id = f"minecraft:{block_id}"

        state = ""
        nbt = ""

        if pos < len(tokens) and tokens[pos].value == "[":
            depth = 0
            while pos < len(tokens):
                val = tokens[pos].value
                if val == "[":
                    depth += 1
                elif val == "]":
                    depth -= 1
                state += val
                pos += 1
                if depth == 0: break

        if pos < len(tokens) and tokens[pos].value == "{":
            depth = 0
            while pos < len(tokens):
                val = tokens[pos].value
                if val == "{":
                    depth += 1
                elif val == "}":
                    depth -= 1
                nbt += val
                pos += 1
                if depth == 0: break

        return BlockStateData(block_id, state, nbt), pos
