"""
Finds first-stage Pokemon whose second damaging level-up move of one of their
own types (their second STAB move) is learned after level 20.

Writes late_stab_moves.csv, latest second move first, and prints the top 15.
"""

from tectonic import (
    attacking_level_moves,
    is_first_stage,
    load_data,
    mon_types,
    parse_args,
    write_table,
)

LATE_LEVEL = 20


def main():
    args = parse_args(__doc__)
    data = load_data(args.dev)

    results = []
    for key, mon in data["pokemon"].items():
        if not is_first_stage(mon):
            continue
        for mon_type in mon_types(mon):
            stab = attacking_level_moves(mon, data["moves"], mon_type)
            if len(stab) >= 2 and stab[1][0] > LATE_LEVEL:
                (first_level, first), (second_level, second) = stab[:2]
                results.append({
                    "pokemon_id": key,
                    "pokemon_name": mon["name"],
                    "type": mon_type,
                    "first_move": first["name"],
                    "first_move_level": first_level,
                    "second_move": second["name"],
                    "second_move_level": second_level,
                    "level_difference": second_level - first_level,
                })

    results.sort(key=lambda r: r["second_move_level"], reverse=True)
    header = list(results[0]) if results else []
    write_table("late_stab_moves.csv", header, (r.values() for r in results))

    print("\nTop 15 Pokemon with latest second STAB moves:")
    for i, r in enumerate(results[:15], 1):
        print(
            f"{i}. {r['pokemon_name']} ({r['type']}): {r['first_move']} (Lvl {r['first_move_level']})"
            f" -> {r['second_move']} (Lvl {r['second_move_level']})"
        )


if __name__ == "__main__":
    main()
