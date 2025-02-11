import os

import mutagen
import mutagen.ogg
import mutagen.oggvorbis

MUSIC_DIR = "music/"

all_tracks = os.listdir(MUSIC_DIR)

ogg_tracks = [track for track in all_tracks if track.endswith(".ogg")]

output = []

for track in ogg_tracks:
    file = mutagen.oggvorbis.OggVorbis(MUSIC_DIR + track)
    gain = file.tags["replaygain_track_gain"][0]
    output.append(f"{track},{gain}")
    del file.tags["replaygain_track_gain"]
    del file.tags["replaygain_track_peak"]
    file.save()

out = "\n".join(output)

with open("replaygain.txt", "w", encoding="utf8") as outfile:
    outfile.write(out)
