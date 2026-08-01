"""
Replicates the type/move-learning statistical analyses described in
pokemon_type_analysis_summary.md, using Pokemon Tectonic's loadedData.json
instead of the official games' veekun dataset.

Move-learning methods:
  - "full" pass:     level-up + line/tutor moves + form-specific moves
  - "natural" pass:  level-up only

In this dataset TMs and tutoring teach the same move pool (lineMoves /
tutorMoves), so there's no separate TM-only category to track.
"""

import csv
import json
import os
from collections import Counter

import matplotlib.pyplot as plt
import pandas as pd

DATA_FILE = "loadedData.json"
OUTPUT_DIR = "type_analysis_output"
MODES = ("full", "natural", "full_no_omni")

# A non-Normal damaging move counts as "omnipresent" if more than this % of
# Pokemon that aren't of its own type can still learn it (Normal moves are
# expected to be near-universal and are handled separately, not flagged here).
OMNIPRESENT_THRESHOLD = 50


def load_data():
    with open(DATA_FILE, encoding="utf8") as f:
        return json.load(f)


def get_real_types(data):
    return sorted(
        (key for key, t in data["types"].items() if t.get("isRealType")),
        key=lambda key: data["types"][key]["index"],
    )


def type_name(data, key):
    return data["types"][key]["name"]


def get_damaging_move_types(data, real_types):
    real_types = set(real_types)
    move_types = {}
    for move in data["moves"].values():
        if move.get("category") == "Status":
            continue
        move_type = move.get("type")
        if move_type in real_types:
            move_types[move["key"]] = move_type
    return move_types


def build_pokemon_records(data, move_types):
    records = []
    for key, mon in data["pokemon"].items():
        types = set()
        if mon.get("type1"):
            types.add(mon["type1"])
        if mon.get("type2"):
            types.add(mon["type2"])

        level_moves = {m["move"] for m in mon.get("levelMoves") or []}
        tutor_moves = set(mon.get("lineMoves") or []) | set(mon.get("tutorMoves") or [])
        form_moves = {m for m in (mon.get("formSpecificMoves") or []) if m}

        records.append({
            "key": key,
            "name": mon.get("name", key),
            "types": types,
            "level_moves": level_moves,
            "full_moves": level_moves | tutor_moves | form_moves,
            "move_types": {},
        })
    return records


def compute_move_type_sets(records, move_types, mode, excluded_moves=frozenset()):
    """Populate record["move_types"][mode] with the set of damaging move types
    learnable under `mode` ("full", "natural", or "full_no_omni")."""
    raw_field = "level_moves" if mode == "natural" else "full_moves"
    for r in records:
        moves = r[raw_field] - excluded_moves if excluded_moves else r[raw_field]
        r["move_types"][mode] = {move_types[m] for m in moves if m in move_types}


def learnable_types(record, mode):
    return record["move_types"][mode]


# ---------------------------------------------------------------------------
# Omnipresent move detection (e.g. Fling) used to build the "full_no_omni" pass
# ---------------------------------------------------------------------------

def find_omnipresent_moves(data, records, move_types, threshold=OMNIPRESENT_THRESHOLD):
    flagged = []
    for move_key, move_type in move_types.items():
        if move_type == "NORMAL":
            continue
        non_type = [r for r in records if move_type not in r["types"]]
        if not non_type:
            continue
        learners = sum(1 for r in non_type if move_key in r["full_moves"])
        pct = 100 * learners / len(non_type)
        if pct > threshold:
            flagged.append({
                "move": move_key,
                "move_name": data["moves"][move_key]["name"],
                "type": type_name(data, move_type),
                "pct": round(pct, 1),
                "learners": learners,
                "eligible": len(non_type),
            })
    flagged.sort(key=lambda x: -x["pct"])
    return flagged


def write_omnipresent_moves(flagged):
    path = os.path.join(OUTPUT_DIR, "omnipresent_moves.csv")
    with open(path, "w", newline="", encoding="utf8") as f:
        writer = csv.DictWriter(f, fieldnames=["move", "move_name", "type", "pct", "learners", "eligible"])
        writer.writeheader()
        writer.writerows(flagged)


# ---------------------------------------------------------------------------
# Analysis 1: Move Type Learnability
# ---------------------------------------------------------------------------

def analysis1_learnability(records, real_types, mode):
    results = {}
    for move_type in real_types:
        eligible = [r for r in records if move_type not in r["types"]]
        learners = [r for r in eligible if move_type in learnable_types(r, mode)]
        pct = 100 * len(learners) / len(eligible) if eligible else 0.0
        results[move_type] = {"pct": pct, "eligible": len(eligible), "learners": len(learners)}
    return results


def round_row(row, keys, ndigits=1):
    return {**row, **{k: round(row[k], ndigits) for k in keys if row.get(k) is not None}}


def write_learnability(data, results, real_types, mode):
    path = os.path.join(OUTPUT_DIR, f"type_learnability_{mode}.csv")
    rows = sorted(
        (round_row({"type": type_name(data, t), **results[t]}, ["pct"]) for t in real_types),
        key=lambda r: -r["pct"],
    )
    with open(path, "w", newline="", encoding="utf8") as f:
        writer = csv.DictWriter(f, fieldnames=["type", "pct", "eligible", "learners"])
        writer.writeheader()
        writer.writerows(rows)
    return rows


# ---------------------------------------------------------------------------
# Analysis 2: Per-Type Move-Learning Affinity Matrix
# ---------------------------------------------------------------------------

def analysis2_affinity_matrix(records, real_types, mode):
    matrix = {}
    for pkmn_type in real_types:
        row = {}
        for move_type in real_types:
            if pkmn_type == move_type:
                row[move_type] = None
                continue
            group = [r for r in records if pkmn_type in r["types"] and move_type not in r["types"]]
            learners = [r for r in group if move_type in learnable_types(r, mode)]
            row[move_type] = 100 * len(learners) / len(group) if group else None
        matrix[pkmn_type] = row
    return matrix


def write_affinity_matrix(data, matrix, real_types, mode):
    path = os.path.join(OUTPUT_DIR, f"type_affinity_matrix_{mode}.csv")
    names = [type_name(data, t) for t in real_types]
    df = pd.DataFrame(
        [[matrix[p][m] for m in real_types] for p in real_types],
        index=names,
        columns=names,
    )
    df.to_csv(path, float_format="%.1f")
    return df


# ---------------------------------------------------------------------------
# Analysis 3: Type Versatility Score (Weighted Affinity)
# ---------------------------------------------------------------------------

def analysis3_versatility(real_types, learnability, affinity_matrix):
    scores = {}
    for pkmn_type in real_types:
        weighted_sum = 0.0
        weight_total = 0.0
        for move_type in real_types:
            if move_type == pkmn_type:
                continue
            p_in = affinity_matrix[pkmn_type][move_type]
            if p_in is None:
                continue
            p_out = learnability[move_type]["pct"]
            if p_out <= 0:
                continue
            weight = 1 / p_out
            weighted_sum += weight * (p_in - p_out)
            weight_total += weight
        scores[pkmn_type] = weighted_sum / weight_total if weight_total else 0.0
    return scores


def write_versatility(data, scores, real_types, mode):
    path = os.path.join(OUTPUT_DIR, f"type_versatility_{mode}.csv")
    rows = sorted(
        (round_row({"type": type_name(data, t), "versatility_score": scores[t]}, ["versatility_score"], 3)
         for t in real_types),
        key=lambda r: -r["versatility_score"],
    )
    with open(path, "w", newline="", encoding="utf8") as f:
        writer = csv.DictWriter(f, fieldnames=["type", "versatility_score"])
        writer.writeheader()
        writer.writerows(rows)
    return rows


# ---------------------------------------------------------------------------
# Analysis 4: Dual-Type Confound Check
# ---------------------------------------------------------------------------

def common_dual_type_pairs(records, top_n=10):
    counts = Counter()
    for r in records:
        if len(r["types"]) == 2:
            counts[frozenset(r["types"])] += 1
    return counts.most_common(top_n)


def analysis4_dual_type_confound(data, records, real_types, mode, dual_pairs):
    rows = []
    for pair, pair_count in dual_pairs:
        for primary, secondary in (tuple(pair), tuple(reversed(tuple(pair)))):
            group = [r for r in records if primary in r["types"]]
            with_secondary = [r for r in group if secondary in r["types"]]
            without_secondary = [r for r in group if secondary not in r["types"]]
            if not with_secondary:
                continue
            for move_type in real_types:
                if move_type in (primary, secondary):
                    continue
                with_pct = 100 * sum(
                    1 for r in with_secondary if move_type in learnable_types(r, mode)
                ) / len(with_secondary)
                if with_pct == 0:
                    continue
                if without_secondary:
                    without_pct = 100 * sum(
                        1 for r in without_secondary if move_type in learnable_types(r, mode)
                    ) / len(without_secondary)
                else:
                    without_pct = None

                if without_pct is None:
                    verdict = f"all {type_name(data, primary)}-types are dual-typed with {type_name(data, secondary)}"
                elif without_pct == 0:
                    verdict = "fully explained by secondary type"
                elif with_pct - without_pct >= 30:
                    verdict = "partially explained by secondary type"
                else:
                    continue

                rows.append({
                    "primary_type": type_name(data, primary),
                    "secondary_type": type_name(data, secondary),
                    "pair_frequency": pair_count,
                    "move_type": type_name(data, move_type),
                    "pct_with_secondary": round(with_pct, 1),
                    "n_with_secondary": len(with_secondary),
                    "pct_without_secondary": round(without_pct, 1) if without_pct is not None else None,
                    "n_without_secondary": len(without_secondary),
                    "verdict": verdict,
                })
    return rows


def write_dual_type_confound(rows, mode):
    path = os.path.join(OUTPUT_DIR, f"dual_type_confound_{mode}.csv")
    fieldnames = [
        "primary_type", "secondary_type", "pair_frequency", "move_type",
        "pct_with_secondary", "n_with_secondary",
        "pct_without_secondary", "n_without_secondary", "verdict",
    ]
    with open(path, "w", newline="", encoding="utf8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


# ---------------------------------------------------------------------------
# Analysis 5: Versatility vs. Learnability Scatterplot
# ---------------------------------------------------------------------------

def plot_versatility_vs_learnability(data, real_types, learnability, versatility, mode):
    path = os.path.join(OUTPUT_DIR, f"versatility_vs_learnability_{mode}.png")
    xs = [learnability[t]["pct"] for t in real_types]
    ys = [versatility[t] for t in real_types]
    labels = [type_name(data, t) for t in real_types]

    fig, ax = plt.subplots(figsize=(9, 7))
    ax.scatter(xs, ys)
    for x, y, label in zip(xs, ys, labels):
        ax.annotate(label, (x, y), textcoords="offset points", xytext=(4, 4), fontsize=8)
    ax.set_xlabel("Learnability % (how widely the type's moves are taught)")
    ax.set_ylabel("Versatility score (weighted affinity)")
    ax.set_title(f"Versatility vs. Learnability ({mode} movesets)")
    ax.axhline(0, color="grey", linewidth=0.5)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Analysis 6: Full-Coverage Individual Pokemon
# ---------------------------------------------------------------------------

def analysis6_full_coverage(records, real_types, mode):
    real_type_set = set(real_types)
    results = []
    for r in records:
        learned = learnable_types(r, mode) & real_type_set
        missing = real_type_set - learned
        if len(missing) <= 1:
            results.append({
                "key": r["key"],
                "name": r["name"],
                "coverage": len(learned),
                "missing_types": ",".join(sorted(missing)),
            })
    results.sort(key=lambda x: -x["coverage"])
    return results


def write_full_coverage(results, mode):
    path = os.path.join(OUTPUT_DIR, f"full_coverage_{mode}.csv")
    with open(path, "w", newline="", encoding="utf8") as f:
        writer = csv.DictWriter(f, fieldnames=["key", "name", "coverage", "missing_types"])
        writer.writeheader()
        writer.writerows(results)
    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    data = load_data()
    real_types = get_real_types(data)
    move_types = get_damaging_move_types(data, real_types)
    records = build_pokemon_records(data, move_types)

    print(f"Loaded {len(records)} Pokemon, {len(move_types)} damaging moves across {len(real_types)} types.\n")

    compute_move_type_sets(records, move_types, "full")
    compute_move_type_sets(records, move_types, "natural")

    omnipresent = find_omnipresent_moves(data, records, move_types)
    write_omnipresent_moves(omnipresent)
    print(f"Omnipresent move check (>{OMNIPRESENT_THRESHOLD}% of non-type Pokemon, excluding Normal moves):")
    if omnipresent:
        for row in omnipresent:
            print(f"  {row['move_name']:<20} {row['type']:<10} {row['pct']:5.1f}% ({row['learners']}/{row['eligible']})")
    else:
        print("  none found")
    print()

    excluded_moves = {row["move"] for row in omnipresent}
    compute_move_type_sets(records, move_types, "full_no_omni", excluded_moves)

    dual_pairs = common_dual_type_pairs(records)

    for mode in MODES:
        print(f"=== {mode.upper()} moveset pass ===")

        learnability = analysis1_learnability(records, real_types, mode)
        learnability_rows = write_learnability(data, learnability, real_types, mode)
        print("Analysis 1 - Move Type Learnability (top 5):")
        for row in learnability_rows[:5]:
            print(f"  {row['type']:<10} {row['pct']:5.1f}%  ({row['learners']}/{row['eligible']})")

        affinity_matrix = analysis2_affinity_matrix(records, real_types, mode)
        write_affinity_matrix(data, affinity_matrix, real_types, mode)
        print("Analysis 2 - Affinity matrix written.")

        versatility = analysis3_versatility(real_types, learnability, affinity_matrix)
        versatility_rows = write_versatility(data, versatility, real_types, mode)
        print("Analysis 3 - Type Versatility Score (top 5):")
        for row in versatility_rows[:5]:
            print(f"  {row['type']:<10} {row['versatility_score']:6.2f}")

        confound_rows = analysis4_dual_type_confound(data, records, real_types, mode, dual_pairs)
        write_dual_type_confound(confound_rows, mode)
        print(f"Analysis 4 - Dual-type confound check: {len(confound_rows)} flagged cases written.")

        plot_versatility_vs_learnability(data, real_types, learnability, versatility, mode)
        print("Analysis 5 - Scatterplot written.")

        coverage_rows = write_full_coverage(analysis6_full_coverage(records, real_types, mode), mode)
        full_coverage = [r for r in coverage_rows if r["coverage"] == len(real_types)]
        print(f"Analysis 6 - Full coverage (18/18): {len(full_coverage)} Pokemon; "
              f"17/18 coverage: {len(coverage_rows) - len(full_coverage)} Pokemon.")
        for row in full_coverage:
            print(f"  {row['name']}")

        print()

    print(f"All outputs written to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
