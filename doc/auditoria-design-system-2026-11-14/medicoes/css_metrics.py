import re, sys, collections, pathlib
root = pathlib.Path("backend/processo_seletivo")
files = [p for p in root.rglob("*.css") if "staticfiles" not in str(p)]
def strip(s): return re.sub(r"/\*.*?\*/", "", s, flags=re.S)
groups = {"gestao": [], "portal": [], "shared": []}
for p in files:
    k = "portal" if "/portal/" in str(p) else "shared" if "/shared/" in str(p) else "gestao"
    groups[k].append(p)
props = ["font-size","border-radius","max-width","font-weight","gap","padding","margin","box-shadow","line-height","min-height","height","width"]
for k, ps in groups.items():
    txt = "\n".join(strip(p.read_text()) for p in ps)
    print(f"\n===== {k}: {len(ps)} arquivos, {len(txt)} chars, ~{txt.count('{')} blocos")
    for prop in props:
        vals = collections.Counter(v.strip() for v in re.findall(r"(?<![-\w])%s\s*:\s*([^;}]+)" % re.escape(prop), txt))
        if prop in ("padding","margin","width","height","min-height","gap","line-height"):
            print(f"  {prop}: {len(vals)} valores distintos, {sum(vals.values())} usos; top: {vals.most_common(8)}")
        else:
            print(f"  {prop}: {len(vals)} distintos / {sum(vals.values())} usos -> {vals.most_common(40)}")
    hexes = collections.Counter(h.lower() for h in re.findall(r"#[0-9a-fA-F]{3,8}\b", txt))
    varuse = collections.Counter(re.findall(r"var\((--[\w-]+)", txt))
    print(f"  cores literais: {len(hexes)} distintas / {sum(hexes.values())} usos -> {hexes.most_common(40)}")
    n_rgba = len(re.findall(r'rgba?\(|hsla?\(', txt))
    print("  rgba/hsl literais:", n_rgba)
    print(f"  var(): {len(varuse)} tokens / {sum(varuse.values())} usos -> {varuse.most_common(40)}")
    defs = collections.Counter(re.findall(r"(--[\w-]+)\s*:", txt))
    print(f"  custom props definidas: {sorted(defs)}")
    media = collections.Counter(m.strip() for m in re.findall(r"@media\s*([^{]+)\{", txt))
    print(f"  @media: {media.most_common(30)}")
    cont = collections.Counter(m.strip() for m in re.findall(r"@container\s*([^{]+)\{", txt))
    print(f"  @container: {cont.most_common(10)}")
