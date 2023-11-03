import re

with open("fulldexdoc.txt", "r", encoding="utf8") as infile:
    doc = infile.read()

mons = doc.split("--------------------------------------------")
mons = mons[:-1]  # remove blank last entry
mons = [mon.strip() for mon in mons]  # remove outer whitespace


def extract_mon_data(mon_text):
    name_match = re.search(r"^(.+):", mon_text)
    name = name_match.group(1)

    tribes_match = re.search(r"Tribes: (.+)", mon_text)
    tribes = tribes_match.group(1).split(", ")
    return (name, tribes)


mon_data = [extract_mon_data(mon) for mon in mons]

lines = [mon[0] + "\t" + "\t".join(mon[1]) for mon in mon_data]

out = "\n".join(lines)

with open("montribes.txt", "w", encoding="utf8") as outfile:
    outfile.write(out)
