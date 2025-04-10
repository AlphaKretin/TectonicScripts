import copy
import json
import re

with open("pokemonforms.txt", "r", encoding="utf8") as infile:
    doc = infile.read()

forms = doc.split("#-------------------------------")
forms = forms[1:]  # first entry is a header, rest fit expected format


def unique(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def extract_form_data(mon_text):
    id_match = re.search(r"\[(.+)\]", mon_text, re.MULTILINE)
    id_text = id_match.group(1)
    id_terms = id_text.split(",")
    id = id_terms[0]
    form_id = int(id_terms[1])

    form_name = None
    form_name_match = re.search(r"^FormName = (.+)", mon_text, re.MULTILINE)
    if form_name_match:
        form_name = form_name_match.group(1)

    type1 = None
    type1_match = re.search(r"^Type1 = (.+)", mon_text, re.MULTILINE)
    if type1_match:
        type1 = type1_match.group(1).title()

    type2 = None
    type2_match = re.search(r"^Type2 = (.+)", mon_text, re.MULTILINE)
    if type2_match:
        type2 = type2_match.group(1).title()

    stats = None
    stats_match = re.search(r"^BaseStats = (.+)", mon_text, re.MULTILINE)
    if stats_match:
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

    abilities = None
    abil_match = re.search(r"^Abilities = (.+)", mon_text, re.MULTILINE)
    if abil_match:
        abil_text = abil_match.group(1)
        abilities = abil_text.split(",")

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

    height = None
    height_match = re.search(r"^Height = (.+)", mon_text, re.MULTILINE)
    if height_match:
        height = float(height_match.group(1))

    weight = None
    weight_match = re.search(r"^Weight = (.+)", mon_text, re.MULTILINE)
    if weight_match:
        weight = float(weight_match.group(1))

    kind = None
    kind_match = re.search(r"^Kind = (.+)", mon_text, re.MULTILINE)
    if kind_match:
        kind = kind_match.group(1)

    pokedex = None
    pokedex_match = re.search(r"^Pokedex = (.+)", mon_text, re.MULTILINE)
    if pokedex_match:
        pokedex = pokedex_match.group(1)

    form_data = {
        "id": id,
        "form_id": form_id,
        "form_name": form_name,
        "type1": type1,
        "type2": type2,
        "stats": stats,
        "abilities": abilities,
        "level_moves": level_moves,
        "line_moves": line_moves,
        "tutor_moves": tutor_moves,
        "height": height,
        "weight": weight,
        "kind": kind,
        "pokedex": pokedex,
    }

    return form_data


form_list = [extract_form_data(form) for form in forms]

form_data = {}

for form in form_list:
    for key in copy.copy(form):
        if form[key] == None:
            del form[key]
    if form["id"] in form_data:
        form_data[form["id"]].append(form)
    else:
        form_data[form["id"]] = [form]


with open("forms.json", "w", encoding="utf8") as outfile:
    outfile.write(json.dumps(form_data, indent=4))
