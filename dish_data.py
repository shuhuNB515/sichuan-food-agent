import json
from encodings import utf_8

KB_FILE = "knowledge/dishes.json"
def _load()->dict:
    with open(KB_FILE, "r",encoding="utf_8") as f:
        return json.load(f)

DISH_DB = _load()