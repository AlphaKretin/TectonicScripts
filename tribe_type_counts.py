import json

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
            "type1": pokemon.get("type1", ""),
            "type2": pokemon.get("type2", ""),
            "tribes": pokemon.get("tribes", [])
        }


# Data structure to store results
results = {}

# Process each pokemon
for pokemon_id, pokemon in pokemon_data.items():
    for tribe in pokemon["tribes"]:
        if tribe not in results:
            results[tribe] = {}
        for type in [pokemon["type1"], pokemon["type2"]]:
            if type:
                if type not in results[tribe]:
                    results[tribe][type] = []    
                results[tribe][type].append(pokemon_id)
        

# Export to TSV
output_file = "tribe_type_counts.tsv"
with open(output_file, "w", encoding="utf8") as tsvfile:
    # Write header
    tsvfile.write("tribe\ttype\tcount\t" + "\t".join([f"pokemon_{i+1}" for i in range(max(len(ids) for types in results.values() for ids in types.values()))]) + "\n")

    for tribe, types in results.items():
        for type, pokemon_ids in types.items():
            tsvfile.write(f"{tribe}\t{type}\t{len(pokemon_ids)}\t" + "\t".join(pokemon_ids) + "\n")