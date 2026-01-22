# Universal Dictionary VLE
# Tier 1 (4 bits):  0xxx           -> 8 single chars (most frequent)
# Tier 2 (6 bits):  10xxxx         -> 16 single chars (next frequent)
# Tier 3 (8 bits):  110xxxxx       -> 32 dictionary tokens
# Tier 4 (10 bits): 1110xxxxxx     -> 64 single chars (rare)
# Fallback (12 bits): 1111xxxxxxxx -> any other char

from collections import Counter

TIER1_CHARS = ['E', 'A', 'R', 'I', 'O', 'T', 'L', 'S']
TIER2_CHARS = ['N', 'C', 'M', 'U', 'D', 'H', 'P', 'G', 'B', 'F', 'Y', 'K', 'W', 'V', 'Z', 'X']
TIER4_CHARS = ['J', 'Q', '2'] + [chr(ord('a') + i) for i in range(26)] + ['0', '1', '3', '4', '5', '6', '7', '8', '9']

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
        return 12


def build_dictionary(all_ids, max_tokens=32, min_freq=10):
    """Build dictionary from analysis of IDs."""
    dict_word_counts = {}
    for word in SEED_DICT_WORDS:
        count = sum(1 for id_str in all_ids for i in range(len(id_str) - len(word) + 1)
                    if id_str[i:i+len(word)] == word)
        if count >= min_freq:
            dict_word_counts[word] = count

    ngram_counts = Counter()
    for n in [3, 4, 5, 6]:
        for id_str in all_ids:
            for i in range(len(id_str) - n + 1):
                ngram = id_str[i:i+n]
                ngram_counts[ngram] += 1

    def token_value(token, freq):
        individual_cost = sum(char_bit_cost(c) for c in token)
        savings_per_use = individual_cost - 8
        if savings_per_use < 4:
            return 0
        return freq * savings_per_use

    all_candidates = {}
    for word, freq in dict_word_counts.items():
        all_candidates[word] = token_value(word, freq)
    for ngram, freq in ngram_counts.items():
        if freq >= min_freq and len(ngram) >= 3:
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

    tokens_sorted = sorted(dict_tokens, key=len, reverse=True)
    return encode_map, decode_map, tokens_sorted


def encode(string, encode_map, tokens_sorted):
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


def decode(bits, decode_map):
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


def test_ids(ids, max_tokens=32):
    """Test encoding on a list of IDs, return (avg_bits, max_bits, dict_tokens)."""
    dict_tokens = build_dictionary(ids, max_tokens=max_tokens)
    encode_map, decode_map, tokens_sorted = build_encoder(dict_tokens)

    total_bits = 0
    max_bits = 0

    for id_str in ids:
        encoded = encode(id_str, encode_map, tokens_sorted)
        bit_length = len(encoded)
        total_bits += bit_length
        if bit_length > max_bits:
            max_bits = bit_length

        decoded = decode(encoded, decode_map)
        if decoded != id_str:
            raise ValueError(f"Round-trip failed: {id_str} -> {decoded}")

    return total_bits / len(ids), max_bits, dict_tokens
