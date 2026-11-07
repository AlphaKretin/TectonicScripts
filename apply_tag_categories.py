"""
Adds each Pokemon's categories from tag_categories.py to its Flags line in the
PBS pokemon.txt, keeping existing flags, and warns about unknown Pokemon.

Edits pokemon.txt in place.
"""

import re

from tag_categories import categories
from tectonic import read_pbs, write_pbs

pokemon_categories = {}
for category, members in categories.items():
    for member in members:
        pokemon_categories.setdefault(member, []).append(category)

header, entries = read_pbs("pokemon.txt")

result = []
not_found = set(pokemon_categories.keys())

for entry in entries:
    id_match = re.match(r"\s*\[(\w+)\]", entry)
    if id_match:
        pokemon_id = id_match.group(1)
        if pokemon_id in pokemon_categories:
            not_found.discard(pokemon_id)
            new_flags = pokemon_categories[pokemon_id]
            flags_match = re.search(r"^Flags = (.*)$", entry, re.MULTILINE)
            if flags_match:
                existing = [f.strip() for f in flags_match.group(1).split(",")]
                combined = existing + [f for f in new_flags if f not in existing]
                entry = entry[:flags_match.start()] + "Flags = " + ",".join(combined) + entry[flags_match.end():]
            else:
                entry = entry.rstrip("\n") + "\nFlags = " + ",".join(new_flags) + "\n"
    result.append(entry)

if not_found:
    print("Warning: the following Pokemon were not found in pokemon.txt:")
    for p in sorted(not_found):
        print(f"  {p}")

write_pbs("pokemon.txt", header, result)

print("Done.")
