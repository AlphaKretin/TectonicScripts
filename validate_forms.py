import copy
import json
import re

with open("forms.json", "r", encoding="utf8") as infile:
    forms = json.loads(infile.read())

for mon in forms:
    for form in forms[mon]:
        if not "form_id" in form:
            print(mon + " " + form["form_name"])
