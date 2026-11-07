"""
For each type, lists the tribe pairs shared by at least 3 fully evolved
Pokemon of that type (at least 2 for Normal).

Writes monotype_dualtribes.csv.
"""

from collections import defaultdict
from itertools import combinations

from tectonic import is_fully_evolved, load_data, mon_types, parse_args, write_table


def main():
    args = parse_args(__doc__)
    data = load_data(args.dev)

    # type -> "TRIBE_A/TRIBE_B" -> names
    pairs = {t: defaultdict(list) for t in data["types"]}
    for mon in data["pokemon"].values():
        if not is_fully_evolved(mon):
            continue
        for mon_type in mon_types(mon):
            for pair in combinations(mon.get("tribes") or [], 2):
                pairs[mon_type]["/".join(sorted(pair))].append(mon["name"])

    rows = [
        (mon_type, pair, len(names), ", ".join(names))
        for mon_type, type_pairs in pairs.items()
        for pair, names in type_pairs.items()
        if len(names) >= 3 or (mon_type == "NORMAL" and len(names) >= 2)
    ]
    write_table("monotype_dualtribes.csv", ("Type", "Tribe Pair", "Count", "Pokemon"), rows)


if __name__ == "__main__":
    main()
