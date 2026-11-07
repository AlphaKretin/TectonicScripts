"""
For every tribe, counts and lists the fully evolved Pokemon in it.

Writes tribe_counts.tsv: tribe, count, then one column per Pokemon.
"""

from collections import defaultdict

from tectonic import is_fully_evolved, load_data, parse_args, write_table


def main():
    args = parse_args(__doc__)

    members = defaultdict(list)
    for mon in load_data(args.dev)["pokemon"].values():
        if is_fully_evolved(mon):
            for tribe in mon.get("tribes") or []:
                members[tribe].append(mon["name"])

    widest = max(len(names) for names in members.values())
    header = ("tribe", "count", *(f"pokemon_{i + 1}" for i in range(widest)))
    rows = [(tribe.title(), len(names), *names) for tribe, names in members.items()]
    write_table("tribe_counts.tsv", header, rows)


if __name__ == "__main__":
    main()
