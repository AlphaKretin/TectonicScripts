import re

with open("pokemon.txt", "r", encoding="utf8") as infile:
    doc = infile.read()

mons = doc.split("#-------------------------------")
mons = mons[1:]  # first entry is a header, rest fit expected format


def extract_mon_data(mon_text):
    name_match = re.search(r"^Name = (.+)", mon_text, re.MULTILINE)
    name = name_match.group(1)

    id_match = re.search(r"^InternalName = (.+)", mon_text, re.MULTILINE)
    id = id_match.group(1)

    evo_match = re.search(r"^Evolutions = (.+?),", mon_text, re.MULTILINE)
    evo = evo_match.group(1) if evo_match else None

    return {"id": id, "name": name, "evo": evo}


mon_data = [extract_mon_data(mon) for mon in mons]
evo_mons = [mon for mon in mon_data if mon["evo"] == None]

lines = [mon["name"] for mon in evo_mons]

out = "\n".join(lines)

with open("evomons.txt", "w", encoding="utf8") as outfile:
    outfile.write(out)
