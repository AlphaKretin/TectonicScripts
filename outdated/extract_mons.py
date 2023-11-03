import re

with open("fulldexdoc.txt", "r", encoding="utf8") as infile:
    doc = infile.read()

matches = re.findall(r'(.+):\n(?:Types: (.+), (.+)|Type: (.+))', doc)

lines = [match[0] + "\t" + match[1] + "\t" +
         match[2] + "\t" + match[3] for match in matches]

out = "\n".join(lines)

with open("montypes.txt", "w", encoding="utf8") as outfile:
    outfile.write(out)
