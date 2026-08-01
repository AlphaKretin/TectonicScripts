#!/usr/bin/env python3
"""
Batch color swap for pixel art images.

Usage:
    # Inline mappings:
    python swap_colors.py -i sprites/ -o recolored/ -m "#FF0000" "#00FF00" -m "#0000FF" "#FFFF00"

    # Palette JSON file:
    python swap_colors.py -i sprites/ -o recolored/ -p palette.json

    # Both (inline mappings override palette file for conflicts):
    python swap_colors.py -i sprites/ -o recolored/ -p palette.json -m "#FF0000" "#FFFFFF"

Palette JSON format:
    { "#FF0000": "#00FF00", "#0000FF": "#FFFF00" }
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image


def parse_color(value: str) -> tuple[int, int, int, int]:
    s = value.lstrip('#')
    if len(s) == 6:
        r, g, b = int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)
        return (r, g, b, 255)
    elif len(s) == 8:
        r, g, b, a = int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), int(s[6:8], 16)
        return (r, g, b, a)
    else:
        raise ValueError(f"Invalid hex color: '{value}' — expected #RRGGBB or #RRGGBBAA")


def swap_colors(image: Image.Image, color_map: dict) -> Image.Image:
    img = image.convert('RGBA')
    arr = np.array(img, dtype=np.uint8)
    result = arr.copy()

    for old, new in color_map.items():
        mask = (
            (arr[:, :, 0] == old[0]) &
            (arr[:, :, 1] == old[1]) &
            (arr[:, :, 2] == old[2]) &
            (arr[:, :, 3] == old[3])
        )
        result[mask] = new

    return Image.fromarray(result, 'RGBA')


def main():
    parser = argparse.ArgumentParser(
        description='Swap specific colors across a batch of images (exact pixel match).',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split('\n', 1)[1],
    )
    parser.add_argument('--input',   '-i', required=True, type=Path, help='Input directory')
    parser.add_argument('--output',  '-o', required=True, type=Path, help='Output directory')
    parser.add_argument('--map',     '-m', nargs=2, metavar=('OLD', 'NEW'), action='append',
                        help='Hex color pair to swap (repeatable). Overrides --palette on conflict.')
    parser.add_argument('--palette', '-p', type=Path,
                        help='JSON file of { "old": "new" } hex color mappings')

    args = parser.parse_args()

    if not args.map and not args.palette:
        parser.error('Provide at least one --map pair or a --palette file.')

    raw_map: dict[str, str] = {}
    if args.palette:
        with open(args.palette) as f:
            raw_map.update(json.load(f))
    if args.map:
        for old, new in args.map:
            raw_map[old] = new

    try:
        color_map = {parse_color(old): parse_color(new) for old, new in raw_map.items()}
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if not args.input.is_dir():
        print(f"Error: input path '{args.input}' is not a directory.", file=sys.stderr)
        sys.exit(1)

    args.output.mkdir(parents=True, exist_ok=True)

    extensions = {'.png', '.bmp', '.gif', '.webp', '.jpg', '.jpeg'}
    images = sorted(p for p in args.input.iterdir() if p.suffix.lower() in extensions)

    if not images:
        print(f"No images found in '{args.input}'.")
        return

    print(f"Processing {len(images)} image(s) with {len(color_map)} color mapping(s)...")

    for path in images:
        img = Image.open(path)
        result = swap_colors(img, color_map)

        out_path = args.output / path.name
        # JPEG doesn't support alpha; everything else saves as RGBA PNG
        if path.suffix.lower() in {'.jpg', '.jpeg'}:
            result = result.convert('RGB')
        result.save(out_path)
        print(f"  {path.name}")

    print("Done.")


if __name__ == '__main__':
    main()
