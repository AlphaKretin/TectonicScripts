import mutagen
import mutagen.oggvorbis

MUSIC_DIR = "music/"

with open("loops.txt", "r", encoding="utf8") as f:
    loops = f.read().splitlines()

for loop in loops:
    params = loop.split(" ")
    loop_start = int(params[0])
    loop_end = int(params[1])
    loop_length = loop_end - loop_start
    filename = " ".join(params[2:])
    file = mutagen.oggvorbis.OggVorbis(MUSIC_DIR + filename)
    file.tags["LOOPSTART"] = str(loop_start)
    file.tags["LOOPLENGTH"] = str(loop_length)
    file.save()
