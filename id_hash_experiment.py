# Experimental encoding approaches

import json
from collections import Counter

TIER4_CHARS = ['J', 'Q', '2'] + [chr(ord('a') + i) for i in range(26)] + ['0', '1', '3', '4', '5', '6', '7', '8', '9']

SEED_DICT_WORDS = [
    'PRIMEVAL', 'EMPOWERED', 'BERRY', 'PUNCH', 'BALL', 'STORM', 'POWER',
    'STONE', 'SHIELD', 'GUARD', 'BREAK', 'STRIKE', 'BLAST', 'BEAM',
    'WAVE', 'PULSE', 'FORCE', 'LIGHT', 'SHADOW', 'FLAME', 'FIRE',
    'WATER', 'ROCK', 'STEEL', 'POISON', 'DRAGON', 'ICE',
]


def load_data():
    with open("loadedData.json", "r") as f:
        data = json.load(f)
    return (
        list(data["pokemon"].keys()) +
        list(data["moves"].keys()) +
        list(data["items"].keys()) +
        list(data["abilities"].keys())
    )


def get_char_frequencies(ids):
    """Get character frequencies from IDs."""
    counts = Counter()
    for id_str in ids:
        for c in id_str:
            counts[c] += 1
    return counts


def test_config(ids, tier1_chars, tier2_chars, dict_tokens, tier3_bits=8, name=""):
    """
    Test a specific configuration.

    tier3_bits: number of bits for dictionary tokens (8 = 32 tokens, 9 = 64 tokens, etc.)
    """
    # Build char_bit_cost function
    def char_bit_cost(char):
        if char in tier1_chars:
            return 4
        elif char in tier2_chars:
            return 6
        elif char in TIER4_CHARS:
            return 10
        else:
            return 12

    # Build encode/decode maps
    encode_map = {}
    decode_map = {}

    for i, char in enumerate(tier1_chars):
        bits = f'0{i:03b}'
        encode_map[char] = bits
        decode_map[bits] = char

    for i, char in enumerate(tier2_chars):
        bits = f'10{i:04b}'
        encode_map[char] = bits
        decode_map[bits] = char

    prefix_len = tier3_bits - 5  # e.g., 8 bits = 3-bit prefix "110", 9 bits = 4-bit prefix "1100"
    if tier3_bits == 8:
        prefix = '110'
        value_bits = 5
    elif tier3_bits == 9:
        prefix = '1100'
        value_bits = 5
    elif tier3_bits == 10:
        prefix = '11000'
        value_bits = 5
    else:
        prefix = '110'
        value_bits = tier3_bits - 3

    for i, token in enumerate(dict_tokens):
        bits = f'{prefix}{i:0{value_bits}b}'
        encode_map[token] = bits
        decode_map[bits] = token

    for i, char in enumerate(TIER4_CHARS):
        bits = f'1110{i:06b}'
        encode_map[char] = bits
        decode_map[bits] = char

    tokens_sorted = sorted(dict_tokens, key=len, reverse=True)

    # Encode function
    def encode(string):
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

    # Test
    total_bits = 0
    max_bits = 0
    for id_str in ids:
        encoded = encode(id_str)
        bit_length = len(encoded)
        total_bits += bit_length
        if bit_length > max_bits:
            max_bits = bit_length

    avg = total_bits / len(ids)
    return avg, max_bits


def build_dictionary(ids, tier1_chars, tier2_chars, max_tokens=32, min_freq=10, include_2grams=False):
    """Build dictionary with configurable parameters."""
    def char_bit_cost(char):
        if char in tier1_chars:
            return 4
        elif char in tier2_chars:
            return 6
        elif char in TIER4_CHARS:
            return 10
        else:
            return 12

    dict_word_counts = {}
    for word in SEED_DICT_WORDS:
        count = sum(1 for id_str in ids for i in range(len(id_str) - len(word) + 1)
                    if id_str[i:i+len(word)] == word)
        if count >= min_freq:
            dict_word_counts[word] = count

    ngram_range = [2, 3, 4, 5, 6] if include_2grams else [3, 4, 5, 6]
    ngram_counts = Counter()
    for n in ngram_range:
        for id_str in ids:
            for i in range(len(id_str) - n + 1):
                ngram = id_str[i:i+n]
                ngram_counts[ngram] += 1

    def token_value(token, freq, token_bits=8):
        individual_cost = sum(char_bit_cost(c) for c in token)
        savings = individual_cost - token_bits
        if savings < 2:  # Lower threshold for 2-grams
            return 0
        return freq * savings

    all_candidates = {}
    for word, freq in dict_word_counts.items():
        all_candidates[word] = token_value(word, freq)
    for ngram, freq in ngram_counts.items():
        if freq >= min_freq and len(ngram) >= 2:
            all_candidates[ngram] = token_value(ngram, freq)

    sorted_candidates = sorted(all_candidates.items(), key=lambda x: x[1], reverse=True)

    selected = []
    for token, value in sorted_candidates:
        if len(selected) >= max_tokens:
            break
        if value == 0:
            continue
        is_substring = any(len(ex) > len(token) and token in ex for ex in selected)
        if not is_substring:
            selected.append(token)

    return selected


def run_experiments():
    """Run various experimental configurations."""
    ids = load_data()
    print(f"Total IDs: {len(ids)}\n")

    # Base tiers (frequency-optimized)
    tier1 = ['E', 'A', 'R', 'I', 'O', 'T', 'L', 'S']
    tier2 = ['N', 'C', 'M', 'U', 'D', 'H', 'P', 'G', 'B', 'F', 'Y', 'K', 'W', 'V', 'Z', 'X']

    results = []

    # Experiment 1: Baseline (current universal)
    print("Exp 1: Baseline (32 tokens, 3-6 n-grams)")
    dict_tokens = build_dictionary(ids, tier1, tier2, max_tokens=32, include_2grams=False)
    avg, max_b = test_config(ids, tier1, tier2, dict_tokens)
    results.append(('Baseline (32 tokens)', avg, max_b))
    print(f"  Avg: {avg:.2f}, Max: {max_b}\n")

    # Experiment 2: Include 2-grams
    print("Exp 2: Include 2-grams")
    dict_tokens = build_dictionary(ids, tier1, tier2, max_tokens=32, include_2grams=True)
    avg, max_b = test_config(ids, tier1, tier2, dict_tokens)
    results.append(('With 2-grams (32)', avg, max_b))
    print(f"  Avg: {avg:.2f}, Max: {max_b}")
    print(f"  Tokens: {dict_tokens[:10]}...\n")

    # Experiment 3: Larger dictionary (64 tokens)
    print("Exp 3: Larger dictionary (64 tokens)")
    dict_tokens = build_dictionary(ids, tier1, tier2, max_tokens=64, include_2grams=True)
    avg, max_b = test_config(ids, tier1, tier2, dict_tokens, tier3_bits=9)
    results.append(('64 tokens + 2-grams', avg, max_b))
    print(f"  Avg: {avg:.2f}, Max: {max_b}\n")

    # Experiment 4: Even larger dictionary (128 tokens, 10 bits)
    print("Exp 4: 128 tokens dictionary")
    dict_tokens = build_dictionary(ids, tier1, tier2, max_tokens=128, include_2grams=True, min_freq=5)
    avg, max_b = test_config(ids, tier1, tier2, dict_tokens, tier3_bits=10)
    results.append(('128 tokens', avg, max_b))
    print(f"  Avg: {avg:.2f}, Max: {max_b}\n")

    # Experiment 5: No dictionary, just optimized single-char
    print("Exp 5: No dictionary (single-char only)")
    avg, max_b = test_config(ids, tier1, tier2, [])
    results.append(('No dictionary', avg, max_b))
    print(f"  Avg: {avg:.2f}, Max: {max_b}\n")

    # Summary
    print("=" * 60)
    print("EXPERIMENT SUMMARY")
    print("=" * 60)
    print(f"{'Configuration':<25} {'Avg Bits':<12} {'Max Bits':<10}")
    print("-" * 60)
    for name, avg, max_b in sorted(results, key=lambda x: x[1]):
        print(f"{name:<25} {avg:<12.2f} {max_b:<10}")
    print("-" * 60)


if __name__ == "__main__":
    run_experiments()
