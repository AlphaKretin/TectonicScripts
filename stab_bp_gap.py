"""
For each type of each first-stage Pokemon, compares the base power of its first
two damaging level-up moves of that type (its first two STAB moves).

Writes type_move_bp_differences.csv, biggest gap first, and prints the top 10.
"""

from tectonic import (
    attacking_level_moves,
    is_first_stage,
    load_data,
    mon_types,
    parse_args,
    write_table,
)


def main():
    args = parse_args(__doc__)
    data = load_data(args.dev)

    results = []
    for key, mon in data["pokemon"].items():
        if not is_first_stage(mon):
            continue
        for mon_type in mon_types(mon):
            stab = attacking_level_moves(mon, data["moves"], mon_type)
            if len(stab) >= 2:
                (first_level, first), (second_level, second) = stab[:2]
                results.append({
                    "pokemon_id": key,
                    "pokemon_name": mon["name"],
                    "type": mon_type,
                    "first_move": first["name"],
                    "first_move_bp": first["power"],
                    "first_move_level": first_level,
                    "second_move": second["name"],
                    "second_move_bp": second["power"],
                    "second_move_level": second_level,
                    "bp_difference": abs(first["power"] - second["power"]),
                })

    results.sort(key=lambda r: r["bp_difference"], reverse=True)
    header = list(results[0]) if results else []
    write_table("type_move_bp_differences.csv", header, (r.values() for r in results))

    print("\nTop 10 highest BP differences:")
    for i, r in enumerate(results[:10], 1):
        print(
            f"{i}. {r['pokemon_name']} ({r['type']}): {r['first_move']} ({r['first_move_bp']} BP)"
            f" vs {r['second_move']} ({r['second_move_bp']} BP) = {r['bp_difference']} difference"
        )


if __name__ == "__main__":
    main()
