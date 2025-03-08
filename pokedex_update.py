import re

with open("pokemon.txt", "r", encoding="utf8") as infile:
    doc = infile.read()

mons = doc.split("#-------------------------------")
mons = mons[1:]  # first entry is a header, rest fit expected format


def extract_mon_data(mon_text):
    id_regex = r"^InternalName = (.+)\n"
    id_match = re.search(id_regex, mon_text, re.MULTILINE)
    id = id_match.group(1)

    no_id_text = re.sub(id_regex, "", mon_text, flags=re.MULTILINE)

    no_id_text = "\n".join(no_id_text.split("\n")[2:])

    return (id, no_id_text)


mon_data = {}

for mon in mons:
    (id, mon_text) = extract_mon_data(mon)
    mon_data[id] = mon_text

dexout = "# See the documentation on the wiki to learn how to edit this file.\n#-------------------------------\n"

for mon_id in mon_data:
    mon_text = mon_data[mon_id]
    dexout += f"[{mon_id}]\n"
    dexout += mon_text
    dexout += "#-------------------------------\n"


with open("pokemon_new.txt", "w", encoding="utf8") as outfile:
    outfile.write(dexout)
