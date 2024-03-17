import re

with open("moves.txt", "r", encoding="utf8") as infile:
    doc = infile.read()

moves = doc.split("#-------------------------------")
moves = moves[1:]  # first entry is a header, rest fit expected format


def extract_move_data(move_text):
    name_match = re.search(r"^Name = (.+)", move_text, re.MULTILINE)
    name = name_match.group(1)

    type_match = re.search(r"^Type = (.+)", move_text, re.MULTILINE)
    typ = type_match.group(1)

    cat_match = re.search(r"^Category = (.+)", move_text, re.MULTILINE)
    cat = cat_match.group(1).title()

    return (name, typ, cat)


move_data = [extract_move_data(move) for move in moves]

lines = [move[0] + "\t" + move[1] + "\t" + move[2] for move in move_data]

out = "\n".join(lines)

with open("movedata.txt", "w", encoding="utf8") as outfile:
    outfile.write(out)
