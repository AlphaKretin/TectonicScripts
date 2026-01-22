

# Variable Length Encoding with Dictionary Words
# Tier 1 (4 bits):  0xxx           → 8 single chars (most frequent)
# Tier 2 (6 bits):  10xxxx         → 16 single chars (next frequent)
# Tier 3 (8 bits):  110xxxxx       → 32 dictionary words/patterns
# Tier 4 (10 bits): 1110xxxxxx     → 64 single chars (rare: J, Q, a-z, 0-9)
# Fallback (12 bits): 1111xxxxxxxx → any other char via ord()

import json
from collections import Counter

# Single character tiers (by actual frequency in loadedData.json)
TIER1_CHARS = ['E', 'A', 'R', 'I', 'O', 'T', 'L', 'S']  # 8 most frequent
TIER2_CHARS = ['N', 'C', 'M', 'U', 'D', 'H', 'P', 'G', 'B', 'F', 'Y', 'K', 'W', 'V', 'Z', 'X']  # next 16

# Tier 4: rare single chars
TIER4_CHARS = ['J', 'Q', '2'] + [chr(ord('a') + i) for i in range(26)] + ['0', '1', '3', '4', '5', '6', '7', '8', '9']

# Known dictionary words to consider (will be filtered by actual frequency)
SEED_DICT_WORDS = [
    'PRIMEVAL', 'EMPOWERED', 'BERRY', 'PUNCH', 'BALL', 'STORM', 'POWER',
    'STONE', 'SHIELD', 'GUARD', 'BREAK', 'STRIKE', 'BLAST', 'BEAM',
    'WAVE', 'PULSE', 'FORCE', 'LIGHT', 'SHADOW', 'FLAME', 'FIRE',
    'WATER', 'ROCK', 'STEEL', 'POISON', 'DRAGON', 'ICE',
]


def char_bit_cost(char):
    """Return the bit cost of encoding a single character."""
    if char in TIER1_CHARS:
        return 4
    elif char in TIER2_CHARS:
        return 6
    elif char in TIER4_CHARS:
        return 10
    else:
        return 12  # fallback


def build_dictionary(all_ids, max_tokens=32, min_freq=10):
    """Build dictionary from analysis of IDs."""
    # Count occurrences of seed dictionary words
    dict_word_counts = {}
    for word in SEED_DICT_WORDS:
        count = sum(1 for id_str in all_ids for i in range(len(id_str) - len(word) + 1)
                    if id_str[i:i+len(word)] == word)
        if count >= min_freq:
            dict_word_counts[word] = count

    # Analyze n-grams (3-6 chars) - skip 2-char, they rarely save enough
    ngram_counts = Counter()
    for n in [3, 4, 5, 6]:
        for id_str in all_ids:
            for i in range(len(id_str) - n + 1):
                ngram = id_str[i:i+n]
                ngram_counts[ngram] += 1

    def token_value(token, freq):
        # Calculate actual bit savings: individual char costs - 8 bit token cost
        individual_cost = sum(char_bit_cost(c) for c in token)
        savings_per_use = individual_cost - 8  # dictionary token = 8 bits
        if savings_per_use < 4:
            return 0  # require at least 4 bits saved per use (12+ bit tokens)
        return freq * savings_per_use

    # Combine dict words and n-grams, calculate values
    all_candidates = {}

    for word, freq in dict_word_counts.items():
        all_candidates[word] = token_value(word, freq)

    for ngram, freq in ngram_counts.items():
        if freq >= min_freq and len(ngram) >= 2:
            # Skip if it's a single char in tier 1 or 2
            if len(ngram) == 1 and ngram in TIER1_CHARS + TIER2_CHARS:
                continue
            all_candidates[ngram] = token_value(ngram, freq)

    # Sort by value descending
    sorted_candidates = sorted(all_candidates.items(), key=lambda x: x[1], reverse=True)

    # Greedily select tokens, avoiding substrings of already-selected longer tokens
    selected = []
    for token, value in sorted_candidates:
        if len(selected) >= max_tokens:
            break

        # Check if this token is a substring of an already-selected longer token
        is_substring = False
        for existing in selected:
            if len(existing) > len(token) and token in existing:
                is_substring = True
                break

        if not is_substring:
            selected.append(token)

    return selected


def build_encoder(dict_tokens):
    """Build encoding/decoding maps from dictionary tokens."""
    encode_map = {}
    decode_map = {}

    for i, char in enumerate(TIER1_CHARS):
        bits = f'0{i:03b}'
        encode_map[char] = bits
        decode_map[bits] = char

    for i, char in enumerate(TIER2_CHARS):
        bits = f'10{i:04b}'
        encode_map[char] = bits
        decode_map[bits] = char

    for i, token in enumerate(dict_tokens):
        bits = f'110{i:05b}'
        encode_map[token] = bits
        decode_map[bits] = token

    for i, char in enumerate(TIER4_CHARS):
        bits = f'1110{i:06b}'
        encode_map[char] = bits
        decode_map[bits] = char

    # Sort tokens by length (longest first) for greedy matching
    tokens_sorted = sorted(dict_tokens, key=len, reverse=True)

    return encode_map, decode_map, tokens_sorted


def id_encode(string, encode_map, tokens_sorted):
    """Encode a string ID to a bit string using greedy longest-match."""
    result = []
    i = 0
    while i < len(string):
        matched = False
        for token in tokens_sorted:
            if string[i:i+len(token)] == token:
                result.append(encode_map[token])
                i += len(token)
                matched = True
                break

        if not matched:
            char = string[i]
            if char in encode_map:
                result.append(encode_map[char])
            else:
                result.append(f'1111{ord(char):08b}')
            i += 1

    return ''.join(result)


def id_decode(bits, decode_map):
    """Decode a bit string back to the original string ID."""
    result = []
    i = 0
    while i < len(bits):
        if bits[i] == '0':
            code = bits[i:i+4]
            result.append(decode_map[code])
            i += 4
        elif bits[i:i+2] == '10':
            code = bits[i:i+6]
            result.append(decode_map[code])
            i += 6
        elif bits[i:i+3] == '110':
            code = bits[i:i+8]
            result.append(decode_map[code])
            i += 8
        elif bits[i:i+4] == '1110':
            code = bits[i:i+10]
            result.append(decode_map[code])
            i += 10
        elif bits[i:i+4] == '1111':
            char_ord = int(bits[i+4:i+12], 2)
            result.append(chr(char_ord))
            i += 12
        else:
            raise ValueError(f"Invalid bit sequence at position {i}")
    return ''.join(result)


if __name__ == "__main__":
    with open("loadedData.json", "r") as f:
        data = json.load(f)

    # Collect all IDs
    all_ids = []
    all_ids.extend(data["pokemon"].keys())
    all_ids.extend(data["moves"].keys())
    all_ids.extend(data["items"].keys())
    all_ids.extend(data["abilities"].keys())

    print(f"Total IDs: {len(all_ids)}")
    print(f"  Pokemon: {len(data['pokemon'])}")
    print(f"  Moves: {len(data['moves'])}")
    print(f"  Items: {len(data['items'])}")
    print(f"  Abilities: {len(data['abilities'])}")
    print()

    # Build dictionary from analysis
    print("Building dictionary from analysis...")
    dict_tokens = build_dictionary(all_ids, max_tokens=32, min_freq=10)
    print(f"Selected {len(dict_tokens)} dictionary tokens:")
    for token in dict_tokens:
        print(f"  '{token}'")
    print()

    # Save dictionary for future decoding
    with open("id_dictionary.json", "w") as f:
        json.dump({
            "tier1_chars": TIER1_CHARS,
            "tier2_chars": TIER2_CHARS,
            "dict_tokens": dict_tokens,
            "tier4_chars": TIER4_CHARS,
        }, f, indent=2)
    print("Dictionary saved to id_dictionary.json")

    # Build encoder
    encode_map, decode_map, tokens_sorted = build_encoder(dict_tokens)

    # Encode all IDs and collect stats
    total_bits = 0
    max_bits = 0
    errors = []

    with open("id_hashes.csv", "w") as out:
        out.write("id,bits,decimal,binary\n")
        for id_str in all_ids:
            encoded = id_encode(id_str, encode_map, tokens_sorted)
            bit_length = len(encoded)
            decimal_value = int(encoded, 2)

            # Verify round-trip
            decoded = id_decode(encoded, decode_map)
            if decoded != id_str:
                errors.append((id_str, decoded))

            total_bits += bit_length
            if bit_length > max_bits:
                max_bits = bit_length

            out.write(f"{id_str},{bit_length},{decimal_value},{encoded}\n")

    avg_bits = total_bits / len(all_ids)
    print(f"\nResults written to id_hashes.csv")
    print(f"Average bits per ID: {avg_bits:.2f}")
    print(f"Max bits: {max_bits}")

    if errors:
        print(f"\nERRORS ({len(errors)} round-trip failures):")
        for orig, decoded in errors[:10]:
            print(f"  '{orig}' -> '{decoded}'")

