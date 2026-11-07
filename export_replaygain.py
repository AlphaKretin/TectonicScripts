"""
Step 1 of volume normalisation, which bakes ReplayGain adjustments into the
music so they apply in-game. First tag the tracks in music/ with ReplayGain
(e.g. in foobar2000); this script records each track's gain and removes the
ReplayGain tags, so the adjustment isn't applied twice once it's baked in.
Then run normalise_volume.py and copy_metadata.py.

Writes replaygain.txt (filename,gain per line) and edits the tracks' tags.
"""

import os

import mutagen
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
