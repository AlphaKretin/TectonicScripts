# export interface Pokemon {
#     id: string;
#     name: string;
#     type1: PokemonType;
#     type2: PokemonType;
#     stats: Stats;
#     moves: Move[];
# }

import json
import re

with open("pokemon.txt", "r", encoding="utf8") as infile:
    doc = infile.read()

pokemon = doc.split("#-------------------------------")
pokemon = pokemon[1:]  # first entry is a header, rest fit expected format


def unique(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def extract_pokemon_data(mon_text):
    id_match = re.search(r"\[([A-Zfm\d]+)\]", mon_text, re.MULTILINE)
    id = id_match.group(1)

    name_match = re.search(r"^Name = (.+)", mon_text, re.MULTILINE)
    name = name_match.group(1)

    type1_match = re.search(r"^Type1 = (.+)", mon_text, re.MULTILINE)
    type1 = type1_match.group(1).title()

    type2_match = re.search(r"^Type2 = (.+)", mon_text, re.MULTILINE)
    type2 = type2_match.group(1).title() if type2_match else ""

    stats_match = re.search(r"^BaseStats = (.+)", mon_text, re.MULTILINE)
    base_stats = stats_match.group(1)
    stat_strings = base_stats.split(",")
    stat_nums = [int(stat) for stat in stat_strings]
    stats = {
        "hp": stat_nums[0],
        "attack": stat_nums[1],
        "defense": stat_nums[2],
        "speed": stat_nums[3],
        "spatk": stat_nums[4],
        "spdef": stat_nums[5],
    }

    level_moves_match = re.search(r"^Moves = (.+)", mon_text, re.MULTILINE)
    level_moves = level_moves_match.group(1)
    level_move_list = level_moves.split(",")
    moves = level_move_list[1::2]

    # TODO: make line moves propagate along evolutions
    line_moves_match = re.search(r"^LineMoves = (.+)", mon_text, re.MULTILINE)
    if line_moves_match:
        line_moves = line_moves_match.group(1)
        moves += line_moves.split(",")

    tutor_moves_match = re.search(r"^TutorMoves = (.+)", mon_text, re.MULTILINE)
    if tutor_moves_match:
        tutor_moves = tutor_moves_match.group(1)
        moves += tutor_moves.split(",")

    moves = unique(moves)

    mon_data = {
        "id": id,
        "name": name,
        "type1": type1,
        "type2": type2,
        "stats": stats,
        "moves": moves,
    }

    return mon_data


mon_list = [extract_pokemon_data(mon) for mon in pokemon]

mon_data = {mon["id"]: mon for mon in mon_list}

with open("pokemon.json", "w", encoding="utf8") as outfile:
    outfile.write(json.dumps(mon_data, indent=4))
