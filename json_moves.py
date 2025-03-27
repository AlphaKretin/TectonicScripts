# export interface Move {
#     id: string;
#     name: string;
#     type: PokemonType;
#     bp: number;
#     category: MoveCategory;
# }

import json
import re

with open("moves.txt", "r", encoding="utf8") as infile:
    doc = infile.read()

moves = doc.split("#-------------------------------")
moves = moves[1:]  # first entry is a header, rest fit expected format
moves = [move for move in moves if not move.startswith("\n#")]  # remove comments


def extract_move_data(move_text):
    id_match = re.search(r"\[([A-Z\d]+)\]", move_text, re.MULTILINE)
    id = id_match.group(1)

    name_match = re.search(r"^Name = (.+)", move_text, re.MULTILINE)
    name = name_match.group(1)

    type_match = re.search(r"^Type = (.+)", move_text, re.MULTILINE)
    type = type_match.group(1).title()

    bp = 0
    bp_match = re.search(r"^Power = (\d+)", move_text, re.MULTILINE)
    if bp_match:
        bp = int(bp_match.group(1))

    cat_match = re.search(r"^Category = (.+)", move_text, re.MULTILINE)
    category = cat_match.group(1).title()

    target_match = re.search(r"^Target = (.+)", move_text, re.MULTILINE)
    target = target_match.group(1)

    move_data = {
        "id": id,
        "name": name,
        "type": type,
        "bp": bp,
        "category": category,
        "target": target,
    }

    return move_data


move_list = [extract_move_data(move) for move in moves]

move_data = {move["id"]: move for move in move_list}

with open("moves.json", "w", encoding="utf8") as outfile:
    outfile.write(json.dumps(move_data, indent=4))

all_targets = list(set([move["target"] for move in move_list]))
with open("movetargets.txt", "w", encoding="utf8") as outfile:
    outfile.write("\n".join(all_targets))
