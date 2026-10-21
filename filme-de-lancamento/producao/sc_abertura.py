"""I. A complexidade invisível  +  II. Transformação  (0:00 – 0:56.25)"""
from kit import *
from timeline import *

WORDS = ["Bolsistas", "Vagas remanescentes", "Pós-graduação", "Cursos FIC", "Outras seleções"]
WORD_POS = [(430, 330), (1430, 300), (560, 800), (1380, 820), (960, 560)]

KINDS = ["form", "sheet", "pdf", "mail", "folder", "check", "calendar", "msg"]
BASE = [(560, 400), (1010, 330), (1420, 430), (720, 730), (1250, 760), (360, 650), (1600, 690), (980, 590)]
SPAWN = [b(8 + i) for i in range(8)]                 # um por compasso, de 0:15 a 0:28
ICON_W, ICON_H = 170, 210

LINKS = [(0, 1, 16.0), (1, 2, 19.1), (3, 2, 21.2), (4, 2, 22.2), (7, 2, 23.1), (1, 5, 25.3), (5, 6, 28.4),
         (6, 0, 31.0), (3, 7, 26.3), (4, 5, 27.2), (7, 1, 29.4), (2, 6, 30.1), (0, 4, 32.0), (5, 3, 32.5)]
CAPTIONS = [(16.0, "Um formulário se conecta a uma planilha."), (19.1, "A planilha depende de documentos."),
            (22.2, "Documentos chegam por diferentes canais."), (25.3, "Resultados precisam ser consolidados."),
            (28.4, "Recursos precisam ser analisados."), (31.0, "Convocações precisam ser acompanhadas.")]

# a Visão Geral com o visual da gestão de 18/10 (barra lateral GPS), capturada na janela de 1440 × 810;
# os alvos dos ícones foram medidos no DOM dessa captura (cap/g_visao_gps.json). A barra lateral, que
# antes não existia, recebe o ícone da mensagem, que ia para a faixa verde do topo
VIS = "g_visao_gps.png"
VIS_CROP = (0, 0, 2880, 1620)
S = 1920 / 2880
TARGETS = {  # px da captura
    "form": (560, 341, 2272, 314), "sheet": (560, 992, 2272, 628), "pdf": (560, 695, 544, 258),
    "mail": (1136, 695, 544, 258), "folder": (1712, 695, 544, 258), "check": (2288, 695, 544, 258),
    "calendar": (560, 160, 1500, 133), "msg": (0, 0, 512, 1620),
}

# duplicatas ao fundo (profundidade), a cada batida entre os compassos 13 e 18
DUPS = []
for j in range(22):
    ts = b(13) + j * BEAT * 0.9
    DUPS.append(dict(t=ts, kind=KINDS[j % 8], x=120 + hash01(j, 1) * 1680, y=120 + hash01(j, 2) * 840,
                     s=0.35 + 0.35 * hash01(j, 3), rz=-20 + 40 * hash01(j, 4), blur=2 + 6 * hash01(j, 5)))

def chaos(t):
    """Amplitude do tremor: cresce até o congelamento."""
    return 0.0 if t < b(12) else e_in3(prog(t, b(12), FREEZE))

def icon_state(i, T):
    """Centro, escala, rotação do ícone i no instante T (antes da reorganização)."""
    t = min(T, FREEZE)
    bx, by = BASE[i]
    x = bx + 34 * math.sin(t * 0.45 + i * 1.7) + chaos(t) * 26 * math.sin(t * 9.3 + i * 4.1)
    y = by + 22 * math.cos(t * 0.38 + i * 1.3) + chaos(t) * 20 * math.cos(t * 8.1 + i * 2.3)
    rz = 7 * math.sin(t * 0.3 + i) + chaos(t) * 5 * math.sin(t * 7 + i)
    k = e_outback(prog(t, SPAWN[i], SPAWN[i] + 0.55), 1.2)
    return x, y, k, rz

# a câmera do ato I termina aproximada em 4% (z de draw); a tela real e os alvos dos ícones desfazem essa
# aproximação, para a Visão Geral caber inteira no quadro — a barra lateral fica na borda e era cortada
ZF = 1 / 1.04
def unzoom(x, y, w, h):
    return (W / 2 + (x - W / 2) * ZF, H / 2 + (y - H / 2) * ZF, w * ZF, h * ZF)

def target_rect(kind):
    x, y, w, h = TARGETS[kind]
    return unzoom(x * S, y * S, w * S, h * S)

def organize_k(i, T):
    st = b(22) + 0.35 + i * BEAT * 0.5
    return e_io3(prog(T, st, st + 2.2))

def draw_icons(c, T, gray=0.0):
    # ligações
    for (a, bb, tl) in LINKS:
        if T < tl: continue
        ka = icon_state(a, T); kb = icon_state(bb, T)
        oa, ob = organize_k(a, T), organize_k(bb, T)
        org = min(oa, ob)
        if org >= 0.999: continue
        def ctr(i, st, ok):
            x, y, _, _ = st
            if ok > 0:
                tx, ty, tw, th = target_rect(KINDS[i])
                x, y = lerp(x, tx + tw / 2, ok), lerp(y, ty + th / 2, ok)
            return x, y
        p0, p3 = ctr(a, ka, oa), ctr(bb, kb, ob)
        t = min(T, FREEZE)
        bend = (1 - org) * (140 + 60 * math.sin(t * 0.7 + a + bb))
        dx, dy = p3[0] - p0[0], p3[1] - p0[1]
        L = math.hypot(dx, dy) + 1e-6
        nx, ny = -dy / L, dx / L
        p1 = (p0[0] + dx * 0.3 + nx * bend, p0[1] + dy * 0.3 + ny * bend)
        p2 = (p0[0] + dx * 0.7 - nx * bend * 0.8, p0[1] + dy * 0.7 - ny * bend * 0.8)
        k = e_out3(prog(T, tl, tl + 0.6))
        col = lerp_col(RED, GREEN, org)
        if gray > 0:
            col = lerp_col("#e0463c" if org < 0.5 else GREEN, "#9a9a9a", gray)
        bezier(c, p0, p1, p2, p3, col, 0.75 * (1 - e_in3(prog(org, 0.7, 1))), 2.4, dash=[14, 9],
               phase=-min(T, FREEZE) * 60, k=k)
        if k >= 1:
            glow_dot(c, *p3, 4, col, 0.8 * (1 - org))
    # ícones
    for i, kind in enumerate(KINDS):
        if T < SPAWN[i]: continue
        x, y, k, rz = icon_state(i, T)
        if k <= 0.001: continue
        ok = organize_k(i, T)
        w, h = ICON_W * k, ICON_H * k
        if ok <= 0:
            c.save(); c.translate(x, y); c.rotate(rz)
            icon(c, kind, -w / 2, -h / 2, w, h, alpha=clamp(k * 1.5), color_amt=1 - gray)
            if T > 24 and i in (0, 1, 2, 3, 5, 7):
                n = 1 + int((min(T, FREEZE) - 24) / BEAT * (0.4 + 0.15 * i)) % 37
                badge(c, w / 2 - 6, -h / 2 + 6, n, clamp((min(T, FREEZE) - 24 - i * 0.3) * 3))
            c.restore()
        else:
            tx, ty, tw, th = target_rect(kind)
            cx, cy = lerp(x, tx + tw / 2, ok), lerp(y, ty + th / 2, ok)
            ww, hh = lerp(w, tw, ok), lerp(h, th, ok)
            r = rz * (1 - ok)
            m = smooth(prog(ok, 0.45, 0.95))
            c.save(); c.translate(cx, cy); c.rotate(r)
            if m < 1:
                icon(c, kind, -ww / 2, -hh / 2, ww, hh, alpha=1 - m)
            if m > 0:
                sx, sy, sw, sh = TARGETS[kind]
                card(c, VIS, skia.Rect.MakeXYWH(sx, sy, sw, sh), dst=rect(-ww / 2, -hh / 2, ww, hh), radius=8 * (1 - ok) + 1,
                     alpha=m, shadow=0.3 * (1 - ok), border=0.0)
            c.restore()

def draw_dups(c, T, alpha=1.0):
    t = min(T, FREEZE)
    out = prog(T, b(22), b(22) + 1.4)
    for d in DUPS:
        if T < d["t"]: continue
        k = e_out3(prog(T, d["t"], d["t"] + 0.5))
        x = d["x"] + 18 * math.sin(t * 0.6 + d["s"] * 10) + chaos(t) * 14 * math.sin(t * 11 + d["x"])
        y = d["y"] + 14 * math.cos(t * 0.5 + d["s"] * 7)
        if out > 0:  # implode para o centro
            x, y = lerp(x, W / 2, e_in3(out)), lerp(y, H / 2, e_in3(out))
        w, h = ICON_W * d["s"], ICON_H * d["s"]
        c.save(); c.translate(x, y); c.rotate(d["rz"])
        icon(c, d["kind"], -w / 2, -h / 2, w, h, alpha=0.55 * k * alpha * (1 - out), blur=d["blur"])
        c.restore()

def draw_words(c, T):
    # palavra a palavra, depois se multiplicam
    t0 = b(4)
    fade_all = 1 - 0.8 * e_io3(prog(T, b(8), b(9.5)))
    if T > FREEZE: fade_all *= 0.6
    out = prog(T, b(22), b(22) + 1.2)
    fade_all *= 1 - out
    if fade_all <= 0.01: return
    for i, wd in enumerate(WORDS):
        ti = t0 + i * BEAT * 2
        if T < ti: continue
        k = e_outexpo(prog(T, ti, ti + 0.6))
        move = e_io3(prog(T, ti + 0.3, ti + 0.85))
        x, y = lerp(W / 2, WORD_POS[i][0], move), lerp(H / 2 + 30, WORD_POS[i][1], move)
        size = lerp(118, 58, move)
        al = k * fade_all * lerp(1, 0.75, move)
        kinetic(c, wd, x, y, size, T - ti, weight=720, color=INK, align="center", alpha=al * (0.4 + 0.6 * k), stagger=0.025)
    # multiplicação
    t1 = b(6.5)
    for j in range(46):
        tj = t1 + j * BEAT / 4
        if T < tj: continue
        k = e_out3(prog(T, tj, tj + 0.3))
        wd = WORDS[j % 5]
        x = 80 + hash01(j, 11) * 1760; y = 90 + hash01(j, 12) * 930
        # as cópias não passam por cima das cinco palavras principais
        if any(abs(x - px) < 330 and abs(y - py) < 75 for (px, py) in WORD_POS): continue
        size = 18 + 46 * hash01(j, 13) ** 2
        drift = (min(T, FREEZE) - tj) * (8 + 14 * hash01(j, 14))
        a = (0.10 + 0.22 * hash01(j, 15)) * k * fade_all
        text(c, wd, x + drift * (1 if j % 2 else -1), y, size, 600, MUTED if j % 3 else INK, a, "center",
             blur=2.5 * (1 - hash01(j, 16)) if size < 30 else 0)

def draw(c, T):
    gray = e_out3(prog(T, FREEZE, FREEZE + 0.25)) * (1 - e_io3(prog(T, b(22), b(22) + 1.0)))
    background(c, T, intensity=0.55 + 0.45 * prog(T, 0, b(4)) * (1 - 0.6 * gray), grid=0.0)
    if T < b(25.5):
        # câmera: leve tremor e aproximação lenta no ato I
        c.save()
        z = 1 + 0.04 * prog(min(T, FREEZE), 0, FREEZE) + 0.02 * gray
        sh = chaos(min(T, FREEZE)) * 3
        c.translate(W / 2 + sh * math.sin(min(T, FREEZE) * 37), H / 2 + sh * math.cos(min(T, FREEZE) * 29))
        c.scale(z, z)
        c.translate(-W / 2, -H / 2)
        layer = None
        if gray > 0.01:
            m = [0.2126 + 0.7874 * (1 - gray), 0.7152 - 0.7152 * (1 - gray), 0.0722 - 0.0722 * (1 - gray), 0, 0,
                 0.2126 - 0.2126 * (1 - gray), 0.7152 + 0.2848 * (1 - gray), 0.0722 - 0.0722 * (1 - gray), 0, 0,
                 0.2126 - 0.2126 * (1 - gray), 0.7152 - 0.7152 * (1 - gray), 0.0722 + 0.9278 * (1 - gray), 0, 0,
                 0, 0, 0, 1, 0]
            lp = skia.Paint(ColorFilter=skia.ColorFilters.Matrix(m))
            dimk = 1 - 0.75 * e_io3(prog(T, FRASE - 0.4, FRASE + 0.6)) * (1 - e_io3(prog(T, b(22) - 0.4, b(22) + 0.6)))
            lp.setAlphaf(dimk)
            if dimk < 0.99:
                bl = 9 * (1 - dimk) / 0.7
                lp.setImageFilter(skia.ImageFilters.Blur(bl, bl))
            c.saveLayer(None, lp)
            layer = True
        draw_words(c, T)
        draw_dups(c, T)
        # a tela real se forma por baixo dos fragmentos
        full = e_io3(prog(T, b(24.2), b(25)))
        if full > 0:
            card(c, VIS, skia.Rect.MakeXYWH(*VIS_CROP), dst=rect(*unzoom(0, 0, W, H)), radius=0, alpha=full, shadow=0, border=0)
        draw_icons(c, T, gray)
        if layer:
            c.restore()
        c.restore()
    # textos do ato I
    kinetic(c, "Cada processo seletivo tem suas regras.", W / 2, H / 2 + 24, 74, T - 1.0, weight=650,
            out_t=5.3, color=INK, stagger=0.022)
    for (tc, s) in CAPTIONS:
        nxt = [x[0] for x in CAPTIONS if x[0] > tc]
        end = (nxt[0] - 0.85) if nxt else FREEZE - 0.05
        if T >= tc and T < end + 0.8:
            scrim_k = env(T, tc, end + 0.5, 0.3, 0.5)
            scrim(c, 0.55 * scrim_k, "bottom", 0.35)
            kinetic(c, s, W / 2, H - 120, 46, T - tc, weight=620, out_t=end - tc, color=INK, stagger=0.018,
                    out_dur=0.35)
    # o congelamento: um clarão curtíssimo
    fl = env(T, FREEZE, FREEZE + 0.18, 0.0, 0.18)
    if fl > 0:
        c.drawRect(rect(0, 0, W, H), paint("#ffffff", 0.12 * fl))
    kinetic(c, "Mas nenhum deveria precisar", W / 2, H / 2 - 20, 80, T - (FRASE + 0.3), weight=720, out_t=b(22) - 0.5 - (FRASE + 0.3), stagger=0.07, by="word", dur=0.9)
    kinetic(c, "começar do zero.", W / 2, H / 2 + 86, 80, T - (FRASE + 1.6), weight=720, color=MINT, out_t=b(22) - 0.5 - (FRASE + 1.6), stagger=0.09, by="word", dur=1.0)
    if T >= b(25.5):
        draw_title(c, T)

def draw_title(c, T):
    """Recuo da tela real e entrada do nome do sistema, sobre a batida (compasso 26)."""
    back = e_ioexpo(prog(T, b(25.5), DROP + 0.2))
    exitk = e_in3(prog(T, b(29.2), b(30)))
    # fundo com grade surge quando a tela recua
    if back > 0:
        c.save()
        background(c, T, intensity=1.0, grid=back, cam=(T * 40, T * 25))
        pose0 = Pose(W / 2, H / 2, W, 0, 0, 0, 0)
        pose1 = Pose(1450, 560, 880, 10, -28, 2, 0)
        p = pose0.mix(pose1, back)
        p.cx -= exitk * 300; p.tz -= exitk * 900; p.alpha = 1 - exitk
        p.ry += (T - DROP) * 1.2 if T > DROP else 0
        shot(c, VIS, VIS_CROP, p, radius=18 * back, glow=0.35 * back, border=0.12)
        c.restore()
    if T >= DROP - 0.1:
        tt = T - DROP
        fl = env(T, DROP, DROP + 0.5, 0.0, 0.5)
        if fl > 0:
            sh = skia.GradientShader.MakeRadial(skia.Point(W * 0.3, H * 0.5), 900, [rgb(GREEN, 0.45 * fl), rgb(GREEN, 0)])
            c.drawRect(rect(0, 0, W, H), skia.Paint(Shader=sh))
        scrim(c, 0.6, "left", 0.5)
        out = b(29.1) - DROP
        tag(c, "Cefor  |  Ifes", 150, 380, env(T, DROP + 0.3, b(29.4), 0.5, 0.4))
        kinetic(c, "Sistema de", 146, 500, 100, tt, weight=800, align="left", stagger=0.03, out_t=out)
        kinetic(c, "Processo Seletivo", 146, 615, 100, tt - 0.18, weight=800, align="left", color=MINT, stagger=0.03, out_t=out)
        k = e_out3(prog(T, DROP + 0.6, DROP + 1.4)) * (1 - e_in3(prog(T, DROP + out, DROP + out + 0.4)))
        c.drawRect(rect(150, 672, 420 * k, 4), paint(GREEN, k))
        text(c, "Da elaboração do edital à convocação.", 150, 730, 34, 500, MUTED, k)
