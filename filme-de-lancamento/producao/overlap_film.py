"""Detector de sobreposição sobre o filme inteiro (tempo do filme)."""
import sys, json
import overlap as O
import engine, film
step = float(sys.argv[1]) if len(sys.argv) > 1 else 0.1
t0 = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
t1 = float(sys.argv[3]) if len(sys.argv) > 3 else film.FILM_TOTAL
s = engine.surface(); groups = {}; n = 0
t = t0
while t < t1:
    O.REC["text"].clear(); O.REC["img"].clear()
    film.draw(s.getCanvas(), t)
    name = film.locate(t)[2]
    imgs = [r for r in O.REC["img"] if O.onscreen(r[2])]
    for (txt, size, al, tq, ts) in O.REC["text"]:
        if al < 0.25 or size < 14 or txt in O.WHITELIST or not O.onscreen(tq): continue
        best = (0, None)
        for (tag, ia, iq, isq) in imgs:
            if ia < 0.25 or isq > ts: continue
            cv = O.coverage(tq, iq)
            if cv > best[0]: best = (cv, tag)
        for (t2, s2, a2, q2, sq2) in O.REC["text"]:
            if t2 == txt or a2 < 0.25 or s2 < 14 or sq2 <= ts or t2 in O.WHITELIST: continue
            cv2 = O.coverage(tq, q2)
            if cv2 >= 0.15 and cv2 > best[0]: best = (cv2, "TEXTO «" + t2[:30] + "»")
        if best[0] >= 0.15:
            n += 1
            k = (name, txt, best[1]); g = groups.setdefault(k, [t, t, 0, size]); g[1] = t; g[2] = max(g[2], best[0])
    t += step
for k, (a, z, cv, size) in sorted(groups.items(), key=lambda kv: kv[1][0]):
    print(f"{a:7.2f}–{z:7.2f}  {k[0]:16} cobre {cv:4.0%}  tam {size:3}  «{k[1][:48]}»  sobre {k[2]}")
print(n, "amostras")
