"""Compositor de quadros: skia desenha, numpy acumula, ffmpeg codifica.

Nada aqui é HTML: cada quadro é pintado num raster 1920x1080 e entregue ao ffmpeg como vídeo bruto.
"""
import math, os, json, subprocess, functools
import numpy as np
import skia

W, H, FPS = 1920, 1080, 30
ROOT = os.path.dirname(os.path.abspath(__file__))
CAP = os.path.join(ROOT, "cap")

# ---------------------------------------------------------------- paleta
def rgb(h, a=1.0):
    h = h.lstrip("#")
    return skia.Color4f(int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255, a)

BG0 = "#050b08"      # fundo quase preto, com verde
BG1 = "#0a1a12"
GREEN = "#2fae5f"    # verde Ifes, iluminado para fundo escuro
GREEN_D = "#0b5a2c"  # o verde do cabeçalho do portal
MINT = "#9be8b8"
RED = "#e0463c"      # acento quente, usado com parcimônia
INK = "#eef5f0"
MUTED = "#8aa596"
PAPER = "#f7f7f5"

# ---------------------------------------------------------------- tempo
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x

def lerp(a, b, t):
    return a + (b - a) * t

def prog(t, a, b):
    if b == a:
        return 1.0 if t >= b else 0.0
    return clamp((t - a) / (b - a))

def e_out3(x): return 1 - (1 - x) ** 3
def e_in3(x): return x ** 3
def e_io3(x): return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2
def e_out5(x): return 1 - (1 - x) ** 5
def e_outexpo(x): return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)
def e_inexpo(x): return 0.0 if x <= 0 else 2 ** (10 * x - 10)
def e_ioexpo(x):
    if x <= 0: return 0.0
    if x >= 1: return 1.0
    return 2 ** (20 * x - 10) / 2 if x < .5 else (2 - 2 ** (-20 * x + 10)) / 2
def e_outback(x, s=1.4):
    x -= 1
    return x * x * ((s + 1) * x + s) + 1
def smooth(x): return x * x * (3 - 2 * x)

def env(t, a, b, fi=0.4, fo=0.4, ease=e_io3):
    """1 dentro de [a,b], com entrada e saída suaves."""
    if t < a or t > b:
        return 0.0
    v = 1.0
    if fi > 0: v = min(v, ease(prog(t, a, a + fi)))
    if fo > 0: v = min(v, ease(1 - prog(t, b - fo, b)))
    return v

# ---------------------------------------------------------------- tipografia
@functools.lru_cache(None)
def typeface(weight=400, italic=False, family=".AppleSystemUIFont"):
    st = skia.FontStyle(weight, skia.FontStyle.kNormal_Width,
                        skia.FontStyle.kItalic_Slant if italic else skia.FontStyle.kUpright_Slant)
    return skia.FontMgr().matchFamilyStyle(family, st)

_SF = None
@functools.lru_cache(512)
def sf(weight, opsz):
    """SF Pro variável: peso e tamanho óptico de verdade (o nome do sistema ignora o peso)."""
    global _SF
    if _SF is None:
        _SF = skia.Typeface.MakeFromFile("/System/Library/Fonts/SFNS.ttf")
    C = skia.FontArguments.VariationPosition.Coordinate
    tag = lambda s: (ord(s[0]) << 24) | (ord(s[1]) << 16) | (ord(s[2]) << 8) | ord(s[3])
    coords = skia.FontArguments.VariationPosition.Coordinates([C(tag("wght"), float(weight)), C(tag("opsz"), float(opsz))])
    args = skia.FontArguments()
    args.setVariationDesignPosition(skia.FontArguments.VariationPosition(coords))
    return _SF.makeClone(args)

@functools.lru_cache(4096)
def font(size, weight=400, family=".AppleSystemUIFont"):
    if family == ".AppleSystemUIFont":
        tf = sf(int(weight), int(clamp(size, 17, 96)))
    else:
        tf = typeface(weight, False, family)
    f = skia.Font(tf, size)
    f.setSubpixel(True)
    f.setEdging(skia.Font.Edging.kSubpixelAntiAlias)
    f.setHinting(skia.FontHinting.kNone)
    return f

def text_width(s, size, weight=400, tracking=0.0, family=".AppleSystemUIFont"):
    f = font(size, weight, family)
    return f.measureText(s) + tracking * size * max(0, len(s) - 1)

def paint(color="#ffffff", alpha=1.0, blur=0.0, aa=True, style=None, stroke=1.0):
    c = rgb(color) if isinstance(color, str) else color
    p = skia.Paint(Color4f=skia.Color4f(c.fR, c.fG, c.fB, c.fA * clamp(alpha)), AntiAlias=aa)
    if blur > 0.05:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    if style == "stroke":
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
        p.setStrokeCap(skia.Paint.kRound_Cap)
        p.setStrokeJoin(skia.Paint.kRound_Join)
    return p

def text(c, s, x, y, size, weight=400, color=INK, alpha=1.0, align="left", tracking=0.0,
         blur=0.0, family=".AppleSystemUIFont"):
    """y é a linha de base."""
    if alpha <= 0.002:
        return
    f = font(size, weight, family)
    w = text_width(s, size, weight, tracking, family)
    if align == "center": x -= w / 2
    elif align == "right": x -= w
    p = paint(color, alpha, blur)
    if tracking == 0:
        c.drawString(s, x, y, f, p)
    else:
        for ch in s:
            c.drawString(ch, x, y, f, p)
            x += f.measureText(ch) + tracking * size

def kinetic(c, s, x, y, size, t, weight=700, color=INK, align="center", tracking=-0.01,
            stagger=0.035, dur=0.7, rise=0.35, out_t=None, out_dur=0.45, blur_in=10.0,
            family=".AppleSystemUIFont", alpha=1.0, by="char"):
    """Revelação por caractere (ou palavra): sobe, desfoca e acende; sai do mesmo jeito, invertido."""
    if t < 0:
        return
    f = font(size, weight, family)
    units = list(s) if by == "char" else [w + (" " if i < len(s.split(" ")) - 1 else "") for i, w in enumerate(s.split(" "))]
    total = text_width(s, size, weight, tracking, family)
    x0 = x - total / 2 if align == "center" else (x - total if align == "right" else x)
    n = len(units)
    cx = x0
    for i, u in enumerate(units):
        uw = f.measureText(u) + tracking * size * len(u)
        k = e_outexpo(prog(t, i * stagger, i * stagger + dur))
        a = k
        dy = (1 - k) * size * rise
        bl = (1 - k) * blur_in
        if out_t is not None and t > out_t:
            j = (n - 1 - i) * stagger * 0.5
            ko = e_in3(prog(t, out_t + j, out_t + j + out_dur))
            a *= 1 - ko
            dy -= ko * size * rise * 0.6
            bl += ko * blur_in
        if a > 0.002 and u.strip():
            p = paint(color, a * alpha, bl)
            if tracking == 0:
                c.drawString(u, cx, y + dy, f, p)
            else:
                xx = cx
                for ch in u:
                    c.drawString(ch, xx, y + dy, f, p)
                    xx += f.measureText(ch) + tracking * size
        cx += uw

def mask_wipe_text(c, s, x, y, size, t, weight=800, color=INK, align="center", dur=0.6,
                   tracking=-0.02, out_t=None, out_dur=0.4):
    """Texto que nasce de uma fenda: recorte horizontal que sobe."""
    if t < 0: return
    k = e_outexpo(prog(t, 0, dur))
    ko = e_in3(prog(t, out_t, out_t + out_dur)) if out_t is not None else 0
    w = text_width(s, size, weight, tracking)
    x0 = x - w / 2 if align == "center" else (x - w if align == "right" else x)
    asc = size * 0.95
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(x0 - size, y - asc - 4, x0 + w + size, y + size * 0.3))
    text(c, s, x0, y + (1 - k) * size * 1.1 - ko * size * 1.1, size, weight, color, 1.0, "left", tracking)
    c.restore()

# ---------------------------------------------------------------- imagens
@functools.lru_cache(64)
def image(name):
    p = name if os.path.isabs(name) else os.path.join(CAP, name)
    img = skia.Image.open(p)
    return img.withDefaultMipmaps()

@functools.lru_cache(64)
def boxes(name):
    p = os.path.join(CAP, name.rsplit(".", 1)[0] + ".json")
    return json.load(open(p)) if os.path.exists(p) else {}

SAMP = skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear)

def quad_matrix(src, dst):
    """src: Rect; dst: 4 pontos (tl, tr, br, bl)."""
    m = skia.Matrix()
    s = [skia.Point(src.left(), src.top()), skia.Point(src.right(), src.top()),
         skia.Point(src.right(), src.bottom()), skia.Point(src.left(), src.bottom())]
    m.setPolyToPoly(s, [skia.Point(*p) for p in dst])
    return m

def project(cx, cy, w, h, rx=0, ry=0, rz=0, tz=0, focal=2200, ox=None, oy=None):
    """Retângulo w×h centrado em (cx,cy), girado em 3D e projetado. Retorna 4 cantos."""
    pts = [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]
    rx, ry, rz = math.radians(rx), math.radians(ry), math.radians(rz)
    out = []
    for x, y in pts:
        z = 0.0
        # rz
        x, y = x * math.cos(rz) - y * math.sin(rz), x * math.sin(rz) + y * math.cos(rz)
        # rx (inclina para trás)
        y, z = y * math.cos(rx) - z * math.sin(rx), y * math.sin(rx) + z * math.cos(rx)
        # ry
        x, z = x * math.cos(ry) + z * math.sin(ry), -x * math.sin(ry) + z * math.cos(ry)
        z += tz
        s = focal / (focal + z)
        out.append((cx + x * s, cy + y * s))
    return out

def card(c, img, src=None, dst=None, quad=None, radius=18, alpha=1.0, shadow=0.55,
         border=0.10, glow=0.0, glow_color=GREEN):
    """Desenha um recorte de screenshot como cartão. dst = Rect, ou quad = 4 pontos."""
    if alpha <= 0.002: return
    if isinstance(img, str): img = image(img)
    if src is None: src = skia.Rect.MakeWH(img.width(), img.height())
    if quad is None:
        quad = [(dst.left(), dst.top()), (dst.right(), dst.top()), (dst.right(), dst.bottom()), (dst.left(), dst.bottom())]
    m = quad_matrix(skia.Rect.MakeWH(src.width(), src.height()), quad)
    rr = skia.RRect.MakeRectXY(skia.Rect.MakeWH(src.width(), src.height()), radius * src.width() / max(1, _qw(quad)), radius * src.width() / max(1, _qw(quad)))
    c.save()
    c.concat(m)
    sc = src.width() / max(1, _qw(quad))
    if shadow > 0:
        c.drawRRect(rr.makeOffset(0, 26 * sc), paint("#000000", shadow * alpha, 40 * sc))
    if glow > 0:
        c.drawRRect(rr, paint(glow_color, glow * alpha, 60 * sc))
    c.save()
    c.clipRRect(rr, True)
    p = skia.Paint(AntiAlias=True)
    p.setAlphaf(clamp(alpha))
    c.drawImageRect(img, src, skia.Rect.MakeWH(src.width(), src.height()), SAMP, p)
    c.restore()
    if border > 0:
        c.drawRRect(rr, paint("#ffffff", border * alpha, style="stroke", stroke=1.5 * sc))
    c.restore()

def _qw(q):
    return math.hypot(q[1][0] - q[0][0], q[1][1] - q[0][1])

def rect(x, y, w, h):
    return skia.Rect.MakeXYWH(x, y, w, h)

def rrect(c, x, y, w, h, r, color, alpha=1.0, style=None, stroke=1.0, blur=0):
    c.drawRRect(skia.RRect.MakeRectXY(rect(x, y, w, h), r, r), paint(color, alpha, blur, style=style, stroke=stroke))

# ---------------------------------------------------------------- fundo e acabamento
_noise = None
def grain(i):
    global _noise
    if _noise is None:
        rng = np.random.default_rng(7)
        _noise = []
        for _ in range(12):
            n = rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32)
            _noise.append(n)
    return _noise[i % 12]

def background(c, t, hue=0.0, intensity=1.0, grid=0.0, cam=(0, 0)):
    c.clear(rgb(BG0))
    # luz difusa que respira
    for (x, y, r, col, a) in [(0.25 + 0.05 * math.sin(t * 0.3), 0.3, 900, GREEN_D, 0.55),
                              (0.85, 0.85 + 0.04 * math.cos(t * 0.25), 1000, "#0c3a2a", 0.5)]:
        sh = skia.GradientShader.MakeRadial(skia.Point(x * W, y * H), r,
                                            [rgb(col, a * intensity), rgb(col, 0)])
        c.drawRect(rect(0, 0, W, H), skia.Paint(Shader=sh))
    if grid > 0:
        p = paint("#ffffff", 0.035 * grid, style="stroke", stroke=1)
        step = 80
        ox, oy = cam[0] % step, cam[1] % step
        for x in range(-step, W + step, step):
            c.drawLine(x + ox, 0, x + ox, H, p)
        for y in range(-step, H + step, step):
            c.drawLine(0, y + oy, W, y + oy, p)

def finish(arr, i, vignette=0.55, grain_amt=5.0):
    """arr: HxWx4 uint8 RGBA. Vinheta e grão leves, em float."""
    f = arr[..., :3].astype(np.float32)
    if vignette > 0:
        f *= _vig(vignette)[..., None]
    if grain_amt > 0:
        g = grain(i)
        g = np.repeat(np.repeat(g, 2, 0), 2, 1)
        f += g[..., None] * grain_amt
    np.clip(f, 0, 255, out=f)
    arr[..., :3] = f.astype(np.uint8)
    return arr

@functools.lru_cache(4)
def _vig(strength):
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((x - W / 2) / (W / 2)) ** 2 + ((y - H / 2) / (H / 2)) ** 2) / math.sqrt(2)
    return (1 - strength * np.clip(d - 0.35, 0, 1) ** 1.6).astype(np.float32)

# ---------------------------------------------------------------- render
def surface():
    return skia.Surface.MakeRaster(skia.ImageInfo.Make(W, H, skia.kRGBA_8888_ColorType, skia.kPremul_AlphaType))

def render_scene(draw, duration, out, mb=None, start_index=0, preview=None, crf=14):
    """draw(canvas, t) pinta o quadro no instante t (segundos locais).
    mb(t) -> número de subquadros de desfoque de movimento (1 = nenhum)."""
    n = int(round(duration * FPS))
    frames = range(n) if preview is None else preview
    if preview is not None:
        os.makedirs(out, exist_ok=True)
    else:
        ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba",
                               "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                               "-crf", str(crf), "-pix_fmt", "yuv420p", "-tune", "film", out], stdin=subprocess.PIPE)
    s = surface()
    for k in frames:
        t = k / FPS
        sub = mb(t) if mb else 1
        if sub <= 1:
            c = s.getCanvas()
            draw(c, t)
            arr = s.toarray(colorType=skia.kRGBA_8888_ColorType).copy()
        else:
            acc = None
            for j in range(sub):
                tt = t + (j / sub - 0.5) * (0.5 / FPS)   # obturador de 180°
                c = s.getCanvas()
                draw(c, tt)
                a = s.toarray(colorType=skia.kRGBA_8888_ColorType).astype(np.float32)
                acc = a if acc is None else acc + a
            arr = (acc / sub).astype(np.uint8)
        arr = finish(arr, start_index + k)
        if preview is not None:
            skia.Image.fromarray(arr, colorType=skia.kRGBA_8888_ColorType).save(os.path.join(out, f"f{k:05d}.png"))
        else:
            ff.stdin.write(arr.tobytes())
    if preview is None:
        ff.stdin.close()
        ff.wait()
