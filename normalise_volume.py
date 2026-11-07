"""
Step 2 of volume normalisation: applies each gain recorded in replaygain.txt
(by export_replaygain.py) to its track in music/ with ffmpeg.

Writes the adjusted tracks to music/normal/; copy_metadata.py then restores
their tags.
"""

import ffmpeg

MUSIC_DIR = "music/"

OUTPUT_DIR = "music/normal/"

with open("replaygain.txt", "r", encoding="utf8") as f:
    gains = f.read().splitlines()

for gain in gains:
    params = gain.split(",")
    filename = params[0]
    gain = params[1]
    ffmpeg.input(MUSIC_DIR + filename).filter("volume", gain).output(
        OUTPUT_DIR + filename
    ).run(quiet=True)
