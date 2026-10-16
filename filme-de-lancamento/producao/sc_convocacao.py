"""III-d. Do resultado à convocação (b78 – b94)."""
from kit import *
from timeline import *

T0 = b(78)

def draw(c, T):
    background(c, T, grid=0.25 * prog(T, b(80), b(81)), cam=(T * 8, -T * 6), intensity=0.6 + 0.4 * prog(T, b(80), b(81.5)))
    # A. respiro
    if T < b(81.0):
        k = env(T, T0, b(81.0), 1.2, 0.6)
        tag(c, "04 · Convocação", W / 2 - 90, 380, env(T, T0 + 0.4, b(80.7), 0.5, 0.4))
        kinetic(c, "O resultado não encerra", W / 2, 520, 92, T - T0 - 0.6, weight=760, out_t=b(80.6) - T0 - 0.6, stagger=0.08, by="word", dur=1.0)
        kinetic(c, "a jornada.", W / 2, 630, 92, T - T0 - 1.6, weight=760, color=MINT, out_t=b(80.6) - T0 - 1.6, stagger=0.1, by="word", dur=1.0)
    # B. a situação de cada pessoa
    if b(80.95) < T < b(83.6):
        kin = e_out5(prog(T, b(80.95), b(81.6))); kout = e_in3(prog(T, b(83.0), b(83.6)))
        CR = (0, 330, 1430, 1270)
        d = Card("p_ana_acomp51.png", CR, moved(frame_in(CR, ZONE_RIGHT), dx=900 * (1 - kin), dy=-1150 * kout)).draw(c, 1, glow=0.2)
        d.focus(c, union(dom("p_ana_acomp51", "Sua situação", "h2"), dom("p_ana_acomp51", "Convocação para vaga inicial", "ul")),
                prog(T, b(81.4), b(81.9)) * (1 - kout), pad=10, color=MINT)
        d.focus(c, dom("p_ana_acomp51", "Se você discordar de Ampla", "p"), prog(T, b(82.1), b(82.5)) * (1 - kout), pad=8)
        caption_block(c, T, b(81.1), b(83.0), "Situação individual.", "Cada pessoa sabe onde está — e por quê.", 110, 560, 66,
                      tag_s="Acompanhamento", wrap=560)
    # C. convocação: titular e fila
    if b(83.2) < T < b(87.0):
        kin = e_out5(prog(T, b(83.2), b(83.9))); kout = e_in3(prog(T, b(86.4), b(87.0)))
        K1, K2 = (0, 860, 1480, 690), (0, 2050, 1480, 690)
        crop = cam_at(T, [(b(84.8), K1), (b(85.5), K2)])
        cv = Card("g_convocacao51.png", crop, moved(frame_in(K1, ZONE_BOTTOM), dx=1000 * (1 - kin), dy=-1100 * kout)).draw(c, 1, glow=0.2)
        cv.focus(c, union(dom("g_convocacao51", "1 Publicadas", "li"), dom("g_convocacao51", "Responderam", "li"), dom("g_convocacao51", "0 A ocupar", "li")),
                 prog(T, b(84.0), b(84.5)) * (1 - prog(T, b(84.8), b(85.0))), pad=8, color=MINT)
        cv.focus(c, union(dom("g_convocacao51", "Bruno Costa", "li"), dom("g_convocacao51", "Clara Dias", "li")),
                 prog(T, b(85.6), b(86.0)) * (1 - kout), pad=10)
        tag(c, "Titulares · suplentes · próxima da fila", 1130, 1000, env(T, b(85.5), b(86.5), 0.3, 0.3))
        caption_block(c, T, b(83.4), b(86.4), "Da classificação", None, 150, 932, 64, tag_s="Convocação")
        kinetic(c, "à convocação.", 150, 1010, 64, T - b(83.7), weight=780, align="left", out_t=b(86.4) - b(83.7), color=MINT)
    # D. Requerimento de Matrícula, pelo portal
    if b(86.5) < T < b(90.0):
        kin = e_out5(prog(T, b(86.5), b(87.2))); kout = e_in3(prog(T, b(89.4), b(90.0)))
        CC = (0, 130, 1440, 1110)
        cc = Card("p_ana_conv51.png", CC, moved(frame_in(CC, (70, 46, 1290, 818)), dx=-1100 * (1 - kin), dy=-1000 * kout)).draw(c, 1, glow=0.15)
        cc.focus(c, dom("p_ana_conv51", "Requerimento de Matrícula enviado", "p"), prog(T, b(87.6), b(88.0)) * (1 - kout), pad=8, color=MINT)
        kp = e_out5(prog(T, b(87.0), b(87.8)))
        device_phone(c, "m_ana_req51.png", (0, 0, 1170, 2532), 1560, 470 + 700 * (1 - kp) - 1300 * kout, 760, alpha=kp)
        cap(c, T, b(86.9), b(89.5), "Requerimento de Matrícula.", "Declarado pelo próprio candidato, no portal.", tag_s="Depois da convocação")
    # E. exportação para o Registro Acadêmico
    if b(89.6) < T < b(94.0):
        kin = e_out5(prog(T, b(89.6), b(90.3))); kout = e_in3(prog(T, b(93.3), b(94.0)))
        K1, K2 = (0, 480, 1600, 720), (0, 1100, 2880, 1300)
        K3 = (0, 1340, 2880, 1300)
        crop = cam_at(T, [(b(90.9), K1), (b(91.6), K2), (b(92.2), K2), (b(92.6), K3)])
        # a câmera recua do filtro (de perto) para o arquivo inteiro: a pose acompanha a largura do recorte
        pose = frame_in(crop, ZONE_BOTTOM)
        m = Card("g_matriculas51_prev.png", crop, moved(pose, dx=1000 * (1 - kin), dy=-1100 * kout)).draw(c, 1, glow=0.2)
        m.focus(c, dom("g_matriculas51_prev", "Quem entra no arquivo", "p"), prog(T, b(90.4), b(90.8)) * (1 - prog(T, b(90.9), b(91.1))), pad=8, color=MINT)
        m.focus(c, dom("g_matriculas51_prev", "RENDA_PER_CAPITA", "dl"), prog(T, b(91.7), b(92.0)) * (1 - prog(T, b(92.2), b(92.4))), pad=8, color=MINT)
        BTN = dom("g_matriculas51_prev", "Baixar o arquivo", "button")
        m.focus(c, BTN, prog(T, b(92.6), b(92.9)) * (1 - kout), pad=8)
        # o arquivo sai do sistema
        kf = prog(T, b(92.9), b(93.7))
        if kf > 0:
            p0 = m.to_screen(BTN[0] + BTN[2] / 2, BTN[1] + BTN[3] / 2)
            x = lerp(p0[0], 1750, e_in3(kf)); y = lerp(p0[1], 300, e_io3(kf))
            icon(c, "sheet", x - 50, y - 62, 100, 124, alpha=1 - e_in3(prog(kf, 0.7, 1)))
        cap(c, T, b(90.0), b(93.6), "Dados prontos para o Registro Acadêmico.",
            "O sistema prepara o arquivo; a matrícula é efetivada no sistema acadêmico.", tag_s="Exportar para matrícula")
