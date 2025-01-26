import mutagen
import mutagen.oggvorbis

with open("loops.txt", "r", encoding="utf8") as f:
    loops = f.read().splitlines()

print(loops)

for loop in loops:
    params = loop.split(" ")
    loop_start = int(params[0])
    loop_end = int(params[1])
    loop_length = loop_end - loop_start
    filename = " ".join(params[2:])
    file = mutagen.oggvorbis.OggVorbis(filename)
    file.tags["LOOPSTART"] = str(loop_start)
    file.tags["LOOPLENGTH"] = str(loop_length)
    file.save()