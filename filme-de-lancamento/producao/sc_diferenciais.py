"""IV. O que torna a plataforma diferente (b94 – b110). Sete capacidades, uma a cada ~2 compassos."""
from kit import *
from timeline import *

T0 = b(94)
T1 = b(95)
DUR = (b(110) - T1) / 7

ITEMS = [
    ("Governança", "Papéis, permissões, escopo institucional e autoridades signatárias.",
     [("g_identificar_papeis.png", (20, 1240, 1100, 1300), (60, 1370, 1000, 1150)),
      ("g_autoridades.png", (0, 300, 1900, 560), None)], None),
    ("Rastreabilidade", "Publicações preservadas, retificações, histórico e auditoria.",
     [("g_auditoria51.png", (0, 200, 1700, 1350), union(dom("g_auditoria51", "prévia de exportação", "p"), dom("g_auditoria51", "Ocupação do marco", "p"))),
      ("g_retificacao.png", (0, 100, 2000, 1100), None)], None),
    ("Operação", "Acompanhamento dos processos, indicadores e sinais de atenção.",
     [("g_visao_v2.png", (1100, 660, 1780, 1040), (2120, 1180, 680, 300)),
      ("g_supervisao.png", (0, 0, 2000, 1300), None)], None),
    ("Transparência", "Consulta pública, cronogramas, resultados por perfil e lista, acompanhamento individual.",
     [("p_edital51.png", (0, 1220, 1600, 740), dom("p_edital51", "Resultados divulgados", "section")),
      ("p_resultado51.png", (0, 100, 2880, 1250), None)], None),
    ("Comunicação", "Avisos complementares vinculados às publicações.",
     [("g_aviso_novo.png", (0, 420, 1500, 1000), dom("g_aviso_novo", "Quem recebe, e de onde veio", "section")),
      ("g_avisos51.png", (0, 0, 1400, 1300), None)],
     "Habilitação condicionada à validação institucional."),
    ("Flexibilidade", "Perfis, critérios, modalidades, etapas — e sorteios verificáveis.",
     [("p_verificar26.png", (0, 120, 1950, 1300), union(dom("p_verificar26", "Sorteio verificado", "p"), dom("p_verificar26", "Este é o sorteio vigente", "p"))),
      ("c02_classificacao.png", (0, 1250, 2880, 420), None)], None),
    ("Evolução", "Assistente de dúvidas com IA, na página do Edital, com a fonte citada.",
     [("asd_3_resposta.png", (1986, 250, 894, 1060), (2046, 920, 733, 102)),
      ("asd_0_pagina.png", (0, 0, 2880, 1800), None)],
     "Em breve"),
]
FRONT_ZONE = (950, 150, 1860, 1000)
BACK_ZONE = (900, 50, 1880, 640)

def draw(c, T):
    background(c, T, grid=0.5, cam=(T * 60, 0))
    # entrada
    if T < T1 + 0.3:
        tag(c, "05 · Diferenciais", 150, 470, env(T, T0, T1 - 0.35, 0.3, 0.3))
        kinetic(c, "O que muda na prática.", 146, 580, 96, T - T0 - 0.1, weight=800, align="left", out_t=T1 - T0 - 0.85, stagger=0.02)
    if T < T1 - 0.2:
        return
    i = min(6, int((T - T1) / DUR))
    for j in (i - 1, i, i + 1):
        if 0 <= j < 7:
            draw_item(c, T, j)
    # trilho de progresso
    a = env(T, T1, b(110), 0.4, 0.4)
    for j in range(7):
        x = 150 + j * 54
        on = prog(T, T1 + j * DUR, T1 + j * DUR + 0.3)
        c.drawRRect(skia.RRect.MakeRectXY(rect(x, 980, 40, 5), 2.5, 2.5), paint("#ffffff", 0.18 * a))
        c.drawRRect(skia.RRect.MakeRectXY(rect(x, 980, 40 * on, 5), 2.5, 2.5), paint(GREEN if j < i or on < 1 or j == i else GREEN, a))

def draw_item(c, T, j):
    title, sub, shots, note = ITEMS[j]
    t0 = T1 + j * DUR
    t1 = t0 + DUR
    if T < t0 - 0.5 or T > t1 + 0.5: return
    kin = e_outexpo(prog(T, t0 - 0.15, t0 + 0.55))
    kout = e_inexpo(prog(T, t1 - 0.35, t1 + 0.1)) if j < 6 else e_in3(prog(T, t1 - 0.5, t1))
    # duas capturas em camadas; a de trás entra um pouco depois
    for s, (img, crop, fbox) in enumerate(reversed(shots)):
        depth = 1 - s  # 1 = de trás
        kk = e_outexpo(prog(T, t0 - 0.1 + 0.12 * (1 - depth), t0 + 0.7 + 0.12 * (1 - depth)))
        base = frame_in(crop, BACK_ZONE if depth else FRONT_ZONE, maxscale=0.75 if depth else 1.0)
        pose = moved(base, dx=900 * (1 - kk), dy=(-1000 * kout if j < 6 else 0), dz=(900 * kout if j == 6 else 0),
                     alpha=(0.55 if depth else 1) * (1 - kout))
        cd = Card(img, crop, pose).draw(c, pose.alpha, glow=0.15 * (1 - depth))
        if fbox and not depth:
            cd.focus(c, fbox, prog(T, t0 + 0.7, t0 + 1.2) * (1 - kout), pad=6, color=MINT)
    scrim(c, 0.82, "left", 0.42)
    a = 1 - kout
    tag(c, f"{j + 1:02d}", 152, 420, prog(T, t0 + 0.12, t0 + 0.4) * (1 - prog(T, t1 - 0.45, t1 - 0.2)), size=20)
    kinetic(c, title, 146, 520, 78, T - t0 + 0.1, weight=800, align="left", out_t=t1 - t0 - 0.45, stagger=0.022, out_dur=0.3)
    # quebra a linha de apoio em até três linhas
    words = sub.split(" "); lines = [""]
    for w_ in words:
        if text_width((lines[-1] + " " + w_).strip(), 34, 450) > 560: lines.append(w_)
        else: lines[-1] = (lines[-1] + " " + w_).strip()
    for li, ln in enumerate(lines):
        kinetic(c, ln, 150, 600 + li * 46, 34, T - t0 - 0.25 - li * 0.06, weight=450, align="left", color=MUTED,
                out_t=t1 - t0 - 0.6, stagger=0.006, rise=0.3, blur_in=4, out_dur=0.3)
    if note:
        k = env(T, t0 + 0.6, t1 - 0.3, 0.3, 0.3)
        y = 620 + len(lines) * 46 + 10
        wn = text_width(note.upper(), 17, 600, 0.16, "Menlo") + 36
        rrect(c, 148, y, wn, 40, 20, "#d9a23a", 0.16 * k)
        rrect(c, 148, y, wn, 40, 20, "#d9a23a", 0.9 * k, style="stroke", stroke=1.5)
        tag(c, note, 166, y + 26, k, color="#f2c46b", size=17)
