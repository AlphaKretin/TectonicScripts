"""
Compares the power and accuracy of the moves fully evolved Pokemon have
access to by level up at various level caps.

Steps:
  1. Filter for fully evolved Pokemon (no evolutions).
  2. Split them by whether they learn any level-up move above level 60.
  3. For the "learns above 60" group, check every multiple of 5 from 40 to 70.
     For the "nothing above 60" group, check level 45 only.
  4. At each level, take each Pokemon's last level-up move learned strictly
     before that level, average the power and accuracy of those moves, and
     count how many have high power, low accuracy, or both, and how many are
     "bread-and-butter" (BB) moves at exactly 90 power and 100 accuracy.

By default only damaging moves are counted, since status moves have no power.
Pass --include-status to count every move. Moves with 0 accuracy (moves that
can't miss) are left out of the accuracy average and never count as low
accuracy.

Prints its tables to stdout.
"""

from tectonic import is_fully_evolved, level_moves, load_data, parse_args

SPLIT_LEVEL = 60
YES_LEVELS = list(range(40, 71, 5))
NO_LEVELS = [45]
HIGH_POWER = 90
FULL_ACCURACY = 100


def last_move_before(mon_moves, level, moves_data, include_status):
    last = None
    for move_level, move_key in mon_moves:
        if move_level >= level:
            break
        move = moves_data.get(move_key)
        if move is None:
            continue
        if not include_status and move.get("category") == "Status":
            continue
        last = move
    return last


def analyse(mons, level, moves_data, include_status):
    powers = []
    accuracies = []
    no_move = 0
    high_power = 0
    low_acc = 0
    both = 0
    bread_and_butter = 0
    for mon in mons:
        move = last_move_before(mon["moves"], level, moves_data, include_status)
        if move is None:
            no_move += 1
            continue
        power = move.get("power") or 0
        acc = move.get("accuracy") or 0
        powers.append(power)
        if acc > 0:
            accuracies.append(acc)
        is_high_power = power > HIGH_POWER
        is_low_acc = 0 < acc < FULL_ACCURACY
        high_power += is_high_power
        low_acc += is_low_acc
        both += is_high_power and is_low_acc
        bread_and_butter += power == HIGH_POWER and acc == FULL_ACCURACY
    return {
        "bread_and_butter": bread_and_butter,
        "high_power": high_power,
        "low_acc": low_acc,
        "both": both,
        "level": level,
        "count": len(powers),
        "no_move": no_move,
        "avg_power": sum(powers) / len(powers) if powers else 0,
        "avg_accuracy": sum(accuracies) / len(accuracies) if accuracies else 0,
        "acc_count": len(accuracies),
    }


def print_table(title, results):
    print(f"\n{title}")
    print(
        f"{'Level':>5}  {'Mons':>5}  {'Avg Power':>9}  {'Avg Acc':>7}  {'Acc n':>5}  "
        f"{'Pow>' + str(HIGH_POWER):>6}  {'Acc<' + str(FULL_ACCURACY):>7}  {'Both':>4}  {'BB':>4}  {'No move':>7}"
    )
    for r in results:
        print(
            f"{r['level']:>5}  {r['count']:>5}  {r['avg_power']:>9.2f}  "
            f"{r['avg_accuracy']:>7.2f}  {r['acc_count']:>5}  "
            f"{r['high_power']:>6}  {r['low_acc']:>7}  {r['both']:>4}  {r['bread_and_butter']:>4}  {r['no_move']:>7}"
        )


def main():
    args = parse_args(
        __doc__,
        lambda p: p.add_argument(
            "--include-status", action="store_true", help="count status moves too"
        ),
    )

    data = load_data(args.dev)
    moves_data = data["moves"]

    fully_evolved = [
        {"key": key, "name": mon["name"], "moves": level_moves(mon)}
        for key, mon in data["pokemon"].items()
        if is_fully_evolved(mon)
    ]

    learns_late = [
        m for m in fully_evolved if any(lvl > SPLIT_LEVEL for lvl, _ in m["moves"])
    ]
    no_late = [
        m for m in fully_evolved if not any(lvl > SPLIT_LEVEL for lvl, _ in m["moves"])
    ]

    print(f"Fully evolved Pokemon: {len(fully_evolved)}")
    print(f"  Learn a move above level {SPLIT_LEVEL}: {len(learns_late)}")
    print(f"  Don't learn a move above level {SPLIT_LEVEL}: {len(no_late)}")
    print("Counting " + ("all moves" if args.include_status else "damaging moves only"))
    print(
        "'Acc n' = moves with an accuracy value (can't-miss moves are excluded from Avg Acc)"
    )
    print("'No move' = Pokemon with no qualifying move before that level")

    print_table(
        f"Learns moves above level {SPLIT_LEVEL}",
        [
            analyse(learns_late, lvl, moves_data, args.include_status)
            for lvl in YES_LEVELS
        ],
    )
    print_table(
        f"No moves above level {SPLIT_LEVEL}",
        [analyse(no_late, lvl, moves_data, args.include_status) for lvl in NO_LEVELS],
    )


if __name__ == "__main__":
    main()
