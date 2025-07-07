import json
import re

with open("abilities.json", "r", encoding="utf8") as infile:
    abilities = json.loads(infile.read())

ability_list = list(abilities.values())

ability_rows = [
    ability["name"] + "\t" + ability["key"] + "\t" + ability["description"]
    for ability in ability_list
]

with open("abilities.csv", "w", encoding="utf8") as outfile:
    outfile.write("\n".join(ability_rows))
