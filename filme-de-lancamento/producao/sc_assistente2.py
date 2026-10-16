"""O assistente do Edital — pergunta sugerida × pergunta livre à IA (14 compassos, 26,25 s; tempo local u).

Telas reais do painel da 074 na página pública do Edital 01/2026 (código da worktree da 074, sem
alteração, sobre ps_filme_074). A pergunta livre foi feita de verdade ao modelo (OpenRouter,
qwen/qwen3.8-27b): "Preciso ter mestrado para a vaga de professor?" — a resposta, com a citação
do requisito do Perfil DOC-INFO, confere com o Edital. Selo "Em breve"."""
from kit import *

DUR = 26.25
PX = 1986                                         # onde o painel começa na captura
PAGE, S1, S2, S3 = "asd_0_pagina.png", "asd_1_inicio.png", "asd_2_opcao.png", "asd_3_resposta.png"
L2, L3, L4 = "al1_2_espera.png", "al1_3_resposta.png", "al1_4_fontes.png"
FULL = (0, 0, 2880, 2300)
HEAD = (PX, 0, 894, 660)                          # o cabeçalho e a linha inteira de perguntas sugeridas
BTN_WIN = (1700, 1360, 1180, 940)                 # o canto da página com o botão "Dúvidas sobre este Edital"
SIDE = (1180, 0, 1700, 2300)                      # a metade direita da página: o painel desliza inteiro
PANEL = (PX, 0, 894, 1250)
ANSWER = (PX, 230, 894, 1110)
COMPOSER = (PX, 1880, 894, 420)
ZONE = (930, 60, 1860, 1010)

BTN = (2392, 2172, 455, 95)
SUG = (2018, 466, 476, 68)
OPC = (2046, 445, 585, 68)
IA = (2018, 76, 311, 38)                          # "Assistente de IA"
ORIGEM = (2046, 1272, 733, 38)                    # "Resposta pronta, montada a partir dos dados do Edital."
SEND = (2690, 2092, 158, 86)
CIT = (2046, 547, 733, 162)                       # a citação do Edital na resposta livre
LIVRE_TXT = (2046, 377, 733, 154)
TYPE_BOX = (PX, 2000, 894, 300)                   # onde as capturas da digitação se encaixam
TYPING = [f"al1_typ{i}.png" for i in range(7)]

# (início, imagem): o que o painel mostra
SEQ = [(0.0, PAGE), (2.3, S1), (6.0, S2), (7.2, S3), (12.2, S1), (16.6, L2), (17.9, L3), (21.3, L4)]
KEYS = [(0.0, FULL), (1.2, FULL), (2.0, BTN_WIN), (2.35, BTN_WIN), (2.95, SIDE), (3.25, SIDE), (3.95, HEAD), (5.4, HEAD), (6.0, PANEL), (8.0, PANEL), (8.8, ANSWER), (11.6, ANSWER),
        (12.3, PANEL), (13.0, COMPOSER), (16.0, COMPOSER), (16.9, PANEL), (18.3, ANSWER), (24.0, ANSWER), (25.0, PANEL)]

def pill(c, x, y, s, a, color="#d9a23a", ink="#f2c46b"):
    if a <= 0.01: return
    wn = text_width(s.upper(), 20, 700, 0.18, "Menlo") + 44
    rrect(c, x, y, wn, 46, 23, color, 0.18 * a)
    rrect(c, x, y, wn, 46, 23, color, 0.95 * a, style="stroke", stroke=2)
    text(c, s.upper(), x + 22, y + 31, 20, 700, ink, a, tracking=0.18, family="Menlo")

def fit(title, base, room=740):
    return min(base, room / max(1.0, text_width(title, 1.0, 780)))

def block(c, u, t0, t1, kicker, title, sub, kcolor=MINT):
    if u < t0 - 0.05 or u > t1 + 0.6: return
    tag(c, kicker, 150, 470, env(u, t0, t1 + 0.3, 0.4, 0.4), color=kcolor)
    caption_block(c, u, t0, t1, title, sub, 146, 560, fit(title, 76), wrap=560)

def draw(c, u):
    T = u + 154.5
    background(c, T, grid=0.3, cam=(-T * 10, 0))
    kin = e_out5(prog(u, 0.0, 0.8)); kout = e_in3(prog(u, 25.5, DUR))
    crop = cam_at(u, KEYS)
    pose = moved(frame_in(crop, ZONE), dx=1000 * (1 - kin), dy=-1150 * kout)
    idx = max(i for i, s in enumerate(SEQ) if u >= s[0])
    cur = SEQ[idx]; prev = SEQ[idx - 1] if idx else None
    cd = Card(cur[1], crop, pose)
    cd.frame(c, 1, glow=0.2)
    k = e_out3(prog(u, cur[0], cur[0] + 0.4)) if prev else 1
    if cur[1] == S1 and prev and prev[1] == PAGE:
        cd.region(c, None, img=PAGE)
        dx = (1 - k) * 894
        cd.region(c, (PX + dx, 0, 894 - dx, 2300), img=S1, offset=(-dx, 0))
    else:
        if prev and k < 1:
            cd.region(c, None, img=prev[1])
        cd.region(c, None, alpha=k if prev else 1)
    # a pergunta livre sendo digitada (capturas reais da caixa de texto)
    if 13.0 <= u < 16.7:
        i = min(6, int(prog(u, 13.4, 15.6) * 6.999))
        cd.region(c, TYPE_BOX, img=TYPING[i], offset=(-TYPE_BOX[0], -TYPE_BOX[1]))
    cd.border(c, 1)
    # destaques
    cd.focus(c, IA, prog(u, 3.8, 4.2) * (1 - prog(u, 5.4, 5.7)), pad=10)
    cd.focus(c, ORIGEM, prog(u, 9.2, 9.6) * (1 - prog(u, 11.4, 11.7)), pad=10, color=MINT)
    cd.focus(c, LIVRE_TXT, prog(u, 18.6, 19.0) * (1 - prog(u, 20.2, 20.5)), pad=10, color=MINT)
    cd.focus(c, CIT, prog(u, 20.4, 20.8) * (1 - prog(u, 23.8, 24.2)), pad=10)
    # cursor: botão flutuante → sugestão → opção; depois a caixa de texto e "Enviar"
    pts = [(0.9, (1500, 900)), (1.9, cd.to_screen(BTN[0] + 220, BTN[1] + 48)), (2.3, cd.to_screen(BTN[0] + 220, BTN[1] + 48)),
           (5.6, cd.to_screen(SUG[0] + 200, SUG[1] + 36)), (6.0, cd.to_screen(SUG[0] + 200, SUG[1] + 36)),
           (6.8, cd.to_screen(OPC[0] + 260, OPC[1] + 36)), (7.2, cd.to_screen(OPC[0] + 260, OPC[1] + 36)),
           (12.8, cd.to_screen(2200, 2060)), (13.3, cd.to_screen(2200, 2060)),
           (16.0, cd.to_screen(SEND[0] + 79, SEND[1] + 43)), (16.6, cd.to_screen(SEND[0] + 79, SEND[1] + 43))]
    cp = path_at(u, pts)
    clicks = [2.2, 5.9, 7.1, 13.2, 16.5]
    press = max(env(u, t - 0.06, t + 0.1, 0.03, 0.08) for t in clicks)
    vis = env(u, 1.0, 7.6, 0.3, 0.3) + env(u, 12.6, 16.9, 0.3, 0.3)
    cursor(c, *cp, alpha=clamp(vis), press=press)
    for t in clicks:
        ripple(c, *cp, prog(u, t, t + 0.6))
    # textos
    tag(c, "Assistente do Edital · com IA", 154, 300, env(u, 0.4, 25.6, 0.4, 0.4))
    pill(c, 150, 330, "Em breve", env(u, 0.7, 25.6, 0.4, 0.4))
    caption_block(c, u, 0.6, 5.5, "Um assistente com IA.", "Na página de cada seleção, para tirar dúvidas sobre o Edital.", 146, 560,
                  fit("Um assistente com IA.", 76), wrap=560)
    block(c, u, 6.1, 11.6, "1 · Pergunta sugerida", "Resposta pronta.",
          "Para as dúvidas mais comuns: a resposta vem montada com os dados do Edital.")
    block(c, u, 12.4, 16.5, "2 · Pergunta livre", "Ou pergunte do seu jeito.",
          "Escreva a dúvida com suas palavras. Quem responde é a IA.")
    block(c, u, 17.5, 21.5, "2 · Pergunta livre", "A IA lê o Edital e responde.",
          "E mostra o trecho exato do Edital de onde tirou a resposta.")
    block(c, u, 22.5, 25.4, "Assistente do Edital", "Não substitui o Edital.",
          "O assistente orienta; quem decide é a seleção.", kcolor=MUTED)
