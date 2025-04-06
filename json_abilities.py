import json
import re

with open("abilities.txt", "r", encoding="utf8") as infile:
    doc = infile.read()

abilities = doc.split("#-------------------------------")
abilities = abilities[1:]  # first entry is a header, rest fit expected format


def extract_ability_data(ability_text):
    id_match = re.search(r"\[(.+)\]", ability_text, re.MULTILINE)
    id = id_match.group(1)

    name_match = re.search(r"^Name = (.+)", ability_text, re.MULTILINE)
    name = name_match.group(1)

    desc_match = re.search(r"^Description = (.+)", ability_text, re.MULTILINE)
    desc = desc_match.group(1)

    flags = None
    flags_match = re.search(r"^Flags = (.+)", ability_text, re.MULTILINE)
    if flags_match:
        flags_text = flags_match.group(1)
        flags = flags_text.split(",")

    ability_data = {"id": id, "name": name, "description": desc, "flags": flags}

    return ability_data


ability_list = [extract_ability_data(ability) for ability in abilities]

ability_data = {ability["id"]: ability for ability in ability_list}

with open("abilities.json", "w", encoding="utf8") as outfile:
    outfile.write(json.dumps(ability_data, indent=4))
