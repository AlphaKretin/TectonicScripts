"""
Shared helpers for the scripts here.

Most read loadedData.json, Pokemon Tectonic's game data as exported for the
Tectonic Tools. loadedData-dev.json is the same export taken from the
development branch; scripts read it when run with --dev.

read_pbs and write_pbs handle the game's PBS text files directly, for the
scripts that edit them or need fields loadedData doesn't carry.
"""

import argparse
import csv
import json

DATA_FILE = "loadedData.json"
DEV_DATA_FILE = "loadedData-dev.json"
PBS_SEPARATOR = "#-------------------------------"


def read_pbs(path):
    """Split a PBS file into its header and entries, the text between separator lines.

    Entries keep their surrounding newlines, so write_pbs reproduces the file
    unchanged. In files with comment blocks (e.g. moves.txt) those come back as
    entries too, starting with "\\n#".
    """
    with open(path, encoding="utf8") as f:
        header, *entries = f.read().split(PBS_SEPARATOR)
    return header, entries


def write_pbs(path, header, entries):
    with open(path, "w", encoding="utf8") as f:
        f.write(PBS_SEPARATOR.join([header, *entries]))


def parse_args(doc, configure=None):
    """Parse the command line of a loadedData script.

    Every such script takes --dev; pass `configure` to add more arguments to
    the parser before parsing.
    """
    parser = argparse.ArgumentParser(
        description=doc, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--dev", action="store_true", help=f"read {DEV_DATA_FILE} instead of {DATA_FILE}"
    )
    if configure:
        configure(parser)
    return parser.parse_args()


def load_data(dev=False):
    with open(DEV_DATA_FILE if dev else DATA_FILE, encoding="utf8") as f:
        return json.load(f)


def is_fully_evolved(mon):
    return not mon.get("evolutions")


def is_first_stage(mon):
    """True for the root of an evolution line, including Pokemon that don't evolve."""
    tree = mon.get("evolutionTreeArray")
    return bool(tree) and tree[0]["data"]["pokemon"] == mon["key"]


def mon_types(mon):
    return [t for t in (mon.get("type1"), mon.get("type2")) if t]


def level_moves(mon):
    """Level-up moves as (level, move_key) pairs, in learn order.

    The sort is stable, so moves learned at the same level keep the data's order.
    """
    return sorted(
        ((entry["level"], entry["move"]) for entry in mon.get("levelMoves") or []),
        key=lambda m: m[0],
    )


def attacking_level_moves(mon, moves, move_type):
    """(level, move) pairs for the damaging level-up moves of one type, in learn order."""
    result = []
    for level, move_key in level_moves(mon):
        move = moves.get(move_key)
        if move and move.get("type") == move_type and (move.get("power") or 0) > 0:
            result.append((level, move))
    return result


def write_table(path, header, rows):
    """Write rows (sequences) under a header row, as TSV for .tsv/.txt paths and CSV otherwise."""
    delimiter = "\t" if path.endswith((".tsv", ".txt")) else ","
    rows = list(rows)
    with open(path, "w", newline="", encoding="utf8") as f:
        writer = csv.writer(f, delimiter=delimiter)
        if header:
            writer.writerow(header)
        writer.writerows(rows)
    print(f"Exported {len(rows)} rows to {path}")
