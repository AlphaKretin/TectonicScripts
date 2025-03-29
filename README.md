# TectonicScripts
Most .txt files expected by the scripts are the PBS files from Pokemon Tectonic.
## JSON exports
All scripts beginning with `json_` extract relevant data from the corresponding PBS and export as JSON for use in the [damage calculator](https://github.com/AlphaKretin/tectonic-damage-calc).
## extract_types_tribes
Extracts a list of all Pokemon alongside their types, tribes, and abilities. Some tribes for 4th or branching evolutions will be blank and need to be added manually. Used to generate the data for the [team builder/coverage calculator](https://docs.google.com/spreadsheets/d/14JS_0oAJpP7EB9LrtIShvPYshig1oSVsBKCSVAVV6tc/edit?usp=sharing).
## filter_legendary
Filters the list of all Pokemon for Pokemon with the "Legendary" flag. Used for easy checking of what's illegal in the Battle Monument.
## filter_full_evo
Filters the list of all Pokemon for Pokemon that do not evolve. Used primarily to fuel the below script.
## calc_tribe_pairs
Calculates how many of each tribe pair exist amongst all fully evolved Pokemon. Uses its own data source derived from cross-referencing the above two scripts' output.
## list_tribe_pairs
Same as the above script, but lists out each Pokemon that fits the tribe pair instead.
## count_types
Counts how many instances of each type appear in the list of Pokemon.
## count_types_filtered
Same as above with additional filters for fully evolved, non-legendary Pokemon, using lists generated by filter_full_evo and filter_legendary
## pokedex_reoder
Parses the game's current pokemon.txt files and rewrites it in a new desired Pokedex order, defined by a list of InternalNames in pokedexorder.txt. It also generates a correct regionaldexes.txt. The output is not formatted perfectly, but can be corrected by having the game compile PBS and rewrite them.
## pokedex_update
Updates a pokemon.txt from from an old format, where entries are indexed by a Pokedex number and list an InternalName seperately, to a new format where entires are indexed by that internal name.
## loop_tag
Import loop points into Ogg Vorbis music files. Relies on a `loops.txt` file generated by the tool [PyMusicLooper](https://github.com/arkrow/PyMusicLooper), using the command `pymusiclooper.exe export-points --export-to TXT --fmt SAMPLES --path [FOLDERNAME]`.
## loop_scan
Scans the Tectonic music folder for Ogg files without a LOOPSTART tag and saves the list, to guide use of the above tool.
## Volume Normalisation
I had a heck of a time making this all work properly, so something that ought to take one script instead takes three. The first step, outside of a script, is to apply ReplayGain tags to the audio using a tool like foobar2000. The purpose of these scripts is to then hardcode those volume adjustments into the audio files so that they're applied in-game.
### extract_replaygain
Extracts the ReplayGain tags from the audio and outputs them to a file to be read later, since modifying the audio in the same script as reading them didn't seem to work for some reason. Deletes the tags from the original file so that the audio adjustment isn't applied twice after it's hardcoded.
### normalise_volume
Reads data from the output of the above script and adjusts the volume of the corresponding tracks accordingly. However, the ffmpeg-python library doesn't seem to properly transfer the loop metadata, hence...
### copy_metadata
Copies the metadata from the original audio tracks to the volume-adjusted ones, in particular to preserve loop points. Because the first script deleted the ReplayGain tags, they won't be copied.