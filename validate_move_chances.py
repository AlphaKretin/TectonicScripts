import re

with open("moves.txt", "r", encoding="utf8") as infile:
    doc = infile.read()

moves = doc.split("#-------------------------------")
moves = moves[1:]  # first entry is a header, rest fit expected format
moves = [move for move in moves if not move.startswith("\n#")]  # remove comments


def extract_move_data(move_text):
    id_match = re.search(r"\[([A-Z\d]+)\]", move_text, re.MULTILINE)
    id = id_match.group(1)

    desc_match = re.search(r"^Description = (.+)", move_text, re.MULTILINE)
    description = desc_match.group(1)

    stated_chance = None
    stated_chance_match = re.search(r"(\d+)%", description)
    if stated_chance_match:
        stated_chance = int(stated_chance_match.group(1))

    true_chance = None
    true_chance_match = re.search(r"^EffectChance = (\d+)", move_text, re.MULTILINE)
    if true_chance_match:
        true_chance = int(true_chance_match.group(1))

    move_data = {
        "id": id,
        "description": description,
        "stated_chance": stated_chance,
        "true_chance": true_chance,
    }

    return move_data


move_list = [extract_move_data(move) for move in moves]
move_list = [
    move
    for move in move_list
    if move["stated_chance"] != None and move["true_chance"] != None
]

errors = []
for move in move_list:
    if move["stated_chance"] != move["true_chance"]:
        id = move["id"]
        stated_chance = str(move["stated_chance"])
        true_chance = str(move["true_chance"])
        desc = move["description"]
        error_string = f"Move {id}'s stated chance {stated_chance}% does not match the effect chance of {true_chance}! Desc: {desc}"
        print(error_string)
        errors.append(error_string)

with open("moveerrors.txt", "w", encoding="utf8") as outfile:
    outfile.write("\n".join(errors))
