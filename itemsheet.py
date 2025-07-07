import json
from collections import OrderedDict

with open("items.json", "r", encoding="utf8") as infile:
    items = json.loads(infile.read(), object_pairs_hook=OrderedDict)

item_list = list(items.values())
print(item_list[0])
item_list = [item for item in item_list if item["pocket"] == 5]  # held items only

item_rows = [
    item["name"] + "\t" + item["key"] + "\t" + item["description"] for item in item_list
]

with open("items.csv", "w", encoding="utf8") as outfile:
    outfile.write("\n".join(item_rows))
