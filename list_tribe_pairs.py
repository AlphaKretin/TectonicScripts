with open("evotribes.txt", "r", encoding="utf8") as infile:
    mons = infile.readlines()

pair_lists = {}

def list_pair(name, tribe1, tribe2):
    tribes = [tribe1, tribe2]
    tribes.sort() # ensure consistent key order
    tribe_tuple = (tribes[0], tribes[1])
    if tribe_tuple in pair_lists:
        pair_lists[tribe_tuple].append(name)
    else:
        pair_lists[tribe_tuple] = [name]
    return

for mon in mons:
    terms = mon.strip().split("\t")
    name = terms[0]
    # name and 0-1 tribes, don't contribute to pairs
    length = len(terms)
    if length < 3:
        continue
    # name and exactly two tribes, one pair
    if length == 3:
        list_pair(name, terms[1], terms[2])
    # name and three tribes, three pairs to handle
    if length == 4:
        list_pair(name, terms[1], terms[2])
        list_pair(name, terms[2], terms[3])
        list_pair(name, terms[1], terms[3])

lines = [pair[0] + "/" + pair[1] + ": " + "\t".join(list) for pair,list in pair_lists.items()]

out = "\n".join(lines)

with open("tribelists.txt", "w", encoding="utf8") as outfile:
    outfile.write(out)