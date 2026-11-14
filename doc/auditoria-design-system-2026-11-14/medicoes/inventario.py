import ast, sys, pathlib, collections, re, json
S = sys.argv[1]
rows = [l.rstrip("\n").split("\t") for l in open(f"{S}/rotas.tsv")]
cache = {}
def modinfo(mod):
    if mod in cache: return cache[mod]
    p = pathlib.Path(mod.replace(".", "/") + ".py")
    if not p.exists():
        p = pathlib.Path(mod.replace(".", "/")) / "__init__.py"
    info = {}
    if p.exists():
        tree = ast.parse(p.read_text())
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                strs = [n.value for n in ast.walk(node) if isinstance(n, ast.Constant) and isinstance(n.value, str)]
                calls = {n.func.id for n in ast.walk(node) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
                decos = [ast.unparse(d) for d in getattr(node, "decorator_list", [])]
                info[node.name] = dict(
                    tpl={s for s in strs if s.endswith(".html")},
                    caps={s for s in strs if re.fullmatch(r"[a-z_]+:[a-z_]+", s)},
                    calls=calls, decos=decos)
    cache[mod] = info
    return info
def closure(mod, name, seen=None, depth=0):
    info = modinfo(mod); seen = seen or set()
    if name in seen or name not in info or depth > 4: return set(), set()
    seen.add(name)
    t, c = set(info[name]["tpl"]), set(info[name]["caps"])
    for callee in info[name]["calls"]:
        if callee in info:
            t2, c2 = closure(mod, callee, seen, depth + 1); t |= t2; c |= c2
    return t, c
out = []
for path, name, mod, view in rows:
    if not mod.startswith("processo_seletivo"): continue
    t, c = closure(mod, view)
    out.append(dict(rota="/" + path.replace("^","").replace("\\Z","").replace("$",""), nome=name, modulo=mod.replace("processo_seletivo.",""), view=view, templates=sorted(t), caps=sorted(c)))
json.dump(out, open(f"{S}/inventario.json","w"), ensure_ascii=False, indent=1)
semtpl = [o for o in out if not o["templates"]]
print(len(out), "rotas do produto;", len(semtpl), "sem template direto (API, POST, download, redirect)")
alltpl = collections.Counter(t for o in out for t in o["templates"])
print(len(alltpl), "templates citados por views")
for o in out:
    area = o["modulo"].split(".")[0]
    print(f'{area}\t{o["rota"]}\t{o["view"]}\t{",".join(x.split("/",1)[-1] for x in o["templates"])[:150]}')
