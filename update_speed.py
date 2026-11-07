"""
Sets new base Speed values in the PBS pokemon.txt from a CSV.

Usage: python update_speed.py [changes.csv]   (default speed_changes.csv)

Each CSV row is: pokemon ID, old speed, (ignored), new speed. Rows without
numeric speeds are skipped. Warns about unknown Pokemon and about Pokemon
whose current speed isn't the expected old one (they're updated anyway).

Edits pokemon.txt in place.
"""

import csv
import re
import sys

from tectonic import read_pbs, write_pbs

header, entries = read_pbs("pokemon.txt")

with open(sys.argv[1] if len(sys.argv) > 1 else "speed_changes.csv", "r", encoding="utf8", newline="") as f:
    reader = csv.reader(f)
    new_speeds = {}
    for row in reader:
        if not row:
            continue
        pokemon_id, old_speed, _unk, new_speed = row[0].strip(), row[1].strip(), row[2].strip(), row[3].strip()
        if not old_speed.lstrip("-").isdigit() or not new_speed.lstrip("-").isdigit():
            continue
        new_speeds[pokemon_id] = (int(old_speed), int(new_speed))

result = []
not_found = set(new_speeds.keys())
mismatches = []

for entry in entries:
    id_match = re.match(r"\s*\[(\w+)\]", entry)
    if id_match:
        pokemon_id = id_match.group(1)
        if pokemon_id in new_speeds:
            not_found.discard(pokemon_id)
            old_speed, new_speed = new_speeds[pokemon_id]
            stats_match = re.search(r"^BaseStats = (.*)$", entry, re.MULTILINE)
            if stats_match:
                stats = [s.strip() for s in stats_match.group(1).split(",")]
                if int(stats[3]) != old_speed:
                    mismatches.append((pokemon_id, stats[3], old_speed))
                stats[3] = str(new_speed)
                entry = entry[:stats_match.start()] + "BaseStats = " + ",".join(stats) + entry[stats_match.end():]
            else:
                print(f"Warning: {pokemon_id} has no BaseStats line")
    result.append(entry)

if not_found:
    print("Warning: the following Pokemon were not found in pokemon.txt:")
    for p in sorted(not_found):
        print(f"  {p}")

if mismatches:
    print("Warning: the following Pokemon had an unexpected current speed (updated anyway):")
    for pokemon_id, actual, expected in mismatches:
        print(f"  {pokemon_id}: expected old speed {expected}, found {actual}")

write_pbs("pokemon.txt", header, result)

print("Done.")
