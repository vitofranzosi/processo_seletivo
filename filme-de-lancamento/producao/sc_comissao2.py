"""Da comissão ao resultado — versão para o público geral (11 compassos, 20,6 s; tempo local u).

Três ideias, uma tela cada: a comissão avalia (a Mesa, com os documentos de cada pessoa), o sistema
classifica pelas regras do Edital (o resultado público), quem discorda recorre pela internet (o
formulário do candidato). Distribuição, consolidação, corte, ocupação e o rito do recurso saíram:
existem no sistema, mas não são assunto para quem não opera seleções."""
from kit import *
import sc_comissao as C

DUR = 20.625
ZONE = ZONE_BOTTOM

AV_CROP = (0, 360, 2140, 930)
RES_CROP = (0, 100, 2880, 1250)
RES_TABLE = dom("p_resultado51", "POSIÇÃO CANDIDATO", "table")
REC_FORM = (0, 120, 1150, 1260)
REC_ZONE = (930, 60, 1860, 1010)

def draw(c, u):
    T = u + 150.0
    background(c, T, grid=0.3, cam=(0, T * 10))
    # A. a planilha avulsa vira a Mesa da comissão (o mesmo gesto da versão anterior, mais devagar)
    if u < 8.4:
        k_in = e_out3(prog(u, 0.1, 0.8))
        morph = prog(u, 2.3, 3.4)
        mesa_a = e_out3(prog(u, 2.8, 3.4))
        e = e_in3(prog(u, 5.4, 6.0))
        pose = moved(frame_in(C.MESA_CROP, (380, 60, 1840, 800)), dx=-1700 * e, alpha=1 - e)
        cd = Card(C.MESA, C.MESA_CROP, pose)
        if mesa_a > 0:
            cd.frame(c, mesa_a * pose.alpha, glow=0.2)
            cd.region(c, (0, 205, 1520, 701), alpha=mesa_a * pose.alpha)
            cd.region(c, (0, 1301, 1520, 39), alpha=mesa_a * pose.alpha)
            cd.region(c, (1456, 906, 64, 395), alpha=mesa_a * pose.alpha)
            cd.border(c, mesa_a * pose.alpha)
        if morph < 1:
            C.draw_sheet(c, T, k_in * (1 - e_in3(prog(morph, 0, 0.6))))
        rows, _ = C.sheet_rows(T)
        for i, r in enumerate(rows):
            ki = e_ioexpo(clamp(morph * 1.5 - i * 0.1))
            tl = cd.to_screen(C.MESA_ROWS[i][0], C.MESA_ROWS[i][1]); br = cd.to_screen(C.MESA_ROWS[i][0] + C.MESA_ROWS[i][2], C.MESA_ROWS[i][1] + C.MESA_ROWS[i][3])
            x = lerp(r[0], tl[0], ki); y = lerp(r[1], tl[1], ki); w = lerp(r[2], br[0] - tl[0], ki); h = lerp(r[3], br[1] - tl[1], ki)
            m = smooth(prog(ki, 0.35, 0.85))
            if m < 1:
                C.draw_sheet_row(c, (x, y, w, h), i, k_in * (1 - m), T)
            if m > 0:
                card(c, C.MESA, skia.Rect.MakeXYWH(*C.MESA_ROWS[i]), dst=rect(x, y, w, h), radius=2, alpha=m * pose.alpha, shadow=0.25 * (1 - ki), border=0)
        # um clique na primeira inscrição abre a avaliação, com os documentos
        p1 = cd.to_screen(48 + 300, 906 + 39)
        cursor(c, *path_at(u, [(3.6, (1500, 760)), (4.6, p1), (5.3, p1)]), alpha=env(u, 3.6, 5.6, 0.3, 0.2),
               press=env(u, 5.0, 5.15, 0.03, 0.08))
        ripple(c, *p1, prog(u, 5.05, 5.65))
    caption_block(c, u, 0.2, 2.3, "Da comissão", None, 150, 470, 80, tag_s="03 · Avaliação")
    kinetic(c, "ao resultado.", 150, 565, 80, u - 0.45, weight=780, align="left", out_t=2.3 - 0.45, color=MINT)
    if 5.4 < u < 8.6:
        kin = e_out5(prog(u, 5.4, 6.1)); kout = e_in3(prog(u, 8.0, 8.6))
        av = Card("g_avaliacao_docs.png", AV_CROP, moved(frame_in(AV_CROP, ZONE), dx=1300 * (1 - kin), dy=-1150 * kout)).draw(c, 1, glow=0.2)
        av.focus(c, C.AV_DOCS, prog(u, 6.2, 6.6) * (1 - kout), pad=8, color=MINT)
        kd = e_outback(prog(u, 6.4, 7.0), 1.1) * (1 - prog(u, 7.6, 8.0))
        if kd > 0.01:
            Card("pdf_docident_01.png", (0, 0, 1190, 1684), Pose(1540, 420, 380 * kd + 1, 0, 0, 5, 0, 1)).draw(c, clamp(kd), radius=4)
    cap(c, u, 3.0, 8.1, "A comissão avalia.", "Cada avaliador vê as inscrições e os documentos de cada pessoa, num só lugar.")
    # B. o resultado público
    if 8.2 < u < 14.4:
        kin = e_out5(prog(u, 8.2, 8.9)); kout = e_in3(prog(u, 13.8, 14.4))
        r = Card("p_resultado51.png", RES_CROP, moved(frame_in(RES_CROP, ZONE), dx=1300 * (1 - kin), dy=-1150 * kout)).draw(c, 1, glow=0.2)
        r.focus(c, RES_TABLE, prog(u, 9.3, 9.8) * (1 - kout), pad=10, color=MINT)
    cap(c, u, 8.7, 13.9, "O sistema classifica.", "Pelas regras do Edital — e o resultado é publicado, igual para todos.")
    # C. quem discorda, recorre
    if u > 14.2:
        kin = e_out5(prog(u, 14.2, 14.9)); kout = e_in3(prog(u, 19.9, DUR))
        a = Card("p_elisa_recorrer_ok.png", REC_FORM, moved(frame_in(REC_FORM, REC_ZONE), dx=1100 * (1 - kin), dy=-1150 * kout)).draw(c, 1, glow=0.15)
        a.focus(c, (48, 575, 1004, 440), prog(u, 15.4, 15.9) * (1 - kout), pad=8, color=MINT)
        a.focus(c, (48, 1178, 330, 92), prog(u, 16.6, 17.0) * (1 - kout), pad=8)
    caption_block(c, u, 14.5, 19.8, "Quem discorda,", None, 146, 520, 76, tag_s="Recurso")
    kinetic(c, "pode recorrer.", 146, 610, 76, u - 14.8, weight=780, align="left", out_t=19.8 - 14.8, color=MINT)
    kinetic(c, "Pela internet — e cada recurso", 150, 680, 30, u - 15.3, weight=480, align="left", color=MUTED,
            out_t=19.8 - 15.3, stagger=0.01, rise=0.3, blur_in=4)
    kinetic(c, "é respondido e fica registrado.", 150, 722, 30, u - 15.4, weight=480, align="left", color=MUTED,
            out_t=19.8 - 15.4, stagger=0.01, rise=0.3, blur_in=4)
