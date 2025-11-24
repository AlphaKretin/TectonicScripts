import json
import csv

# Load the comprehensive loadedData.json file
with open("loadedData.json", "r", encoding="utf8") as f:
    data = json.load(f)

pokemon_data = {}
moves_data = {}

# Extract pokemon data - only first-stage Pokemon
for pokemon_key, pokemon in data.get("pokemon", {}).items():
    # Check if this is a first-stage Pokemon (root of evolution tree)
    evolution_tree = pokemon.get("evolutionTreeArray", [])
    if evolution_tree:
        # Find the entry for this Pokemon in its evolution tree
        current_pokemon_key = pokemon.get("key", pokemon_key)
        
        # The first entry in evolutionTreeArray is always the root (first stage)
        first_stage = evolution_tree[0].get("data", {}).get("pokemon", "")
        
        # Only include if this Pokemon is the first stage (no evolution has occurred)
        if first_stage == current_pokemon_key:
            pokemon_data[pokemon_key] = {
                "id": pokemon.get("key", pokemon_key),
                "name": pokemon.get("name", pokemon_key),
                "type1": pokemon.get("type1", "").upper() if pokemon.get("type1") else "",
                "type2": pokemon.get("type2", "").upper() if pokemon.get("type2") else "",
                "level_moves": pokemon.get("levelMoves", [])
            }

# Extract moves data
for move_key, move in data.get("moves", {}).items():
    moves_data[move_key] = {
        "id": move.get("key", move_key),
        "name": move.get("name", move_key),
        "type": move.get("type", "").upper() if move.get("type") else "",
        "bp": move.get("power", 0),
        "category": move.get("category", "Unknown")
    }

# Data structure to store results
results = []

# Process each pokemon
for pokemon_id, pokemon in pokemon_data.items():
    # Get the pokemon's types
    types = []
    if pokemon.get("type1"):
        types.append(pokemon["type1"])
    if pokemon.get("type2"):
        types.append(pokemon["type2"])
    
    # For each type, find the second attacking move of that type
    for pokemon_type in types:
        attacking_moves_of_type = []
        
        # Get level-up moves for this pokemon
        if pokemon.get("level_moves"):
            for move_entry in pokemon["level_moves"]:
                # Handle both dict format {level, move} and tuple format
                if isinstance(move_entry, dict):
                    level = move_entry.get("level")
                    move_id = move_entry.get("move")
                else:
                    level, move_id = move_entry
                
                # Check if the move exists and is of the correct type
                if move_id in moves_data:
                    move = moves_data[move_id]
                    if move.get("type", "") == pokemon_type:
                        # Check if it's an attacking move (has BP > 0)
                        if move.get("bp", 0) > 0:
                            attacking_moves_of_type.append({
                                "move_id": move_id,
                                "move_name": move.get("name", move_id),
                                "level": level,
                                "bp": move.get("bp", 0),
                                "category": move.get("category", "Unknown")
                            })
        
        # Get the second attacking move of this type if it exists
        if len(attacking_moves_of_type) >= 2:
            second_move = attacking_moves_of_type[1]
            
            # Check if second move is learned at level > 20
            if second_move["level"] > 20:
                results.append({
                    "pokemon_id": pokemon_id,
                    "pokemon_name": pokemon.get("name", pokemon_id),
                    "type": pokemon_type,
                    "first_move": attacking_moves_of_type[0]["move_name"],
                    "first_move_level": attacking_moves_of_type[0]["level"],
                    "second_move": second_move["move_name"],
                    "second_move_level": second_move["level"],
                    "level_difference": second_move["level"] - attacking_moves_of_type[0]["level"]
                })

# Sort by second move level in descending order
results.sort(key=lambda x: x["second_move_level"], reverse=True)

# Export to CSV
output_file = "late_stab_moves.csv"
with open(output_file, "w", newline="", encoding="utf8") as csvfile:
    fieldnames = [
        "pokemon_id",
        "pokemon_name",
        "type",
        "first_move",
        "first_move_level",
        "second_move",
        "second_move_level",
        "level_difference"
    ]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)

print(f"Exported {len(results)} records to {output_file}")
if results:
    print(f"\nTop 15 Pokemon with latest second STAB moves:")
    for i, record in enumerate(results[:15], 1):
        print(f"{i}. {record['pokemon_name']} ({record['type']}): {record['first_move']} (Lvl {record['first_move_level']}) -> {record['second_move']} (Lvl {record['second_move_level']})")
else:
    print("No results found.")
