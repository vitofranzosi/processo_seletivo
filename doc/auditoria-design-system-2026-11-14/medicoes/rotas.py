import re, inspect
from django.urls import get_resolver, URLPattern, URLResolver
def walk(patterns, prefix="", ns=""):
    for p in patterns:
        if isinstance(p, URLResolver):
            n = (ns + ":" if ns else "") + (p.namespace or "") if p.namespace else ns
            yield from walk(p.url_patterns, prefix + str(p.pattern), n)
        else:
            cb = p.callback
            cb = getattr(cb, "view_class", cb)
            mod = getattr(cb, "__module__", "?")
            name = getattr(cb, "__name__", str(cb))
            yield prefix + str(p.pattern), (ns + ":" if ns else "") + (p.name or ""), mod, name
rows = list(walk(get_resolver().url_patterns))
import collections
by = collections.Counter(r[2].rsplit(".",1)[0] if "views" in r[2] else r[2] for r in rows)
print(len(rows), "rotas"); 
for k,v in by.most_common(): print(v, k)
with open(__import__("os").environ["ROTAS_OUT"], "w") as f:
    for r in rows: f.write("\t".join(r) + "\n")
