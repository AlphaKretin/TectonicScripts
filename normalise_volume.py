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
