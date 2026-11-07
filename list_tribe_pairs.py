"""
For every pair of tribes, lists the fully evolved Pokemon that have both.

Writes tribe_pairs.txt, tab-separated with no header: tribe, tribe, then one
column per Pokemon.
"""

from collections import defaultdict
from itertools import combinations

from tectonic import is_fully_evolved, load_data, parse_args, write_table


def main():
    args = parse_args(__doc__)

    pairs = defaultdict(list)
    for mon in load_data(args.dev)["pokemon"].values():
        if is_fully_evolved(mon):
            for pair in combinations(mon.get("tribes") or [], 2):
                pairs[tuple(sorted(pair))].append(mon["name"])

    rows = [
        (tribe1.title(), tribe2.title(), *names)
        for (tribe1, tribe2), names in sorted(pairs.items())
    ]
    write_table("tribe_pairs.txt", None, rows)


if __name__ == "__main__":
    main()
