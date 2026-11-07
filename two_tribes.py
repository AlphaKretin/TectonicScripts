"""
Lists every fully evolved Pokemon that has exactly two tribes.

Writes two_tribes.csv.
"""

from tectonic import is_fully_evolved, load_data, parse_args, write_table


def main():
    args = parse_args(__doc__)
    rows = [
        (key, mon["name"], *mon["tribes"])
        for key, mon in load_data(args.dev)["pokemon"].items()
        if is_fully_evolved(mon) and len(mon.get("tribes") or []) == 2
    ]
    write_table("two_tribes.csv", ("pokemon_id", "pokemon_name", "tribe1", "tribe2"), rows)


if __name__ == "__main__":
    main()
