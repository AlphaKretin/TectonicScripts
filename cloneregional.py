import shutil
import sys

TECTONIC_PATH = "C:/Users/lunal/Documents/Code/Pokemon-Tectonic-Fork"

orig_mon = sys.argv[1]
new_mon = sys.argv[2]

paths = [
    "Graphics/Pokemon/Back",
    "Graphics/Pokemon/Back shiny",
    "Graphics/Pokemon/Front",
    "Graphics/Pokemon/Front shiny",
    "Graphics/Pokemon/Icons",
    "Graphics/Pokemon/Icons shiny",
    "Graphics/Characters/Followers",
    "Graphics/Characters/Followers shiny",
    "Audio/SE/Cries",
]

for path in paths:
    ext = ".png" if "Graphics" in path else ".ogg"
    oldfile = orig_mon + ext
    newfile = new_mon + ext
    shutil.copy2(
        f"{TECTONIC_PATH}/{path}/{oldfile}", f"{TECTONIC_PATH}/{path}/{newfile}"
    )
