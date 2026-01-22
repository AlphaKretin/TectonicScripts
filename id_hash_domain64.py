# Domain-specific VLE with 64 tokens per domain
# Best average compression: 39.72 bits avg
#
# Each domain (pokemon, moves, items, abilities) gets:
# - Optimized character frequency tiers
# - 64-token dictionary (10 bits each)
#
# Encoding scheme:
# Tier 1 (4 bits):  0xxx           -> 8 most frequent chars
# Tier 2 (6 bits):  10xxxx         -> 16 next frequent chars
# Dict (10 bits):   1100xxxxxx     -> 64 dictionary tokens
# Tier 4 (10 bits): 1110xxxxxx     -> 64 rare chars
# Fallback (12 bits): 1111xxxxxxxx -> any other char

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


def build_domain_encoder(ids, max_tokens=64, min_freq=3):
    """Build a domain-specific encoder with 64 dictionary tokens."""
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
    for n in [2, 3, 4, 5, 6]:
        for id_str in ids:
            for i in range(len(id_str) - n + 1):
                ngram = id_str[i:i+n]
                ngram_counts[ngram] += 1

    def token_value(token, freq):
        individual_cost = sum(char_bit_cost(c) for c in token)
        savings = individual_cost - 10  # 10 bits for dictionary token
        if savings < 2:
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
        bits = f'1100{i:06b}'  # 10 bits for 64 tokens
        encode_map[token] = bits
        decode_map[bits] = token

    for i, char in enumerate(TIER4_CHARS):
        bits = f'1110{i:06b}'
        encode_map[char] = bits
        decode_map[bits] = char

    tokens_sorted = sorted(selected, key=len, reverse=True)

    return {
        'encode_map': encode_map,
        'decode_map': decode_map,
        'tokens_sorted': tokens_sorted,
        'tier1': tier1,
        'tier2': tier2,
        'dict_tokens': selected,
    }


def encode(string, encoder):
    """Encode a string ID to a bit string using greedy longest-match."""
    encode_map = encoder['encode_map']
    tokens_sorted = encoder['tokens_sorted']

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


def decode(bits, encoder):
    """Decode a bit string back to the original string ID."""
    decode_map = encoder['decode_map']

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
        elif bits[i:i+4] == '1100':
            code = bits[i:i+10]
            result.append(decode_map[code])
            i += 10
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


def test_domain(ids, domain_name):
    """Test encoding on a single domain, return stats dict."""
    encoder = build_domain_encoder(ids)

    total_bits = 0
    max_bits = 0
    errors = []

    for id_str in ids:
        encoded = encode(id_str, encoder)
        bit_length = len(encoded)
        total_bits += bit_length
        if bit_length > max_bits:
            max_bits = bit_length

        # Verify round-trip
        decoded = decode(encoded, encoder)
        if decoded != id_str:
            errors.append((id_str, decoded))

    return {
        'domain': domain_name,
        'count': len(ids),
        'avg_bits': total_bits / len(ids),
        'max_bits': max_bits,
        'total_bits': total_bits,
        'encoder': encoder,
        'errors': errors,
    }


def test_all_domains(domains_dict):
    """Test encoding on all domains, return overall stats."""
    results = {}
    total_bits = 0
    total_count = 0
    overall_max = 0

    for domain_name, ids in domains_dict.items():
        stats = test_domain(ids, domain_name)
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


if __name__ == "__main__":
    import json

    with open("loadedData.json", "r") as f:
        data = json.load(f)

    domains = {
        'pokemon': list(data["pokemon"].keys()),
        'moves': list(data["moves"].keys()),
        'items': list(data["items"].keys()),
        'abilities': list(data["abilities"].keys()),
    }

    print("Domain-specific VLE with 64 tokens")
    print("=" * 60)

    results = test_all_domains(domains)

    for domain_name in domains:
        r = results[domain_name]
        enc = r['encoder']
        print(f"\n{domain_name}:")
        print(f"  Count: {r['count']}")
        print(f"  Average: {r['avg_bits']:.2f} bits")
        print(f"  Max: {r['max_bits']} bits")
        print(f"  Tier1: {enc['tier1']}")
        print(f"  Dictionary: {len(enc['dict_tokens'])} tokens")
        if r['errors']:
            print(f"  ERRORS: {len(r['errors'])}")

    print("\n" + "=" * 60)
    print(f"OVERALL: {results['overall']['avg_bits']:.2f} avg bits, {results['overall']['max_bits']} max bits")
