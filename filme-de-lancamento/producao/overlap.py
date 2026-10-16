"""Detector de sobreposição: texto visível × imagem (captura, celular, ícone).

Intercepta drawString e as funções que pintam imagens, mapeia tudo para a tela pela matriz total
do canvas e mede, para cada texto, a fração da caixa que cai dentro de alguma imagem."""
import sys, importlib, json, math
import skia
import engine

REC = {"text": [], "img": [], "seq": [0]}
def _seq():
    REC["seq"][0] += 1
    return REC["seq"][0]

def _map(c, pts):
    m = c.getTotalMatrix()
    out = []
    for x, y in pts:
        p = m.mapXY(x, y)
        out.append((p.x(), p.y()))
    return out

_orig_ds = skia.Canvas.drawString
_K = {"on": False, "pts": [], "a": 0.0}
def _ds(self, s, x, y, font, paint):
    a = paint.getAlphaf()
    if _K["on"]:
        if s.strip() and a > 0.02:
            size = font.getSize(); w = font.measureText(s)
            _K["pts"] += _map(self, [(x, y - size * 0.75), (x + w, y + size * 0.2)])
            _K["a"] = max(_K["a"], a); _K["size"] = size
        return _orig_ds(self, s, x, y, font, paint)
    if s.strip() and a > 0.02:
        size = font.getSize()
        w = font.measureText(s)
        q = _map(self, [(x, y - size * 0.75), (x + w, y - size * 0.75), (x + w, y + size * 0.2), (x, y + size * 0.2)])
        REC["text"].append((s, size, a, q, _seq()))
    return _orig_ds(self, s, x, y, font, paint)
skia.Canvas.drawString = _ds

def _img(c, quad, a, tag):
    if a > 0.05:
        REC["img"].append((tag, a, _map(c, quad), _seq()))

_orig_kin = engine.kinetic
def kinetic(c, s, *a, **kw):
    _K["on"] = True; _K["pts"] = []; _K["a"] = 0.0
    try:
        return _orig_kin(c, s, *a, **kw)
    finally:
        _K["on"] = False
        if _K["pts"]:
            xs = [p[0] for p in _K["pts"]]; ys = [p[1] for p in _K["pts"]]
            q = [(min(xs), min(ys)), (max(xs), min(ys)), (max(xs), max(ys)), (min(xs), max(ys))]
            REC["text"].append((s, _K.get("size", 20), _K["a"], q, _seq()))
engine.kinetic = kinetic
_orig_text = engine.text
def text(c, s, *a, **kw):
    if _K["on"]:
        return _orig_text(c, s, *a, **kw)
    _K["on"] = True; _K["pts"] = []; _K["a"] = 0.0
    try:
        return _orig_text(c, s, *a, **kw)
    finally:
        _K["on"] = False
        if _K["pts"]:
            xs = [p[0] for p in _K["pts"]]; ys = [p[1] for p in _K["pts"]]
            q = [(min(xs), min(ys)), (max(xs), min(ys)), (max(xs), max(ys)), (min(xs), max(ys))]
            REC["text"].append((s, _K.get("size", 20), _K["a"], q, _seq()))
engine.text = text

_orig_card = engine.card
def card(c, img, src=None, dst=None, quad=None, radius=18, alpha=1.0, **kw):
    q = quad if quad is not None else [(dst.left(), dst.top()), (dst.right(), dst.top()), (dst.right(), dst.bottom()), (dst.left(), dst.bottom())]
    _img(c, q, alpha, img if isinstance(img, str) else "img")
    return _orig_card(c, img, src, dst, quad, radius, alpha, **kw)
engine.card = card

import kit
kit.card = card
_orig_frame = kit.Card.frame
def frame(self, c, alpha=1.0, *a, **kw):
    _img(c, self.quad, alpha, self.img)
    return _orig_frame(self, c, alpha, *a, **kw)
kit.Card.frame = frame
_orig_icon = kit.icon
def icon(c, kind, x, y, w, h, alpha=1.0, **kw):
    _img(c, [(x, y), (x + w, y), (x + w, y + h), (x, y + h)], alpha, "icon:" + kind)
    return _orig_icon(c, kind, x, y, w, h, alpha, **kw)
kit.icon = icon
_orig_phone = kit.device_phone
def device_phone(c, img, crop, cx, cy, h, alpha=1.0, rx=0, ry=0, rz=0):
    x, y, w, hh = crop
    ww = h * w / hh
    _img(c, kit.project(cx, cy, ww * 1.07, h * 1.07, rx, ry, rz), alpha, "phone:" + img)
    return _orig_phone(c, img, crop, cx, cy, h, alpha, rx, ry, rz)
kit.device_phone = device_phone

def inside(pt, quad):
    # quadrilátero convexo (projetado): mesmo sinal em todos os lados
    s = None
    for i in range(4):
        x1, y1 = quad[i]; x2, y2 = quad[(i + 1) % 4]
        cr = (x2 - x1) * (pt[1] - y1) - (y2 - y1) * (pt[0] - x1)
        if abs(cr) < 1e-9: continue
        if s is None: s = cr > 0
        elif (cr > 0) != s: return False
    return True

def coverage(tq, iq):
    n = 0; hit = 0
    for i in range(10):
        for j in range(3):
            u, v = (i + 0.5) / 10, (j + 0.5) / 3
            top = (tq[0][0] + (tq[1][0] - tq[0][0]) * u, tq[0][1] + (tq[1][1] - tq[0][1]) * u)
            bot = (tq[3][0] + (tq[2][0] - tq[3][0]) * u, tq[3][1] + (tq[2][1] - tq[3][1]) * u)
            p = (top[0] + (bot[0] - top[0]) * v, top[1] + (bot[1] - top[1]) * v)
            n += 1
            if inside(p, iq): hit += 1
    return hit / n

def onscreen(q):
    xs = [p[0] for p in q]; ys = [p[1] for p in q]
    return max(xs) > 0 and min(xs) < engine.W and max(ys) > 0 and min(ys) < engine.H

# textos que pertencem à imagem de propósito (digitação simulada, rótulos dentro do celular etc.)
WHITELIST = {"informática", "informátic", "informáti", "informát", "informá", "inform", "infor", "info", "inf", "in", "i",
             "PDF"}

if __name__ == "__main__":
    from render import MODS
    from timeline import SECTIONS, b
    step = float(sys.argv[1]) if len(sys.argv) > 1 else 1 / 6
    only = sys.argv[2:]
    s = engine.surface()
    events = []
    for name, a, z in SECTIONS:
        if only and name not in only: continue
        mod = importlib.import_module(MODS[name])
        t = b(a)
        while t < b(z):
            REC["text"].clear(); REC["img"].clear()
            mod.draw(s.getCanvas(), t)
            imgs = [r for r in REC["img"] if onscreen(r[2]) and not r[0].startswith("icon:pdf_strip")]
            for (txt, size, al, tq, ts) in REC["text"]:
                if al < 0.25 or size < 14 or txt in WHITELIST or not onscreen(tq): continue
                best = (0, None)
                for (tag, ia, iq, isq) in imgs:
                    if ia < 0.25 or isq > ts: continue
                    cv = coverage(tq, iq)
                    if cv > best[0]: best = (cv, tag)
                for (t2, s2, a2, q2, sq2) in REC["text"]:
                    if t2 == txt or a2 < 0.25 or s2 < 14 or sq2 <= ts or t2 in WHITELIST: continue
                    cv2 = coverage(tq, q2)
                    if cv2 >= 0.15 and cv2 > best[0]: best = (cv2, "TEXTO «" + t2[:30] + "»")
                if best[0] >= 0.15:
                    events.append((round(t, 2), name, txt, round(size), round(al, 2), round(best[0], 2), best[1]))
            t += step
    json.dump(events, open("overlap.json", "w"), ensure_ascii=False)
    # agrupa por (seção, texto, imagem) em intervalos
    groups = {}
    for (t, name, txt, size, al, cv, tag) in events:
        k = (name, txt, tag)
        g = groups.setdefault(k, [t, t, 0, size])
        g[0] = min(g[0], t); g[1] = max(g[1], t); g[2] = max(g[2], cv)
    for k, (t0, t1, cv, size) in sorted(groups.items(), key=lambda kv: kv[1][0]):
        print(f"{t0:7.2f}–{t1:7.2f}  {k[0]:16} cobre {cv:4.0%}  tam {size:3}  «{k[1][:48]}»  sobre {k[2]}")
    print(len(events), "amostras com sobreposição")
