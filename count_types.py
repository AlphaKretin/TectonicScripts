import re

with open("pokemon.txt", "r", encoding="utf8") as infile:
    doc = infile.read()

mons = doc.split("#-------------------------------")
mons = mons[1:]  # first entry is a header, rest fit expected format


def extract_mon_data(mon_text):
    id_match = re.search(r"^InternalName = (.+)", mon_text, re.MULTILINE)
    id = id_match.group(1)

    type1_match = re.search(r"^Type1 = (.+)", mon_text, re.MULTILINE)
    type1 = type1_match.group(1).title()

    type2_match = re.search(r"^Type2 = (.+)", mon_text, re.MULTILINE)
    type2 = type2_match.group(1).title() if type2_match else ""

    return (id, type1, type2)


mon_data = {}

type_counts = {}

for mon in mons:
    (id, type1, type2) = extract_mon_data(mon)
    if type1 in type_counts:
        type_counts[type1] += 1
    else:
        type_counts[type1] = 1
    if len(type2) > 0:
        if type2 in type_counts:
            type_counts[type2] += 1
        else:
            type_counts[type2] = 1

sorted_counts = {k: v for k, v in sorted(type_counts.items(), key=lambda item: item[1])}

lines = [type + ": " + str(count) for type, count in sorted_counts.items()]

out = "\n".join(lines)

with open("typecounts.txt", "w", encoding="utf8") as outfile:
    outfile.write(out)
