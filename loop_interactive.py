"""
Picks loop points for Ogg tracks with PyMusicLooper's interactive mode, one
track at a time, then runs loop_tag.py to write them into the files.

Usage: python loop_interactive.py FILE_OR_DIR... [--approx START END]
Bare filenames are looked up in music/.

Writes loops.txt (replacing any existing one) and the tracks' loop tags.
"""

import argparse
import os
import subprocess
import sys

MUSIC_DIR = "music/"

parser = argparse.ArgumentParser(
    description="Interactively set loop points using PyMusicLooper."
)
parser.add_argument("files", nargs="+", help="OGG files or a directory of OGG files")
parser.add_argument(
    "--approx", nargs=2, type=float, metavar=("START", "END"),
    help="Approximate loop start and end in seconds (±2s search window)"
)
args = parser.parse_args()

filepaths = []
for arg in args.files:
    if os.path.isdir(arg):
        filepaths += [os.path.join(arg, f) for f in os.listdir(arg) if f.endswith(".ogg")]
    elif os.path.isfile(arg):
        filepaths.append(arg)
    else:
        candidate = os.path.join(MUSIC_DIR, arg)
        if os.path.isfile(candidate):
            filepaths.append(candidate)
        else:
            print(f"Warning: {arg} not found, skipping.")

if os.path.exists("loops.txt"):
    os.remove("loops.txt")

for filepath in filepaths:
    filename = os.path.basename(filepath)
    print(f"\n=== {filename} ===")
    cmd = [
        "pymusiclooper", "-i", "-s",
        "export-points",
        "--export-to", "TXT",
        "--fmt", "SAMPLES",
        "--path", filepath,
        "--output-dir", ".",
    ]
    if args.approx:
        cmd += ["--approx-loop-position", str(args.approx[0]), str(args.approx[1])]
    proc = subprocess.Popen(cmd)
    while True:
        try:
            proc.wait()
            break
        except KeyboardInterrupt:
            pass  # Ctrl+C is for PML to handle; keep waiting for it to finish

print("\nApplying loop tags...")
subprocess.run([sys.executable, "loop_tag.py"])
print("Done.")
