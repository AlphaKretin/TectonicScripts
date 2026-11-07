import json
import csv

# Load the comprehensive loadedData.json file
with open("loadedData-dev.json", "r", encoding="utf8") as f:
    data = json.load(f)

pokemon_data = {}

# Extract pokemon data
for pokemon_key, pokemon in data.get("pokemon", {}).items():
    evolutions = pokemon.get("evolutions", [])
    if evolutions:  # Only include Pokemon with evolutions
        for evo in evolutions:
            evo_key = evo.get("pokemon", "")
            evo_data = data.get("pokemon", {}).get(evo_key, {})

            pair_key = f"{pokemon_key} -> {evo_key}"

            pokemon_data[pair_key] = {
                "key": pair_key,
                "id": pokemon.get("key", pokemon_key),
                "name": pokemon.get("name", pokemon_key),
                "evo_id": evo_key,
                "evo_name": evo.get("name", evo_key),
                "bst": pokemon.get("bst", 0),
                "evo_bst": evo_data.get("bst", 0),
                "bst_diff": evo_data.get("bst", 0) - pokemon.get("bst", 0),
            }


# Data structure to store results
results = []

# Process each pokemon
for pokemon_id, pokemon in pokemon_data.items():
    results.append(
        {
            "evo_key": pokemon.get("key", ""),
            "bst": pokemon.get("bst", 0),
            "evo_bst": pokemon.get("evo_bst", 0),
            "bst_diff": pokemon.get("bst_diff", 0),
        }
    )


# Export to CSV
output_file = "evobst.csv"
with open(output_file, "w", newline="", encoding="utf8") as csvfile:
    fieldnames = [
        "evo_key",
        "bst",
        "evo_bst",
        "bst_diff",
    ]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)

print(f"Exported {len(results)} records to {output_file}")
