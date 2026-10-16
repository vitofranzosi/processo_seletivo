"""Inserção: o assistente do Edital (18,75 s, tempo local u).

Telas reais do painel da 074 (assistente na página do Edital), capturadas na página pública do
Edital 01/2026 com o código da worktree da 074 e o banco do filme. O percurso é o das perguntas
sugeridas — resposta pronta, montada dos dados do Edital, com as fontes. A pergunta livre ao
modelo não aparece: nas três tentativas sobre este Edital de demonstração, duas voltaram "não foi
possível confirmar" e uma trouxe um horário contraditório; mostrar uma resposta livre sugeriria um
desempenho que o teste não confirmou. Selo "Em breve": a funcionalidade ainda não está em produção."""
from kit import *

DUR = 18.75
PAGE, S1, S2, S3, S4 = "asd_0_pagina.png", "asd_1_inicio.png", "asd_2_opcao.png", "asd_3_resposta.png", "asd_4_fontes.png"
FULL = (0, 0, 2880, 2300)
PX = 1986                                   # onde o painel começa na captura
TOPO = (PX, 0, 894, 1010)
RESP = (PX, 250, 894, 1060)
FONT = (PX, 1150, 894, 870)
ZONE = (930, 70, 1860, 1010)
BTN = (2392, 2172, 455, 95)
SUG = (2018, 466, 476, 68)                  # "Que documentos preciso enviar?"
OPC = (2046, 445, 585, 68)                  # "Professor de Informática — Campus Serra"
FONTES_BTN = (2046, 1214, 300, 45)

KEYS = [(0.0, FULL), (3.0, FULL), (4.2, TOPO), (6.6, TOPO), (7.4, RESP), (10.8, RESP), (11.6, FONT), (14.3, FONT)]

def cam_crop(u):
    return cam_at(u, KEYS)

def state(u):
    """Captura da vez e a anterior (para a troca suave do conteúdo do painel)."""
    seq = [(0.0, PAGE), (2.55, S1), (4.95, S2), (6.25, S3), (11.0, S4)]
    cur = [s for s in seq if u >= s[0]][-1]
    prev = seq[seq.index(cur) - 1] if seq.index(cur) > 0 else None
    return prev, cur

def fit(title, base, room=740):
    """Tamanho do título que cabe na coluna da esquerda."""
    return min(base, room / max(1.0, text_width(title, 1.0, 780)))

def pill(c, x, y, s, a):
    if a <= 0.01: return
    wn = text_width(s.upper(), 20, 700, 0.18, "Menlo") + 44
    rrect(c, x, y, wn, 46, 23, "#d9a23a", 0.18 * a)
    rrect(c, x, y, wn, 46, 23, "#d9a23a", 0.95 * a, style="stroke", stroke=2)
    text(c, s.upper(), x + 22, y + 31, 20, 700, "#f2c46b", a, tracking=0.18, family="Menlo")

def draw(c, u):
    t_bg = u + 131.25
    background(c, t_bg, grid=0.3, cam=(-t_bg * 10, 0))
    kin = e_out5(prog(u, 0.0, 0.8)); kout = e_in3(prog(u, 14.0, 14.7))
    crop = cam_crop(u)
    pose = moved(frame_in(crop, ZONE), dx=1000 * (1 - kin), dy=-1150 * kout)
    prev, cur = state(u)
    cd = Card(cur[1], crop, pose)
    if pose.alpha > 0.01 and kout < 1:
        cd.frame(c, 1, glow=0.2)
        k = e_out3(prog(u, cur[0], cur[0] + 0.45)) if prev else 1
        if cur[1] == S1 and prev:
            # o painel desliza da direita sobre a página
            cd.region(c, (0, 0, 2880, 2300), img=PAGE)
            dx = (1 - k) * 894
            cd.region(c, (PX + dx, 0, 894 - dx, 2300), img=S1, offset=(-dx, 0))
        else:
            if prev and k < 1:
                cd.region(c, None, img=prev[1])
            cd.region(c, None, alpha=k if prev else 1)
        cd.border(c, 1)
        # destaques
        cd.focus(c, (2046, 539, 733, 195), prog(u, 7.6, 8.0) * (1 - prog(u, 8.9, 9.1)), pad=10, color=MINT)
        cd.focus(c, (2046, 920, 733, 102), prog(u, 9.1, 9.5) * (1 - prog(u, 10.7, 10.9)), pad=10)
        cd.focus(c, (2046, 1520, 733, 261), prog(u, 11.9, 12.3) * (1 - prog(u, 13.6, 13.9)), pad=10, color=MINT)
        # cursor: botão flutuante → sugestão → opção → "Consultar fontes"
        pts = [(0.9, (1500, 900)), (2.0, cd.to_screen(BTN[0] + 220, BTN[1] + 48)), (2.4, cd.to_screen(BTN[0] + 220, BTN[1] + 48)),
               (4.5, cd.to_screen(SUG[0] + 200, SUG[1] + 36)), (4.95, cd.to_screen(SUG[0] + 200, SUG[1] + 36)),
               (5.85, cd.to_screen(OPC[0] + 260, OPC[1] + 36)), (6.25, cd.to_screen(OPC[0] + 260, OPC[1] + 36)),
               (10.6, cd.to_screen(FONTES_BTN[0] + 120, FONTES_BTN[1] + 24)), (11.0, cd.to_screen(FONTES_BTN[0] + 120, FONTES_BTN[1] + 24))]
        cp = path_at(u, pts)
        clicks = [2.3, 4.85, 6.15, 10.9]
        press = max(env(u, t - 0.06, t + 0.1, 0.03, 0.08) for t in clicks)
        cursor(c, *cp, alpha=env(u, 1.0, 11.4, 0.3, 0.3) * (1 - prog(u, 6.3, 6.6)) + env(u, 10.2, 11.4, 0.3, 0.3) * prog(u, 6.3, 6.6), press=press)
        for t in clicks:
            ripple(c, *cp, prog(u, t, t + 0.6))
    # o celular, com a mesma resposta
    if u > 14.2:
        for j, (img, cx) in enumerate([("asm_1_inicio.png", 1180), ("asm_3_resposta.png", 1600)]):
            kj = e_out5(prog(u, 14.3 + j * 0.2, 15.2 + j * 0.2)) * (1 - e_in3(prog(u, 18.0, DUR)))
            device_phone(c, img, (0, 0, 1170, 2532), cx, 560 + (1 - kj) * 800, 860, alpha=clamp(kj * 1.5))
    # textos
    tag(c, "Assistente do Edital · com IA", 154, 300, env(u, 0.4, 18.3, 0.4, 0.4))
    pill(c, 150, 330, "Em breve", env(u, 0.7, 18.3, 0.4, 0.4))
    caption_block(c, u, 0.6, 6.4, "Pergunte ao Edital.", "Dúvidas respondidas na própria página da seleção.", 146, 560, fit("Pergunte ao Edital.", 80), wrap=560)
    caption_block(c, u, 7.0, 10.6, "Respostas do texto oficial.", "Na versão vigente — e avisa quando há Retificação.", 146, 560, fit("Respostas do texto oficial.", 68), wrap=560)
    caption_block(c, u, 11.4, 13.8, "Com a fonte citada.", "Cada resposta mostra o trecho do Edital de onde veio.", 146, 560, fit("Com a fonte citada.", 72), wrap=560)
    caption_block(c, u, 14.6, 18.2, "Não substitui o Edital.", "Nem a comissão. O assistente orienta; quem decide é a seleção.", 146, 560, fit("Não substitui o Edital.", 72), wrap=560)
