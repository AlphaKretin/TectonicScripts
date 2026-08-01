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
    # mutagen normalises VComment keys to lowercase; patch back to uppercase
    # since LOOPSTART/LOOPLENGTH are the same byte length, no offsets change
    filepath = MUSIC_DIR + filename
    with open(filepath, "rb") as fh:
        data = fh.read()
    data = data.replace(b"loopstart=", b"LOOPSTART=")
    data = data.replace(b"looplength=", b"LOOPLENGTH=")
    with open(filepath, "wb") as fh:
        fh.write(data)
