"""III-a. Da ideia ao edital (b30 – b46)."""
from kit import *
from timeline import *

T0 = b(30)
STEPS = ["identificacao", "perfis", "cronograma", "etapas", "classificacao", "inscricao", "anexos", "conteudo", "revisao"]
STEP_BOX = lambda i: (48 + i * 311, 410, 297, 135)
# Câmera: a faixa das etapas rola para manter a etapa ativa à vista; o conteúdo da etapa aparece de
# perto, alinhado à esquerda, no trecho que interessa (caixas medidas no DOM).
CROP = (0, 390, 1900, 826)
HEAD = (0, 390, 1900, 170)
BODY = (0, 560, 1900, 656)
def step_body(i):
    """(deslocamento vertical, caixa do destaque) do conteúdo de cada etapa."""
    n = "c02_" + STEPS[i]
    spec = {1: ("Perfis deste Edital", "table"), 2: ("EVENTO DO CRONOGRAMA 1 DE 3", "fieldset"),
            3: ("ETAPA DE AVALIAÇÃO 1 DE 3", "fieldset"), 4: ("Classificação dos Perfis", "table"),
            5: ("DOCUMENTO EXIGIDO 1 DE 3", "fieldset"), 6: ("ANEXO 1 DE 2", "fieldset"),
            8: ("O que falta para submeter", "section")}.get(i)
    alvo = dom(n, *spec) if spec else None
    if alvo is None:
        return 0, None
    top = dom(n, "Documentos exigidos", "h2")[1] - 20 if i == 5 else alvo[1] - 40
    return max(0, top - 560), alvo
SCHED = [(t, i, step_body(i)[0]) for t, i in [(b(32.4), 0), (b(35.4), 1), (b(36.6), 2), (b(37.4), 3), (b(38.2), 4),
                                              (b(39.0), 5), (b(39.5), 6), (b(40.0), 8)]]

def head_x(i):
    return clamp(48 + 311 * i + 148 - 950, 0, 2880 - CROP[2])

P_IN = frame_in(CROP, ZONE_RIGHT)
P_MAIN = frame_in(CROP, ZONE_BOTTOM)
P_SIDE = Pose(640, 420, 1100, 0, 0, 0, 500)
P_BACK = Pose(980, 430, 1300, 0, 0, 0, 300)
REAP_CROP = (0, 1150, 2880, 1100)
P_REAP = frame_in(REAP_CROP, ZONE_BOTTOM)

def comp_pose(T):
    return pose_at(T, [(b(31.4), P_IN), (b(32.6), P_MAIN), (b(33.5), P_MAIN), (b(34.0), P_SIDE),
                       (b(35.1), P_SIDE), (b(35.6), P_MAIN), (b(40.4), P_MAIN), (b(41.2), P_BACK)])

def step_state(T):
    idx = 0
    for i, s in enumerate(SCHED):
        if T >= s[0]: idx = i
    return (SCHED[idx - 1] if idx > 0 else None), SCHED[idx]

def hx_at(T):
    prev, cur = step_state(T)
    return lerp(head_x(prev[1]), head_x(cur[1]), e_io3(prog(T, cur[0], cur[0] + 0.6))) if prev else head_x(cur[1])

def draw_comp(c, T, alpha=1.0):
    pose = comp_pose(T)
    prev, cur = step_state(T)
    k = e_outexpo(prog(T, cur[0], cur[0] + 0.55)) if prev else 1.0
    sy = lerp(prev[2], cur[2], e_io3(prog(T, cur[0], cur[0] + 0.7))) if prev else cur[2]
    hx = hx_at(T)
    card_ = Card(f"c02_{STEPS[cur[1]]}.png", CROP, pose)
    card_.frame(c, alpha, glow=0.18)
    if prev and k < 1:
        card_.region(c, HEAD, img=f"c02_{STEPS[prev[1]]}.png", offset=(hx, 0), alpha=alpha)
        card_.region(c, BODY, img=f"c02_{STEPS[prev[1]]}.png", offset=(0, sy + 120 * k), alpha=alpha * (1 - k))
    card_.region(c, HEAD, offset=(hx, 0), alpha=alpha * (k if prev else 1))
    card_.region(c, BODY, offset=(0, sy - 120 * (1 - k)), alpha=alpha * k)
    card_.border(c, alpha)
    i = cur[1]
    bx, by, bw, bh = STEP_BOX(i)
    card_.focus(c, (bx - hx, by, bw, bh), e_out3(prog(T, cur[0] + 0.05, cur[0] + 0.5)) * alpha, pad=6, color=GREEN)
    alvo = step_body(i)[1]
    if alvo:
        kf = prog(T, cur[0] + 0.5, cur[0] + 1.0)
        if kf > 0:
            card_.focus(c, (alvo[0], alvo[1] - sy, alvo[2], alvo[3]), e_out3(kf) * alpha, pad=8, color=MINT)
    return card_

def draw(c, T):
    background(c, T, grid=0.35, cam=(T * 12, 0))
    # A. a folha isolada
    pdf_k = e_out3(prog(T, T0 + 0.1, T0 + 0.9))
    split = prog(T, b(31.3), b(32.5))
    if T < b(32.6) and split <= 0:
        cx, cy = 1380 + 18 * math.sin(T * 0.9), 540 + 12 * math.cos(T * 0.7)
        w, h = 320, 400
        c.save(); c.translate(cx, cy); c.rotate(-6 + 3 * math.sin(T))
        icon(c, "pdf", -w / 2 * pdf_k, -h / 2 * pdf_k, w * pdf_k, h * pdf_k, alpha=pdf_k)
        c.restore()
    caption_block(c, T, T0 + 0.25, b(31.25), "Da ideia ao edital.", "O sistema guia a montagem do Edital, passo a passo.", 150, 560, 92,
                  tag_s="01 · Elaboração", wrap=560)
    if T >= b(31.3) and T < b(40.9):
        a = e_out3(prog(T, b(31.6), b(32.5)))
        card_ = draw_comp(c, T, a)
        # B. a folha se parte em faixas que pousam nas etapas do assistente
        if 0 < split < 1:
            for i in range(6):
                ki = e_ioexpo(clamp(split * 1.6 - i * 0.1))
                y0 = 540 - 200 + 40 + i * 36
                src = (1380 - 140, y0, 280, 30)
                tx, ty, tw, th = STEP_BOX(i)
                p0 = card_.to_screen(tx, ty); p1 = card_.to_screen(tx + tw, ty + th)
                x = lerp(src[0], p0[0], ki); y = lerp(src[1], p0[1], ki)
                ww = lerp(src[2], p1[0] - p0[0], ki); hh = lerp(src[3], p1[1] - p0[1], ki)
                al = 1 - e_in3(prog(ki, 0.75, 1))
                rrect(c, x, y, ww, hh, 6, PAPER_C, al)
                rrect(c, x + 8, y + hh * 0.4, ww * 0.55, max(2, hh * 0.18), 2, LINE_C, al * 0.5)
                if ki > 0.05:
                    rrect(c, x, y, ww, hh, 6, GREEN, al * 0.9, style="stroke", stroke=2)
        tag(c, "Começa a partir de um Edital anterior", 154, 900, env(T, b(32.7), b(33.5), 0.3, 0.3))
        # reaproveitar: o cartão entra pela direita, à frente da composição recuada
        if b(33.6) < T < b(35.6):
            kin = e_out3(prog(T, b(33.6), b(34.2))); kout = e_in3(prog(T, b(35.0), b(35.5)))
            pr = moved(P_REAP, dx=900 * (1 - kin) + 1100 * kout)
            img = "g_reaproveitar02.png" if T < b(34.55) else "g_reaproveitar02_sel.png"
            rc = Card(img, REAP_CROP, pr).draw(c, 1, glow=0.25)
            rc.focus(c, (60, 1785, 2780, 180), prog(T, b(34.55), b(35.0)), pad=4)
            p_radio = rc.to_screen(128, 1820); p_btn = rc.to_screen(2680, 2110)
            cp = path_at(T, [(b(34.0), (1600, 760)), (b(34.45), p_radio), (b(34.75), p_radio), (b(34.95), p_btn)])
            cursor(c, *cp, alpha=env(T, b(34.0), b(35.1), 0.2, 0.2), press=env(T, b(34.45), b(34.6), 0.03, 0.08))
            ripple(c, *p_radio, prog(T, b(34.5), b(34.5) + 0.6))
            tag(c, "Nada começa do zero", 154, 900, env(T, b(34.1), b(35.3), 0.3, 0.3))
        if T > b(35.4):
            cap(c, T, b(35.6), b(40.3), "Regras organizadas.", "Vagas, datas, etapas e critérios — cada coisa no seu lugar.", tag_s="Montar o Edital")
        # cursor percorrendo a barra de etapas
        if b(35.2) < T < b(40.6):
            pts = []
            for (ts, i, _) in SCHED[1:]:
                bx, by, bw, bh = STEP_BOX(i)
                p = card_.to_screen(bx + bw * 0.5 - head_x(i), by + bh * 0.55)
                pts.append((ts - 0.35, p)); pts.append((ts, p))
            cp = path_at(T, pts)
            press = max(env(T, ts - 0.06, ts + 0.1, 0.03, 0.08) for (ts, _, _) in SCHED[1:])
            cursor(c, *cp, alpha=env(T, b(35.2), b(40.4), 0.3, 0.3), press=press)
            for (ts, _, _) in SCHED[1:]:
                ripple(c, *cp, prog(T, ts, ts + 0.6))
    # D. o Edital oficial em linguagem simples
    if b(40.5) <= T < b(43.4):
        draw_pdf(c, T)
    # E. publicação, retificações
    if T >= b(42.9):
        draw_pub(c, T)

PAGES = [f"pdf_edital01_{i:02d}.png" for i in range(1, 5)]

def draw_pdf(c, T):
    t = T - b(40.5)
    fan = e_out5(prog(t, 0.2, 1.4))
    hero = e_io3(prog(t, 2.2, 3.2))
    out = e_in3(prog(T, b(42.9), b(43.4)))
    for i in reversed(range(4)):
        k = clamp(fan * 1.25 - i * 0.08)
        ang = (i - 1.5) * 11 * k
        cx = 1400 + (i - 1.5) * 190 * k
        cy = 560 + abs(i - 1.5) * 24 * k + (1 - k) * 80
        w = 420
        if i == 0:
            cx = lerp(cx, 1400, hero); cy = lerp(cy, 680, hero); w = lerp(w, 820, hero); ang *= 1 - hero
        al = clamp(k * 3) * (1 - out) * (1 - (0.75 * hero if i else 0))
        p = Pose(cx + out * 900, cy, w, 0, -10 * (1 - hero) if i else -6 * (1 - hero), ang, 0, al)
        Card(PAGES[i], (0, 0, 1785, 2526), p).draw(c, al, radius=4, border=0.0)
    caption_block(c, T, b(40.9), b(42.0), "Linguagem simples.", "O Edital oficial, gerado pelo sistema.", 150, 560, 76,
                  tag_s="Documento oficial", wrap=560)

def draw_pub(c, T):
    t0 = b(42.9)
    kin = e_out5(prog(T, t0, t0 + 0.8))
    kexit = e_in3(prog(T, b(45.4), b(46)))
    sy = lerp(330, 1180, e_io3(prog(T, b(44.6), b(45.3))))
    crop = (0, sy, 2880, 1250)
    base = frame_in(crop, ZONE_BOTTOM)
    card_ = Card("g_edital01.png", crop, moved(base, dx=800 * (1 - kin) - 1700 * kexit))
    card_.draw(c, 1, glow=0.2)
    dots = [(100, 457), (640, 457), (1180, 457), (1722, 457)]
    kl = prog(T, t0 + 0.6, t0 + 2.0)
    if sy < 600:
        for j in range(3):
            kk = clamp(kl * 3 - j)
            if kk <= 0: continue
            a = card_.to_screen(*dots[j]); bb = card_.to_screen(*dots[j + 1])
            c.drawLine(a[0], a[1], lerp(a[0], bb[0], e_out3(kk)), lerp(a[1], bb[1], e_out3(kk)), paint(GREEN, 0.9, style="stroke", stroke=4))
        for j in range(4):
            if kl * 3 >= j - 0.05:
                p = card_.to_screen(*dots[j]); glow_dot(c, *p, 7, GREEN, 1)
        card_.focus(c, (1505, 755, 1285, 135), prog(T, t0 + 2.2, t0 + 2.8) * (1 - prog(T, b(44.5), b(44.7))), pad=6)
    for j, yy in enumerate([1610, 1677, 1743]):
        card_.focus(c, (85, yy, 930, 46), prog(T, b(45.0) + j * 0.22, b(45.0) + j * 0.22 + 0.4) * (1 - kexit), pad=6, color=MINT)
    cap(c, T, t0 + 0.4, b(45.7), "Publicado, fica registrado.", "Se algo muda, o Edital é retificado — e a versão anterior continua disponível.",
        tag_s="Publicação")
