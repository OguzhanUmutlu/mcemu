from .command_tree.dispatcher import dispatcher
from .entity import World, Player, ExecutionContext
from .tokenizer import Tokenizer
import mcemu.commands  # Register commands



class Emulator:
    def __init__(self):
        self.world = World()

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

    def execute_file(self, filepath: str, ctx: ExecutionContext = None) -> int:
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

    emu = Emulator()
    print("\033[96mMinecraft Command Engine v3.0 (Programmatic API)\033[0m")
    print("\033[93mType 'exit' to quit, 'scores' to list scoreboards, 'entities' to list entities.\033[0m")
    while True:
        try:
            cmd = input("\033[94mmcemu> \033[0m")
            if not cmd.strip():
                continue
            if cmd.strip().lower() == "exit":
                break
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
            res = emu.execute_command(cmd)
            if res != 0:
                print(f"\033[92mdata returned {res}\033[0m")
        except KeyboardInterrupt:
            break
        except EOFError:
            break


if __name__ == "__main__":
    start_repl()
