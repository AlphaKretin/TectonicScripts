"""
Lists the BST change for every evolution (pre-evolution -> evolution pair).

Writes evobst.csv.
"""

from tectonic import load_data, parse_args, write_table


def main():
    args = parse_args(__doc__)
    pokemon = load_data(args.dev)["pokemon"]

    rows = []
    for key, mon in pokemon.items():
        for evo in mon.get("evolutions") or []:
            evo_bst = pokemon[evo["pokemon"]]["bst"]
            rows.append((f"{key} -> {evo['pokemon']}", mon["bst"], evo_bst, evo_bst - mon["bst"]))

    write_table("evobst.csv", ("evo_key", "bst", "evo_bst", "bst_diff"), rows)


if __name__ == "__main__":
    main()
