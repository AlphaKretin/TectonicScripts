"""
Lists every fully evolved Pokemon (one with no further evolutions).

Writes evomons.csv.
"""

from tectonic import is_fully_evolved, load_data, parse_args, write_table


def main():
    args = parse_args(__doc__)
    rows = [
        (key, mon["name"])
        for key, mon in load_data(args.dev)["pokemon"].items()
        if is_fully_evolved(mon)
    ]
    write_table("evomons.csv", ("pokemon_id", "pokemon_name"), rows)


if __name__ == "__main__":
    main()
