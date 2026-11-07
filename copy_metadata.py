"""
Step 3 of volume normalisation: copies the tags of each music/*.ogg onto its
volume-adjusted copy in music/normal/, since ffmpeg drops them (loop points
in particular). The ReplayGain tags were already removed by export_replaygain.py,
so they aren't copied.
"""

import os

import mutagen
import mutagen.oggvorbis

MUSIC_DIR = "music/"

OUTPUT_DIR = "music/normal/"

all_tracks = os.listdir(MUSIC_DIR)

ogg_tracks = [track for track in all_tracks if track.endswith(".ogg")]

for track in ogg_tracks:
    file = mutagen.oggvorbis.OggVorbis(MUSIC_DIR + track)
    tags = file.tags
    new_file = mutagen.oggvorbis.OggVorbis(OUTPUT_DIR + track)
    new_file.tags = tags
    new_file.save()
