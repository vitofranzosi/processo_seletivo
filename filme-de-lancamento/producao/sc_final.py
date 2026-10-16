"""V. Clímax (b110 – b122)  +  VI. Encerramento (b122 – b133)."""
from kit import *
from timeline import *

T0 = b(110)
NODES = [  # rótulo, captura, recorte, posição 3D (x, y, z)
    ("Editais", "pdf_edital01_01.png", (0, 0, 1785, 1400), (-620, -260, 900)),
    ("Candidatos", "m_ana_minhas.png", (0, 0, 1170, 1600), (520, -300, 1500)),
    ("Inscrições", "p_insc01_11_comprovante.png", (0, 0, 2880, 1700), (-380, 260, 2100)),
    ("Documentos", "g_avaliacao_docs.png", (0, 0, 2880, 1700), (640, 220, 2700)),
    ("Comissões", "g_comissao.png", (0, 0, 2880, 1700), (-700, -120, 3300)),
    ("Avaliações", "g_mesa51_d1.png", (0, 0, 2880, 1700), (300, -330, 3900)),
    ("Resultados", "p_resultado51.png", (0, 0, 2880, 1400), (-640, 120, 4500)),
    ("Recursos", "g_recurso.png", (0, 0, 2880, 1700), (-120, 330, 5100)),
    ("Convocações", "g_convocacao51.png", (0, 400, 2880, 1300), (-520, -200, 5700)),
]
CHAIN = ["EDITAL", "INSCRIÇÃO", "AVALIAÇÃO", "RESULTADO", "RECURSO", "CONVOCAÇÃO"]
CHAIN_FROM = [0, 2, 5, 6, 7, 8]
FOCAL = 1100.0

def cam_z(T):
    """Atravessa a rede e depois recua até revelar tudo."""
    if T < b(112.3):
        return lerp(-600, 3700, e_io3(prog(T, T0, b(112.3))))
    return lerp(3700, -1500, e_io3(prog(T, b(112.3), b(113.3))))

def node_screen(i, T):
    x, y, z = NODES[i][3]
    dz = z - cam_z(T)
    if dz < 60: return None
    s = FOCAL / dz
    sway = 40 * math.sin(T * 0.5 + i)
    return (W / 2 + (x * 1.6 + sway) * s, H / 2 + y * 1.3 * s, s, dz)

def chain_pos(j):
    return (W / 2 + (j - 2.5) * 290, 330)

def draw(c, T):
    if T < b(122):
        draw_climax(c, T)
    else:
        draw_end(c, T)

GRID = [(960 + (k % 3 - 1) * 560, 455 + (k // 3 - 1) * 262) for k in range(9)]

def fit_w(crop, maxw=360, maxh=178):
    return min(maxw, maxh * crop[2] / crop[3])

def draw_climax(c, T):
    background(c, T, grid=0.6 * (1 - prog(T, b(113), b(114))), cam=(0, cam_z(T) * 0.05), intensity=1.0)
    gk = e_io3(prog(T, b(112.4), b(113.3)))       # a rede se organiza numa grade: o sistema inteiro
    conv = e_io3(prog(T, b(113.7), b(114.5)))     # seis nós viram a cadeia
    pts = [node_screen(i, min(T, b(113.3))) for i in range(len(NODES))]
    # posição de cada nó: voo 3D → grade → cadeia
    pos = []
    for i, (label, img, crop, _) in enumerate(NODES):
        ns = pts[i]
        gx, gy = GRID[i]; gw = fit_w(crop)
        if ns:
            sx, sy, s, dz = ns
            w = 1100 * s
            al = clamp((dz - 60) / 400) * clamp(s * 4) * e_out3(prog(T, T0 + i * 0.2, T0 + i * 0.2 + 0.5)) * (1 - prog(w, 620, 980))
        else:
            sx, sy, w, al = gx, gy + 300, gw * 0.6, 0.0
        sx, sy, w = lerp(sx, gx, gk), lerp(sy, gy, gk), lerp(w, gw, gk)
        al = lerp(al, 1.0, gk)
        j = CHAIN_FROM.index(i) if i in CHAIN_FROM else None
        if conv > 0:
            if j is None:
                al *= 1 - conv
            else:
                tx, ty = chain_pos(j)
                sx, sy, w = lerp(sx, tx, conv), lerp(sy, ty, conv), lerp(w, 220, conv)
        pos.append((sx, sy, w, al, (ns[3] if ns else 0)))
    # ligações: no voo, curvas tracejadas; na grade, somem
    if gk < 1:
        for (a, bb) in [(i, i + 1) for i in range(8)] + [(0, 4), (2, 6), (1, 3), (5, 8)]:
            pa, pb = pos[a], pos[bb]
            al = min(pa[3], pb[3]) * (1 - gk) * prog(T, T0 + a * 0.15, T0 + a * 0.15 + 0.6)
            if al <= 0.01: continue
            bezier(c, pa[:2], (pa[0], (pa[1] + pb[1]) / 2), (pb[0], (pa[1] + pb[1]) / 2), pb[:2], GREEN, 0.7 * al, 2.0,
                   dash=[10, 8], phase=-T * 80)
    order = sorted(range(len(NODES)), key=lambda i: -pos[i][4]) if gk < 0.5 else list(range(len(NODES)))
    drawn = []
    allq = {}
    for i in order:
        label, img, crop, _ = NODES[i]
        sx, sy, w, al, _ = pos[i]
        if al > 0.2 and w >= 10:
            allq[i] = project(sx, sy, w, w * crop[3] / crop[2])
    for i in order:
        label, img, crop, _ = NODES[i]
        sx, sy, w, al, _ = pos[i]
        if al <= 0.01 or w < 10: continue
        cd_ = Card(img, crop, Pose(sx, sy, w, 0, 0, 0, 0, al)).draw(c, al, radius=10, glow=0.25 * al, shadow=0.4)
        # rótulo em placa própria: no voo só nos nós próximos; na grade, em todos
        lab_a = al * (1 - conv) * max(gk, clamp((w - 240) / 120))
        if lab_a > 0.02:
            fs = lerp(26 * min(1.4, max(0.7, w / 500)), 22, gk)
            tw = text_width(label, fs, 650)
            ly = sy + w * crop[3] / crop[2] / 2 + 10
            # o rótulo só aparece onde não há outro cartão por baixo
            lab_a *= clamp(1 - 10 * covered((sx - tw / 2 - fs * 0.6, ly, tw + fs * 1.2, fs * 1.6), [q for q, aa in drawn if aa > 0.2] + [q for k_, q in allq.items() if k_ != i]))
            rrect(c, sx - tw / 2 - fs * 0.6, ly, tw + fs * 1.2, fs * 1.6, fs * 0.8, BG0, 0.92 * lab_a)
            rrect(c, sx - tw / 2 - fs * 0.6, ly, tw + fs * 1.2, fs * 1.6, fs * 0.8, GREEN, 0.8 * lab_a, style="stroke", stroke=1.5)
            text(c, label, sx, ly + fs * 1.12, fs, 650, INK, lab_a, "center")
            if lab_a > 0.2:
                lx0, lx1, ly1 = sx - tw / 2 - fs * 0.6, sx + tw / 2 + fs * 0.6, ly + fs * 1.6
                drawn.append(([(lx0, ly), (lx1, ly), (lx1, ly1), (lx0, ly1)], lab_a))
        drawn.append((cd_.quad, al))
    # B. a cadeia
    if conv > 0:
        for j, name in enumerate(CHAIN):
            tj = b(114.5) + j * BEAT
            k = e_outexpo(prog(T, tj, tj + 0.5))
            x, y = chain_pos(j)
            dim = 1 - 0.5 * prog(T, b(115.8), b(116.4))
            text(c, name, x, y + 150 + (1 - k) * 20, 26, 760, INK, k * dim, "center", tracking=0.08)
            if j < 5:
                ka = e_out3(prog(T, tj + 0.2, tj + 0.6))
                x2 = chain_pos(j + 1)[0]
                c.drawLine(x + 120, y + 140, x + 120 + (x2 - x - 240) * ka, y + 140, paint(GREEN, 0.9 * ka * dim, style="stroke", stroke=3))
                if ka > 0.95:
                    xe = x2 - 120
                    path = skia.Path(); path.moveTo(xe, y + 140); path.lineTo(xe - 12, y + 133); path.lineTo(xe - 12, y + 147); path.close()
                    c.drawPath(path, paint(GREEN, dim))
    # C. a tese
    if T > b(116.0):
        for k_, (s, tt, col) in enumerate([("Uma plataforma.", b(116.0), INK), ("Diferentes seleções.", b(117.0), INK),
                                           ("Uma jornada integrada.", b(118.0), MINT)]):
            kinetic(c, s, W / 2, 640 + k_ * 92, 78, T - tt, weight=780, color=col, out_t=b(118.8) - tt, stagger=0.025)
    # D. consequências, uma por compasso e meio
    if T > b(119.25) - 0.1:
        conts = ["Menos fragmentação.", "Mais organização.", "Mais transparência.", "Mais capacidade de gestão."]
        for k_, s in enumerate(conts):
            tt = b(119.25) + k_ * BEAT * 3
            end = tt + BEAT * 3 - 0.5 if k_ < 3 else b(122) - 0.45
            if tt - 0.1 <= T <= end + 0.5:
                mask_wipe_text(c, s, W / 2, 760, 104, T - tt, weight=820, color=MINT if k_ == 3 else INK, out_t=end - tt, dur=0.45)

def draw_end(c, T):
    t = T - b(122)
    c.clear(rgb(BG0))
    sh = skia.GradientShader.MakeRadial(skia.Point(W / 2, H / 2), 900, [rgb(GREEN_D, 0.35 * prog(t, 0, 2)), rgb(GREEN_D, 0)])
    c.drawRect(rect(0, 0, W, H), skia.Paint(Shader=sh))
    fade = 1 - e_io3(prog(T, b(132.2), b(133)))
    # linha que se desenha
    k = e_io3(prog(t, 0.2, 1.8)) * fade
    k *= 1 - e_in3(prog(t, b(125) - b(122) - 1.0, b(125) - b(122) - 0.4))
    c.drawRect(rect(W / 2 - 260 * k, 470, 520 * k, 3), paint(GREEN, k))
    out1 = b(125) - b(122)
    kinetic(c, "SISTEMA DE PROCESSO SELETIVO", W / 2, 430, 50, t - 0.6, weight=700, tracking=0.18, stagger=0.02,
            out_t=out1 - 1.3, dur=0.9, alpha=fade)
    kinetic(c, "Cefor  |  Ifes", W / 2, 545, 32, t - 1.2, weight=500, color=MUTED, tracking=0.12, stagger=0.02, out_t=out1 - 2.0, alpha=fade)
    t2 = T - b(125.3)
    kinetic(c, "A complexidade faz parte da seleção.", W / 2, 470, 66, t2, weight=700, by="word", stagger=0.12, dur=1.0, alpha=fade)
    kinetic(c, "A fragmentação não precisa fazer.", W / 2, 570, 66, t2 - 1.8, weight=700, color=MINT, by="word", stagger=0.12, dur=1.0, alpha=fade)
    # assinatura
    ka = env(T, b(127.5), b(133), 1.2, 0.8)
    text(c, "SISTEMA DE PROCESSO SELETIVO", W / 2, 840, 22, 700, INK, ka * 0.9, "center", tracking=0.22)
    text(c, "Centro de Referência em Formação e em Educação a Distância  ·  Instituto Federal do Espírito Santo", W / 2, 882, 19, 450, MUTED, ka * 0.8, "center", tracking=0.02)
