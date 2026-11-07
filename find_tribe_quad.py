"""
Finds teams of 4 fully evolved Pokemon in which at least 4 tribes each appear
on 3 or more team members.

Very slow: it tries every 4-combination of distinct tribe sets, which runs to
billions of combinations.

Writes tribe_quads.txt.
"""

from collections import Counter, defaultdict
from itertools import combinations_with_replacement

from tectonic import is_fully_evolved, load_data, parse_args


def main():
    args = parse_args(__doc__)

    # Pokemon names grouped by their set of tribes
    tribe_groups = defaultdict(list)
    for mon in load_data(args.dev)["pokemon"].values():
        if is_fully_evolved(mon) and mon.get("tribes"):
            tribe_groups[frozenset(mon["tribes"])].append(mon["name"])

    group_list = sorted(tribe_groups.items(), key=lambda x: sorted(x[0]))
    print(f"Unique tribe sets among fully-evolved Pokemon: {len(group_list)}")

    results = []
    # With replacement, since two team members can share a tribe set
    for idx_combo in combinations_with_replacement(range(len(group_list)), 4):
        idx_counts = Counter(idx_combo)
        if not all(len(group_list[idx][1]) >= count for idx, count in idx_counts.items()):
            continue

        tribe_counts = Counter()
        for idx in idx_combo:
            tribe_counts.update(group_list[idx][0])

        qualifying_tribes = [tribe for tribe, count in tribe_counts.items() if count >= 3]
        if len(qualifying_tribes) >= 4:
            results.append((idx_counts, qualifying_tribes))

    print(f"Found {len(results)} valid combinations")

    lines = []
    for idx_counts, qualifying_tribes in results:
        lines.append(f"Qualifying tribes (3+ copies): {', '.join(sorted(qualifying_tribes))}")
        for idx, count in sorted(idx_counts.items()):
            tribes, names = group_list[idx]
            label = f" × {count}" if count > 1 else ""
            lines.append(f"  {sorted(tribes)}{label}: {', '.join(names[:count])}")
        lines.append("")

    with open("tribe_quads.txt", "w", encoding="utf8") as f:
        f.write("\n".join(lines))
    print("Results saved to tribe_quads.txt")


if __name__ == "__main__":
    main()
