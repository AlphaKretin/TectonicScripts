# Single-character VLE (no dictionary)
# Tier 1 (4 bits):  0xxx           -> 8 single chars (most frequent)
# Tier 2 (6 bits):  10xxxx         -> 16 single chars (next frequent)
# Tier 4 (10 bits): 1110xxxxxx     -> 64 single chars (rare)
# Fallback (12 bits): 1111xxxxxxxx -> any other char

TIER1_CHARS = ['E', 'A', 'R', 'I', 'O', 'T', 'L', 'S']
TIER2_CHARS = ['N', 'C', 'M', 'U', 'D', 'H', 'P', 'G', 'B', 'F', 'Y', 'K', 'W', 'V', 'Z', 'X']
TIER4_CHARS = ['J', 'Q', '2'] + [chr(ord('a') + i) for i in range(26)] + ['0', '1', '3', '4', '5', '6', '7', '8', '9']


def build_encoder():
    """Build encoding/decoding maps for single-char VLE."""
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

    for i, char in enumerate(TIER4_CHARS):
        bits = f'1110{i:06b}'
        encode_map[char] = bits
        decode_map[bits] = char

    return encode_map, decode_map


def encode(string, encode_map):
    """Encode a string ID to a bit string."""
    result = []
    for char in string:
        if char in encode_map:
            result.append(encode_map[char])
        else:
            result.append(f'1111{ord(char):08b}')
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


def test_ids(ids):
    """Test encoding on a list of IDs, return (avg_bits, max_bits)."""
    encode_map, decode_map = build_encoder()
    total_bits = 0
    max_bits = 0

    for id_str in ids:
        encoded = encode(id_str, encode_map)
        bit_length = len(encoded)
        total_bits += bit_length
        if bit_length > max_bits:
            max_bits = bit_length

        # Verify round-trip
        decoded = decode(encoded, decode_map)
        if decoded != id_str:
            raise ValueError(f"Round-trip failed: {id_str} -> {decoded}")

    return total_bits / len(ids), max_bits
