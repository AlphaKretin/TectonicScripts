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

    type1_match = re.search(r"^Type1 = (.+)", mon_text, re.MULTILINE)
    type1 = type1_match.group(1).title()

    type2_match = re.search(r"^Type2 = (.+)", mon_text, re.MULTILINE)
    type2 = type2_match.group(1).title() if type2_match else ""

    tribes_match = re.search(r"^Tribes = (.+)", mon_text, re.MULTILINE)
    tribe = tribes_match.group(1).title() if tribes_match else ""

    abilities_match = re.search(r"^Abilities = (.+)", mon_text, re.MULTILINE)
    ability = abilities_match.group(1) if abilities_match else ""

    evo_match = re.search(r"^Evolutions = (.+?),", mon_text, re.MULTILINE)
    evo = evo_match.group(1) if evo_match else None

    return (id, name, type1, type2, tribe, ability, evo)


mon_data = {}
evo_tribes = {}

with open("abilities.txt", "r", encoding="utf8") as infile:
    abil_raw = infile.readlines()

abil = {}

for line in abil_raw:
    parts = line.split(",")
    abil[parts[1]] = parts[2]

for mon in mons:
    (id, name, type1, type2, tribe, ability, evo) = extract_mon_data(mon)
    tribes = tribe.split(",")
    shapedTribes = [tribes[0], tribes[1] if len(
        tribes) > 1 else "", tribes[2] if len(tribes) > 2 else ""]
    if (tribe != "") and evo:
        evo_tribes[evo] = shapedTribes
    abilities = ability.split(",")
    shapedAbils = [abil[abilities[0]],
                   abil[abilities[1]] if len(abilities) > 1 else ""]
    mon_data[id] = {"name": name, "type1": type1,
                    "type2": type2, "tribes": shapedTribes,
                    "abilities": shapedAbils, "evo": evo}

new_evo_tribes = {}

for evo, tribe in evo_tribes.items():
    mon_data[evo]["tribes"] = tribe
    if (mon_data[evo]["evo"]):
        new_evo_tribes[mon_data[evo]["evo"]] = tribe

# repeat for evolutions
for evo, tribe in new_evo_tribes.items():
    mon_data[evo]["tribes"] = tribe

lines = [mon["name"] + "\t" + mon["type1"] + "\t" + mon["type2"] + "\t" + "\t".join(mon["tribes"]) + "\t" + "\t".join(mon["abilities"])
         for _, mon in mon_data.items()]

out = "\n".join(lines)

with open("mondata.txt", "w", encoding="utf8") as outfile:
    outfile.write(out)
