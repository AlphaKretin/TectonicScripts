import json
import csv
import sys

sys.stdout.reconfigure(newline="")

with open("loadedData-dev.json", "r", encoding="utf8") as f:
    data = json.load(f)

rows = []
for key, p in data.get("pokemon", {}).items():
    flags = p.get("flags", [])
    tribes = p.get("tribes", [])
    is_fully_evolved = len(p.get("evolutions", [])) == 0

    rows.append({
        "key": p.get("key", key),
        "dex_num": p.get("dexNum", ""),
        "name": p.get("name", key),
        "type1": p.get("type1", ""),
        "type2": p.get("type2", ""),
        "tribe1": tribes[0] if len(tribes) > 0 else "",
        "tribe2": tribes[1] if len(tribes) > 1 else "",
        "tribe3": tribes[2] if len(tribes) > 2 else "",
        "num_tribes": len(tribes),
        "hp": p.get("hp", ""),
        "attack": p.get("attack", ""),
        "defense": p.get("defense", ""),
        "speed": p.get("speed", ""),
        "sp_attack": p.get("spAttack", ""),
        "sp_defense": p.get("spDefense", ""),
        "bst": p.get("bst", ""),
        "fully_evolved": is_fully_evolved,
        "legendary": "Legendary" in flags,
        "ultra_beast": "UltraBeast" in flags,
        "flags": "/".join(flags),
    })

rows.sort(key=lambda r: (r["dex_num"] if isinstance(r["dex_num"], int) else 9999, r["key"]))

fieldnames = [
    "key", "dex_num", "name",
    "type1", "type2",
    "tribe1", "tribe2", "tribe3", "num_tribes",
    "hp", "attack", "defense", "speed", "sp_attack", "sp_defense", "bst",
    "fully_evolved", "legendary", "ultra_beast",
    "flags",
]

writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames, delimiter="\t")
writer.writeheader()
writer.writerows(rows)
