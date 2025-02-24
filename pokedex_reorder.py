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

outdoc = "# See the documentation on the wiki to learn how to edit this file.\n#-------------------------------\n"

for i in range(1, len(order) + 1):
    outdoc += f"[{i}]\n"
    outdoc += mon_data[order[i - 1]]
    outdoc += "#-------------------------------\n"

with open("pokemon_reordered.txt", "w", encoding="utf8") as outfile:
    outfile.write(outdoc)
