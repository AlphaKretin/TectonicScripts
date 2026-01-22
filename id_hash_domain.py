# Domain-specific VLE
# Each domain (pokemon, moves, items, abilities) gets its own:
# - Character frequency tiers
# - N-gram dictionary

from collections import Counter

TIER4_CHARS = ['J', 'Q', '2'] + [chr(ord('a') + i) for i in range(26)] + ['0', '1', '3', '4', '5', '6', '7', '8', '9']

SEED_DICT_WORDS = [
    'PRIMEVAL', 'EMPOWERED', 'BERRY', 'PUNCH', 'BALL', 'STORM', 'POWER',
    'STONE', 'SHIELD', 'GUARD', 'BREAK', 'STRIKE', 'BLAST', 'BEAM',
    'WAVE', 'PULSE', 'FORCE', 'LIGHT', 'SHADOW', 'FLAME', 'FIRE',
    'WATER', 'ROCK', 'STEEL', 'POISON', 'DRAGON', 'ICE',
]


def get_optimal_tiers(ids):
    """Get optimal tier assignments based on character frequency in this domain."""
    char_counts = Counter()
    for id_str in ids:
        for c in id_str:
            char_counts[c] += 1

    uppercase = [c for c, _ in char_counts.most_common() if c.isupper()]
    tier1 = uppercase[:8] if len(uppercase) >= 8 else uppercase
    tier2 = uppercase[8:24] if len(uppercase) >= 24 else uppercase[8:]

    return tier1, tier2


def build_domain_encoder(ids, max_tokens=32, min_freq=5):
    """Build a domain-specific encoder."""
    tier1, tier2 = get_optimal_tiers(ids)

    def char_bit_cost(char):
        if char in tier1:
            return 4
        elif char in tier2:
            return 6
        elif char in TIER4_CHARS:
            return 10
        else:
            return 12

    # Build dictionary
    dict_word_counts = {}
    for word in SEED_DICT_WORDS:
        count = sum(1 for id_str in ids for i in range(len(id_str) - len(word) + 1)
                    if id_str[i:i+len(word)] == word)
        if count >= min_freq:
            dict_word_counts[word] = count

    ngram_counts = Counter()
    for n in [3, 4, 5, 6]:
        for id_str in ids:
            for i in range(len(id_str) - n + 1):
                ngram = id_str[i:i+n]
                ngram_counts[ngram] += 1

    def token_value(token, freq):
        individual_cost = sum(char_bit_cost(c) for c in token)
        savings = individual_cost - 8
        if savings < 4:
            return 0
        return freq * savings

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

    # Build encoder maps
    encode_map = {}
    decode_map = {}

    for i, char in enumerate(tier1):
        bits = f'0{i:03b}'
        encode_map[char] = bits
        decode_map[bits] = char

    for i, char in enumerate(tier2):
        bits = f'10{i:04b}'
        encode_map[char] = bits
        decode_map[bits] = char

    for i, token in enumerate(selected):
        bits = f'110{i:05b}'
        encode_map[token] = bits
        decode_map[bits] = token

    for i, char in enumerate(TIER4_CHARS):
        bits = f'1110{i:06b}'
        encode_map[char] = bits
        decode_map[bits] = char

    tokens_sorted = sorted(selected, key=len, reverse=True)

    return encode_map, decode_map, tokens_sorted, tier1, tier2, selected


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


def test_domain(ids, domain_name, max_tokens=32):
    """Test encoding on a single domain, return stats dict."""
    encode_map, decode_map, tokens_sorted, tier1, tier2, dict_tokens = build_domain_encoder(ids, max_tokens)

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

    return {
        'domain': domain_name,
        'count': len(ids),
        'avg_bits': total_bits / len(ids),
        'max_bits': max_bits,
        'total_bits': total_bits,
        'tier1': tier1,
        'tier2': tier2,
        'dict_tokens': dict_tokens,
    }


def test_all_domains(domains_dict, max_tokens=32):
    """Test encoding on all domains, return overall stats."""
    results = {}
    total_bits = 0
    total_count = 0
    overall_max = 0

    for domain_name, ids in domains_dict.items():
        stats = test_domain(ids, domain_name, max_tokens)
        results[domain_name] = stats
        total_bits += stats['total_bits']
        total_count += stats['count']
        if stats['max_bits'] > overall_max:
            overall_max = stats['max_bits']

    results['overall'] = {
        'avg_bits': total_bits / total_count,
        'max_bits': overall_max,
        'total_count': total_count,
    }

    return results
