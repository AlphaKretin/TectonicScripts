import re

with open("pokemon.txt", "r", encoding="utf8") as infile:
    doc = infile.read()

mons = doc.split("#-------------------------------")
mons = mons[1:]  # first entry is a header, rest fit expected format


def extract_mon_data(mon_text):
    id_match = re.search(r"^InternalName = (.+)", mon_text, re.MULTILINE)
    id = id_match.group(1)

    no_id_text = "\n".join(mon_text.split("\n")[2:])

    return (id, no_id_text)


mon_data = {}

for mon in mons:
    (id, mon_text) = extract_mon_data(mon)
    mon_data[id] = mon_text

with open("pokedexorder.txt", "r", encoding="utf8") as infile:
    order = infile.read().split("\n")

dexout = "# See the documentation on the wiki to learn how to edit this file.\n#-------------------------------\n"

regout = "# See the documentation on the wiki to learn how to edit this file.\n#-------------------------------\n[0]\n"

for i in range(1, len(order) + 1):
    mon_id = order[i - 1]
    mon_text = mon_data[mon_id]
    dexout += f"[{i}]\n"
    dexout += mon_text
    dexout += "#-------------------------------\n"

    evo_line = False

    evo_match = re.search(r"^Evolutions = (.+?),", mon_text, re.MULTILINE)
    if evo_match:
        evo = evo_match.group(1)
        if order[i] == evo:
            evo_line = True

    if evo_line:
        regout += f"{mon_id},"
    else:
        regout += f"{mon_id}\n"


with open("pokemon_reordered.txt", "w", encoding="utf8") as outfile:
    outfile.write(dexout)

with open("regionaldexes.txt", "w", encoding="utf8") as outfile:
    outfile.write(regout)
