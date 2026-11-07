"""
Lists the Ogg files in the Tectonic BGM folder (../Pokemon-Tectonic-Main/Audio/BGM)
that have no LOOPSTART tag, to find tracks that still need loop points.

Writes loopless_files.txt.
"""

import os

import mutagen
import mutagen.oggvorbis

TECTONIC_DIR = "../Pokemon-Tectonic-Main/Audio/BGM"

files = os.listdir(TECTONIC_DIR)

oggFiles = [file for file in files if file.endswith(".ogg")]

looping_files = []
loopless_files = []

for filename in oggFiles:
    file = mutagen.oggvorbis.OggVorbis(TECTONIC_DIR + "/" + filename)
    if "LOOPSTART" in file.tags:
        looping_files.append(filename)
    else:
        loopless_files.append(filename)

print("Total Files: " + str(len(oggFiles)))
print("Looping Files: " + str(len(looping_files)))
print("Loopless Files: " + str(len(loopless_files)))

out = "\n".join(loopless_files)

with open("loopless_files.txt", "w", encoding="utf8") as outfile:
    outfile.write(out)
