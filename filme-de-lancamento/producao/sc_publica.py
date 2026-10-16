"""Quem atuou, e publicar põe no ar (10 compassos, 18,75 s; tempo local u).

Telas do Edital 02/2026 publicado de verdade no banco do filme: elaborado por ana.elaboradora,
homologado por bruno.homologador, publicado por carla.publicadora. A área da equipe (/gestao) e a
página pública (/selecoes) aparecem lado a lado: antes, uma seleção aberta; depois da publicação,
duas — sem nenhum passo a mais."""
from kit import *

DUR = 18.75
G = "pub_gestao_depois.png"
G_CROP = (0, 370, 2000, 880)
G_ETAPAS = dom("pub_gestao_depois", "Em elaboração Em revisão", "ol")
G_QUEM = dom("pub_gestao_depois", "Elaborou e submeteu", "dl")
C = "pub_publicar_confirmar.png"
C_CROP = (0, 1720, 2000, 1050)
C_PUBLICO = (110, 2030, 1300, 60)             # "A Publicação passa a constar da consulta pública…"
C_BTN = (90, 2618, 332, 80)
P_ANTES, P_DEPOIS = "pub_portal_antes.png", "pub_portal_depois.png"
P_CROP = (0, 130, 1300, 1000)
P_CONTA = (48, 228, 1371, 51)                 # "1 seleção / 2 seleções com inscrições abertas."
P_NOVO = (48, 717, 1200, 672)                 # o cartão do Edital 02, novo, no topo
G_MINI = (0, 130, 1400, 262)                  # o cabeçalho da gestão: Edital 02/2026 · Publicado

L_ZONE = (70, 190, 680, 800)
R_ZONE = (740, 190, 1860, 800)

def label(c, s, path, x, y, a, color=MINT):
    if a <= 0.01: return
    tag(c, s, x, y, a, color=color, size=17)
    text(c, path, x, y + 34, 26, 600, INK, a, family="Menlo")

def draw(c, u):
    T = u + 105.75
    background(c, T, grid=0.3, cam=(-T * 10, 0))
    # A. quem atuou: três pessoas, três etapas, com data e hora
    if u < 7.0:
        kin = e_out5(prog(u, 0.0, 0.7)); kout = e_in3(prog(u, 6.4, 7.0))
        g = Card(G, G_CROP, moved(frame_in(G_CROP, ZONE_BOTTOM), dx=1300 * (1 - kin), dy=-1150 * kout)).draw(c, 1, glow=0.2)
        g.focus(c, G_ETAPAS, prog(u, 0.9, 1.4) * (1 - prog(u, 2.6, 2.9)), pad=8, color=MINT)
        g.focus(c, G_QUEM, prog(u, 2.9, 3.4) * (1 - kout), pad=10, color=MINT)
    cap(c, u, 0.4, 6.1, "Cada etapa, uma pessoa.", "Quem elaborou, quem revisou e quem publicou fica registrado — com data e hora.",
        tag_s="Publicação")
    # B. o ato de publicar
    if 6.6 < u < 10.4:
        kin = e_out5(prog(u, 6.6, 7.3)); kout = e_in3(prog(u, 9.8, 10.4))
        cf = Card(C, C_CROP, moved(frame_in(C_CROP, ZONE_BOTTOM), dx=1300 * (1 - kin), dy=-1150 * kout)).draw(c, 1, glow=0.2)
        cf.focus(c, C_PUBLICO, prog(u, 7.5, 7.9) * (1 - kout), pad=10, color=MINT)
        p = cf.to_screen(C_BTN[0] + 166, C_BTN[1] + 40)
        cursor(c, *path_at(u, [(7.6, (1400, 760)), (8.6, p), (9.4, p)]), alpha=env(u, 7.6, 9.8, 0.3, 0.2),
               press=env(u, 8.9, 9.05, 0.03, 0.08))
        ripple(c, *p, prog(u, 8.95, 9.55))
    cap(c, u, 7.0, 9.9, "Publicar.", "Um clique — e o ato não pode ser desfeito: correções, só por Retificação.")
    # C. /gestao e /selecoes, lado a lado: a seleção aparece na página pública
    if u > 10.2:
        kin = e_out5(prog(u, 10.2, 11.0)); kout = e_in3(prog(u, 18.2, DUR))
        gm = Card(G, G_MINI, moved(frame_in(G_MINI, L_ZONE), dx=-1200 * (1 - kin), alpha=1 - kout)).draw(c, 1 - kout, glow=0.15)
        gm.focus(c, dom("pub_gestao_depois", "Edital 02/2026 — Professor Substituto", "p"), prog(u, 11.2, 11.6) * (1 - kout), pad=8, color=MINT)
        sw = e_io3(prog(u, 12.6, 13.4))
        pose = moved(frame_in(P_CROP, R_ZONE), dx=1200 * (1 - kin), alpha=1 - kout)
        pd = Card(P_DEPOIS, P_CROP, pose)
        pd.frame(c, 1 - kout, glow=0.2)
        pd.region(c, None, img=P_ANTES, alpha=1 - kout)
        if sw > 0:
            pd.region(c, None, img=P_DEPOIS, alpha=sw * (1 - kout))
        pd.border(c, 1 - kout)
        pd.focus(c, P_CONTA, prog(u, 11.6, 12.0) * (1 - prog(u, 12.4, 12.6)) + prog(u, 13.5, 13.9) * (1 - prog(u, 14.4, 14.7)), pad=8)
        pd.focus(c, P_NOVO, prog(u, 14.6, 15.2) * (1 - kout), pad=10, color=MINT)
        # a seta: da área da equipe para a página pública
        ka = prog(u, 12.2, 12.9) * (1 - kout)
        if ka > 0:
            a0 = gm.to_screen(G_MINI[0] + G_MINI[2], G_MINI[1] + G_MINI[3] / 2)
            a1 = pd.to_screen(P_CROP[0], P_CROP[1] + 600)
            bezier(c, (a0[0] + 10, a0[1]), (a0[0] + 80, a0[1]), (a1[0] - 80, a1[1]), (a1[0] - 10, a1[1]), GREEN, 0.95, 4, k=e_out3(ka))
            if ka >= 1:
                glow_dot(c, a1[0] - 10, a1[1], 7, GREEN, 1)
        la = env(u, 10.6, 18.3, 0.4, 0.4)
        label(c, "Área da equipe", "/gestao", 74, 120, la)
        label(c, "Página pública · candidatos", "/selecoes", 760, 120, la)
    cap(c, u, 10.6, 18.2, "Publicou, está no ar.", "O Edital aparece na hora na página pública, onde os candidatos se inscrevem.")
