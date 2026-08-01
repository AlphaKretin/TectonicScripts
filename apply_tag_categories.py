import re
from tagcategories import categories

pokemon_categories = {}
for category, members in categories.items():
    for member in members:
        pokemon_categories.setdefault(member, []).append(category)

with open("pokemon.txt", "r", encoding="utf8") as f:
    doc = f.read()

separator = "#-------------------------------"
sections = doc.split(separator)
header = sections[0]
entries = sections[1:]

result = [header]
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

with open("pokemon.txt", "w", encoding="utf8") as f:
    f.write(separator.join(result))

print("Done.")
