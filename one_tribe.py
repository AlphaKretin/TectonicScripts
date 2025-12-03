import json
import csv

# Load the comprehensive loadedData.json file
with open("loadedData.json", "r", encoding="utf8") as f:
    data = json.load(f)

pokemon_data = {}

# Extract pokemon data - only first-stage Pokemon
for pokemon_key, pokemon in data.get("pokemon", {}).items():
    pokemon_data[pokemon_key] = {
        "id": pokemon.get("key", pokemon_key),
        "name": pokemon.get("name", pokemon_key),
        "tribes": pokemon.get("tribes", [])
    }


# Data structure to store results
results = []

# Process each pokemon
for pokemon_id, pokemon in pokemon_data.items():
    if len(pokemon["tribes"]) == 1:
        results.append({
            "pokemon_id": pokemon_id,
            "pokemon_name": pokemon.get("name", pokemon_id),
            "tribe": pokemon["tribes"][0]
        })
        

# Export to CSV
output_file = "one_tribes.csv"
with open(output_file, "w", newline="", encoding="utf8") as csvfile:
    fieldnames = [
        "pokemon_id",
        "pokemon_name",
        "tribe"
    ]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)

print(f"Exported {len(results)} records to {output_file}")
