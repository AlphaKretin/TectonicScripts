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

    level_moves = None
    level_moves_match = re.search(r"^Moves = (.+)", mon_text, re.MULTILINE)
    if level_moves_match:
        level_moves_text = level_moves_match.group(1)
        level_move_list = level_moves_text.split(",")
        level_moves = []
        for i in range(0, len(level_move_list), 2):
            level_moves.append((int(level_move_list[i]), level_move_list[i + 1]))

    line_moves = None
    line_moves_match = re.search(r"^LineMoves = (.+)", mon_text, re.MULTILINE)
    if line_moves_match:
        line_moves_text = line_moves_match.group(1)
        line_moves = line_moves_text.split(",")

    tutor_moves = None
    tutor_moves_match = re.search(r"^TutorMoves = (.+)", mon_text, re.MULTILINE)
    if tutor_moves_match:
        tutor_moves_text = tutor_moves_match.group(1)
        tutor_moves = tutor_moves_text.split(",")

    evos = None
    evos_match = re.search(r"^Evolutions = (.+)", mon_text, re.MULTILINE)
    if evos_match:
        evos_text = evos_match.group(1)
        evos_list = evos_text.split(",")
        evos = []
        for i in range(0, len(evos_list), 3):
            evos.append(
                {
                    "target": evos_list[i],
                    "method": evos_list[i + 1],
                    "param": evos_list[i + 2],
                }
            )

    tribes = None
    tribes_match = re.search(r"^Tribes = (.+)", mon_text, re.MULTILINE)
    if tribes_match:
        tribes_text = tribes_match.group(1)
        tribes = tribes_text.split(",")

    height_match = re.search(r"^Height = (.+)", mon_text, re.MULTILINE)
    height = float(height_match.group(1))

    weight_match = re.search(r"^Weight = (.+)", mon_text, re.MULTILINE)
    weight = float(weight_match.group(1))

    kind_match = re.search(r"^Kind = (.+)", mon_text, re.MULTILINE)
    kind = kind_match.group(1)

    pokedex_match = re.search(r"^Pokedex = (.+)", mon_text, re.MULTILINE)
    pokedex = pokedex_match.group(1)

    mon_data = {
        "id": id,
        "name": name,
        "type1": type1,
        "type2": type2,
        "stats": stats,
        "level_moves": level_moves,
        "line_moves": line_moves,
        "tutor_moves": tutor_moves,
        "tribes": tribes,
        "height": height,
        "weight": weight,
        "kind": kind,
        "pokedex": pokedex,
        "evos": evos,
    }

    return mon_data


mon_list = [extract_pokemon_data(mon) for mon in pokemon]

# propagate moves through evos, combine move lists
for mon in mon_list:
    if mon["evos"] != None:
        for evo in mon["evos"]:
            evo_index = next(
                i for i, v in enumerate(mon_list) if v["id"] == evo["target"]
            )
            if mon["level_moves"] != None:
                mon_list[evo_index]["level_moves"] = (
                    mon_list[evo_index]["level_moves"] or []
                ) + mon["level_moves"]
            if mon["line_moves"] != None:
                mon_list[evo_index]["line_moves"] = (
                    mon_list[evo_index]["line_moves"] or []
                ) + mon["line_moves"]
            if mon_list[evo_index]["tribes"] == None:
                mon_list[evo_index]["tribes"] = mon["tribes"]


mon_data = {mon["id"]: mon for mon in mon_list}

with open("pokemon.json", "w", encoding="utf8") as outfile:
    outfile.write(json.dumps(mon_data, indent=4))
