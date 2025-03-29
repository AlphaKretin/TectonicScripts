# interface TrainerPokemon {
#     pokemon: Pokemon;
#     sp: StylePoints;
#     level: number;
# }

# export interface Trainer {
#     class: string;
#     name: string;
#     hashName?: string; // for masked villains
#     version: number;
#     pokemon: TrainerPokemon[];
# }


import copy
import json
import re

with open("trainers.txt", "r", encoding="utf8") as infile:
    doc = infile.read()

trainers = doc.split("#-------------------------------")
trainers = trainers[1:]  # first entry is a header, rest fit expected format


def extract_trainer_pokemon(mon_text):
    terms = mon_text.split("\n")[0].split(",")
    id = terms[0]
    level = int(terms[1])
    sp_match = re.search(r"EV = (.+)", mon_text, re.MULTILINE)
    sp_text = sp_match.group(1) if sp_match else None
    if sp_text:
        sp_terms = sp_text.split(",")
        sp = {
            "hp": int(sp_terms[0]),
            "attacks": int(sp_terms[1]),
            "defense": int(sp_terms[2]),
            "speed": int(sp_terms[3]),
            # 4 is spatk, dupe with atk
            "spdef": int(sp_terms[5]),
        }
    else:
        sp = {"hp": 10, "attacks": 10, "defense": 10, "speed": 10, "spdef": 10}

    nickname_match = re.search(r"Name = (.+)", mon_text, re.MULTILINE)
    nickname = nickname_match.group(1) if nickname_match else None
    mon_data = {"id": id, "level": level, "sp": sp, "nickname": nickname}

    return mon_data


def extract_trainer_data(trainer_text):
    id_match = re.search(r"\[(.+)\]", trainer_text, re.MULTILINE)
    id = id_match.group(1)
    terms = id.split(",")
    trainer_class = terms[0]
    name = terms[1]
    if len(terms) > 2:
        version = int(terms[2])
    else:
        version = 0

    hash_name_match = re.search(r"^NameForHashing = (.+)", trainer_text, re.MULTILINE)
    hash_name = hash_name_match.group(1) if hash_name_match else None

    extend_match = re.search(r"^ExtendsVersion = (.+)", trainer_text, re.MULTILINE)
    extends = int(extend_match.group(1)) if extend_match else None

    trainer_mons = trainer_text.split("Pokemon = ")
    trainer_mons = trainer_mons[
        1:
    ]  # first entry is misc data, rest fit expected format

    mon_data = [extract_trainer_pokemon(mon) for mon in trainer_mons]

    trainer_data = {
        "class": trainer_class,
        "name": name,
        "version": version,
        "extends": extends,
        "hashName": hash_name,
        "pokemon": mon_data,
    }

    return trainer_data


trainer_data = [extract_trainer_data(trainer) for trainer in trainers]


def is_extension(trainer, base_trainer):
    return (
        trainer["class"] == base_trainer["class"]
        and trainer["name"] == base_trainer["name"]
        and trainer["extends"] == base_trainer["version"]
    )


# apply extensions
for trainer in trainer_data:
    if trainer["extends"] != None:
        base_trainer = next(
            (
                base_trainer
                for base_trainer in trainer_data
                if is_extension(trainer, base_trainer)
            ),
            None,
        )
        if base_trainer:
            new_mons = []
            for mon in trainer["pokemon"]:
                base_mon = next(
                    (
                        base_mon
                        for base_mon in base_trainer["pokemon"]
                        if mon["id"] == base_mon["id"]
                    ),
                    None,
                )
                # TODO: Append data of base mon if different
                if base_mon == None:
                    new_mons.append(mon)

            trainer["pokemon"] = base_trainer["pokemon"] + new_mons


with open("trainers.json", "w", encoding="utf8") as outfile:
    outfile.write(json.dumps(trainer_data, indent=4))
