import re

SURFING_FOLLOWERS = [
    # Gen 1
    "BEEDRILL", "VENOMOTH", "ABRA", "GEODUDE", "MAGNEMITE", "GASTLY", "HAUNTER",
    "KOFFING", "WEEZING", "PORYGON", "MEWTWO", "MEW",
    # Gen 2
    "MISDREAVUS", "UNOWN", "PORYGON2", "CELEBI",
    # Gen 3
    "DUSTOX", "SHEDINJA", "MEDITITE", "VOLBEAT", "ILLUMISE", "FLYGON", "LUNATONE",
    "SOLROCK", "BALTOY", "CLAYDOL", "CASTFORM", "SHUPPET", "DUSKULL", "CHIMECHO",
    "GLALIE", "BELDUM", "METANG", "LATIAS", "LATIOS", "JIRACHI",
    # Gen 4
    "MISMAGIUS", "BRONZOR", "BRONZONG", "SPIRITOMB", "CARNIVINE", "MAGNEZONE",
    "PORYGONZ", "PROBOPASS", "DUSKNOIR", "FROSLASS", "ROTOM", "UXIE", "MESPRIT",
    "AZELF", "GIRATINA", "CRESSELIA", "DARKRAI",
    # Gen 5
    "MUNNA", "MUSHARNA", "YAMASK", "COFAGRIGUS", "SOLOSIS", "DUOSION", "REUNICLUS",
    "VANILLITE", "VANILLISH", "VANILLUXE", "ELGYEM", "BEHEEYEM", "LAMPENT",
    "CHANDELURE", "CRYOGONAL", "HYDREIGON", "VOLCARONA", "RESHIRAM", "ZEKROM",
    # Gen 6
    "SPRITZEE", "DRAGALGE", "CARBINK", "KLEFKI", "PHANTUMP", "DIANCIE", "HOOPA",
    # Gen 7
    "VIKAVOLT", "CUTIEFLY", "RIBOMBEE", "COMFEY", "DHELMISE", "TAPUKOKO", "TAPULELE",
    "TAPUBULU", "COSMOG", "COSMOEM", "LUNALA", "NIHILEGO", "KARTANA", "NECROZMA",
    "MAGEARNA", "POIPOLE", "NAGANADEL",
    # Gen 8
    "ORBEETLE", "FLAPPLE", "SINISTEA", "POLTEAGEIST", "FROSMOTH", "DREEPY", "DRAKLOAK",
    "DRAGAPULT", "ETERNATUS", "REGIELEKI", "REGIDRAGO", "CALYREX",
    # Tectonic original
    "MGOLDEEN", "MSEAKING", "MMUNNA", "MMUSHARNA", "MBEAUTIFLY", "MDUSTOX"
]

SURFING_FOLLOWERS_EXCEPTIONS = [
    # Gen I
    "CHARIZARD", "PIDGEY", "SPEAROW", "FARFETCHD", "DODUO", "DODRIO", "SCYTHER",
    "ZAPDOS_1","KRABBY","KINGLER","KLAWSAR",
    # Gen II
    "NATU", "XATU", "MURKROW", "DELIBIRD",
    # Gen III
    "TAILLOW", "VIBRAVA", "TROPIUS",
    # Gen IV
    "STARLY", "HONCHKROW", "CHINGLING", "CHATOT", "ROTOM_1", "ROTOM_2", "ROTOM_3",
    "ROTOM_5", "SHAYMIN_1", "ARCEUS_2",
    # Gen V
    "ARCHEN", "DUCKLETT", "EMOLGA", "EELEKTRIK", "EELEKTROSS", "RUFFLET", "VULLABY",
    "LANDORUS_1",
    # Gen VI
    "FLETCHLING", "HAWLUCHA",
    # Gen VII
    "ROWLET", "DARTRIX", "PIKIPEK", "ORICORIO", "SILVALLY_2",
    # Gen VIII
    "ROOKIDEE",
    # Tectonic original
    "MVULLABY", "MMANDIBUZZ"
]

def add_flag_to_pokemon(content, pokemon_name, flag):
    """Add a flag to a Pokemon entry, creating the Flags line if needed."""
    # Pattern to find the Pokemon section
    section_pattern = rf'(\[{re.escape(pokemon_name)}\].*?)(?=\n#-+\n|\n\[|\Z)'

    match = re.search(section_pattern, content, re.DOTALL)
    if not match:
        print(f"Warning: Could not find Pokemon [{pokemon_name}]")
        return content

    section = match.group(1)
    section_start = match.start(1)
    section_end = match.end(1)

    # Check if Flags line exists
    flags_match = re.search(r'^(Flags\s*=\s*)(.*)$', section, re.MULTILINE)

    if flags_match:
        # Flags line exists - add the flag if not already present
        existing_flags = flags_match.group(2)
        if flag in existing_flags.split(','):
            print(f"  {pokemon_name}: Flag '{flag}' already exists")
            return content

        new_flags = existing_flags + ',' + flag
        new_section = section[:flags_match.start(2)] + new_flags + section[flags_match.end(2):]
        print(f"  {pokemon_name}: Added '{flag}' to existing Flags")
    else:
        # No Flags line - need to add one
        # Find a good place to insert it (after Generation line, or at end of section)
        gen_match = re.search(r'^(Generation\s*=\s*.*)$', section, re.MULTILINE)
        if gen_match:
            insert_pos = gen_match.end()
            new_section = section[:insert_pos] + f'\nFlags = {flag}' + section[insert_pos:]
            print(f"  {pokemon_name}: Added new Flags line with '{flag}'")
        else:
            # No Generation line, add at end of section (before any trailing whitespace)
            stripped = section.rstrip()
            new_section = stripped + f'\nFlags = {flag}' + section[len(stripped):]
            print(f"  {pokemon_name}: Added new Flags line with '{flag}' (no Generation line found)")

    content = content[:section_start] + new_section + content[section_end:]
    return content

def main():
    # Read the pokemon.txt file
    with open('pokemon.txt', 'r', encoding='utf-8') as f:
        content = f.read()

    print("Adding FollowSurf flags...")
    for pokemon in SURFING_FOLLOWERS:
        content = add_flag_to_pokemon(content, pokemon, 'FollowSurf')

    print("\nAdding NoFollowSurf flags...")
    for pokemon in SURFING_FOLLOWERS_EXCEPTIONS:
        content = add_flag_to_pokemon(content, pokemon, 'NoFollowSurf')

    # Write the updated content back
    with open('pokemon.txt', 'w', encoding='utf-8') as f:
        f.write(content)

    print("\nDone! pokemon.txt has been updated.")

if __name__ == '__main__':
    main()
