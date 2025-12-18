import json

# Load the comprehensive loadedData.json file
with open("loadedData.json", "r", encoding="utf8") as f:
    data = json.load(f)

pokemon_data = {}

# Extract pokemon data
for pokemon_key, pokemon in data.get("pokemon", {}).items():
    # Filter for fully evolved Pokemon only (those with no evolutions)
    evolutions = pokemon.get("evolutions", [])
    flags = pokemon.get("flags", [])
    if not evolutions:  # Only include Pokemon with no evolutions
        pokemon_data[pokemon_key] = {
            "id": pokemon.get("key", pokemon_key),
            "name": pokemon.get("name", pokemon_key),
            "tribes": pokemon.get("tribes", [])
        }


# Data structure to store results
results = {}

# Process each pokemon
for pokemon_id, pokemon in pokemon_data.items():
    for tribe in pokemon["tribes"]:
        if tribe not in results:
            results[tribe] = []
        results[tribe].append(pokemon["name"])
        

# Export to TSV
output_file = "tribe_counts.tsv"
with open(output_file, "w", encoding="utf8") as tsvfile:
    # Write header
    tsvfile.write("tribe\tcount\t" + "\t".join([f"pokemon_{i+1}" for i in range(max(len(ids) for ids in results.values()))]) + "\n")
    for tribe,pokemon_ids in results.items():
        tsvfile.write(f"{tribe.title()}\t{len(pokemon_ids)}\t" + "\t".join(pokemon_ids) + "\n")