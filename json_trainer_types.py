import json
import re

with open("trainertypes.txt", "r", encoding="utf8") as infile:
    doc = infile.read()

types = doc.split("#-------------------------------")
types = types[1:]  # first entry is a header, rest fit expected format


def extract_type_data(type_text):
    id_match = re.search(r"\[(.+)\]", type_text, re.MULTILINE)
    id = id_match.group(1)

    name_match = re.search(r"^Name = (.+)", type_text, re.MULTILINE)
    name = name_match.group(1)

    return (id, name)


type_list = [extract_type_data(type) for type in types]

type_data = {type[0]: type[1] for type in type_list}

with open("trainertypes.json", "w", encoding="utf8") as outfile:
    outfile.write(json.dumps(type_data, indent=4))
