"""O sistema escreve o Edital, em linguagem simples (7 compassos, 13,1 s; tempo local u).

Continua do último quadro da composição (a Revisão do Edital 02/2026): o formulário recua e o PDF
que o sistema gerou dele se compõe ao lado, de cima para baixo. Depois, a página assume o centro e,
à esquerda, a Lei nº 15.263/2025 (Política Nacional de Linguagem Simples) em três ideias. A página
termina na pose em que a sequência de linguagem simples começa (sc_linguagem.HERO)."""
from kit import *
import sc_edital as E
from timeline import b

DUR = 13.125
PDF1 = "pdfhi_edital02_01.png"
PW, PH = 3570, 5052
HERO = Pose(1400, 680, 820)
P_COMP_L = frame_in(E.CROP, (70, 140, 900, 760))
P_PAGE_R = Pose(1440, 470, 560)

def comp_card(c, pose, alpha):
    """A composição como a cena anterior a deixa: a Revisão, com a faixa das etapas no fim."""
    if alpha <= 0.01: return None
    sy = E.SCHED[-1][2]; hx = E.head_x(8)
    cd = Card("c02_revisao.png", E.CROP, pose)
    cd.frame(c, alpha, glow=0.18)
    cd.region(c, E.HEAD, offset=(hx, 0), alpha=alpha)
    cd.region(c, E.BODY, offset=(0, sy), alpha=alpha)
    cd.border(c, alpha)
    return cd

def page(c, pose, reveal=1.0, alpha=1.0):
    """A página 1 do Edital; reveal ∈ [0,1] compõe a página de cima para baixo, com borda suave."""
    if alpha <= 0.01: return
    h = pose.w * PH / PW
    x0, y0 = pose.cx - pose.w / 2, pose.cy - h / 2
    c.drawRect(rect(x0, y0 + 18, pose.w, h), paint("#000000", 0.45 * alpha, 30))
    c.drawRect(rect(x0, y0, pose.w, h), paint("#ffffff", alpha))
    yr = y0 + h * reveal
    c.save()
    c.clipRect(rect(x0, y0, pose.w, max(0, yr - y0)), skia.ClipOp.kIntersect, True)
    p = skia.Paint(AntiAlias=True); p.setAlphaf(alpha)
    c.drawImageRect(image(PDF1), skia.Rect.MakeWH(PW, PH), rect(x0, y0, pose.w, h), SAMP, p)
    c.restore()
    if 0 < reveal < 1:
        sh = skia.GradientShader.MakeLinear([skia.Point(0, yr - 60), skia.Point(0, yr)], [rgb("#ffffff", 0), rgb("#ffffff", alpha)])
        c.drawRect(rect(x0, yr - 60, pose.w, 60), skia.Paint(Shader=sh))
        c.drawRect(rect(x0, yr - 1.5, pose.w, 3), paint(GREEN, 0.9 * alpha))
        c.drawRect(rect(x0, yr - 10, pose.w, 20), paint(GREEN, 0.25 * alpha, 10))

def draw(c, u):
    T = u + 75.75
    background(c, T, grid=0.35, cam=(T * 12, 0))
    # 1. o formulário recua para a esquerda; a página se compõe à direita
    k1 = e_io3(prog(u, 0.0, 1.3))
    kout = e_in3(prog(u, 4.6, 5.4))
    pc = E.comp_pose(b(40.4)).mix(P_COMP_L, k1)
    cd = comp_card(c, moved(pc, dx=-1300 * kout), 1 - kout)
    reveal = e_io3(prog(u, 1.2, 3.6))
    k2 = e_io3(prog(u, 4.6, 6.0))
    pp = P_PAGE_R.mix(HERO, k2)
    pin = e_out3(prog(u, 0.9, 1.4))
    if pin > 0:
        page(c, pp, reveal, pin)
    # os dados atravessam: pontos de luz do formulário para a página, enquanto ela se compõe
    if cd is not None and 1.2 < u < 3.8:
        h = pp.w * PH / PW
        for j in range(7):
            k = prog(u, 1.3 + j * 0.3, 2.1 + j * 0.3)
            if k <= 0 or k >= 1: continue
            a = cd.to_screen(E.CROP[0] + E.CROP[2] * (0.55 + 0.06 * (j % 3)), E.CROP[1] + 240 + 70 * j)
            z = (pp.cx - pp.w / 2 + 20, pp.cy - h / 2 + h * (0.12 + 0.11 * j))
            t = e_io3(k)
            x = (1 - t) ** 2 * a[0] + 2 * (1 - t) * t * ((a[0] + z[0]) / 2) + t * t * z[0]
            y = (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * (min(a[1], z[1]) - 80) + t * t * z[1]
            glow_dot(c, x, y, 5, MINT, math.sin(math.pi * k))
    cap(c, u, 0.5, 4.6, "O sistema escreve o Edital.", "Automaticamente, a partir do que a equipe preencheu.", tag_s="Documento oficial")
    # 2. em linguagem simples, como pede a lei
    la = env(u, 5.6, 12.6, 0.5, 0.5)
    tag(c, "Lei nº 15.263/2025", 152, 300, la, size=20)
    text(c, "Política Nacional de Linguagem Simples", 152, 340, 26, 500, MUTED, la)
    kinetic(c, "Em linguagem", 146, 470, 88, u - 5.9, weight=800, align="left", out_t=12.4 - 5.9, stagger=0.03)
    kinetic(c, "simples.", 146, 568, 88, u - 6.1, weight=800, align="left", out_t=12.4 - 6.1, color=MINT, stagger=0.03)
    for j, s in enumerate(["Frases diretas.", "Voz ativa.", "Sem jargão."]):
        t0 = 7.3 + j * 0.7
        k = e_outback(prog(u, t0, t0 + 0.45), 1.6) * (1 - e_in3(prog(u, 12.2, 12.7)))
        if k <= 0.01: continue
        y = 670 + j * 66
        c.drawCircle(166, y - 12, 17 * k, paint(GREEN, clamp(k)))
        pth = skia.Path(); pth.moveTo(158, y - 12); pth.lineTo(164, y - 5); pth.lineTo(175, y - 19)
        c.drawPath(pth, paint("#ffffff", clamp(k), style="stroke", stroke=3.5))
        kinetic(c, s, 200, y, 40, u - t0, weight=650, align="left", out_t=12.2 - t0, stagger=0.015, rise=0.3)
