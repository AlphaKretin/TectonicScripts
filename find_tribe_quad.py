import json
from itertools import combinations_with_replacement
from collections import defaultdict, Counter

with open("loadedData.json", "r", encoding="utf8") as f:
    data = json.load(f)

# Group fully-evolved Pokemon by their tribe frozenset
tribe_groups = defaultdict(list)

for pokemon_key, pokemon in data.get("pokemon", {}).items():
    if pokemon.get("evolutions"):
        continue
    tribes = pokemon.get("tribes", [])
    if not tribes:
        continue
    tribe_groups[frozenset(tribes)].append(pokemon.get("name", pokemon_key))

group_list = sorted(tribe_groups.items(), key=lambda x: sorted(x[0]))
print(f"Unique tribe sets among fully-evolved Pokemon: {len(group_list)}")

results = []

# Iterate all 4-picks of tribe sets (with replacement: two Pokemon can share the same set)
for idx_combo in combinations_with_replacement(range(len(group_list)), 4):
    idx_counts = Counter(idx_combo)

    # Ensure enough distinct Pokemon exist in each reused group
    if not all(len(group_list[idx][1]) >= count for idx, count in idx_counts.items()):
        continue

    # Count how many times each tribe appears across the 4 selected sets
    tribe_counts = Counter()
    for idx in idx_combo:
        for tribe in group_list[idx][0]:
            tribe_counts[tribe] += 1

    qualifying_tribes = [tribe for tribe, count in tribe_counts.items() if count >= 3]
    if len(qualifying_tribes) >= 4:
        results.append((idx_combo, qualifying_tribes))

print(f"Found {len(results)} valid combinations")

lines = []
for idx_combo, qualifying_tribes in results:
    idx_counts = Counter(idx_combo)
    lines.append(f"Qualifying tribes (3+ copies): {', '.join(sorted(qualifying_tribes))}")
    for idx, count in sorted(idx_counts.items()):
        tribes, names = group_list[idx]
        selected = names[:count]
        label = f" × {count}" if count > 1 else ""
        lines.append(f"  {sorted(tribes)}{label}: {', '.join(selected)}")
    lines.append("")

with open("tribe_quads.txt", "w", encoding="utf8") as f:
    f.write("\n".join(lines))

print("Results saved to tribe_quads.txt")
