import json
import os
import re
import readline
from importlib.metadata import version as get_version

from .command_tree.dispatcher import dispatcher
from .entity import World, Player, ExecutionContext
from .exceptions import CommandReturn
from .tokenizer import Tokenizer
from . import commands
_ = commands


class Emulator:
    def __init__(self, allow_functions: bool = True):
        self.world = World()
        self.allow_functions = allow_functions
        self.namespace_map = {}
        self.function_tags = {}

        self.default_player = Player("Player")
        self.world.add_entity(self.default_player)

    def execute_command(self, cmd_str: str, ctx: ExecutionContext = None) -> int:
        if not cmd_str.strip() or cmd_str.strip().startswith("#"):
            return 0
        tokens = Tokenizer(cmd_str).tokenize()
        try:
            if ctx is None:
                ctx = ExecutionContext(self.world, executor=None, position=(0.0, 0.0, 0.0), emulator=self)
            return dispatcher.dispatch(tokens, ctx)
        except Exception as e:
            if isinstance(e, CommandReturn):
                raise e
            print(f"Error parsing/executing: '{cmd_str}'\n{e}")
        return 0

    def load_datapack(self, pack_path: str) -> int:
        if not self.allow_functions:
            print("\033[91m[Security] File system access is disabled. Cannot load datapacks.\033[0m")
            return 0
            
        if not os.path.isdir(pack_path):
            print(f"Datapack path not found: {pack_path}")
            return 0
            
        mcmeta_path = os.path.join(pack_path, "pack.mcmeta")
        if not os.path.exists(mcmeta_path):
            print(f"Invalid datapack (no pack.mcmeta): {pack_path}")
            return 0
            
        data_dir = os.path.join(pack_path, "data")
        if not os.path.isdir(data_dir):
            return 1

        for ns in os.listdir(data_dir):
            ns_dir = os.path.join(data_dir, ns)
            if os.path.isdir(ns_dir):
                if ns not in self.namespace_map:
                    self.namespace_map[ns] = []
                self.namespace_map[ns].append(ns_dir)
                
                tags_dir = os.path.join(ns_dir, "tags", "functions")
                if os.path.isdir(tags_dir):
                    for root, _, files in os.walk(tags_dir):
                        for file in files:
                            if file.endswith(".json"):
                                full_path = os.path.join(root, file)
                                rel_path = os.path.relpath(full_path, tags_dir)
                                tag_id = f"{ns}:{rel_path[:-5].replace(os.sep, '/')}"
                                
                                try:
                                    with open(full_path, "r") as f:
                                        tag_data = json.load(f)
                                        if "values" in tag_data:
                                            if tag_id not in self.function_tags:
                                                self.function_tags[tag_id] = []
                                            self.function_tags[tag_id].extend(tag_data["values"])
                                except Exception as e:
                                    print(f"Error parsing tag {full_path}: {e}")
                                    
        if "minecraft:load" in self.function_tags:
            ctx = ExecutionContext(self.world, executor=None, position=(0.0, 0.0, 0.0), emulator=self)
            self.execute_function("#minecraft:load", ctx)
            
        print(f"\033[92mSuccessfully loaded datapack: {os.path.basename(pack_path)}\033[0m")
        return 1

    def execute_function(self, func_id: str, ctx: ExecutionContext = None, macro_args: dict = None) -> int:
        if not self.allow_functions:
            print("\033[91m[Security] File system access is disabled. Cannot run functions.\033[0m")
            return 0
            
        if ctx is None:
            ctx = ExecutionContext(self.world, executor=None, position=(0.0, 0.0, 0.0), emulator=self)

        if func_id.startswith("#"):
            tag_name = func_id[1:]
            if ":" not in tag_name:
                tag_name = f"minecraft:{tag_name}"
                
            if tag_name not in self.function_tags:
                return 0
                
            total_ret = 0
            for fn in self.function_tags[tag_name]:
                total_ret += self.execute_function(fn, ctx, macro_args)
            return total_ret
            
        if ":" in func_id:
            ns, path = func_id.split(":", 1)
        else:
            if os.path.exists(func_id) or os.path.exists(func_id + ".mcfunction"):
                return self.execute_file(func_id, ctx, macro_args)
            ns, path = "minecraft", func_id
            
        if ns not in self.namespace_map:
            print(f"Unknown namespace: {ns}")
            return 0
            
        target_file = None
        for base_dir in reversed(self.namespace_map[ns]):
            potential_path = os.path.join(base_dir, "functions", f"{path}.mcfunction")
            if os.path.exists(potential_path):
                target_file = potential_path
                break
                
        if target_file:
            return self.execute_file(target_file, ctx, macro_args)
        else:
            print(f"Function not found: {func_id}")
            return 0

    def execute_file(self, filepath: str, ctx: ExecutionContext = None, macro_args: dict = None) -> int:
        if not self.allow_functions:
            print("\033[91m[Security] File system access is disabled. Cannot run .mcfunction\033[0m")
            return 0
        if not os.path.exists(filepath):
            if os.path.exists(filepath + ".mcfunction"):
                filepath += ".mcfunction"
            else:
                print(f"Function file not found: {filepath}")
                return 0

        if ctx is None:
            ctx = ExecutionContext(self.world, executor=None, position=(0.0, 0.0, 0.0), emulator=self)

        try:
            with open(filepath, "r") as f:
                lines = f.readlines()
            for line in lines:
                if macro_args:
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
            self.execute_function(task["path"], task["ctx"])
            
        if "minecraft:tick" in self.function_tags:
            ctx = ExecutionContext(self.world, executor=None, position=(0.0, 0.0, 0.0), emulator=self)
            self.execute_function("#minecraft:tick", ctx)


def start_repl():
    try:
        readline.parse_and_bind(r'"\C-l": clear-screen')

        readline.parse_and_bind(r'"\e[1;5C": forward-word')
        readline.parse_and_bind(r'"\e[1;5D": backward-word')
        readline.parse_and_bind(r'"\e[5C": forward-word')
        readline.parse_and_bind(r'"\e[5D": backward-word')
    except ImportError:
        pass

    try:
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
                emu.default_player = Player("Player")
                emu.world.add_entity(emu.default_player)
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
