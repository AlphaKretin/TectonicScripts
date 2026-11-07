# TectonicScripts

A personal scratchpad of scripts for working on Pokemon Tectonic. Each script's docstring says what it does, what it reads and what it writes.

## Data

- **Game data analysis** reads `loadedData.json`, the game data export used by the [Tectonic Tools](https://github.com/AlphaKretin/tectonic-damage-calc). `--dev` makes these scripts read `loadedData-dev.json` (the same export from the development branch) instead.
- **PBS editing and validation** scripts work on the game's PBS files (`pokemon.txt`, `moves.txt`, and so on), copied into this folder.
- **Audio** scripts work on `.ogg` files in `music/`, apart from `loop_scan.py`, which reads the game's BGM folder. **Image** scripts take their folders as arguments.

Shared helpers for both kinds of data are in `tectonic.py`. Run scripts from this folder. Inputs and outputs are not tracked.
