"""Peças gráficas reutilizadas pelas cenas: ícones das ferramentas avulsas, cursor, foco,
rótulos, e a 'câmera' sobre capturas reais."""
import math
from engine import *

PAPER_C = "#f3f1ea"
LINE_C = "#2a3330"

# ---------------------------------------------------------------- ícones (genéricos, não são telas de produto)
def _p(col, a=1.0, st=None, w=1.0):
    return paint(col, a, style=st, stroke=w)

def icon(c, kind, x, y, w, h, alpha=1.0, k_detail=1.0, color_amt=1.0, blur=0.0):
    """Desenha a ferramenta 'kind' num cartão de papel com canto em (x,y)."""
    if alpha <= 0.003:
        return
    c.save()
    if blur > 0.3:
        lp = skia.Paint(ImageFilter=skia.ImageFilters.Blur(blur, blur))
        c.saveLayer(rect(x - 40, y - 40, w + 80, h + 80), lp)
    r = min(w, h) * 0.07
    # sombra e papel
    c.drawRRect(skia.RRect.MakeRectXY(rect(x, y + h * 0.05, w, h), r, r), paint("#000000", 0.45 * alpha, w * 0.08))
    c.drawRRect(skia.RRect.MakeRectXY(rect(x, y, w, h), r, r), paint(PAPER_C, alpha))
    ink = lambda a=1.0: paint(LINE_C, alpha * a)
    u = w / 100.0
    def bar(xx, yy, ww, hh, col=LINE_C, a=0.85, rr=None):
        rr = hh / 2 if rr is None else rr
        c.drawRRect(skia.RRect.MakeRectXY(rect(x + xx * u, y + yy * u, ww * u, hh * u), rr * u, rr * u), paint(col, alpha * a))
    def box(xx, yy, ww, hh, col=LINE_C, a=0.6, sw=1.2):
        c.drawRRect(skia.RRect.MakeRectXY(rect(x + xx * u, y + yy * u, ww * u, hh * u), 2 * u, 2 * u),
                    paint(col, alpha * a, style="stroke", stroke=sw * u))
    red = lambda: lerp_col(LINE_C, RED, color_amt)
    if kind == "form":
        bar(10, 10, 56, 7, a=0.9)
        for i in range(3):
            bar(10, 26 + i * 26, 30, 4, a=0.5)
            box(10, 33 + i * 26, 80, 11)
        bar(10, 110, 34, 11, col=lerp_col(LINE_C, "#3b6fd8", color_amt), a=0.9, rr=3)
    elif kind == "sheet":
        cols, rows = 5, 8
        gx, gy, gw, gh = 8, 10, 84, 104
        c.drawRect(rect(x + gx * u, y + gy * u, gw * u, gh / rows * u), paint(lerp_col(LINE_C, "#1f8f4e", color_amt), alpha * 0.85))
        p = paint(LINE_C, alpha * 0.35, style="stroke", stroke=0.8 * u)
        for i in range(cols + 1):
            c.drawLine(x + (gx + gw * i / cols) * u, y + gy * u, x + (gx + gw * i / cols) * u, y + (gy + gh) * u, p)
        for j in range(rows + 1):
            c.drawLine(x + gx * u, y + (gy + gh * j / rows) * u, x + (gx + gw) * u, y + (gy + gh * j / rows) * u, p)
        for j in range(1, rows):
            for i in range(cols):
                ww = (gw / cols - 6) * (0.35 + 0.6 * ((i * 7 + j * 3) % 5) / 5)
                bar(gx + gw * i / cols + 3, gy + gh * j / rows + 4.5, ww, 3.2, a=0.45)
    elif kind == "pdf":
        # canto dobrado
        path = skia.Path()
        path.moveTo(x + 70 * u, y); path.lineTo(x + w, y + 30 * u); path.lineTo(x + 70 * u, y + 30 * u); path.close()
        c.drawPath(path, paint("#d8d4c8", alpha))
        bar(10, 12, 26, 13, col=red(), a=0.95, rr=2)
        text(c, "PDF", x + 13 * u, y + 22.5 * u, 9 * u, 800, PAPER_C, alpha)
        for i in range(8):
            bar(10, 38 + i * 10, 80 - (i % 3) * 14, 3.4, a=0.45)
    elif kind == "mail":
        box(10, 16, 80, 52, a=0.8, sw=2)
        path = skia.Path(); path.moveTo(x + 10 * u, y + 16 * u); path.lineTo(x + 50 * u, y + 46 * u); path.lineTo(x + 90 * u, y + 16 * u)
        c.drawPath(path, paint(LINE_C, alpha * 0.8, style="stroke", stroke=2 * u))
        for i in range(4):
            bar(10, 80 + i * 10, 76 - i * 12, 3.4, a=0.45)
    elif kind == "folder":
        col = lerp_col(LINE_C, "#d99a2b", color_amt)
        bar(10, 20, 34, 12, col=col, a=0.9, rr=3)
        bar(10, 28, 80, 56, col=col, a=0.9, rr=4)
        for i in range(3):
            bar(14, 92 + i * 10, 70 - i * 15, 3.4, a=0.45)
    elif kind == "check":
        for i in range(5):
            yy = 14 + i * 21
            box(10, yy, 11, 11, a=0.7)
            if i in (0, 1, 3):
                pth = skia.Path(); pth.moveTo(x + 12 * u, y + (yy + 6) * u); pth.lineTo(x + 15 * u, y + (yy + 9) * u); pth.lineTo(x + 20 * u, y + (yy + 2) * u)
                c.drawPath(pth, paint(lerp_col(LINE_C, "#1f8f4e", color_amt), alpha, style="stroke", stroke=2 * u))
            elif i == 4:
                c.drawLine(x + 12 * u, y + (yy + 2) * u, x + 19 * u, y + (yy + 9) * u, paint(red(), alpha, style="stroke", stroke=2 * u))
                c.drawLine(x + 19 * u, y + (yy + 2) * u, x + 12 * u, y + (yy + 9) * u, paint(red(), alpha, style="stroke", stroke=2 * u))
            bar(27, yy + 3.5, 56 - (i % 2) * 18, 4, a=0.5)
    elif kind == "calendar":
        c.drawRect(rect(x + 8 * u, y + 12 * u, 84 * u, 16 * u), paint(red(), alpha * 0.9))
        for i in range(7):
            for j in range(5):
                bar(12 + i * 11.6, 36 + j * 15, 7, 7, a=0.28, rr=1.5)
        c.drawCircle(x + (12 + 4 * 11.6 + 3.5) * u, y + (36 + 2 * 15 + 3.5) * u, 7.5 * u, paint(red(), alpha, style="stroke", stroke=1.8 * u))
    elif kind == "msg":
        bar(8, 14, 62, 22, col="#c9d6cf", a=0.95, rr=6)
        bar(30, 44, 62, 22, col=lerp_col(LINE_C, "#36a565", color_amt), a=0.75, rr=6)
        bar(8, 74, 50, 22, col="#c9d6cf", a=0.95, rr=6)
        for (xx, yy) in [(14, 22), (36, 52), (14, 82)]:
            bar(xx, yy, 40, 3.4, a=0.5)
    if blur > 0.3:
        c.restore()
    c.restore()

def lerp_col(a, b, t):
    ca, cb = rgb(a), rgb(b)
    return skia.Color4f(lerp(ca.fR, cb.fR, t), lerp(ca.fG, cb.fG, t), lerp(ca.fB, cb.fB, t), 1.0)

def badge(c, x, y, n, alpha=1.0, scale=1.0):
    if alpha <= 0.01: return
    r = 15 * scale
    c.drawCircle(x, y, r + 3 * scale, paint(BG0, alpha))
    c.drawCircle(x, y, r, paint(RED, alpha))
    text(c, str(n), x, y + 6 * scale, 17 * scale, 700, "#ffffff", alpha, "center")

# ---------------------------------------------------------------- cursor
def cursor(c, x, y, alpha=1.0, scale=1.0, press=0.0):
    if alpha <= 0.01: return
    s = 1.15 * scale * (1 - 0.12 * press)
    pts = [(0, 0), (0, 25), (6.5, 19), (11, 29), (15, 27.3), (10.5, 17.6), (18.5, 17.6)]
    path = skia.Path()
    path.moveTo(x + pts[0][0] * s, y + pts[0][1] * s)
    for px, py in pts[1:]:
        path.lineTo(x + px * s, y + py * s)
    path.close()
    c.drawPath(path.makeOffset(1.5, 3) if hasattr(path, "makeOffset") else path, paint("#000000", 0.35 * alpha, 3))
    c.drawPath(path, paint("#111111", alpha))
    c.drawPath(path, paint("#ffffff", alpha, style="stroke", stroke=1.6 * scale))

def ripple(c, x, y, k, color=GREEN):
    """k ∈ [0,1] — onda de clique."""
    if k <= 0 or k >= 1: return
    r = 8 + 46 * e_out3(k)
    c.drawCircle(x, y, r, paint(color, 0.6 * (1 - k), style="stroke", stroke=3))
    c.drawCircle(x, y, r * 0.5, paint(color, 0.25 * (1 - k)))

# ---------------------------------------------------------------- texto de apoio
def tag(c, s, x, y, alpha=1.0, color=MINT, size=17):
    """Rótulo monoespaçado em caixa alta: '01 · ELABORAÇÃO'."""
    if alpha <= 0.01: return
    text(c, s.upper(), x, y, size, 600, color, alpha, tracking=0.16, family="Menlo")

def headline(c, s, x, y, t, size=92, color=INK, align="left", out_t=None, weight=760, stagger=0.03, accent=None):
    kinetic(c, s, x, y, size, t, weight=weight, color=color, align=align, out_t=out_t, stagger=stagger,
            tracking=-0.02, dur=0.75, rise=0.4)

def scrim(c, alpha=0.6, side="left", w=0.55):
    """Escurece um lado para o texto respirar sobre as capturas."""
    if alpha <= 0.01: return
    if side == "left":
        sh = skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(W * w, 0)], [rgb(BG0, alpha), rgb(BG0, 0)])
    elif side == "bottom":
        sh = skia.GradientShader.MakeLinear([skia.Point(0, H), skia.Point(0, H * (1 - w))], [rgb(BG0, alpha), rgb(BG0, 0)])
    else:
        sh = skia.GradientShader.MakeLinear([skia.Point(W, 0), skia.Point(W * (1 - w), 0)], [rgb(BG0, alpha), rgb(BG0, 0)])
    c.drawRect(rect(0, 0, W, H), skia.Paint(Shader=sh))

# ---------------------------------------------------------------- câmera sobre capturas
# Telas de interface ficam de frente enquanto são lidas: a perspectiva deformava a letra em
# trapézio. O giro sobrevive só no movimento (mrx, mry, postos por moved()) — ver eff_rot().
FLAT = True

class Pose:
    __slots__ = ("cx", "cy", "w", "rx", "ry", "rz", "tz", "alpha", "mrx", "mry")
    def __init__(self, cx=W / 2, cy=H / 2, w=1500, rx=0, ry=0, rz=0, tz=0, alpha=1.0, mrx=0.0, mry=0.0):
        self.cx, self.cy, self.w, self.rx, self.ry, self.rz, self.tz, self.alpha = cx, cy, w, rx, ry, rz, tz, alpha
        self.mrx, self.mry = mrx, mry
    def mix(self, o, k):
        return Pose(*(lerp(getattr(self, a), getattr(o, a), k) for a in Pose.__slots__))

def eff_rot(p):
    return (p.mrx, p.mry) if FLAT else (p.rx + p.mrx, p.ry + p.mry)

def crop_lerp(a, b, k):
    return tuple(lerp(a[i], b[i], k) for i in range(4))

def shot(c, img, crop, pose, radius=16, glow=0.0, shadow=0.55, border=0.10):
    """Mostra o recorte crop=(x,y,w,h) da captura 'img' com a pose dada. Devolve a função que
    converte um ponto da captura em ponto da tela (para foco e cursor)."""
    x, y, w, h = crop
    hh = pose.w * h / w
    quad = project(pose.cx, pose.cy, pose.w, hh, pose.rx, pose.ry, pose.rz, pose.tz)
    card(c, img, skia.Rect.MakeXYWH(x, y, w, h), quad=quad, radius=radius, alpha=pose.alpha,
         glow=glow, shadow=shadow, border=border)
    m = quad_matrix(skia.Rect.MakeXYWH(0, 0, w, h), quad)
    def to_screen(px, py):
        p = m.mapXY(px - x, py - y)
        return (p.x(), p.y())
    return to_screen

def focus(c, to_screen, box, k, color=GREEN, pad=10, dim=0.0, radius=12):
    """Contorno que se desenha em volta de um elemento (box em px da captura)."""
    if k <= 0: return
    x, y, w, h = box
    pts = [to_screen(x - pad, y - pad), to_screen(x + w + pad, y - pad), to_screen(x + w + pad, y + h + pad), to_screen(x - pad, y + h + pad)]
    path = skia.Path()
    path.moveTo(*pts[0])
    for p in pts[1:]:
        path.lineTo(*p)
    path.close()
    if dim > 0:
        c.save()
        c.clipPath(path, skia.ClipOp.kDifference, True)
        c.drawRect(rect(0, 0, W, H), paint(BG0, dim * k))
        c.restore()
    meas = skia.PathMeasure(path, False)
    L = meas.getLength()
    seg = skia.Path()
    meas.getSegment(0, L * e_out3(clamp(k)), seg, True)
    c.drawPath(seg, paint(color, 0.35 * clamp(k * 2), 8, style="stroke", stroke=6))
    c.drawPath(seg, paint(color, 0.95, style="stroke", stroke=3))

def device_phone(c, img, crop, cx, cy, h, alpha=1.0, rx=0, ry=0, rz=0):
    """Celular: moldura arredondada escura com a captura móvel dentro."""
    x, y, w, hh = crop
    ww = h * w / hh
    frame_pad = h * 0.035
    quad_out = project(cx, cy, ww + frame_pad * 2, h + frame_pad * 2, rx, ry, rz)
    m = quad_matrix(skia.Rect.MakeWH(ww + frame_pad * 2, h + frame_pad * 2), quad_out)
    c.save()
    c.concat(m)
    R = h * 0.075
    c.drawRRect(skia.RRect.MakeRectXY(rect(0, 26, ww + frame_pad * 2, h + frame_pad * 2), R, R), paint("#000000", 0.5 * alpha, 40))
    c.drawRRect(skia.RRect.MakeRectXY(rect(0, 0, ww + frame_pad * 2, h + frame_pad * 2), R, R), paint("#0d1110", alpha))
    c.drawRRect(skia.RRect.MakeRectXY(rect(0, 0, ww + frame_pad * 2, h + frame_pad * 2), R, R), paint("#3a4440", alpha, style="stroke", stroke=2))
    rr = skia.RRect.MakeRectXY(rect(frame_pad, frame_pad, ww, h), R * 0.8, R * 0.8)
    c.save()
    c.clipRRect(rr, True)
    p = skia.Paint(AntiAlias=True); p.setAlphaf(alpha)
    c.drawImageRect(image(img) if isinstance(img, str) else img, skia.Rect.MakeXYWH(x, y, w, hh), rect(frame_pad, frame_pad, ww, h), SAMP, p)
    c.restore()
    # ilha
    c.drawRRect(skia.RRect.MakeRectXY(rect(frame_pad + ww / 2 - ww * 0.14, frame_pad + h * 0.012, ww * 0.28, h * 0.032), h * 0.016, h * 0.016), paint("#000000", alpha))
    c.restore()

# ---------------------------------------------------------------- linhas
def bezier(c, p0, p1, p2, p3, color, alpha, width=2.0, dash=None, phase=0.0, k=1.0, blur=0.0):
    if alpha <= 0.01 or k <= 0: return
    path = skia.Path()
    path.moveTo(*p0)
    path.cubicTo(*p1, *p2, *p3)
    if k < 1:
        meas = skia.PathMeasure(path, False)
        seg = skia.Path()
        meas.getSegment(0, meas.getLength() * k, seg, True)
        path = seg
    p = paint(color, alpha, blur, style="stroke", stroke=width)
    if dash:
        p.setPathEffect(skia.DashPathEffect.Make(dash, phase))
    c.drawPath(path, p)

def glow_dot(c, x, y, r, color, alpha=1.0):
    c.drawCircle(x, y, r * 3, paint(color, 0.25 * alpha, r * 2))
    c.drawCircle(x, y, r, paint(color, alpha))

def hash01(*a):
    h = 0
    for v in a:
        h = (h * 1000003) ^ int(v * 7919 + 13)
        h &= 0xFFFFFFFF
    h ^= h >> 13; h = (h * 0x5bd1e995) & 0xFFFFFFFF; h ^= h >> 15
    return (h & 0xFFFFFF) / float(0xFFFFFF)

# ---------------------------------------------------------------- cartão com regiões
class Card:
    """Uma captura recortada, posta em pose 3D. Permite trocar regiões (passo a passo) sem mexer
    na pose, e converte coordenadas da captura em coordenadas da tela."""
    def __init__(self, img, crop, pose):
        self.img, self.crop, self.pose = img, crop, pose
        x, y, w, h = crop
        hh = pose.w * h / w
        rx, ry = eff_rot(pose)
        self.quad = project(pose.cx, pose.cy, pose.w, hh, rx, ry, pose.rz, pose.tz)
        self.M = quad_matrix(skia.Rect.MakeXYWH(0, 0, w, h), self.quad)
        self.sc = w / max(1.0, math.hypot(self.quad[1][0] - self.quad[0][0], self.quad[1][1] - self.quad[0][1]))

    def to_screen(self, px, py):
        p = self.M.mapXY(px - self.crop[0], py - self.crop[1])
        return (p.x(), p.y())

    def frame(self, c, alpha=1.0, radius=16, shadow=0.55, glow=0.0, border=0.10, fill=PAPER):
        x, y, w, h = self.crop
        c.save(); c.concat(self.M)
        rr = skia.RRect.MakeRectXY(skia.Rect.MakeWH(w, h), radius * self.sc, radius * self.sc)
        if shadow > 0:
            c.drawRRect(rr.makeOffset(0, 26 * self.sc), paint("#000000", shadow * alpha, 40 * self.sc))
        if glow > 0:
            c.drawRRect(rr, paint(GREEN, glow * alpha, 60 * self.sc))
        c.drawRRect(rr, paint(fill, alpha))
        c.restore()

    def region(self, c, sub=None, img=None, offset=(0, 0), alpha=1.0, radius=16):
        """Pinta a região sub=(x,y,w,h) — em px da captura — com a imagem img deslocada por offset."""
        img = img or self.img
        x, y, w, h = self.crop
        if sub is None: sub = (x, y, w, h)
        sx, sy, sw, sh = sub
        c.save(); c.concat(self.M)
        rr = skia.RRect.MakeRectXY(skia.Rect.MakeWH(w, h), radius * self.sc, radius * self.sc)
        c.clipRRect(rr, True)
        c.clipRect(skia.Rect.MakeXYWH(sx - x, sy - y, sw, sh), skia.ClipOp.kIntersect, True)
        p = skia.Paint(AntiAlias=True); p.setAlphaf(clamp(alpha))
        im = image(img) if isinstance(img, str) else img
        # recorta a fonte aos limites da imagem (página curta não estica)
        ox, oy = offset
        top = max(0.0, -(sy + oy)); bot = max(0.0, (sy + oy + sh) - im.height())
        if sh - top - bot > 1:
            c.drawImageRect(im, skia.Rect.MakeXYWH(sx + ox, sy + oy + top, sw, sh - top - bot),
                            skia.Rect.MakeXYWH(sx - x, sy - y + top, sw, sh - top - bot), SAMP, p)
        c.restore()

    def border(self, c, alpha=1.0, radius=16, a=0.12):
        x, y, w, h = self.crop
        c.save(); c.concat(self.M)
        rr = skia.RRect.MakeRectXY(skia.Rect.MakeWH(w, h), radius * self.sc, radius * self.sc)
        c.drawRRect(rr, paint("#ffffff", a * alpha, style="stroke", stroke=1.5 * self.sc))
        c.restore()

    def draw(self, c, alpha=1.0, glow=0.0, shadow=0.55, radius=16, border=0.10):
        if alpha <= 0.003: return self
        self.frame(c, alpha, radius, shadow, glow, border)
        self.region(c, alpha=alpha, radius=radius)
        if border: self.border(c, alpha, radius, border)
        return self

    def focus(self, c, box, k, **kw):
        # o destaque nunca passa da borda do recorte: a câmera pode ter cortado parte do alvo
        pad = kw.get("pad", 10)
        x, y, w, h = box
        cx, cy, cw, ch = self.crop
        m = pad + 6
        x0 = max(x, cx + m); y0 = max(y, cy + m)
        x1 = min(x + w, cx + cw - m); y1 = min(y + h, cy + ch - m)
        if x1 - x0 < 20 or y1 - y0 < 10: return
        focus(c, self.to_screen, (x0, y0, x1 - x0, y1 - y0), k, **kw)

def pose_at(T, keys, ease=e_io3):
    """keys: [(t, Pose), ...] — interpola por trechos."""
    if T <= keys[0][0]: return keys[0][1]
    for (t0, p0), (t1, p1) in zip(keys, keys[1:]):
        if T <= t1:
            return p0.mix(p1, ease(prog(T, t0, t1)))
    return keys[-1][1]

def path_at(T, keys, ease=e_io3):
    """keys: [(t, (x,y)), ...]"""
    if T <= keys[0][0]: return keys[0][1]
    for (t0, a), (t1, bb) in zip(keys, keys[1:]):
        if T <= t1:
            k = ease(prog(T, t0, t1))
            return (lerp(a[0], bb[0], k), lerp(a[1], bb[1], k))
    return keys[-1][1]

def caption_block(c, T, t0, t1, title, sub=None, x=150, y=900, size=84, color=INK, tag_s=None, wrap=None):
    """Título cinético com tag acima e linha de apoio; sai antes de t1."""
    if T < t0 - 0.05 or T > t1 + 0.6: return
    out = t1 - t0
    if tag_s:
        tag(c, tag_s, x + 4, y - size - 22, env(T, t0, t1 + 0.3, 0.4, 0.4))
    kinetic(c, title, x, y, size, T - t0, weight=780, align="left", out_t=out, color=color, stagger=0.028)
    if sub:
        ss = size * 0.38
        lines = [sub]
        if wrap:
            lines = [""]
            for w_ in sub.split(" "):
                if lines[-1] and text_width(lines[-1] + " " + w_, ss, 480) > wrap: lines.append(w_)
                else: lines[-1] = (lines[-1] + " " + w_).strip()
        for i, ln in enumerate(lines):
            kinetic(c, ln, x + 2, y + size * 0.62 + i * ss * 1.35, ss, T - t0 - 0.35 - i * 0.06, weight=480, align="left",
                    out_t=out - 0.35, color=MUTED, stagger=0.01, rise=0.3, blur_in=4)


# ---------------------------------------------------------------- zonas livres para a imagem
# Regra de layout: texto e imagem não se cruzam. Com legenda embaixo, a imagem fica acima da faixa;
# com legenda à esquerda, a imagem fica à direita da coluna.
ZONE_BOTTOM = (70, 46, 1850, 800)     # legenda embaixo (tag em ~868, título em ~962)
ZONE_RIGHT = (770, 60, 1860, 1020)    # legenda à esquerda (coluna até ~720)
CAP_Y = 962                           # linha de base do título da faixa de baixo
CAP_SIZE = 72

def _bbox(p, crop):
    rx, ry = eff_rot(p)
    q = project(p.cx, p.cy, p.w, p.w * crop[3] / crop[2], rx, ry, p.rz, p.tz)
    xs = [a for a, _ in q]; ys = [b for _, b in q]
    return min(xs), min(ys), max(xs), max(ys)

def room(pose, crop, zone, k=1.0):
    """Encaixa a pose na zona (encolhendo e deslocando). k ∈ [0,1] mistura com a pose original,
    para que a imagem abra espaço quando a legenda entra."""
    if k <= 0.001: return pose
    p = Pose(*(getattr(pose, a) for a in Pose.__slots__))
    for _ in range(4):
        x0, y0, x1, y1 = _bbox(p, crop)
        s = min(1.0, (zone[2] - zone[0]) / max(1, x1 - x0), (zone[3] - zone[1]) / max(1, y1 - y0))
        p.w *= s * 0.995
        x0, y0, x1, y1 = _bbox(p, crop)
        dx = (zone[0] - x0 if x0 < zone[0] else 0) - (x1 - zone[2] if x1 > zone[2] else 0)
        dy = (zone[1] - y0 if y0 < zone[1] else 0) - (y1 - zone[3] if y1 > zone[3] else 0)
        p.cx += dx; p.cy += dy
    return pose.mix(p, clamp(k))

def moved(pose, dx=0.0, dy=0.0, dz=0.0, alpha=None):
    """Entrada e saída aplicadas depois do encaixe. O deslocamento inclina a tela na direção do
    movimento, e a inclinação some quando ela assenta."""
    return Pose(pose.cx + dx, pose.cy + dy, pose.w, pose.rx, pose.ry, pose.rz, pose.tz + dz,
                pose.alpha if alpha is None else alpha,
                pose.mrx + clamp(dy * 0.014, -16, 16), pose.mry + clamp(-dx * 0.018, -26, 26))

def cap(c, T, t0, t1, title, sub=None, tag_s=None, color=INK):
    """Legenda padrão da faixa de baixo."""
    caption_block(c, T, t0, t1, title, sub, 150, CAP_Y, CAP_SIZE, color=color, tag_s=tag_s, wrap=1500)


def _inside(pt, quad):
    sgn = None
    for i in range(4):
        x1, y1 = quad[i]; x2, y2 = quad[(i + 1) % 4]
        cr = (x2 - x1) * (pt[1] - y1) - (y2 - y1) * (pt[0] - x1)
        if abs(cr) < 1e-9: continue
        if sgn is None: sgn = cr > 0
        elif (cr > 0) != sgn: return False
    return True

def covered(box, quads):
    """Fração do retângulo box=(x,y,w,h) que cai dentro de algum dos quadriláteros."""
    x, y, w, h = box
    n = hit = 0
    for i in range(8):
        for j in range(3):
            p = (x + (i + 0.5) / 8 * w, y + (j + 0.5) / 3 * h)
            n += 1
            if any(_inside(p, q) for q in quads): hit += 1
    return hit / n


# ---------------------------------------------------------------- caixas medidas no DOM
_DOM = None
def dom(name, text, tag=None, i=0):
    """Caixa (x, y, w, h), em px da captura, do i-ésimo elemento da tela `name` cujo texto contém
    `text` (e cuja tag casa com o prefixo `tag`). Medidas por domboxes.py no DOM real."""
    global _DOM
    if _DOM is None:
        import json as _j
        _DOM = _j.load(open(os.path.join(ROOT, "dom.json")))
    name = name.rsplit(".", 1)[0]
    hits = [e for e in _DOM[name]["els"] if text.lower() in e[1].lower() and (tag is None or e[0].startswith(tag))]
    if not hits:
        raise KeyError(f"{name}: «{text}» ({tag})")
    t, s, x, y, w, h = hits[i]
    return (x, y, w, h)

def union(*bs):
    x0 = min(b[0] for b in bs); y0 = min(b[1] for b in bs)
    x1 = max(b[0] + b[2] for b in bs); y1 = max(b[1] + b[3] for b in bs)
    return (x0, y0, x1 - x0, y1 - y0)

def window(box, zone, pad=60, aspect=None, maxw=2880, minw=1500):
    """Janela de câmera (crop) em volta de `box`, com a proporção da zona e sem ampliar além de 1:1."""
    zx0, zy0, zx1, zy1 = zone
    za = (zx1 - zx0) / (zy1 - zy0) if aspect is None else aspect
    x, y, w, h = box
    w2 = max(minw, min(maxw, w + 2 * pad)); h2 = w2 / za
    if h + 2 * pad > h2:
        h2 = h + 2 * pad; w2 = min(maxw, h2 * za)
    cx = x + w / 2; cy = y + h / 2
    x0 = clamp(cx - w2 / 2, 0, 2880 - w2) if w2 < 2880 else 0
    x0 = min(x0, max(0, x - pad))
    return (x0, max(0, cy - h2 / 2), w2, h2)

def frame_in(crop, zone, maxscale=1.0, align="center"):
    """Pose plana que põe o crop dentro da zona, na maior escala possível até maxscale."""
    zx0, zy0, zx1, zy1 = zone
    s = min(maxscale, (zx1 - zx0) / crop[2], (zy1 - zy0) / crop[3])
    w = crop[2] * s; h = crop[3] * s
    cx = (zx0 + zx1) / 2 if align == "center" else zx0 + w / 2
    return Pose(cx, (zy0 + zy1) / 2, w)

def cam_at(T, keys, ease=e_io3):
    """Câmera sobre a captura: keys = [(t, crop), ...]; o recorte desliza entre os quadros-chave."""
    if T <= keys[0][0]: return keys[0][1]
    for (t0, a), (t1, b_) in zip(keys, keys[1:]):
        if T <= t1:
            return crop_lerp(a, b_, ease(prog(T, t0, t1)))
    return keys[-1][1]

def chips(name, texts, tag="a"):
    return union(*[dom(name, t, tag) for t in texts])
