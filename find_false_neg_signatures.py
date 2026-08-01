"""
Detect false-negative signature abilities.

An ability is "signature" if only one evolution line has it.
False negatives are signature abilities that a naive check would miss:
  - Pre-evo only: appears in prior stage(s) but not the final evolution
  - Form-exclusive: appears only in a form (pokemonforms.txt), not in any
    base species entry
"""

import re
from collections import defaultdict

POKEMON_FILE = "pokemon.txt"
FORMS_FILE = "pokemonforms.txt"


def parse_pokemon(filename):
    pokemon = {}
    current = None
    with open(filename, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            m = re.match(r"^\[([A-Za-z0-9_]+)\]$", line)
            if m:
                current = m.group(1)
                pokemon[current] = {"abilities": set(), "evolutions": []}
                continue
            if current is None:
                continue
            if line.startswith("Abilities = "):
                abilities = line[len("Abilities = "):].split(",")
                pokemon[current]["abilities"] = {a.strip() for a in abilities}
            elif line.startswith("Evolutions = "):
                parts = [p.strip() for p in line[len("Evolutions = "):].split(",")]
                i = 0
                while i + 3 <= len(parts):
                    pokemon[current]["evolutions"].append(parts[i])
                    i += 3
    return pokemon


def parse_forms(filename):
    forms = {}
    current = None
    with open(filename, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            m = re.match(r"^\[([A-Za-z0-9_]+),(\d+)\]$", line)
            if m:
                current = (m.group(1), int(m.group(2)))
                forms[current] = {"abilities": set()}
                continue
            if current is None:
                continue
            if line.startswith("Abilities = "):
                abilities = line[len("Abilities = "):].split(",")
                forms[current]["abilities"] = {a.strip() for a in abilities}
    return forms


def build_evo_lines(pokemon):
    evolved_from = {}
    for pid, data in pokemon.items():
        for target in data["evolutions"]:
            if target in pokemon:
                evolved_from[target] = pid

    children = defaultdict(set)
    for child, parent in evolved_from.items():
        children[parent].add(child)

    roots = [pid for pid in pokemon if pid not in evolved_from]

    lines = []
    for root in roots:
        line = set()
        stack = [root]
        while stack:
            pid = stack.pop()
            line.add(pid)
            stack.extend(children[pid])
        lines.append(frozenset(line))
    return lines


def get_finals(pokemon):
    return {
        pid for pid, data in pokemon.items()
        if not any(evo in pokemon for evo in data["evolutions"])
    }


def main():
    pokemon = parse_pokemon(POKEMON_FILE)
    forms = parse_forms(FORMS_FILE)
    evo_lines = build_evo_lines(pokemon)
    finals = get_finals(pokemon)

    pid_to_line_idx = {}
    for i, line in enumerate(evo_lines):
        for pid in line:
            pid_to_line_idx[pid] = i

    # Per-line: collect abilities from base entries and from forms
    line_base_abilities = defaultdict(set)    # from pokemon.txt only
    line_form_abilities = defaultdict(set)    # from pokemonforms.txt only
    line_final_abilities = defaultdict(set)   # from final-evo base entries + their forms

    for i, line in enumerate(evo_lines):
        for pid in line:
            line_base_abilities[i] |= pokemon[pid]["abilities"]

        line_finals = line & finals
        for pid in line_finals:
            line_final_abilities[i] |= pokemon[pid]["abilities"]

        for (pid, _form_num), form_data in forms.items():
            if pid not in pid_to_line_idx:
                continue
            if pid_to_line_idx[pid] != i:
                continue
            line_form_abilities[i] |= form_data["abilities"]
            if pid in line_finals:
                line_final_abilities[i] |= form_data["abilities"]

    # All abilities per line (base + forms)
    line_all_abilities = {
        i: line_base_abilities[i] | line_form_abilities[i]
        for i in range(len(evo_lines))
    }

    # Map ability -> set of line indices that have it
    ability_to_lines = defaultdict(set)
    for i, abilities in line_all_abilities.items():
        for ability in abilities:
            ability_to_lines[ability].add(i)

    signature_abilities = {ab for ab, ls in ability_to_lines.items() if len(ls) == 1}

    # Identify false negatives among signature abilities
    results = []
    for ability in sorted(signature_abilities):
        line_idx = next(iter(ability_to_lines[ability]))
        line = evo_lines[line_idx]
        reasons = []

        # Form-exclusive: in a form but not in any base species of the line
        if ability not in line_base_abilities[line_idx]:
            form_holders = sorted(
                f"{pid} (form {fn})"
                for (pid, fn), fd in forms.items()
                if pid in line and ability in fd["abilities"]
            )
            reasons.append(f"form-exclusive ({', '.join(form_holders)})")

        # Pre-evo only: in a base species but absent from all final evos (base + forms)
        if (ability in line_base_abilities[line_idx]
                and ability not in line_final_abilities[line_idx]):
            pre_evo_holders = sorted(
                pid for pid in line
                if pid not in finals and ability in pokemon[pid]["abilities"]
            )
            line_finals_sorted = sorted(line & finals)
            reasons.append(
                f"pre-evo only (in {', '.join(pre_evo_holders)}; "
                f"finals: {', '.join(line_finals_sorted)})"
            )

        if reasons:
            results.append((ability, line, reasons))

    print(f"Signature abilities (full check): {len(signature_abilities)}")
    print(f"False negatives: {len(results)}\n")

    for ability, line, reasons in results:
        print(f"{ability}")
        for reason in reasons:
            print(f"  {reason}")
        print()


if __name__ == "__main__":
    main()
