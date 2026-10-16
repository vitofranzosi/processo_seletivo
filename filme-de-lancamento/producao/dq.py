import json, sys, re
D = json.load(open("dom.json"))
def q(name, text=None, tag=None, minw=0, maxh=99999, first=False):
    r = []
    for t, s, x, y, w, h in D[name]["els"]:
        if tag and not re.match(tag, t): continue
        if text and text.lower() not in s.lower(): continue
        if w < minw or h > maxh: continue
        r.append((t, s, x, y, w, h))
    return r[0] if first and r else r
if __name__ == "__main__":
    name = sys.argv[1]; text = sys.argv[2] if len(sys.argv) > 2 else None; tag = sys.argv[3] if len(sys.argv) > 3 else None
    for e in q(name, text, tag)[:40]:
        print(f"{e[0][:28]:28} {e[2]:5} {e[3]:5} {e[4]:5} {e[5]:5}  {e[1][:60]}")
