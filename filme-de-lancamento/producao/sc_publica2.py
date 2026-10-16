"""Revisado, publicado, aberto a todos (8 compassos, 15 s; tempo local u).

Telas do Edital 02/2026 publicado de verdade no banco do filme (ana.elaboradora elaborou,
bruno.homologador homologou, carla.publicadora publicou). Depois do clique em "Confirmar:
Publicar", a página pública do Edital entra em cena; o PDF que o sistema gerou — o mesmo da
sequência de linguagem simples — encaixa no botão "Ler o Edital completo (PDF)", e a cena termina
no clique em "Ver vagas e inscrever-se", que abre o capítulo da inscrição."""
from kit import *

DUR = 15.0
G = "pub_gestao_depois.png"
G_CROP = (0, 370, 2000, 880)
G_QUEM = dom("pub_gestao_depois", "Elaborou e submeteu", "dl")
G_ETAPAS = dom("pub_gestao_depois", "Em elaboração Em revisão", "ol")
C = "pub_publicar_confirmar.png"
C_CROP = (0, 1720, 2000, 1050)
C_BTN = (90, 2618, 332, 80)
PUB = "pub_portal_edital02.png"
PUB_CROP = (0, 120, 1500, 1010)
PUB_ABERTA = (48, 226, 1260, 260)             # "ABERTA", o título e "Inscrições abertas desde…"
PUB_PDF = (48, 1000, 481, 94)                 # "Ler o Edital completo (PDF)"
PUB_INSC = (79, 713, 429, 86)                 # "Ver vagas e inscrever-se"
PDF1 = "pdfhi_edital02_01.png"

def draw(c, u):
    T = u + 105.75 - 1.875
    background(c, T, grid=0.3, cam=(-T * 10, 0))
    # A. revisado e aprovado: cada etapa, uma pessoa
    if u < 5.6:
        kin = e_out5(prog(u, 0.0, 0.7)); kout = e_in3(prog(u, 5.0, 5.6))
        g = Card(G, G_CROP, moved(frame_in(G_CROP, ZONE_BOTTOM), dx=1300 * (1 - kin), dy=-1150 * kout)).draw(c, 1, glow=0.2)
        g.focus(c, G_ETAPAS, prog(u, 0.8, 1.2) * (1 - prog(u, 2.2, 2.5)), pad=8, color=MINT)
        g.focus(c, G_QUEM, prog(u, 2.5, 3.0) * (1 - kout), pad=10, color=MINT)
    cap(c, u, 0.4, 4.9, "Revisado e aprovado.", "Quem elaborou, quem revisou e quem publicou fica registrado, com data e hora.",
        tag_s="Publicação")
    # B. publicar
    if 5.3 < u < 8.9:
        kin = e_out5(prog(u, 5.3, 6.0)); kout = e_in3(prog(u, 8.3, 8.9))
        cf = Card(C, C_CROP, moved(frame_in(C_CROP, ZONE_BOTTOM), dx=1300 * (1 - kin), dy=-1150 * kout)).draw(c, 1, glow=0.2)
        p = cf.to_screen(C_BTN[0] + 166, C_BTN[1] + 40)
        cursor(c, *path_at(u, [(6.0, (1400, 760)), (7.0, p), (7.9, p)]), alpha=env(u, 6.0, 8.3, 0.3, 0.2),
               press=env(u, 7.45, 7.6, 0.03, 0.08))
        ripple(c, *p, prog(u, 7.5, 8.1))
    cap(c, u, 5.6, 8.3, "Publicar.", "Um clique — e o Edital passa a valer, sem poder ser alterado.")
    # C. aberto a todos: a página pública do Edital, com o PDF e as inscrições
    if u > 8.6:
        kin = e_out5(prog(u, 8.6, 9.4))
        pub = Card(PUB, PUB_CROP, moved(frame_in(PUB_CROP, ZONE_BOTTOM), dy=900 * (1 - kin))).draw(c, 1, glow=0.2)
        # o PDF gerado voa até o botão "Ler o Edital completo (PDF)"
        kp = e_io3(prog(u, 9.5, 10.7))
        if kp < 1 and u > 9.3:
            a = (1560, 360); z = pub.to_screen(PUB_PDF[0] + 70, PUB_PDF[1] + PUB_PDF[3] / 2)
            w = lerp(300, 60, kp)
            Card(PDF1, (0, 0, 3570, 5052), Pose(lerp(a[0], z[0], kp), lerp(a[1], z[1], kp) - 120 * math.sin(math.pi * kp), w, 0, 0, -8 * (1 - kp), 0,
                 1 - e_in3(prog(kp, 0.8, 1)))).draw(c, 1 - e_in3(prog(kp, 0.8, 1)), radius=3, border=0.0)
        pub.focus(c, PUB_PDF, prog(u, 10.6, 11.0) * (1 - prog(u, 11.7, 12.0)), pad=8, color=MINT)
        pub.focus(c, PUB_ABERTA, prog(u, 11.8, 12.3) * (1 - prog(u, 13.0, 13.3)), pad=10, color=MINT)
        pi = pub.to_screen(PUB_INSC[0] + 215, PUB_INSC[1] + 43)
        pub.focus(c, PUB_INSC, prog(u, 13.2, 13.6), pad=8)
        cursor(c, *path_at(u, [(12.6, (1500, 760)), (13.7, pi), (DUR, pi)]), alpha=env(u, 12.6, DUR, 0.3, 0.0),
               press=env(u, 14.2, 14.35, 0.03, 0.08))
        ripple(c, *pi, prog(u, 14.25, 14.85))
    cap(c, u, 9.0, 14.6, "Publicado, aberto a todos.", "Na hora, o Edital está na página pública — e as inscrições começam.")
