with open("evotribes.txt", "r", encoding="utf8") as infile:
    mons = infile.readlines()

pair_counts = {}

def count_pair(tribe1, tribe2):
    tribes = [tribe1, tribe2]
    tribes.sort() # ensure consistent key order
    tribe_tuple = (tribes[0], tribes[1])
    if tribe_tuple in pair_counts:
        pair_counts[tribe_tuple] += 1
    else:
        pair_counts[tribe_tuple] = 1
    return

for mon in mons:
    terms = mon.strip().split("\t")
    # name and 0-1 tribes, don't contribute to pairs
    length = len(terms)
    if length < 3:
        continue
    # name and exactly two tribes, one pair
    if length == 3:
        count_pair(terms[1], terms[2])
    # name and three tribes, three pairs to handle
    if length == 4:
        count_pair(terms[1], terms[2])
        count_pair(terms[2], terms[3])
        count_pair(terms[1], terms[3])

lines = [pair[0] + "/" + pair[1] + ": " + str(count) for pair,count in pair_counts.items()]

out = "\n".join(lines)

with open("tribecounts.txt", "w", encoding="utf8") as outfile:
    outfile.write(out)