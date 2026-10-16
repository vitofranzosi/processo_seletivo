"""Da comissão ao resultado — versão para o público geral (11 compassos, 20,6 s; tempo local u).

Três ideias, uma tela cada: a comissão avalia (a Mesa, com os documentos de cada pessoa), o sistema
classifica pelas regras do Edital (o resultado público), quem discorda recorre pela internet (o
formulário do candidato). Distribuição, consolidação, corte, ocupação e o rito do recurso saíram:
existem no sistema, mas não são assunto para quem não opera seleções."""
from kit import *
import sc_comissao as C

DUR = 28.125
SH = 5.625                                        # o sorteio entra depois do recurso
ZONE = ZONE_BOTTOM

# a avaliação, numa tomada contínua sobre a mesma tela: o diploma aberto no visualizador, a lista com a
# consulta registrada ("1 de 2 abertos", "aberto") e a nota com o parecer
AV = "av_doc_1_aberto.png"
ZONE_R = (790, 60, 1870, 1010)
_AR = (ZONE_R[2] - ZONE_R[0]) / (ZONE_R[3] - ZONE_R[1])
def _win(x, y, w):
    return (x, y, w, w / _AR)
AV_K0 = _win(0, 130, 2310)
AV_K1 = _win(560, 600, 1060)
AV_K2 = _win(1530, 380, 1330)
AV_K3 = _win(1530, 2176 - 1330 / _AR, 1330)
AV_POSE = frame_in(AV_K1, ZONE_R)
AV_BAR = (48, 407, 1463, 117)
AV_PAGE = (655, 665, 820, 1195)
AV_LIDO = union((1559, 682, 1273, 36), (1559, 926, 1273, 183))
AV_NOTA = (1559, 1450, 1273, 330)
STEPS = [("O documento, aberto ao lado.", 5.9, 7.7), ("Cada consulta, registrada.", 7.8, 9.6), ("A nota, com o parecer.", 9.7, 11.6)]
RES_CROP = (0, 100, 2880, 1250)
RES_TABLE = dom("p_resultado51", "POSIÇÃO CANDIDATO", "table")
_SAR = (ZONE_R[2] - ZONE_R[0]) / (ZONE_R[3] - ZONE_R[1])
SORT_K0 = (0, 110, 1250, 1250 / _SAR)              # "Sorteio verificado…" e os primeiros itens
SORT_K1 = (0, 560, 1250, 1250 / _SAR)              # desce até a ordem publicada
SORT_POSE = frame_in(SORT_K0, ZONE_R)
SORT_ITEMS = [("Lista fechada antes do sorteio.", 17.7, (40, 728, 1880, 100)),        # a relação publicada — confere
              ("Números de sorteio público, de fora.", 19.1, (40, 996, 1880, 95)),    # a semente — confere
              ("Qualquer pessoa refaz e confere.", 20.5, (40, 1122, 1880, 105))]       # a ordem publicada — confere
SORT_OK = dom("p_verificar26", "Sorteio verificado", "p")
SORT_CONF = dom("p_verificar26", "A relação publicada", "dl")
REC_FORM = (0, 120, 1150, 1260)
REC_ZONE = (930, 60, 1860, 1010)

def draw(c, u):
    T = u + 150.0
    background(c, T, grid=0.3, cam=(0, T * 10))
    # A. a planilha avulsa vira a Mesa da comissão (o mesmo gesto da versão anterior, mais devagar)
    if u < 5.2:
        k_in = e_out3(prog(u, 0.1, 0.8))
        morph = prog(u, 2.3, 3.4)
        mesa_a = e_out3(prog(u, 2.8, 3.4))
        e = e_in3(prog(u, 4.6, 5.1))
        pose = moved(frame_in(C.MESA_CROP, ZONE_R), dy=-1200 * e, alpha=1 - e)
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
        cursor(c, *path_at(u, [(3.4, (1500, 760)), (4.0, p1), (4.6, p1)]), alpha=env(u, 3.4, 4.8, 0.3, 0.2),
               press=env(u, 4.3, 4.45, 0.03, 0.08))
        ripple(c, *p1, prog(u, 4.35, 4.95))
    caption_block(c, u, 0.2, 2.3, "Da comissão", None, 150, 470, 80, tag_s="03 · Avaliação")
    kinetic(c, "ao resultado.", 150, 565, 80, u - 0.45, weight=780, align="left", out_t=2.3 - 0.45, color=MINT)
    if 4.8 < u < 12.2:
        kin = e_out5(prog(u, 4.8, 5.5)); kout = e_in3(prog(u, 11.6, 12.2))
        crop = cam_at(u, [(5.0, AV_K0), (5.9, AV_K1), (7.6, AV_K1), (8.2, AV_K2), (9.5, AV_K2), (10.1, AV_K3)])
        av = Card(AV, crop, moved(AV_POSE, dx=1200 * (1 - kin), dy=-1200 * kout)).draw(c, 1, glow=0.2)
        av.focus(c, AV_PAGE, prog(u, 6.0, 6.5) * (1 - prog(u, 7.5, 7.8)), pad=10, color=MINT)
        av.focus(c, AV_LIDO, prog(u, 8.3, 8.8) * (1 - prog(u, 9.4, 9.7)), pad=10, color=MINT)
        av.focus(c, AV_NOTA, prog(u, 10.2, 10.7) * (1 - kout), pad=10, color=MINT)
    # legenda na coluna da esquerda: o título fica, e os três passos acendem junto com a câmera
    caption_block(c, u, 3.0, 11.6, "A comissão avalia.", None, 146, 470, 64, tag_s="Mesa de avaliação")
    for i, (s_, a, z) in enumerate(STEPS):
        vis = env(u, 3.4 + i * 0.15, 11.8, 0.4, 0.4)
        on = env(u, a, z, 0.25, 0.25)
        y = 560 + i * 56
        c.drawCircle(160, y - 10, 7, paint(GREEN if on > 0.5 else MUTED, vis * (0.5 + 0.5 * on)))
        text(c, s_, 182, y, 30, 600 if on > 0.5 else 450, INK if on > 0.5 else MUTED, vis * (0.55 + 0.45 * on))
    # B. o resultado público
    if 11.8 < u < 17.0:
        kin = e_out5(prog(u, 11.8, 12.5)); kout = e_in3(prog(u, 16.4, 17.0))
        r = Card("p_resultado51.png", RES_CROP, moved(frame_in(RES_CROP, ZONE), dx=1300 * (1 - kin), dy=-1150 * kout)).draw(c, 1, glow=0.2)
        r.focus(c, RES_TABLE, prog(u, 12.8, 13.3) * (1 - kout), pad=10, color=MINT)
    cap(c, u, 12.3, 16.5, "O sistema classifica.", "Pelas regras do Edital — e o resultado é publicado, igual para todos.")
    # C. quem discorda, recorre — logo depois do resultado da avaliação
    u2 = u
    if u2 > 16.8:
        kin = e_out5(prog(u2, 16.8, 17.5)); kout = e_in3(prog(u2, 21.8, 22.425))
        a = Card("p_elisa_recorrer_ok.png", REC_FORM, moved(frame_in(REC_FORM, REC_ZONE), dx=1100 * (1 - kin), dy=-1150 * kout)).draw(c, 1, glow=0.15)
        # caixas medidas nos pixels da captura (a tela não reabre: o recurso já foi interposto)
        a.focus(c, (38, 574, 1044, 472), prog(u2, 17.8, 18.3) * (1 - kout), pad=10, color=MINT)
        a.focus(c, (48, 1216, 326, 84), prog(u2, 19.0, 19.4) * (1 - kout), pad=8)
    caption_block(c, u2, 17.1, 21.7, "Quem discorda,", None, 146, 520, 76, tag_s="Recurso")
    kinetic(c, "pode recorrer.", 146, 610, 76, u2 - 17.4, weight=780, align="left", out_t=21.7 - 17.4, color=MINT)
    kinetic(c, "Pela internet — e cada recurso", 150, 680, 30, u2 - 17.9, weight=480, align="left", color=MUTED,
            out_t=21.7 - 17.9, stagger=0.01, rise=0.3, blur_in=4)
    kinetic(c, "é respondido e fica registrado.", 150, 722, 30, u2 - 18.0, weight=480, align="left", color=MUTED,
            out_t=21.7 - 18.0, stagger=0.01, rise=0.3, blur_in=4)
    # D. outra forma de classificar: por sorteio. Vem depois do recurso, e não antes: logo após o sorteio, o
    # recurso parecia contestar o sorteio, cuja confiança vem de conferir, não de recorrer. Três garantias em
    # linguagem simples, cada uma acendendo o item "confere" da página pública (linhas medidas nos pixels)
    us = u - SH
    if 16.8 < us < 22.5:
        kin = e_out5(prog(us, 16.8, 17.5)); kout = e_in3(prog(us, 21.85, 22.4))
        crop = cam_at(us, [(17.4, SORT_K0), (19.0, SORT_K1)])
        v = Card("p_verificar26.png", crop, moved(SORT_POSE, dx=1200 * (1 - kin), dy=-1200 * kout)).draw(c, 1, glow=0.2)
        for i, (_, t0, box) in enumerate(SORT_ITEMS):
            v.focus(c, box, prog(us, t0, t0 + 0.4) * (1 - (prog(us, SORT_ITEMS[i + 1][1], SORT_ITEMS[i + 1][1] + 0.3) if i < 2 else kout)),
                    pad=10, color=MINT)
    caption_block(c, us, 17.1, 21.8, "Por sorteio.", None, 146, 470, 64, tag_s="Outra forma de classificar")
    for i, (s_, t0, _) in enumerate(SORT_ITEMS):
        k = e_outback(prog(us, t0, t0 + 0.45), 1.6) * (1 - e_in3(prog(us, 21.8, 22.3)))
        if k <= 0.01: continue
        y = 572 + i * 60
        c.drawCircle(166, y - 11, 16 * k, paint(GREEN, clamp(k)))
        pth = skia.Path(); pth.moveTo(158, y - 11); pth.lineTo(164, y - 4); pth.lineTo(175, y - 18)
        c.drawPath(pth, paint("#ffffff", clamp(k), style="stroke", stroke=3.5))
        kinetic(c, s_, 198, y, 32, us - t0, weight=620, align="left", out_t=21.8 - t0, stagger=0.012, rise=0.3)
