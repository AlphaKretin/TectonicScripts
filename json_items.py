import json
import re

with open("items.txt", "r", encoding="utf8") as infile:
    doc = infile.read()

items = doc.split("#-------------------------------")
items = items[1:]  # first entry is a header, rest fit expected format


def extract_item_data(item_text):
    id_match = re.search(r"\[(.+)\]", item_text, re.MULTILINE)
    id = id_match.group(1)

    name_match = re.search(r"^Name = (.+)", item_text, re.MULTILINE)
    name = name_match.group(1)

    desc_match = re.search(r"^Description = (.+)", item_text, re.MULTILINE)
    desc = desc_match.group(1)

    flags = None
    flags_match = re.search(r"^Flags = (.+)", item_text, re.MULTILINE)
    if flags_match:
        flags_text = flags_match.group(1)
        flags = flags_text.split(",")

    item_data = {"id": id, "name": name, "description": desc, "flags": flags}

    return item_data


item_list = [extract_item_data(item) for item in items]

item_data = {item["id"]: item for item in item_list}

with open("items.json", "w", encoding="utf8") as outfile:
    outfile.write(json.dumps(item_data, indent=4))
