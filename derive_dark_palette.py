#!/usr/bin/env python3
"""
Derives a dark mode palette from manually paired reference images, then
extrapolates to cover colors not present in the references using k-nearest-
neighbor in HLS color space.

Reference pairs live in the same directory as regular input images. A dark-mode
reference for "button.png" is named "button_dark.png". Any image without a
corresponding _dark file is treated as input-only.

Usage:
    python derive_dark_palette.py -i sprites/ -o dark_palette.json

    -k 1               Only use the single nearest reference (crisper, less blending)
    --max-distance 0.2 Tighter threshold (only confident extrapolations in palette)

Then open dark_palette.html to review, edit the JSON as needed, and run:
    python swap_colors.py -i sprites/ -o dark_sprites/ -p dark_palette.json
"""

import argparse
import json
from collections import Counter, defaultdict
from colorsys import hls_to_rgb, rgb_to_hls
from pathlib import Path

import numpy as np
from PIL import Image


# ── Utilities ─────────────────────────────────────────────────────────────────

def rgba_to_hex(r, g, b, a=255):
    if a == 255:
        return f"#{r:02X}{g:02X}{b:02X}"
    return f"#{r:02X}{g:02X}{b:02X}{a:02X}"


def luminance(r, g, b):
    def lin(c):
        c /= 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def text_color(r, g, b):
    return "#000" if luminance(r, g, b) > 0.179 else "#fff"


def to_hls(r, g, b):
    return rgb_to_hls(r / 255, g / 255, b / 255)  # (h, l, s)


def hls_dist(a, b):
    dh = min(abs(a[0] - b[0]), 1.0 - abs(a[0] - b[0]))  # hue is circular
    return (0.5 * dh**2 + 1.0 * (a[1] - b[1])**2 + 0.7 * (a[2] - b[2])**2) ** 0.5


# ── Reference extraction ──────────────────────────────────────────────────────

def find_pairs(sprites_dir):
    """
    Find reference pairs in a single directory.
    A file named foo_dark.ext is the dark reference for foo.ext.
    Returns (pairs, input_only) where:
      pairs:       [(light_path, dark_path), ...]
      input_only:  [path, ...]  — images with no _dark counterpart
    """
    exts = {".png", ".bmp", ".gif", ".webp", ".jpg", ".jpeg"}
    all_files = {p.name: p for p in sprites_dir.iterdir() if p.suffix.lower() in exts}

    pairs      = []
    dark_names = set()
    for name, path in sorted(all_files.items()):
        p = Path(name)
        if p.stem.endswith("_dark"):
            light_stem = p.stem[:-5]  # strip "_dark"
            light_name = light_stem + p.suffix
            if light_name in all_files:
                pairs.append((all_files[light_name], path))
                dark_names.add(name)
                dark_names.add(light_name)

    input_only = [p for name, p in sorted(all_files.items()) if name not in dark_names]
    return pairs, input_only


def extract_reference(sprites_dir):
    """
    Compare paired images pixel-by-pixel to build ground-truth color mappings.
    Returns (direct_map, unchanged, conflicts) where:
      direct_map: {old_rgba: new_rgba}
      unchanged:  set of rgba tuples that map to themselves
      conflicts:  {old_rgba: Counter} where multiple new colors were seen
    """
    pairs, _ = find_pairs(sprites_dir)
    if not pairs:
        raise SystemExit(
            f"No reference pairs found in '{sprites_dir}'.\n"
            "Dark references must be named with a _dark suffix, e.g. button_dark.png."
        )
    print(f"  Reference pairs ({len(pairs)}): {', '.join(l.name for l, d in pairs)}")

    votes = defaultdict(Counter)
    for light_path, dark_path in pairs:
        li = Image.open(light_path).convert("RGBA")
        di = Image.open(dark_path).convert("RGBA")
        if li.size != di.size:
            print(f"  Warning: size mismatch for '{light_path.name}', skipping.")
            continue
        la = np.array(li, dtype=np.uint8).reshape(-1, 4)
        da = np.array(di, dtype=np.uint8).reshape(-1, 4)
        pairs = np.concatenate([la, da], axis=1)
        unique_pairs, counts = np.unique(pairs, axis=0, return_counts=True)
        for pair, cnt in zip(unique_pairs, counts):
            old = tuple(int(v) for v in pair[:4])
            new = tuple(int(v) for v in pair[4:])
            votes[old][new] += int(cnt)

    direct_map = {}
    unchanged  = set()
    conflicts  = {}
    for old, vcounts in votes.items():
        total  = sum(vcounts.values())
        winner, _ = vcounts.most_common(1)[0]
        if len(vcounts) > 1:
            runner_up = vcounts.most_common(2)[1][1]
            if runner_up > total * 0.15:
                conflicts[old] = vcounts
        if winner == old:
            unchanged.add(old)
        else:
            direct_map[old] = winner
    return direct_map, unchanged, conflicts


# ── K-NN extrapolation ────────────────────────────────────────────────────────

def build_pool(direct_map, unchanged):
    """
    Build the reference pool for k-NN.
    Unchanged colors are included with delta=0 so they anchor the interpolation —
    unseen colors near an unchanged reference won't be pushed to change much.
    """
    pool = []
    for old, new in direct_map.items():
        pool.append((to_hls(*old[:3]), to_hls(*new[:3]), old, new))
    for rgba in unchanged:
        hls = to_hls(*rgba[:3])
        pool.append((hls, hls, rgba, rgba))
    return pool


def extrapolate_color(rgba, pool, k):
    """Returns (new_rgba, nearest_dist, nearest_ref_rgba)."""
    r, g, b, a = rgba
    if a == 0:
        return rgba, 0.0, rgba

    hls = to_hls(r, g, b)
    ranked = sorted(
        (hls_dist(hls, hls_o), hls_o, hls_n, ref_old)
        for hls_o, hls_n, ref_old, _ in pool
    )
    k_nn    = ranked[:k]
    weights = [1.0 / (d + 1e-9) for d, *_ in k_nn]
    total_w = sum(weights)

    dh = dl = ds = 0.0
    for w, (d, hls_o, hls_n, _) in zip(weights, k_nn):
        dh_ = hls_n[0] - hls_o[0]
        if dh_ >  0.5: dh_ -= 1.0
        if dh_ < -0.5: dh_ += 1.0
        dh += w * dh_
        dl += w * (hls_n[1] - hls_o[1])
        ds += w * (hls_n[2] - hls_o[2])

    h2 = (hls[0] + dh / total_w) % 1.0
    l2 = max(0.0, min(1.0, hls[1] + dl / total_w))
    s2 = max(0.0, min(1.0, hls[2] + ds / total_w))
    r2, g2, b2 = hls_to_rgb(h2, l2, s2)
    return (round(r2 * 255), round(g2 * 255), round(b2 * 255), a), k_nn[0][0], k_nn[0][3]


# ── HTML output ───────────────────────────────────────────────────────────────

def _cell(r, g, b, a, sub=None):
    hex_v = rgba_to_hex(r, g, b, a)
    bg    = f"rgba({r},{g},{b},{a/255:.3f})"
    tc    = text_color(r, g, b)
    note  = f"<br><span class='sub'>{sub}</span>" if sub else ""
    return f'<td style="background:{bg};color:{tc}" title="{hex_v}">{hex_v}{note}</td>'


def _arr():
    return "<td class='arr'>→</td>"


def _conf(dist, max_dist):
    if dist < max_dist * 0.33: return "high", "#4a8"
    if dist < max_dist * 0.67: return "med",  "#a82"
    return "low", "#a44"


def write_html(direct_map, conflicts, extrapolated, no_change, uncertain, max_dist, path):
    def section(rows_list):
        return "\n".join(rows_list) or "<tr><td colspan='4' class='empty'>—</td></tr>"

    # Conflicts warning
    conflict_html = ""
    if conflicts:
        crows = []
        for old, vcounts in sorted(conflicts.items()):
            winner = max(vcounts, key=vcounts.get)
            row = _cell(*old)
            for new, cnt in vcounts.most_common():
                tag = " ✓" if new == winner else ""
                row += _arr() + _cell(*new, sub=f"{cnt}px{tag}")
            crows.append(f"<tr>{row}</tr>")
        conflict_html = (
            f"<h3 class='warn'>⚠ Conflicts in reference ({len(conflicts)})</h3>"
            f"<p class='note'>Same source color mapped to different values across reference pairs. "
            f"Most common was kept (✓).</p>"
            f"<table>{''.join(crows)}</table>"
        )

    # Reference rows
    ref_rows = []
    for old, new in direct_map.items():
        flag = "<td class='warn_cell'>⚠ conflict</td>" if old in conflicts else "<td class='dim'></td>"
        ref_rows.append(f"<tr>{_cell(*old)}{_arr()}{_cell(*new)}{flag}</tr>")

    # Extrapolated rows (sorted closest-first)
    ext_rows = []
    for old, (new, dist, near) in sorted(extrapolated.items(), key=lambda x: x[1][1]):
        lbl, col = _conf(dist, max_dist)
        nr, ng, nb, na = near
        nhex = rgba_to_hex(nr, ng, nb, na)
        nbg  = f"rgba({nr},{ng},{nb},{na/255:.3f})"
        ntc  = text_color(nr, ng, nb)
        ext_rows.append(
            f"<tr>{_cell(*old)}{_arr()}{_cell(*new)}"
            f"<td class='dim'><span style='color:{col}'>{lbl}</span> · nearest "
            f"<span style='background:{nbg};color:{ntc};padding:1px 5px;"
            f"border-radius:2px'>{nhex}</span> (d={dist:.3f})</td></tr>"
        )

    # Uncertain rows
    unc_rows = [
        f"<tr>{_cell(*old)}"
        f"<td class='dim'>nearest ref: {rgba_to_hex(*near)} (d={dist:.3f})</td></tr>"
        for old, dist, near in sorted(uncertain, key=lambda x: x[1])
    ]

    # No-change rows
    noc_rows = [
        f"<tr>{_cell(*rgba)}"
        f"<td class='dim'>extrapolated delta &lt;2/255 per channel — left unchanged</td></tr>"
        for rgba in no_change
    ]

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"><title>Dark Mode Palette</title>
  <style>
    body      {{background:#1a1a1a;color:#bbb;font-family:sans-serif;padding:1em}}
    h2        {{color:#ddd;margin-bottom:.2em}}
    h3        {{color:#999;font-size:.9em;margin-top:1.6em;border-bottom:1px solid #2e2e2e;padding-bottom:.3em}}
    h3.warn   {{color:#c84}}
    p.note    {{color:#777;font-size:.82em;margin:.2em 0 .5em}}
    table     {{border-collapse:collapse;margin-top:.4em}}
    td        {{border:1px solid #333;padding:5px 8px;font-size:11px;font-family:monospace;
                text-align:center;min-width:95px}}
    .arr      {{background:none!important;border:none!important;color:#555;min-width:18px;padding:0 3px}}
    .dim      {{color:#666;font-size:10px;text-align:left!important;min-width:220px;border-color:#252525}}
    .sub      {{font-size:9px;opacity:.7}}
    .empty    {{color:#444;border:none}}
    .warn_cell{{color:#c84;font-size:10px;border-color:#2a2a2a}}
  </style>
</head>
<body>
  <h2>Dark Mode Palette Preview</h2>
  <p class='note'>Review, edit <code>dark_palette.json</code> as needed, then run:<br>
  <code>swap_colors.py -i &lt;input&gt; -o &lt;output&gt; -p dark_palette.json</code></p>

  {conflict_html}

  <h3>From reference ({len(direct_map)} mappings — in palette)</h3>
  <table><tr><th>Original</th><th></th><th>Dark</th><th></th></tr>
  {section(ref_rows)}</table>

  <h3>Extrapolated ({len(ext_rows)} colors — in palette)</h3>
  <p class='note'>Suggested by k-NN from reference colors. Sorted closest-first.
  Lower confidence = further from any reference — review carefully.</p>
  <table><tr><th>Original</th><th></th><th>Suggested</th><th>Basis</th></tr>
  {section(ext_rows)}</table>

  <h3>Too far from reference ({len(uncertain)} colors — not in palette)</h3>
  <p class='note'>Beyond --max-distance threshold. Add to the JSON manually if needed,
  or re-run with a larger --max-distance to include them.</p>
  <table><tr><th>Color</th><th>Notes</th></tr>
  {section(unc_rows)}</table>

  <h3>No change needed ({len(no_change)} colors — not in palette)</h3>
  <p class='note'>Extrapolation suggested a negligible change (&lt;2/255 per channel).</p>
  <table><tr><th>Color</th><th>Notes</th></tr>
  {section(noc_rows)}</table>
</body>
</html>"""
    path.write_text(html, encoding="utf-8")


# ── Color collection ──────────────────────────────────────────────────────────

def collect_colors(images):
    counts = Counter()
    for p in images:
        img = Image.open(p).convert("RGBA")
        pixels = np.array(img, dtype=np.uint8).reshape(-1, 4)
        unique, freq = np.unique(pixels, axis=0, return_counts=True)
        for rgba, n in zip(unique, freq):
            counts[tuple(int(v) for v in rgba)] += int(n)
    return counts


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Derive a dark mode palette from reference pairs, then extrapolate.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("\n", 1)[1],
    )
    parser.add_argument("--input", "-i",  required=True, type=Path,
                        help="Sprites directory. Images named foo_dark.ext are treated as "
                             "dark-mode references for foo.ext; all others are input.")
    parser.add_argument("--output", "-o", default="dark_palette.json", type=Path,
                        help="Output palette JSON (default: dark_palette.json)")
    parser.add_argument("--preview",      type=Path,
                        help="HTML preview path (default: <output>.html)")
    parser.add_argument("-k",             type=int, default=3,
                        help="Neighbors for k-NN extrapolation (default: 3; "
                             "try 1 for crisper results that follow the nearest reference more closely)")
    parser.add_argument("--max-distance", type=float, default=0.25,
                        help="HLS distance threshold; colors further from all references "
                             "than this get no suggestion (default: 0.25)")
    parser.add_argument("--min-pixels",   type=int, default=1,
                        help="Ignore colors with fewer than N total pixels (default: 1)")
    args = parser.parse_args()

    preview_path = args.preview or args.output.with_suffix(".html")

    print("Extracting reference mappings...")
    direct_map, unchanged_ref, conflicts = extract_reference(args.input)
    print(f"  {len(direct_map)} changed, {len(unchanged_ref)} unchanged"
          + (f", {len(conflicts)} conflicted" if conflicts else ""))

    pool = build_pool(direct_map, unchanged_ref)
    if not pool:
        raise SystemExit("No reference data found — cannot extrapolate.")

    # Gather colors from all light-mode images (input-only + light halves of reference pairs)
    pairs, input_only = find_pairs(args.input)
    ref_light_paths   = [light for light, dark in pairs]
    all_input_images  = input_only + ref_light_paths
    print(f"\nScanning {len(all_input_images)} input image(s)...")
    color_counts = collect_colors(all_input_images)
    input_colors = {rgba for rgba, cnt in color_counts.items() if cnt >= args.min_pixels}
    print(f"  {len(input_colors)} unique color(s).")

    # Classify each color not already in the reference
    extrapolated = {}   # old_rgba → (new_rgba, dist, nearest_ref)
    no_change    = []   # rgba — negligible delta
    uncertain    = []   # (rgba, dist, nearest_ref) — beyond max_distance

    for rgba in input_colors:
        if rgba in direct_map or rgba in unchanged_ref:
            continue
        if rgba[3] == 0:
            continue  # fully transparent

        new_rgba, dist, nearest_ref = extrapolate_color(rgba, pool, args.k)

        if all(abs(c1 - c2) <= 2 for c1, c2 in zip(rgba[:3], new_rgba[:3])):
            no_change.append(rgba)
        elif dist <= args.max_distance:
            extrapolated[rgba] = (new_rgba, dist, nearest_ref)
        else:
            uncertain.append((rgba, dist, nearest_ref))

    # Build and write palette
    palette = {rgba_to_hex(*old): rgba_to_hex(*new) for old, new in direct_map.items()}
    for old, (new, _, _) in extrapolated.items():
        palette[rgba_to_hex(*old)] = rgba_to_hex(*new)

    args.output.write_text(json.dumps(palette, indent=2), encoding="utf-8")
    print(f"\nPalette: {len(direct_map)} reference + {len(extrapolated)} extrapolated"
          f" = {len(palette)} total → '{args.output}'")
    if uncertain:
        print(f"  {len(uncertain)} color(s) beyond max-distance — in preview but not palette.")

    write_html(direct_map, conflicts, extrapolated, no_change, uncertain, args.max_distance, preview_path)
    print(f"Preview: '{preview_path}'")


if __name__ == "__main__":
    main()
