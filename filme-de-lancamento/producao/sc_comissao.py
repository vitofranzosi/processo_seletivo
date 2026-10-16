"""III-c. Da comissão ao resultado (b62 – b78).

Telas planas em repouso, câmera no detalhe: cada tomada recorta a região que se lê, e os destaques
vêm de caixas medidas no DOM (dom.json)."""
from kit import *
from timeline import *

T0 = b(62)
MESA = "g_mesa51_d1.png"
MESA_ROWS = [(48, 906 + i * 79, 1408, 78) for i in range(5)]
MESA_CROP = (0, 205, 1520, 1135)
MESA_ZONE = (420, 70, 1840, 1010)
P_MESA = frame_in(MESA_CROP, MESA_ZONE)

DISTRIB_CHIPS = chips("g_distrib51_d1", ["5 todas", "sem nenhum avaliador", "sem avaliador suficiente", "com avaliação pendente",
                                          "prontas para consolidar", "ainda não consolidáveis", "já consolidadas"])
DISTRIB_CARGA = dom("g_distrib51_d1", "Carga por avaliador", "table")
DISTRIB_CROP = (0, 380, 2000, 880)
RESULT_TABLE = dom("g_result_etapa51_d1", "Resultados da Etapa", "table")
RESULT_CROP = (0, 470, 1900, 860)

AV_DOCS = dom("g_avaliacao_docs", "Documento de identificação com foto", "ul")
AV_SECAO = union(dom("g_avaliacao_docs", "Avaliação", "h2"), dom("g_avaliacao_docs", "8,5", "strong"))
AV_A = (0, 360, 2140, 930)
AV_B = (0, 1100, 2140, 930)

MARCO_TABLE = dom("g_marco51", "Participantes com posição", "table")
MARCO_CROP = (0, 780, 2880, 1250)
CORTE_RESUMO = dom("g_corte51", "Alvo declarado", "ul")
CORTE_TABLE = dom("g_corte51", "Participantes considerados", "table")
CORTE_CROP = (0, 840, 2880, 1080)
OCUP_RESUMO = dom("g_ocupacao51", "Publicadas", "ul")
OCUP_CROP = (0, 205, 1700, 760)

REC_FORM = (0, 320, 1150, 980)
REC_A = (0, 180, 2300, 1000)
REC_B = (0, 990, 2300, 1000)
REC_PECA = dom("g_recurso", "INTERPOSTO POR", "dl")
REC_ADM = union(dom("g_recurso", "Admissibilidade", "h2"), dom("g_recurso", "Não admitir", "button"))

RES_CROP = (0, 100, 2880, 1250)
RES_TABLE = dom("p_resultado51", "POSIÇÃO CANDIDATO", "table")

def sheet_rows(T):
    x0, y0, w = 760, 300, 760
    return [(x0, y0 + 70 + i * 64, w, 56) for i in range(5)], (x0, y0, w, 64)

def draw_sheet(c, T, alpha):
    rows, head = sheet_rows(T)
    x0, y0, w, _ = head
    c.drawRRect(skia.RRect.MakeRectXY(rect(x0 - 20, y0 - 20, w + 40, 70 + 5 * 64 + 40), 14, 14), paint("#000000", 0.4 * alpha, 30))
    c.drawRRect(skia.RRect.MakeRectXY(rect(x0 - 20, y0 - 20, w + 40, 70 + 5 * 64 + 40), 14, 14), paint(PAPER_C, alpha))
    c.drawRect(rect(x0, y0, w, 56), paint("#1f8f4e", alpha * 0.9))
    for j, hname in enumerate(["INSCRIÇÃO", "NOTA 1", "NOTA 2", "MÉDIA", "OBS."]):
        text(c, hname, x0 + 14 + j * w / 5, y0 + 36, 15, 700, "#ffffff", alpha, family="Menlo")

def draw_sheet_row(c, r, i, alpha, T):
    x, y, w, h = r
    c.drawRect(rect(x, y, w, h), paint("#ffffff", alpha))
    p = paint(LINE_C, alpha * 0.25, style="stroke", stroke=1)
    c.drawRect(rect(x, y, w, h), p)
    for j in range(1, 5):
        c.drawLine(x + j * w / 5, y, x + j * w / 5, y + h, p)
    vals = [f"#{1023 + i * 7}", "7,5" if i != 3 else "?", "8,0" if i % 2 else "", "=MÉDIA(B:C)" if i == 2 else ("7,8" if i != 3 else "#REF!"), "ver e-mail" if i in (1, 4) else ""]
    for j, v in enumerate(vals):
        col = RED if v in ("#REF!", "?") else LINE_C
        text(c, v, x + 12 + j * w / 5, y + h * 0.65, 17 if j != 3 else 15, 500, col, alpha, family="Menlo")

def draw(c, T):
    background(c, T, grid=0.3, cam=(0, T * 10))
    # A. planilha → Mesa
    if T < b(64.8):
        k_in = e_out3(prog(T, T0 + 0.1, T0 + 0.8))
        morph = prog(T, b(63.2), b(64.1))
        mesa_a = e_out3(prog(T, b(63.6), b(64.2)))
        e = e_in3(prog(T, b(64.3), b(64.8)))
        pose = moved(P_MESA, dy=-1200 * e, alpha=1 - e)
        cd = Card(MESA, MESA_CROP, pose)
        if mesa_a > 0:
            # a moldura e o que não é linha da tabela aparecem por baixo das linhas que chegam
            cd.frame(c, mesa_a * pose.alpha, glow=0.2)
            cd.region(c, (0, 205, 1520, 701), alpha=mesa_a * pose.alpha)
            cd.region(c, (0, 1301, 1520, 39), alpha=mesa_a * pose.alpha)
            cd.region(c, (1456, 906, 64, 395), alpha=mesa_a * pose.alpha)
            cd.border(c, mesa_a * pose.alpha)
        if morph < 1:
            draw_sheet(c, T, k_in * (1 - e_in3(prog(morph, 0, 0.6))))
        rows, _ = sheet_rows(T)
        for i, r in enumerate(rows):
            ki = e_ioexpo(clamp(morph * 1.5 - i * 0.1))
            tl = cd.to_screen(MESA_ROWS[i][0], MESA_ROWS[i][1]); br = cd.to_screen(MESA_ROWS[i][0] + MESA_ROWS[i][2], MESA_ROWS[i][1] + MESA_ROWS[i][3])
            x = lerp(r[0], tl[0], ki); y = lerp(r[1], tl[1], ki); w = lerp(r[2], br[0] - tl[0], ki); h = lerp(r[3], br[1] - tl[1], ki)
            m = smooth(prog(ki, 0.35, 0.85))
            if m < 1:
                draw_sheet_row(c, (x, y, w, h), i, k_in * (1 - m), T)
            if m > 0:
                card(c, MESA, skia.Rect.MakeXYWH(*MESA_ROWS[i]), dst=rect(x, y, w, h), radius=2, alpha=m * pose.alpha, shadow=0.25 * (1 - ki), border=0)
        cd.focus(c, union(dom("g_mesa51_d1", "no total", "a"), dom("g_mesa51_d1", "concluídas", "a")),
                 prog(T, b(64.0), b(64.3)) * pose.alpha, pad=6, color=MINT)
    caption_block(c, T, T0 + 0.2, b(63.2), "Da comissão", None, 150, 470, 80, tag_s="03 · Avaliação")
    kinetic(c, "ao resultado.", 150, 565, 80, T - T0 - 0.45, weight=780, align="left", out_t=b(63.2) - T0 - 0.45, color=MINT)
    # B. avaliação com documentos: a câmera desce dos documentos à nota
    if b(64.3) < T < b(66.9):
        kin = e_out5(prog(T, b(64.3), b(64.9))); kout = e_in3(prog(T, b(66.3), b(66.9)))
        crop = cam_at(T, [(b(65.4), AV_A), (b(65.9), AV_B)])
        pose = moved(frame_in(AV_A, ZONE_BOTTOM), dx=900 * (1 - kin), dy=-1100 * kout)
        cd = Card("g_avaliacao_docs.png", crop, pose).draw(c, 1, glow=0.2)
        cd.focus(c, AV_DOCS, prog(T, b(64.9), b(65.3)) * (1 - prog(T, b(65.4), b(65.6))), pad=8, color=MINT)
        cd.focus(c, AV_SECAO, prog(T, b(65.95), b(66.3)) * (1 - kout), pad=10)
        kd = e_outback(prog(T, b(65.1), b(65.7)), 1.1) * (1 - prog(T, b(65.4), b(65.7)))
        if kd > 0.01:
            Card("pdf_docident_01.png", (0, 0, 1190, 1684), Pose(1520, 420, 380 * kd + 1, 0, 0, 5, 0, 1)).draw(c, clamp(kd), radius=4)
        cap(c, T, b(64.6), b(66.5), "Avaliações organizadas.", "Documentos associados ao candidato e à etapa.", tag_s="Mesa de avaliação")
    # C. distribuição e resultados da etapa
    if b(66.5) < T < b(70.6):
        kin = e_out5(prog(T, b(66.5), b(67.1))); kout = e_in3(prog(T, b(70.0), b(70.6)))
        sw = e_io3(prog(T, b(68.3), b(68.9)))
        p1 = moved(frame_in(DISTRIB_CROP, ZONE_BOTTOM), dx=1000 * (1 - kin) - 1900 * sw)
        p2 = moved(frame_in(RESULT_CROP, ZONE_BOTTOM), dx=1900 * (1 - sw), dy=-1100 * kout)
        if sw < 1:
            d = Card("g_distrib51_d1.png", DISTRIB_CROP, p1).draw(c, 1, glow=0.2)
            d.focus(c, DISTRIB_CHIPS, prog(T, b(67.2), b(67.6)) * (1 - prog(T, b(67.75), b(67.9))), pad=8, color=MINT)
            d.focus(c, DISTRIB_CARGA, prog(T, b(67.9), b(68.2)) * (1 - sw), pad=8, color=MINT)
        if sw > 0:
            r = Card("g_result_etapa51_d1.png", RESULT_CROP, p2).draw(c, 1, glow=0.2)
            r.focus(c, RESULT_TABLE, prog(T, b(69.0), b(69.4)) * (1 - kout), pad=8, color=MINT)
        cap(c, T, b(66.8), b(68.3), "Comissão em ação.", "Distribuição entre avaliadores, carga e conclusão acompanhadas.", tag_s="Distribuição")
        cap(c, T, b(68.75), b(69.95), "Critérios definidos.", "Cada etapa diz por que habilitou ou eliminou.", tag_s="Resultado da etapa")
    # D. classificação → corte → ocupação, em cortes laterais
    if b(70.2) < T < b(74.3):
        shots = [("g_marco51.png", MARCO_CROP, MARCO_TABLE, b(70.2), b(71.5)),
                 ("g_corte51.png", CORTE_CROP, union(CORTE_RESUMO, CORTE_TABLE), b(71.5), b(72.6)),
                 ("g_ocupacao51.png", OCUP_CROP, OCUP_RESUMO, b(72.6), b(74.3))]
        for j, (img, crop, fb, ta, tb) in enumerate(shots):
            kin = e_out5(prog(T, ta - 0.1, ta + 0.5)); kout = e_in3(prog(T, tb - 0.4, tb + 0.1))
            if kin <= 0 or kout >= 1: continue
            pose = moved(frame_in(crop, ZONE_BOTTOM), dx=1900 * (1 - kin) - 1900 * kout)
            cd = Card(img, crop, pose).draw(c, 1, glow=0.15)
            cd.focus(c, fb, prog(T, ta + 0.5, ta + 0.9) * (1 - kout), pad=8, color=MINT)
        cap(c, T, b(70.5), b(73.9), "Resultados estruturados.", "Classificação pelas regras do Edital, faixa de corte, ocupação de vagas.",
            tag_s="Classificação · Corte · Ocupação")
    # E. recurso: interposto no portal, julgado na gestão
    if b(73.9) < T < b(76.6):
        kin = e_out5(prog(T, b(73.9), b(74.5))); sw = e_io3(prog(T, b(74.9), b(75.4))); kout = e_in3(prog(T, b(76.0), b(76.6)))
        if sw < 1:
            a = Card("p_elisa_recorrer_ok.png", REC_FORM, moved(frame_in(REC_FORM, ZONE_BOTTOM), dx=-1000 * (1 - kin) - 1900 * sw)).draw(c, 1, glow=0.15)
            a.focus(c, (48, 575, 1004, 440), prog(T, b(74.4), b(74.8)) * (1 - sw), pad=6, color=MINT)
            tag(c, "Portal do candidato", 154, 868, env(T, b(74.1), b(75.0), 0.3, 0.3))
        if sw > 0:
            crop = cam_at(T, [(b(75.5), REC_A), (b(75.85), REC_B)])
            g = Card("g_recurso.png", crop, moved(frame_in(REC_A, ZONE_BOTTOM), dx=1900 * (1 - sw), dy=-1100 * kout)).draw(c, 1, glow=0.15)
            g.focus(c, REC_PECA, prog(T, b(75.3), b(75.5)) * (1 - prog(T, b(75.5), b(75.6))), pad=8, color=MINT)
            g.focus(c, REC_ADM, prog(T, b(75.85), b(76.05)) * (1 - kout), pad=8)
            tag(c, "Gestão · julgamento do recurso", 154, 868, env(T, b(75.2), b(76.1), 0.3, 0.3))
        caption_block(c, T, b(74.2), b(76.1), "Recursos com rito.", "Tempestividade, admissibilidade e efeito sobre o resultado.",
                      150, CAP_Y, CAP_SIZE, wrap=1500)
    # F. resultado publicado
    if T > b(76.2):
        kin = e_out5(prog(T, b(76.2), b(76.8))); kout = e_in3(prog(T, b(77.6), b(78)))
        r = Card("p_resultado51.png", RES_CROP, moved(frame_in(RES_CROP, ZONE_BOTTOM), dx=900 * (1 - kin))).draw(c, 1 - kout, glow=0.2)
        r.focus(c, RES_TABLE, prog(T, b(76.8), b(77.2)) * (1 - kout), pad=8, color=MINT)
        cap(c, T, b(76.4), b(77.8), "Decisões rastreáveis.", "Quem avalia é a comissão. O sistema organiza e registra.",
            tag_s="Resultado publicado · trilha de auditoria")
