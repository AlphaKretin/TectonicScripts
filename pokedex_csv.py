"""
Dumps the whole Pokedex, one row per Pokemon in dex order, with types, tribes,
base stats and flags.

Writes pokedex.tsv.
"""

from tectonic import is_fully_evolved, load_data, parse_args, write_table

HEADER = (
    "key", "dex_num", "name",
    "type1", "type2",
    "tribe1", "tribe2", "tribe3", "num_tribes",
    "hp", "attack", "defense", "speed", "sp_attack", "sp_defense", "bst",
    "fully_evolved", "legendary", "ultra_beast",
    "flags",
)


def main():
    args = parse_args(__doc__)

    rows = []
    for key, mon in load_data(args.dev)["pokemon"].items():
        flags = mon.get("flags") or []
        tribes = (mon.get("tribes") or []) + ["", "", ""]
        rows.append((
            key, mon.get("dexNum", ""), mon["name"],
            mon.get("type1", ""), mon.get("type2", ""),
            *tribes[:3], len(mon.get("tribes") or []),
            mon["hp"], mon["attack"], mon["defense"], mon["speed"],
            mon["spAttack"], mon["spDefense"], mon["bst"],
            is_fully_evolved(mon), "Legendary" in flags, "UltraBeast" in flags,
            "/".join(flags),
        ))

    rows.sort(key=lambda r: (r[1] if isinstance(r[1], int) else 9999, r[0]))
    write_table("pokedex.tsv", HEADER, rows)


if __name__ == "__main__":
    main()
