# mcemu

A lightweight, programmatic, and interactive Minecraft Command Emulator designed as a standalone Python library and REPL
environment. It simulates a virtual Minecraft environment, allowing you to test, debug, and execute complex command
sequences and `.mcfunction` files without needing to launch the game!

## 🚀 Features

- **Interactive REPL Environment:** Start the engine right from your terminal and type commands in real time. Features
  colored syntax feedback, auto-suggestions, and deep typo detection.
- **`.mcfunction` & Macros Support:** Load and execute function files, complete with support for scheduling, ticking,
  and dynamic NBT macro arguments via regex substitution (e.g., `/function namespace:test {a: 42}` matching `$(a)`).
- **Security Control:** Includes a rigorous `allow_functions` engine configuration to restrict potentially malicious
  local file system access when evaluating untrusted text.
- **Robust Entity Management:** Create and manage players and entities dynamically within a simulated world, complete
  with inventory, nbt properties, and active effects tracking.
- **Scoreboard Simulation:** A fully-featured programmatic scoreboard that replicates the in-game behavior for
  mathematical operations and player tracking.
- **Command Dispatcher:** An exact replica of the Minecraft command-tree parsing structure, enabling you to powerfully
  chain `execute` subcommands seamlessly.
- **Vast Command Library:** Emulates over 60 native Minecraft commands directly out of the box, cleanly modularized for
  easy extendability.

## 📦 Installation

To install `mcemu` directly from PyPI (once published):

```bash
pip install mcemu
```

If you are developing locally, clone the repository and install it in editable mode with development dependencies:

```bash
git clone https://github.com/OguzhanUmutlu/mcemu.git
cd mcemu
pip install -e .[dev]
```

## 🎮 Usage

Once installed, `mcemu` exposes a powerful command-line interface. Simply open your terminal and type:

```bash
mcemu
```

### Supported Commands

The emulator currently supports an extensive array of commands, grouped intuitively in the backend but accessible
seamlessly:

**Entities & Players:** `summon`, `kill`, `tp`, `teleport`, `damage`, `ride`, `spectate`, `xp`, `experience`, `clear`,
`give`, `item`, `effect`, `enchant`
**Data & Logic:** `data`, `execute`, `function`, `return`, `schedule`, `scoreboard`, `tag`, `attribute`, `advancement`,
`recipe`
**World Manipulation:** `setblock`, `fill`, `clone`, `time`, `weather`, `difficulty`, `gamerule`, `seed`, `worldborder`,
`spawnpoint`, `setworldspawn`
**Administration:** `op`, `deop`, `ban`, `pardon`, `ban-ip`, `pardon-ip`, `whitelist`, `kick`, `stop`, `save-all`,
`save-on`, `save-off`, `reload`, `debug`, `jfr`, `perf`, `publish`, `stopwatch`
**Chat & Visuals:** `say`, `tell`, `msg`, `w`, `me`, `teammsg`, `tellraw` (with ANSI JSON Component parsing!), `title`,
`tm`, `bossbar`, `particle`, `playsound`, `stopsound`, `dialog`, `team`, `setidletimeout`, `forceload`, `datapack`,
`list`, `transfer`

### Special REPL Commands

The interactive console also provides helpful emulator-specific utilities:

- `entities`: Prints all tracked entities, inventories, and effects.
- `scores`: Prints the current scoreboard dictionary.
- `toggleblocks`: Enables or disables actual block data storage in memory (useful for large `/fill` commands).
- `getblock <x> <y> <z>`: Returns the stored blockstate at a coordinate.
- `returncode`: Prints the integer return value of the last evaluated command to prevent clutter.
- `reset`: Completely resets the internal environment memory map.
- `exit`: Shuts down the emulator.

### Example Interaction

```py
mcemu> scoreboard objectives add kills dummy

mcemu> give @p minecraft:diamond_sword{Enchantments:[{id:"minecraft:sharpness",lvl:5}]} 1

mcemu> effect give @p minecraft:speed 100 2 true

mcemu> entities
- Dev (minecraft:player) at (0.0, 0.0, 0.0) tags: set()
  inventory: {'inventory.0': {'id': 'minecraft:diamond_sword', 'count': 1, 'nbt': '{Enchantments:[{id:"minecraft:sharpness",lvl:5}]}'}}
  effects: {'minecraft:speed': {'duration': 2000, 'amplifier': 2, 'hideParticles': True}}

mcemu> toggleblocks
Block tracking enabled.

mcemu> setblock 0 0 0 minecraft:stone
mcemu> getblock 0 0 0
Block at 0 0 0: minecraft:stone
```

## 🧪 Testing

To run the built-in test suite locally, use the provided script:

```bash
./run_tests.sh
```

This automatically sets up a virtual environment and runs `pytest` across the package.

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
