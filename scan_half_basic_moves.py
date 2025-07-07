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

    func_match = re.search(r"^FunctionCode = (.+)", move_text, re.MULTILINE)
    func = func_match.group(1)

    chance = None
    chance_match = re.search(r"^EffectChance = (\d+)", move_text, re.MULTILINE)
    if chance_match:
        chance = int(chance_match.group(1))

    move_data = {
        "id": id,
        "name": name,
        "function": func,
        "chance": chance,
    }

    return move_data


move_list = [extract_move_data(move) for move in moves]

half_basic_moves = [
    move for move in move_list if move["function"] == "Basic" and move["chance"] != None
]

basic_names = [move["id"] for move in half_basic_moves]

with open("halfbasicmoves.txt", "w", encoding="utf8") as outfile:
    outfile.write("\n".join(basic_names))
