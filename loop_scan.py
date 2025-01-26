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

# with open("loops.txt", "r", encoding="utf8") as f:
#     loops = f.read().splitlines()

# print(loops)

# for loop in loops:
#     params = loop.split(" ")
#     loop_start = int(params[0])
#     loop_end = int(params[1])
#     loop_length = loop_end - loop_start
#     filename = " ".join(params[2:])
#     file = mutagen.oggvorbis.OggVorbis(filename)
#     file.tags["LOOPSTART"] = str(loop_start)
#     file.tags["LOOPLENGTH"] = str(loop_length)
#     file.save()
