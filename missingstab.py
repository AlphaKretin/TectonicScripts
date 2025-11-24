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
    
    # For each type, find the first two attacking moves of that type
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
        
        # Get the first two attacking moves of this type
        if len(attacking_moves_of_type) >= 2:
            first_move = attacking_moves_of_type[0]
            second_move = attacking_moves_of_type[1]
            
            bp_difference = abs(first_move["bp"] - second_move["bp"])
            
            results.append({
                "pokemon_id": pokemon_id,
                "pokemon_name": pokemon.get("name", pokemon_id),
                "type": pokemon_type,
                "first_move": first_move["move_name"],
                "first_move_bp": first_move["bp"],
                "first_move_level": first_move["level"],
                "second_move": second_move["move_name"],
                "second_move_bp": second_move["bp"],
                "second_move_level": second_move["level"],
                "bp_difference": bp_difference
            })

# Sort by BP difference in descending order
results.sort(key=lambda x: x["bp_difference"], reverse=True)

# Export to CSV
output_file = "type_move_bp_differences.csv"
with open(output_file, "w", newline="", encoding="utf8") as csvfile:
    fieldnames = [
        "pokemon_id",
        "pokemon_name",
        "type",
        "first_move",
        "first_move_bp",
        "first_move_level",
        "second_move",
        "second_move_bp",
        "second_move_level",
        "bp_difference"
    ]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)

print(f"Exported {len(results)} records to {output_file}")
if results:
    print(f"\nTop 10 highest BP differences:")
    for i, record in enumerate(results[:10], 1):
        print(f"{i}. {record['pokemon_name']} ({record['type']}): {record['first_move']} ({record['first_move_bp']} BP) vs {record['second_move']} ({record['second_move_bp']} BP) = {record['bp_difference']} difference")
else:
    print("No results found. Please ensure pokemon.txt and moves.txt files are available.")
