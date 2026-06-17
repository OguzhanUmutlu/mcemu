from .command_tree.dispatcher import dispatcher
from .entity import World, Player, ExecutionContext
from .tokenizer import Tokenizer


class Emulator:
    def __init__(self, allow_functions: bool = True):
        self.world = World()
        self.allow_functions = allow_functions

        self.dev_player = Player("Dev")
        self.world.add_entity(self.dev_player)

    def execute_command(self, cmd_str: str, ctx: ExecutionContext = None) -> int:
        if not cmd_str.strip() or cmd_str.strip().startswith("#"):
            return 0
        tokens = Tokenizer(cmd_str).tokenize()
        try:
            if ctx is None:
                ctx = ExecutionContext(self.world, executor=self.dev_player, position=self.dev_player.pos,
                                       emulator=self)
            return dispatcher.dispatch(tokens, ctx)
        except Exception as e:
            from .exceptions import CommandReturn
            if isinstance(e, CommandReturn):
                raise e
            print(f"Error parsing/executing: '{cmd_str}'\n{e}")
        return 0

    def execute_file(self, filepath: str, ctx: ExecutionContext = None, macro_args: dict = None) -> int:
        if not self.allow_functions:
            print("\033[91m[Security] File system access is disabled. Cannot run .mcfunction\033[0m")
            return 0
        from .exceptions import CommandReturn
        import os
        if not os.path.exists(filepath):
            if os.path.exists(filepath + ".mcfunction"):
                filepath += ".mcfunction"
            else:
                print(f"Function file not found: {filepath}")
                return 0

        if ctx is None:
            ctx = ExecutionContext(self.world, executor=self.dev_player, position=self.dev_player.pos, emulator=self)

        try:
            with open(filepath, "r") as f:
                lines = f.readlines()
            for line in lines:
                if macro_args:
                    import re
                    def replace_macro(match):
                        key = match.group(1)
                        if key in macro_args:
                            return str(macro_args[key])
                        return match.group(0)

                    line = re.sub(r'\$\(([a-zA-Z0-9_]+)\)', replace_macro, line)
                self.execute_command(line, ctx)
        except CommandReturn as e:
            return e.value
        return 1

    def tick(self):
        self.world.current_tick += 1
        tasks_to_run = [t for t in self.world.scheduled_tasks if t["tick"] <= self.world.current_tick]
        self.world.scheduled_tasks = [t for t in self.world.scheduled_tasks if t["tick"] > self.world.current_tick]

        for task in tasks_to_run:
            self.execute_file(task["path"], task["ctx"])


def start_repl():
    try:
        import readline

        readline.parse_and_bind(r'"\C-l": clear-screen')

        readline.parse_and_bind(r'"\e[1;5C": forward-word')
        readline.parse_and_bind(r'"\e[1;5D": backward-word')
        readline.parse_and_bind(r'"\e[5C": forward-word')
        readline.parse_and_bind(r'"\e[5D": backward-word')
    except ImportError:
        pass

    try:
        from importlib.metadata import version as get_version
        version_str = "v" + get_version("mcemu")
    except Exception:
        version_str = "v1.0"

    emu = Emulator()
    print(f"\033[96mMinecraft Command Engine {version_str} (Programmatic API)\033[0m")
    print(
        "\033[93mSpecial commands: exit, reset, scores, entities, toggleblocks, getblock <x> <y> <z>, returncode\033[0m")
    last_returncode = 0
    while True:
        try:
            cmd = input("\033[94mmcemu> \033[0m")
            if not cmd.strip():
                continue
            if cmd.strip().lower() == "exit":
                break
            elif cmd.strip().lower() == "returncode":
                print(f"\033[92mLast return code: {last_returncode}\033[0m")
                continue
            elif cmd.strip().lower() == "scores":
                import json
                print(json.dumps(emu.world.scoreboards, indent=2))
                continue
            elif cmd.strip().lower() == "entities":
                for e in emu.world.entities:
                    print(f"- {e.uuid} ({e.type}) at {e.pos} tags: {e.tags}")
                    if e.inventory:
                        print(f"  inventory: {e.inventory}")
                    if e.effects:
                        print(f"  effects: {e.effects}")
                continue
            elif cmd.strip().lower() == "reset":
                emu.world = World()
                emu.dev_player = Player("Dev")
                emu.world.add_entity(emu.dev_player)
                print("\033[92mWorld reset successfully.\033[0m")
                continue
            elif cmd.strip().lower() == "toggleblocks":
                emu.world.track_blocks = not emu.world.track_blocks
                state = "enabled" if emu.world.track_blocks else "disabled"
                print(f"\033[92mBlock tracking {state}.\033[0m")
                continue
            elif cmd.strip().lower().startswith("getblock "):
                parts = cmd.strip().split()
                if len(parts) == 4:
                    try:
                        x, y, z = int(parts[1]), int(parts[2]), int(parts[3])
                        block = emu.world.blocks.get((x, y, z), "minecraft:air")
                        print(f"\033[92mBlock at {x} {y} {z}: {block}\033[0m")
                    except ValueError:
                        print("\033[91mInvalid coordinates. Usage: getblock <x> <y> <z>\033[0m")
                else:
                    print("\033[91mUsage: getblock <x> <y> <z>\033[0m")
                continue
            res = emu.execute_command(cmd)
            last_returncode = res
        except KeyboardInterrupt:
            break
        except EOFError:
            break


if __name__ == "__main__":
    start_repl()
