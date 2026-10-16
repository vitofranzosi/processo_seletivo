"""O que muda na prática — versão para o público geral (8 compassos, 15 s; tempo local u).

Três ideias em vez de sete itens: tudo fica registrado, tudo é público, tudo num só lugar.
Governança, flexibilidade e avisos saíram; o assistente já teve cena própria."""
from kit import *

DUR = 15.0
T1 = 1.9
STEP = (DUR - T1) / 3
ZONE = (900, 110, 1860, 1000)

ITEMS = [
    ("Tudo fica registrado.", "Cada decisão guarda quem fez, quando e por quê.",
     "g_auditoria51.png", (0, 200, 1700, 1250),
     union(dom("g_auditoria51", "prévia de exportação", "p"), dom("g_auditoria51", "Ocupação do marco", "p"))),
    ("Tudo é público.", "Cronograma, documentos e resultados, abertos a qualquer pessoa.",
     "p_edital01.png", (0, 120, 2000, 1150), None),
    ("Tudo num só lugar.", "A gestão vê todas as seleções de uma vez: editais, vagas, inscrições e situação.",
     "g_visao_v2.png", (20, 660, 1430, 860), (48, 687, 1340, 258)),
]

def wrap(s, size, w):
    lines = [""]
    for word in s.split(" "):
        if lines[-1] and text_width(lines[-1] + " " + word, size, 480) > w: lines.append(word)
        else: lines[-1] = (lines[-1] + " " + word).strip()
    return lines

def draw(c, u):
    T = u + 183.75
    background(c, T, grid=0.5, cam=(T * 60, 0))
    tag(c, "05 · Na prática", 150, 470, env(u, 0.0, T1 - 0.2, 0.3, 0.3))
    kinetic(c, "O que muda na prática.", 146, 580, 92, u - 0.1, weight=800, align="left", out_t=T1 - 0.95, stagger=0.02, out_dur=0.3)
    for j, (title, sub, img, crop, fbox) in enumerate(ITEMS):
        t0 = T1 + j * STEP; t1 = t0 + STEP
        if u < t0 - 0.3 or u > t1 + 0.3: continue
        kin = e_outexpo(prog(u, t0 - 0.1, t0 + 0.6)); kout = e_in3(prog(u, t1 - 0.45, t1 + 0.05))
        cd = Card(img, crop, moved(frame_in(crop, ZONE), dx=900 * (1 - kin), dy=-1100 * kout)).draw(c, 1, glow=0.15)
        if fbox:
            cd.focus(c, fbox, prog(u, t0 + 0.8, t0 + 1.2) * (1 - kout), pad=8, color=MINT)
        kinetic(c, title, 146, 540, 74, u - t0, weight=800, align="left", out_t=STEP - 0.55, stagger=0.022, out_dur=0.3)
        for li, ln in enumerate(wrap(sub, 32, 600)):
            kinetic(c, ln, 150, 610 + li * 44, 32, u - t0 - 0.25 - li * 0.06, weight=450, align="left", color=MUTED,
                    out_t=STEP - 0.75, stagger=0.006, rise=0.3, blur_in=4, out_dur=0.3)
    # trilho: três passos
    a = env(u, T1, DUR, 0.4, 0.4)
    for j in range(3):
        on = prog(u, T1 + j * STEP, T1 + j * STEP + 0.3)
        c.drawRRect(skia.RRect.MakeRectXY(rect(150 + j * 54, 980, 40, 5), 2.5, 2.5), paint("#ffffff", 0.18 * a))
        c.drawRRect(skia.RRect.MakeRectXY(rect(150 + j * 54, 980, 40 * on, 5), 2.5, 2.5), paint(GREEN, a))
