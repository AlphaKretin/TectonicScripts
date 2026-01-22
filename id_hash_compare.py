# Compare all ID encoding approaches

import json
import id_hash_single
import id_hash_universal
import id_hash_universal64
import id_hash_domain
import id_hash_domain64


def load_data():
    """Load all IDs from loadedData.json."""
    with open("loadedData.json", "r") as f:
        data = json.load(f)

    all_ids = (
        list(data["pokemon"].keys()) +
        list(data["moves"].keys()) +
        list(data["items"].keys()) +
        list(data["abilities"].keys())
    )

    domains = {
        'pokemon': list(data["pokemon"].keys()),
        'moves': list(data["moves"].keys()),
        'items': list(data["items"].keys()),
        'abilities': list(data["abilities"].keys()),
    }

    return all_ids, domains


def compare_all():
    """Compare all encoding approaches."""
    all_ids, domains = load_data()

    print(f"Total IDs: {len(all_ids)}")
    for name, ids in domains.items():
        print(f"  {name}: {len(ids)}")
    print()

    results = {}

    # 1. Single-char VLE
    print("Testing Single-char VLE...")
    avg, max_b = id_hash_single.test_ids(all_ids)
    results['single'] = {'avg': avg, 'max': max_b}
    print(f"  Average: {avg:.2f} bits, Max: {max_b} bits")
    print()

    # 2. Universal dictionary (32 tokens)
    print("Testing Universal Dictionary (32 tokens)...")
    avg, max_b, tokens = id_hash_universal.test_ids(all_ids, max_tokens=32)
    results['universal32'] = {'avg': avg, 'max': max_b, 'tokens': tokens}
    print(f"  Average: {avg:.2f} bits, Max: {max_b} bits")
    print()

    # 3. Universal dictionary (64 tokens)
    print("Testing Universal Dictionary (64 tokens)...")
    avg, max_b, tokens = id_hash_universal64.test_ids(all_ids)
    results['universal64'] = {'avg': avg, 'max': max_b, 'tokens': tokens}
    print(f"  Average: {avg:.2f} bits, Max: {max_b} bits")
    print()

    # 4. Domain-specific (32 tokens)
    print("Testing Domain-specific (32 tokens)...")
    domain_results = id_hash_domain.test_all_domains(domains)
    results['domain32'] = domain_results
    print(f"  Overall: {domain_results['overall']['avg_bits']:.2f} avg, {domain_results['overall']['max_bits']} max")
    print()

    # 5. Domain-specific (64 tokens) - BEST AVERAGE
    print("Testing Domain-specific (64 tokens)...")
    domain64_results = id_hash_domain64.test_all_domains(domains)
    results['domain64'] = domain64_results
    print(f"  Overall: {domain64_results['overall']['avg_bits']:.2f} avg, {domain64_results['overall']['max_bits']} max")
    print()

    # Summary - sorted by average bits
    print("=" * 70)
    print("SUMMARY (sorted by avg bits)")
    print("=" * 70)
    print(f"{'Approach':<30} {'Avg Bits':<12} {'Max Bits':<10} {'Notes':<18}")
    print("-" * 70)

    summary = [
        ('Single-char VLE', results['single']['avg'], results['single']['max'], 'baseline'),
        ('Universal dict (32 tokens)', results['universal32']['avg'], results['universal32']['max'], ''),
        ('Universal dict (64 tokens)', results['universal64']['avg'], results['universal64']['max'], 'best max'),
        ('Domain-specific (32 tokens)', results['domain32']['overall']['avg_bits'], results['domain32']['overall']['max_bits'], ''),
        ('Domain-specific (64 tokens)', results['domain64']['overall']['avg_bits'], results['domain64']['overall']['max_bits'], 'best avg'),
    ]

    for name, avg, max_b, note in sorted(summary, key=lambda x: x[1]):
        print(f"{name:<30} {avg:<12.2f} {max_b:<10} {note:<18}")

    print("-" * 70)

    return results


if __name__ == "__main__":
    compare_all()
