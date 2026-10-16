"""III-b. Da oportunidade à inscrição (b46 – b62)."""
from kit import *
from timeline import *

T0 = b(46)
LIST_CROP = (0, 120, 1300, 1290)
P_LIST = frame_in(LIST_CROP, ZONE_RIGHT)
ACESSO_CROP = (0, 100, 1300, 820)

# os estados da inscrição, na ordem em que aconteceram: (início, captura, deslocamento vertical)
STATES = [(b(54.0), "p_insc01_1", 0), (b(54.7), "p_insc01_2_modalidade", 1250), (b(55.3), "p_insc01_3_arquivo0", 1780),
          (b(55.7), "p_insc01_4_enviado0", 1780), (b(56.1), "p_insc01_4_enviado1", 1780),
          (b(56.6), "p_insc01_7_pronta", 1830), (b(57.15), "p_insc01_9_revisao_ok", 1320),
          (b(57.7), "p_insc01_11_comprovante", 0)]

def draw(c, T):
    background(c, T, grid=0.3, cam=(-T * 14, 0))
    # A. o formulário avulso se desdobra no portal
    morph = e_io3(prog(T, T0 + 0.9, b(47.6)))
    if T < b(49.7):
        pose = P_LIST
        if T > b(48.9):
            e = e_in3(prog(T, b(48.9), b(49.7)))
            pose = moved(pose, dx=200 * e, dy=-1150 * e, alpha=1 - e)
        img = "pub_portal_depois.png" if T < b(48.25) else "p_lista_busca.png"
        cd = Card(img, LIST_CROP, pose)
        q = cd.quad
        if morph < 1:
            k = e_out3(prog(T, T0 + 0.1, T0 + 0.7))
            x0, y0, w0, h0 = 1240, 330, 300 * k, 380 * k
            minx = min(p[0] for p in q); maxx = max(p[0] for p in q); miny = min(p[1] for p in q); maxy = max(p[1] for p in q)
            x = lerp(x0, minx, morph); y = lerp(y0, miny, morph); w = lerp(w0, maxx - minx, morph); h = lerp(h0, maxy - miny, morph)
            m = smooth(prog(morph, 0.4, 0.9))
            if m < 1:
                icon(c, "form", x, y, w, h, alpha=(1 - m) * k)
            if m > 0:
                cd.draw(c, m, glow=0.2)
        else:
            cd.draw(c, pose.alpha, glow=0.2)
        # digitando a busca
        if b(47.6) < T < b(49.0):
            pin = cd.to_screen(120, 510)
            cursor(c, *path_at(T, [(b(47.6), (1500, 900)), (b(47.95), cd.to_screen(400, 520))]), alpha=env(T, b(47.6), b(48.9), 0.2, 0.2),
                   press=env(T, b(47.95), b(48.05), 0.02, 0.06))
            typed = "informática"[: int(clamp((T - b(48.0)) / 0.4) * 11)]
            if T < b(48.25) and typed:
                sz = 34 * cd.pose.w / 2880
                text(c, typed, pin[0], pin[1] + sz * 0.35, sz, 400, "#222222", 1)
            cd.focus(c, (48, 386, 2432, 199), prog(T, b(47.7), b(48.2)) * (1 - prog(T, b(48.6), b(48.9))), pad=4)
        cd.focus(c, (48, 717, 1200, 672), prog(T, b(48.3), b(48.8)) * (1 - prog(T, b(48.9), b(49.1))), pad=8, color=MINT)
    caption_block(c, T, T0 + 0.2, b(47.3), "Da oportunidade", None, 150, 470, 80, tag_s="02 · Inscrição")
    kinetic(c, "à inscrição.", 150, 565, 80, T - T0 - 0.45, weight=780, align="left", out_t=b(47.3) - T0 - 0.45, color=MINT)
    big_word(c, T, b(47.6), b(48.75), "Encontre.")
    # B. o Edital no portal
    if b(49.0) < T < b(52.4):
        kin = e_out5(prog(T, b(49.15), b(49.9))); kout = e_in3(prog(T, b(51.85), b(52.3)))
        sy = lerp(0, 1150, e_io3(prog(T, b(50.0), b(51.0))))
        crop = (0, sy, 2880, 1250)
        pose = moved(frame_in(crop, ZONE_BOTTOM), dx=1200 * (1 - kin) - 1900 * kout)
        cd = Card("p_edital01.png", crop, pose).draw(c, pose.alpha, glow=0.2)
        cd.focus(c, (48, 1356, 2112, 700), prog(T, b(50.8), b(51.2)) * (1 - kout), pad=10, color=MINT)
        cd.focus(c, (2224, 1356, 608, 900), prog(T, b(50.9), b(51.3)) * (1 - kout), pad=10, color=MINT)
        btn = cd.to_screen(1454 + 240, 1857 + 42)
        cursor(c, *path_at(T, [(b(51.0), (1700, 780)), (b(51.4), btn)]), alpha=env(T, b(51.0), b(52.0), 0.2, 0.2), press=env(T, b(51.45), b(51.55), 0.02, 0.06))
        ripple(c, *btn, prog(T, b(51.5), b(51.5) + 0.6))
        tag(c, "Vagas, requisitos, documentos e datas", 154, 900, env(T, b(49.6), b(52.0), 0.3, 0.3))
    # C. acesso por código
    if b(52.25) < T < b(54.4):
        kin = e_out5(prog(T, b(52.25), b(52.8))); kout = e_in3(prog(T, b(53.8), b(54.3)))
        steps = [(b(52.25), "p_ana_acesso_vazio"), (b(52.5), "p_ana_acesso_email"), (b(52.95), "p_ana_codigo"), (b(53.3), "p_ana_codigo_preenchido")]
        cur = [s for s in steps if T >= s[0]][-1]
        pose = moved(frame_in(ACESSO_CROP, ZONE_RIGHT),
                     dy=300 * (1 - kin) - 1000 * kout, alpha=kin * (1 - kout))
        cd = Card(cur[1] + ".png", ACESSO_CROP, pose).draw(c, pose.alpha, glow=0.25)
        # código de seis dígitos digitado
        if cur[1] == "p_ana_codigo":
            pass
        e_in = cd.to_screen(48 + 300, 390 + 42)
        cursor(c, *path_at(T, [(b(52.3), (1600, 950)), (b(52.6), cd.to_screen(180, 548)), (b(53.1), cd.to_screen(180, 548))]),
               alpha=env(T, b(52.3), b(53.7), 0.2, 0.2), press=max(env(T, b(52.62), b(52.72), 0.02, 0.06), env(T, b(53.45), b(53.55), 0.02, 0.06)))
        caption_block(c, T, b(52.3), b(53.45), "Sem senha.", "Basta o e-mail: um código chega na hora.", 150, 560, 84,
                      tag_s="Acesso por código", wrap=540)
    # D. a inscrição, estado a estado
    if b(53.9) < T < b(59.0):
        idx = max(i for i, s in enumerate(STATES) if T >= s[0]) if T >= STATES[0][0] else 0
        cur = STATES[idx]; prev = STATES[idx - 1] if idx else None
        k = e_out3(prog(T, cur[0], cur[0] + 0.35)) if prev else 1
        sy = lerp(prev[2], cur[2], e_io3(prog(T, cur[0], cur[0] + 0.6))) if prev else cur[2]
        kin = e_out5(prog(T, b(54.0), b(54.6))); kout = e_in3(prog(T, b(58.4), b(59.0)))
        CR = (0, 0, 2880, 1250)
        pose = moved(frame_in(CR, ZONE_BOTTOM), dx=900 * (1 - kin), dy=-1100 * kout)
        hd = 330
        cd = Card(cur[1] + ".png", CR, pose)
        cd.frame(c, 1 - kout, glow=0.2)
        if prev and k < 1:
            cd.region(c, (0, hd, 2880, 1250 - hd), img=prev[1] + ".png", offset=(0, sy), alpha=(1 - k) * (1 - kout))
        cd.region(c, (0, hd, 2880, 1250 - hd), offset=(0, sy), alpha=(k if prev else 1) * (1 - kout))
        cd.region(c, (0, 0, 2880, hd), alpha=1 - kout)
        cd.border(c, 1 - kout)
        if cur[1].endswith("comprovante"):
            cd.focus(c, (2380, 540, 460, 120), prog(T, cur[0] + 0.5, cur[0] + 1.0) * (1 - kout), pad=8)
            cd.focus(c, (48, 510, 2784, 160), prog(T, cur[0] + 0.3, cur[0] + 0.8) * (1 - kout), pad=6, color=MINT)
        cap(c, T, b(54.2), b(58.5), "Inscreva-se.", "Envie os documentos, revise e receba o comprovante.",
            tag_s="Do rascunho ao comprovante")
    # E. acompanhar, no celular e no computador
    if T > b(58.6):
        tE = T - b(58.6)
        kout = e_in3(prog(T, b(61.4), b(62)))
        kin = e_out5(prog(tE, 0, 0.9))
        Card("p_ana_acomp51.png", (0, 0, 2880, 1900), moved(frame_in((0, 0, 2880, 1900), ZONE_RIGHT), dx=600 * (1 - kin), dy=-900 * kout)).draw(c, 0.9 * kin * (1 - kout), glow=0.15)
        phones = [("m_ana_minhas.png", 1010, -10), ("m_ana_acomp51.png", 1360, 0), ("m_insc01_comprovante.png", 1710, 10)]
        for j, (img, cx, rz) in enumerate(phones):
            kj = e_out5(prog(tE, 0.25 + j * 0.18, 1.1 + j * 0.18))
            from engine import image as _im
            ih = min(_im(img).height(), 2532)
            device_phone(c, img, (0, 0, 1170, ih * 0 + 2532), cx + 40 * math.sin(T * 0.6 + j), 600 + (1 - kj) * 700 - 900 * kout,
                         720, alpha=kj, ry=-18 + j * 8, rz=rz * 0.4)
        caption_block(c, T, b(58.8), b(61.5), "Acompanhe.", "No computador ou no celular.", 120, 560, 92, wrap=560)

def big_word(c, T, t0, t1, s):
    if T < t0 or T > t1 + 0.6: return
    scrim(c, 0.7 * env(T, t0, t1 + 0.4, 0.3, 0.4), "left", 0.45)
    kinetic(c, s, 150, 600, 120, T - t0, weight=800, align="left", out_t=t1 - t0, color=INK, stagger=0.035)
