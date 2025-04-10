import json
import re

with open("encounters.txt", "r", encoding="utf8") as infile:
    doc = infile.read()

encounters = doc.split("#-------------------------------")
encounters = encounters[1:]  # first entry is a header, rest fit expected format


def extract_encounter_data(enc_text):
    id_match = re.search(r"\[(.+)\]", enc_text, re.MULTILINE)
    id = id_match.group(1)

    # Trust comments
    name_match = re.search(r"^\[\d+\] # (.+)", enc_text, re.MULTILINE)
    name = name_match.group(1)

    encounters = {}
    current_patch = None
    for line in enc_text.split("\n"):
        header_match = re.search(r"^([^ ]+),\d+", line, re.MULTILINE)
        if header_match:
            current_patch = header_match.group(1)
            encounters[current_patch] = []
            continue
        special_match = re.search(r"^Special", line, re.MULTILINE)
        if special_match:
            current_patch = "Special"
            encounters[current_patch] = []
            continue
        if current_patch == None:
            continue
        terms = line.split(",")
        if len(terms) < 2:
            continue
        weight = int(terms[0])
        mon = terms[1]
        encounters[current_patch].append({"weight": weight, "pokemon": mon})

    enc_data = {"id": id, "name": name, "encounters": encounters}

    return enc_data


enc_list = [extract_encounter_data(enc) for enc in encounters]

enc_data = {enc["id"]: enc for enc in enc_list}

with open("encounters.json", "w", encoding="utf8") as outfile:
    outfile.write(json.dumps(enc_data, indent=4))
