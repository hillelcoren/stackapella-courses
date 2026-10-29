"""Format a course file as the Vibrato one is: 4-space indents, with small leaf objects (a note,
a chord, a { "en": ... } word, a card) on one line."""
import json, sys

def leaf(v):
    if isinstance(v, dict):
        return all(not isinstance(x, (dict, list)) or (isinstance(x, dict) and set(x) == {"en"}) for x in v.values())
    return False

def fmt(v, depth=0):
    pad, inner = "    " * depth, "    " * (depth + 1)
    if isinstance(v, dict):
        if leaf(v) or not v:
            return json.dumps(v, ensure_ascii=False)
        items = [f'{inner}{json.dumps(k)}: {fmt(x, depth + 1)}' for k, x in v.items()]
        return "{\n" + ",\n".join(items) + "\n" + pad + "}"
    if isinstance(v, list):
        if all(not isinstance(x, (dict, list)) for x in v):
            return json.dumps(v, ensure_ascii=False)
        if all(leaf(x) for x in v) and len(json.dumps(v)) < 100:
            return json.dumps(v, ensure_ascii=False)
        return "[\n" + ",\n".join(inner + fmt(x, depth + 1) for x in v) + "\n" + pad + "]"
    return json.dumps(v, ensure_ascii=False)

for path in sys.argv[1:]:
    data = json.load(open(path))
    open(path, "w").write(fmt(data) + "\n")
