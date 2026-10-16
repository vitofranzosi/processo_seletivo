"""Você preenche, o sistema escreve o Edital (8 compassos, 15 s; tempo local u).

O formulário da composição do Edital 02/2026 em cima, o PDF que o sistema gerou dele embaixo
(o mesmo Edital publicado depois, na cena seguinte). Cada linha preenchida "escreve" a linha
correspondente no documento: as linhas do PDF começam cobertas e se revelam quando o dado chega.
Coordenadas do formulário: DOM (dom.json); do PDF: pdftotext -bbox, página renderizada a 6×."""
from kit import *
import sc_edital as E
from timeline import b

DUR = 15.0
PDF2 = "pdfhi_edital02_02.png"
PDF1 = "pdfhi_edital02_01.png"
PW, PH = 3570, 5052
TOP = (70, 40, 1850, 395)
BOT = (70, 425, 1850, 800)

# par 1: a tabela de Perfis do formulário → Tabela 1 do Edital
F1_IMG, F1_CROP = "c02_perfis.png", (40, 1250, 2600, 360)
F1_ROWS = [dom("c02_perfis", "DOC-INFO Professor", "tr"), dom("c02_perfis", "TEC-LAB Técnico", "tr")]
P1_CROP = (330, 470, 2810, 410)
P1_ROWS = [(336, 685, 2800, 74), (336, 786, 2800, 74)]
# par 2: o primeiro evento do Cronograma → Tabela 5
F2_IMG, F2_CROP = "c02_cronograma.png", (40, 1320, 2800, 450)
F2_ROWS = [dom("c02_cronograma", "EVENTO DO CRONOGRAMA 1 DE 3", "fieldset")]
P2_CROP = (330, 2320, 2900, 700)
P2_ROWS = [(336, 2526, 2890, 166), (336, 2718, 2890, 166), (336, 2910, 2890, 74)]

HERO = Pose(1400, 680, 820)

def write_rows(c, cd, rows, ks):
    """Cobre as linhas do PDF ainda não 'escritas'; a cobertura recua da esquerda para a direita."""
    for (x, y, w, h), k in zip(rows, ks):
        if k >= 1: continue
        a = cd.to_screen(x + w * e_io3(k), y - 6); z = cd.to_screen(x + w, y + h + 6)
        c.drawRect(skia.Rect.MakeLTRB(a[0], a[1], z[0], z[1]), paint("#ffffff", 1.0))
        if 0 < k < 1:  # a "caneta": um traço verde na frente da escrita
            c.drawRect(skia.Rect.MakeLTRB(a[0] - 3, a[1], a[0] + 3, z[1]), paint(GREEN, 0.9))

def link(c, fcd, fbox, pcd, pbox, k, alpha=1.0):
    if k <= 0: return
    fx, fy, fw, fh = fbox; px, py, pw, ph = pbox
    p0 = fcd.to_screen(fx + 40, fy + fh / 2); p0 = (p0[0] - 18, p0[1])
    p3 = pcd.to_screen(px, py + ph / 2); p3 = (p3[0] - 18, p3[1])
    xm = max(26, min(p0[0], p3[0]) - 44)
    bezier(c, p0, (xm, p0[1]), (xm, p3[1]), p3, GREEN, 0.95 * alpha, 3.5, k=e_out3(k))
    glow_dot(c, *p0, 6, GREEN, alpha)
    if k >= 1: glow_dot(c, *p3, 6, GREEN, alpha)

def pair(c, u, t0, t1, fimg, fcrop, frows, pimg, pcrop, prows):
    if u < t0 or u > t1: return
    kin = e_out5(prog(u, t0, t0 + 0.6)); kout = e_in3(prog(u, t1 - 0.45, t1))
    fcd = Card(fimg, fcrop, moved(frame_in(fcrop, TOP), dx=-1500 * (1 - kin), dy=-900 * kout)).draw(c, 1, glow=0.15)
    pcd = Card(pimg, pcrop, moved(frame_in(pcrop, BOT), dx=1500 * (1 - kin), dy=-900 * kout)).draw(c, 1, glow=0.15, radius=6)
    n = max(len(frows), len(prows))
    ks = []
    for i in range(len(prows)):
        a = t0 + 1.0 + i * 0.9
        ks.append(prog(u, a + 0.35, a + 0.95))
    write_rows(c, pcd, prows, ks)
    for i in range(len(prows)):
        a = t0 + 1.0 + i * 0.9
        fb = frows[min(i, len(frows) - 1)]
        fcd.focus(c, fb, prog(u, a - 0.1, a + 0.25) * (1 - prog(u, a + 1.2, a + 1.5)) * (1 - kout), pad=6, color=MINT)
        link(c, fcd, fb, pcd, prows[i], prog(u, a, a + 0.4) * (1 - prog(u, a + 1.2, a + 1.5)), 1 - kout)
    # rótulos: o que é formulário, o que é documento
    tag(c, "O que a equipe preenche", 74, 32, env(u, t0 + 0.3, t1 - 0.2, 0.3, 0.3), size=16)
    pq = pcd.quad
    tag(c, "O Edital que o sistema gera", 74, pq[0][1] - 10, env(u, t0 + 0.3, t1 - 0.2, 0.3, 0.3), size=16)

def draw(c, u):
    T = u + 75.75
    background(c, T, grid=0.35, cam=(T * 12, 0))
    # a composição, como a cena anterior a deixou, sai de cena
    if u < 0.7:
        E.draw_comp(c, b(40.4), alpha=1 - e_in3(prog(u, 0.0, 0.6)))
    pair(c, u, 0.4, 6.6, F1_IMG, F1_CROP, F1_ROWS, PDF2, P1_CROP, P1_ROWS)
    pair(c, u, 6.6, 11.6, F2_IMG, F2_CROP, F2_ROWS, PDF2, P2_CROP, P2_ROWS)
    # o documento inteiro aparece: a página 1, na pose em que a cena de linguagem simples começa
    if u > 11.4:
        k = e_out5(prog(u, 11.4, 12.4))
        p = Pose(HERO.cx + 500 * (1 - k), HERO.cy + 200 * (1 - k), HERO.w * (0.8 + 0.2 * k), 0, 0, 0, 0, k)
        Card(PDF1, (0, 0, PW, PH), p).draw(c, k, radius=4, border=0.0)
    cap(c, u, 0.7, 6.3, "Você preenche.", "Vagas, requisitos, datas e etapas — num formulário, uma vez só.", tag_s="Montar o Edital")
    cap(c, u, 6.9, 11.3, "O sistema escreve o Edital.", "Cada informação vai para o documento oficial, automaticamente.")
    caption_block(c, u, 11.7, 14.8, "Edital pronto.", "Gerado pelo sistema, sem redigitar nada.", 150, 560, 84, wrap=560,
                  tag_s="Documento oficial")
