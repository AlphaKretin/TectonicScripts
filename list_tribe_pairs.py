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
            "tribes": pokemon.get("tribes", [])
        }


# Data structure to store results
results = {}

def count_tribes(key, pokemon):
    if key in results:
        results[key].append(pokemon["name"])
    else:
        results[key] = [pokemon["name"]]

# Process each pokemon
for pokemon_id, pokemon in pokemon_data.items():
    tribes = pokemon["tribes"]
    if len(tribes) == 2:
        key = "|".join(sorted(tribes))
        count_tribes(key, pokemon)
    if len(tribes) == 3:
        keys = ["|".join(sorted([tribes[0],tribes[1]])),
                "|".join(sorted([tribes[0],tribes[2]])),
                "|".join(sorted([tribes[1],tribes[2]]))]
        for key in keys:
            count_tribes(key, pokemon)

# Export to text file with tab-separated values
output_file = "tribe_pairs.txt"
with open(output_file, "w", encoding="utf8") as f:
    for tribe_pair_key in sorted(results.keys()):
        # Split the key and convert tribes to Title Case
        tribes = tribe_pair_key.split("|")
        tribe1_title = tribes[0].title()
        tribe2_title = tribes[1].title()
        
        # Get the pokemon list for this pair
        pokemon_list = results[tribe_pair_key]
        
        # Create tab-separated line: Tribe1 \t Tribe2 \t Pokemon1 \t Pokemon2 \t ...
        line = f"{tribe1_title}\t{tribe2_title}\t" + "\t".join(pokemon_list)
        f.write(line + "\n")

print(f"Exported tribe pairs to {output_file}")
