"""
For every tribe and type, counts and lists the fully evolved Pokemon with both.

Writes tribe_type_counts.tsv: tribe, type, count, then one column per Pokemon.
"""

from collections import defaultdict

from tectonic import is_fully_evolved, load_data, mon_types, parse_args, write_table


def main():
    args = parse_args(__doc__)

    # tribe -> type -> names
    members = defaultdict(lambda: defaultdict(list))
    for mon in load_data(args.dev)["pokemon"].values():
        if is_fully_evolved(mon):
            for tribe in mon.get("tribes") or []:
                for mon_type in mon_types(mon):
                    members[tribe][mon_type].append(mon["name"])

    rows = [
        (tribe.title(), mon_type.title(), len(names), *names)
        for tribe, types in members.items()
        for mon_type, names in types.items()
    ]
    widest = max(len(row) for row in rows) - 3
    header = ("tribe", "type", "count", *(f"pokemon_{i + 1}" for i in range(widest)))
    write_table("tribe_type_counts.tsv", header, rows)


if __name__ == "__main__":
    main()
