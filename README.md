# mcemu

A lightweight, programmatic, and interactive Minecraft Command Emulator designed as a standalone Python library and REPL
environment. It simulates a virtual Minecraft environment, allowing you to test, debug, and execute complex command
sequences and `.mcfunction` files without needing to launch the game!

## 🚀 Features

- **Interactive REPL Environment:** Start the engine right from your terminal and type commands in real time. Features
  colored syntax feedback, auto-suggestions, and deep typo detection.
- **`.mcfunction` Support:** Load and execute function files, complete with support for scheduling and ticking.
- **Robust Entity Management:** Create and manage players and entities dynamically within a simulated world, complete with inventory and active effects tracking.
- **Scoreboard Simulation:** A fully-featured programmatic scoreboard that replicates the in-game behavior for
  mathematical operations and player tracking.
- **Command Dispatcher:** An exact replica of the Minecraft command-tree parsing structure, enabling you to chain
  `execute` contexts.

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

This will launch the interactive engine:

```text
Minecraft Command Engine v3.0 (Programmatic API)
Type 'exit' to quit, 'scores' to list scoreboards, 'entities' to list entities.
mcemu> 
```

### Supported Commands

The emulator currently supports the following base commands:

- `clear`
- `data`
- `effect`
- `enchant`
- `execute`
- `function`
- `give`
- `item`
- `kill`
- `return`
- `schedule`
- `scoreboard`
- `summon`
- `tag`
- `teleport` (and `tp`)
- `tick`

### Example Interaction

```text
mcemu> scoreboard objectives add kills dummy
data returned 1

mcemu> give @p minecraft:diamond_sword{Enchantments:[{id:"minecraft:sharpness",lvl:5}]} 1
data returned 1

mcemu> effect give @p minecraft:speed 100 2 true
data returned 1

mcemu> entities
- Dev (minecraft:player) at (0.0, 0.0, 0.0) tags: set()
  inventory: {'inventory.0': {'id': 'minecraft:diamond_sword', 'count': 1, 'nbt': '{Enchantments:[{id:"minecraft:sharpness",lvl:5}]}'}}
  effects: {'minecraft:speed': {'duration': 2000, 'amplifier': 2, 'hideParticles': True}}
```

## 🧪 Testing

To run the built-in test suite locally, use the provided script:

```bash
./run_tests.sh
```

This automatically sets up a virtual environment and runs `pytest` across the package.

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
