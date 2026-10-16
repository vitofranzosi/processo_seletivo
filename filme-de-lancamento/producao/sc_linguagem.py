"""Inserção: o Edital oficial em linguagem simples, de perto (15 s, tempo local u).

Entra e sai exatamente no quadro em que a elaboração mostra a página 1 em destaque (sc_edital,
draw_pdf com hero=1), para a emenda não se ver. A câmera desce pelo próprio documento: resumo,
sumário em perguntas e, rolando, a seção de vagas da página 2. Coordenadas das linhas vêm do
pdftotext -bbox, na página renderizada a 6× (3570×5052)."""
from kit import *

DUR = 15.0
PW, PH = 3570, 5052
GAP = 260                                   # vão entre as páginas empilhadas, em px da página
PAGES = ["pdfhi_edital02_01.png", "pdfhi_edital02_02.png"]   # o Edital 02/2026, gerado na cena anterior
LOW = [f"pdf_edital02_{i:02d}.png" for i in range(1, 5)]

# janelas da câmera (x, y, w, h) no documento empilhado (página 2 começa em PH + GAP)
FULL = (0, 0, PW, PH)
RESUMO = (230, 1450, 3110, 830)
SUMARIO = (230, 2290, 3110, 1200)
VAGAS = (230, PH + GAP + 380, 3110, 1300)
ZONE = (70, 46, 1850, 800)

HERO = Pose(1400, 680, 820)                 # a página 1 como a elaboração a deixa

def screen_of(win, T):
    """Retângulo de tela onde a janela da câmera aparece."""
    if win is FULL:
        h = HERO.w * PH / PW
        return (HERO.cx - HERO.w / 2, HERO.cy - h / 2, HERO.w, h)
    p = frame_in(win, ZONE)
    h = p.w * win[3] / win[2]
    return (p.cx - p.w / 2, p.cy - h / 2, p.w, h)

KEYS = [(0.0, FULL), (0.6, FULL), (1.9, RESUMO), (4.7, RESUMO), (5.5, SUMARIO), (9.0, SUMARIO),
        (10.0, VAGAS), (12.9, VAGAS), (14.2, FULL), (DUR, FULL)]

def camera(u):
    """Interpola janela e retângulo de tela; a escala anda em log, para o zoom não acelerar."""
    for (u0, w0), (u1, w1) in zip(KEYS, KEYS[1:]):
        if u <= u1:
            k = e_io3(prog(u, u0, u1))
            r0, r1 = screen_of(w0, u0), screen_of(w1, u1)
            s0, s1 = r0[2] / w0[2], r1[2] / w1[2]
            s = math.exp(lerp(math.log(s0), math.log(s1), k))
            # o centro da janela e o centro de tela andam juntos
            cx_doc = lerp(w0[0] + w0[2] / 2, w1[0] + w1[2] / 2, k)
            cy_doc = lerp(w0[1] + w0[3] / 2, w1[1] + w1[3] / 2, k)
            cx_scr = lerp(r0[0] + r0[2] / 2, r1[0] + r1[2] / 2, k)
            cy_scr = lerp(r0[1] + r0[3] / 2, r1[1] + r1[3] / 2, k)
            vw = lerp(r0[2], r1[2], k); vh = lerp(r0[3], r1[3], k)
            return s, (cx_doc, cy_doc), (cx_scr, cy_scr), (vw, vh)
    return camera(DUR - 1e-6)

def doc_to_screen(cam, x, y):
    s, (cdx, cdy), (csx, csy), _ = cam
    return (csx + (x - cdx) * s, csy + (y - cdy) * s)

def draw_doc(c, cam, alpha=1.0):
    s, (cdx, cdy), (csx, csy), (vw, vh) = cam
    vx, vy = csx - vw / 2, csy - vh / 2
    rr = skia.RRect.MakeRectXY(rect(vx, vy, vw, vh), 6, 6)
    c.drawRRect(rr.makeOffset(0, 22), paint("#000000", 0.5 * alpha, 36))
    c.save()
    c.clipRRect(rr, True)
    c.drawRect(rect(vx, vy, vw, vh), paint("#2a302d", alpha))      # o vão entre páginas
    for i, img in enumerate(PAGES):
        top = i * (PH + GAP)
        x0, y0 = doc_to_screen(cam, 0, top)
        x1, y1 = doc_to_screen(cam, PW, top + PH)
        if y1 < vy or y0 > vy + vh: continue
        p = skia.Paint(AntiAlias=True); p.setAlphaf(alpha)
        c.drawImageRect(image(img), skia.Rect.MakeWH(PW, PH), skia.Rect.MakeLTRB(x0, y0, x1, y1), SAMP, p)
    c.restore()
    return (vx, vy, vw, vh)

def hl(c, cam, box, k, color=GREEN, pad=24):
    """Marca-texto: faixa translúcida atrás da linha e contorno que se desenha."""
    if k <= 0: return
    x, y, w, h = box
    a = doc_to_screen(cam, x - pad, y - pad); z = doc_to_screen(cam, x + w + pad, y + h + pad)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(a[0], a[1], lerp(a[0], z[0], e_out3(k)), z[1]), 6, 6), paint(color, 0.16 * k))
    focus(c, lambda px, py: (px, py), (a[0], a[1], z[0] - a[0], z[1] - a[1]), k, color=color, pad=0, radius=6)

def back_pages(c, alpha):
    """As três páginas que a elaboração mantém atrás da página 1 (draw_pdf com hero=1)."""
    if alpha <= 0.01: return
    for i in (3, 2, 1):
        ang = (i - 1.5) * 11
        cx = 1400 + (i - 1.5) * 190
        cy = 560 + abs(i - 1.5) * 24
        Card(LOW[i], (0, 0, 1785, 2526), Pose(cx, cy, 420, 0, 0, ang, 0, 0.25 * alpha)).draw(c, 0.25 * alpha, radius=4, border=0.0)

def draw(c, u):
    background(c, u + 88.875, grid=0.35, cam=((u + 88.875) * 12, 0))
    cam = camera(u)
    draw_doc(c, cam)
    # marcações no documento
    hl(c, cam, (384, 1565, 2700, 610), prog(u, 2.1, 2.6) * (1 - prog(u, 4.6, 4.9)))                 # o resumo
    for j, (y, x1) in enumerate([(2478, 3124), (2587, 3234), (3134, 3234)]):                       # perguntas
        a = 5.9 + j * 0.85
        hl(c, cam, (336, y, 1500, 59), prog(u, a, a + 0.4) * (1 - prog(u, 8.9, 9.2)), color=MINT, pad=14)
    hl(c, cam, (336, PH + GAP + 489, 2780, 380), prog(u, 10.4, 10.8) * (1 - prog(u, 12.8, 13.1)), color=MINT)
    # legendas da faixa de baixo
    cap(c, u, 2.0, 4.6, "Resumo em cinco linhas.", "O essencial — vagas, prazos e como será a seleção — logo na primeira página.",
        tag_s="Documento oficial · linguagem simples")
    cap(c, u, 5.6, 8.9, "Um sumário que responde.", "Quem pode se inscrever? Quantas vagas há, e onde? Como recorrer?")
    cap(c, u, 10.1, 12.8, "Escrito para ser entendido.", "O Edital oficial que o sistema gera — o mesmo que é publicado.")
