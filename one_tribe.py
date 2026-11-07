"""
Lists every Pokemon, at any evolution stage, that has exactly one tribe.

Writes one_tribes.csv.
"""

from tectonic import load_data, parse_args, write_table


def main():
    args = parse_args(__doc__)
    rows = [
        (key, mon["name"], mon["tribes"][0])
        for key, mon in load_data(args.dev)["pokemon"].items()
        if len(mon.get("tribes") or []) == 1
    ]
    write_table("one_tribes.csv", ("pokemon_id", "pokemon_name", "tribe"), rows)


if __name__ == "__main__":
    main()
