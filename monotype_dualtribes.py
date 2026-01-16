import json
import csv

# Load the comprehensive loadedData.json file
with open("loadedData.json", "r", encoding="utf8") as f:
    data = json.load(f)

pokemon_data = {}

# Extract pokemon data
for pokemon_key, pokemon in data.get("pokemon", {}).items():
    # Filter for fully evolved Pokemon only (those with no evolutions)
    evolutions = pokemon.get("evolutions", [])
    if not evolutions:  # Only include Pokemon with no evolutions
        pokemon_data[pokemon_key] = {
            "id": pokemon.get("key", pokemon_key),
            "name": pokemon.get("name", pokemon_key),
            "tribes": pokemon.get("tribes", []),
            "type1": pokemon.get("type1", ""),
            "type2": pokemon.get("type2", "")
        }


types = list(data.get("types", {}).keys())

# Data structure to store results
results = {}

for ptype in types:
    results[ptype] = {}
    filtered_pokemon = [p for p in pokemon_data.values() if p.get("type1") == ptype or p.get("type2") == ptype]
    for pokemon in filtered_pokemon:
        tribes = pokemon["tribes"]
        if len(tribes) >= 2:
            for i in range(len(tribes)):
                for j in range(i + 1, len(tribes)):
                    pair = tuple(sorted([tribes[i], tribes[j]]))
                    key = f"{pair[0]}/{pair[1]}"
                    if key not in results[ptype]:
                        results[ptype][key] = []
                    results[ptype][key].append(pokemon["name"])

# Export to CSV - for each type, list tribes with 4+ Pokemon
output_file = "monotype_dualtribes.csv"

with open(output_file, "w", newline="", encoding="utf8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Type", "Tribe Pair", "Count", "Pokemon"])

    for ptype in types:
        for tribe, pokemon_list in results[ptype].items():
            if len(pokemon_list) >= 3 or (ptype == "NORMAL" and len(pokemon_list) >= 2):
                writer.writerow([ptype, tribe, len(pokemon_list), ", ".join(pokemon_list)])

print(f"Exported results to {output_file}")
