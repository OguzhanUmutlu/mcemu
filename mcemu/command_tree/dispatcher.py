from typing import List, Dict, Any, Tuple

from .arguments import CommandSyntaxError, TargetSelectorData
from .nodes import CommandNode, LiteralNode, ArgumentNode
from ..context import ExecutionContext, resolve_target_selector
from ..tokenizer import Token


class ParseContext:
    def __init__(self, ctx: ExecutionContext):
        self.ctx = ctx
        self.arguments: Dict[str, Any] = {}
        self.executable = None
        self.modifiers: List[Tuple[Any, Dict[str, Any]]] = []

    def clone(self):
        new_ctx = ParseContext(self.ctx)
        new_ctx.arguments = self.arguments.copy()
        new_ctx.executable = self.executable
        new_ctx.modifiers = list(self.modifiers)
        return new_ctx


class CommandDispatcher:
    def __init__(self):
        self.root = CommandNode()

    def register(self, node: CommandNode):
        self.root.children[node.get_name()] = node

    def get_valid_paths(self, node: CommandNode) -> List[str]:
        return [child.get_usage() for child in node.children.values()]

    def parse_node(self, node: CommandNode, tokens: List[Token], pos: int, parse_ctx: ParseContext) -> Tuple[
        bool, int, ParseContext, CommandNode]:

        if isinstance(node, (LiteralNode, ArgumentNode)):
            try:
                val, pos = node.parse(tokens, pos)
                if isinstance(node, ArgumentNode):
                    parse_ctx.arguments[node.name] = val
            except CommandSyntaxError:
                return False, pos, parse_ctx, node

        if node.executable:
            parse_ctx.executable = node.executable

        if pos >= len(tokens):
            if parse_ctx.executable:
                return True, pos, parse_ctx, node
            return False, pos, parse_ctx, node

        if node.redirect:
            if node.modifier:
                parse_ctx.modifiers.append((node.modifier, parse_ctx.arguments.copy()))
            return self.parse_node(node.redirect, tokens, pos, parse_ctx)

        best_fail_node = node
        best_fail_pos = pos

        for child in node.children.values():
            child_ctx = parse_ctx.clone()
            success, child_pos, final_ctx, last_node = self.parse_node(child, tokens, pos, child_ctx)
            if success:
                return True, child_pos, final_ctx, last_node

            if child_pos > best_fail_pos:
                best_fail_pos = child_pos
                best_fail_node = last_node

        return False, best_fail_pos, parse_ctx, best_fail_node

    def get_combinations(self, node: CommandNode, current_path: str = "", depth: int = 0) -> List[str]:
        if not node.children or depth >= 4:
            return [current_path.strip() + (" ..." if node.children else "")]
        combos = []
        for child in node.children.values():
            usage = child.get_usage()
            combos.extend(self.get_combinations(child, current_path + " " + usage, depth + 1))
        return list(dict.fromkeys(combos))

    def dispatch(self, tokens: List[Token], ctx: ExecutionContext) -> int:
        if not tokens:
            return 0

        parse_ctx = ParseContext(ctx)
        best_fail_pos = 0
        best_fail_node = self.root

        for child in self.root.children.values():
            child_ctx = parse_ctx.clone()
            success, pos, final_ctx, last_node = self.parse_node(child, tokens, 0, child_ctx)
            if success:
                if pos < len(tokens):
                    print(f"Error parsing: Trailing data at token {pos} ('{tokens[pos].value}')")
                    return 0
                return self.execute(final_ctx)

            if pos > best_fail_pos:
                best_fail_pos = pos
                best_fail_node = last_node

        import difflib
        err_token = tokens[best_fail_pos].value if best_fail_pos < len(tokens) else ""
        paths = self.get_valid_paths(best_fail_node)

        did_you_mean = ""
        if paths and err_token != "":
            literal_paths = [p for p in paths if not p.startswith("<")]
            matches = difflib.get_close_matches(err_token, literal_paths, n=1, cutoff=0.5)
            if matches:
                did_you_mean = f", did you mean \"{matches[0]}\"?"

        prev_tokens = " ".join([t.value for t in tokens[:best_fail_pos]])
        prefix = f"{prev_tokens} " if prev_tokens else ""

        RED = "\033[91m"
        GREEN = "\033[92m"
        YELLOW = "\033[93m"
        CYAN = "\033[96m"
        RESET = "\033[0m"

        if best_fail_node == self.root:
            print(f"{RED}Command not found: '{err_token}'{did_you_mean}{RESET}")
            print(f"{CYAN}Available commands:{RESET}")
            for p in sorted(paths):
                print(f"  {GREEN}- {p}{RESET}")
        else:
            combinations = self.get_combinations(best_fail_node, prev_tokens)
            print(f"{CYAN}Potential command combinations:{RESET}")
            for combo in combinations[:15]:
                print(f"  {GREEN}- {combo}{RESET}")
            if len(combinations) > 15:
                print(f"  {YELLOW}- ... and {len(combinations) - 15} more{RESET}")

            print(f"\n{RED}Error: {prefix}>>{err_token}<< invalid argument{did_you_mean}{RESET}")

        return 0

    def _resolve_args(self, args: dict, ctx: ExecutionContext) -> dict:
        resolved_args = {}
        for key, val in args.items():
            if isinstance(val, TargetSelectorData):
                targets = resolve_target_selector(val, ctx)
                if not targets and not val.is_pseudo:
                    print(f"No entity was found for selector {val.base}")
                resolved_args[key] = targets
            else:
                resolved_args[key] = val
        return resolved_args

    def _run_with_modifiers(self, parse_ctx: ParseContext, ctx: ExecutionContext, mod_idx: int) -> int:
        if mod_idx >= len(parse_ctx.modifiers):
            if parse_ctx.executable:
                resolved_args = self._resolve_args(parse_ctx.arguments, ctx)
                return parse_ctx.executable(ctx, **resolved_args)
            return 0

        modifier, args = parse_ctx.modifiers[mod_idx]
        resolved_args = self._resolve_args(args, ctx)

        contexts = modifier.modify(ctx, resolved_args)

        total_res = 0
        for sub_ctx in contexts:
            res = self._run_with_modifiers(parse_ctx, sub_ctx, mod_idx + 1)
            modifier.on_result(sub_ctx, resolved_args, res)
            total_res += res

        return total_res

    def execute(self, parse_ctx: ParseContext) -> int:
        return self._run_with_modifiers(parse_ctx, parse_ctx.ctx, 0)


dispatcher = CommandDispatcher()
