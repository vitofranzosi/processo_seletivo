"""Convocação e matrícula — versão para o público geral (7 compassos, 13,1 s; tempo local u).

Duas ideias: quem foi aprovado é chamado e acompanha pelo celular; a matrícula sai numa planilha
pronta para o sistema acadêmico. A planilha é a real: baixada da tela "Exportar para matrícula" do
Edital 51/2026 (aba Import_ModeloCefor, 34 colunas); o CPF não aparece no filme. Fila de suplentes, recortes, comunicações pendentes e formato de importação saíram."""
from kit import *
import os

DUR = 16.875
EXP_CROP = (0, 120, 1500, 1000)

def draw(c, u):
    T = u + 170.625
    background(c, T, grid=0.25, cam=(T * 8, -T * 6))
    # A. a convocação, no celular
    phones = [("m_ana_acomp51.png", 1160, -4), ("m_ana_conv51.png", 1580, 3)]
    for j, (img, cx, rz) in enumerate(phones):
        kj = e_out5(prog(u, 0.3 + j * 0.25, 1.2 + j * 0.25)) * (1 - e_in3(prog(u, 6.0, 6.6)))
        if kj > 0.01:
            device_phone(c, img, (0, 0, 1170, 2532), cx, 540 + (1 - kj) * 800, 900, alpha=clamp(kj * 1.5), rz=rz * 0.3)
    caption_block(c, u, 0.4, 6.1, "Aprovado?", None, 146, 450, 84, tag_s="04 · Convocação")
    kinetic(c, "A convocação chega.", 146, 550, 70, u - 0.8, weight=780, align="left", out_t=6.1 - 0.8, color=MINT)
    kinetic(c, "E cada pessoa acompanha a", 150, 625, 32, u - 1.3, weight=480, align="left", color=MUTED, out_t=6.1 - 1.3,
            stagger=0.01, rise=0.3, blur_in=4)
    kinetic(c, "própria situação, pelo celular.", 150, 668, 32, u - 1.4, weight=480, align="left", color=MUTED, out_t=6.1 - 1.4,
            stagger=0.01, rise=0.3, blur_in=4)
    # B. a matrícula: do requerimento à planilha, da planilha ao sistema acadêmico
    if u > 6.3:
        kout = e_in3(prog(u, 16.2, DUR))
        kp = e_out5(prog(u, 6.4, 7.2)) * (1 - kout)
        device_phone(c, "m_ana_req51.png", (0, 0, 1170, 2532), 270, 480 + (1 - e_out5(prog(u, 6.4, 7.2))) * 800 - 900 * kout, 640, alpha=clamp(kp * 1.5))
        ks = e_out5(prog(u, 7.6, 8.4)) * (1 - kout)
        fill = prog(u, 8.6, 11.6)
        sheet(c, 520, 160, 1010, 500, ks, fill)
        kb = e_out5(prog(u, 12.0, 12.8)) * (1 - kout)
        sistema(c, 1580, 250, 290, 270, kb, prog(u, 13.0, 14.0))
        flow(c, (395, 420), (515, 400), prog(u, 8.0, 8.7) * (1 - kout))
        flow(c, (1535, 400), (1575, 400), prog(u, 12.4, 13.0) * (1 - kout))
        la = env(u, 7.0, 16.2, 0.4, 0.4)
        tag(c, "Requerimento · candidato", 110, 132, la, size=16)
        tag(c, "Planilha gerada pelo sistema", 520, 140, la * ks, size=16)
        tag(c, "Sistema acadêmico", 1580, 230, la * kb, size=16)
    # o Requerimento de Matrícula é opcional por Edital (na inscrição, na convocação ou nenhum): é recurso
    # das seleções de estudantes, e a legenda diz a condição
    cap(c, u, 6.8, 16.0, "Matrícula: planilha pronta.",
        "Quando o Edital pede o Requerimento de Matrícula, o sistema gera a planilha no modelo do sistema acadêmico.",
        tag_s="Seleção de estudantes")

# ---------------------------------------------------------------- a planilha real
from openpyxl import load_workbook as _lw
_wb = _lw(os.path.join(ROOT, "matriculas51.xlsx")).worksheets[0]
_HEAD = [c.value for c in _wb[1]]
_ROW = [c.value for c in _wb[2]]
COLS = ["INSC", "NOME", "EMAIL", "DATA_NASCIMENTO", "CIDADE", "ESTADO"]
WIDTH = {"INSC": 1.45, "NOME": 0.85, "EMAIL": 1.25, "DATA_NASCIMENTO": 1.2, "CIDADE": 0.75, "ESTADO": 0.6}
SHEET_NAME = _wb.title

def sheet(c, x, y, w, h, a, fill):
    if a <= 0.01: return
    c.drawRRect(skia.RRect.MakeRectXY(rect(x, y + 20, w, h), 14, 14), paint("#000000", 0.45 * a, 30))
    c.drawRRect(skia.RRect.MakeRectXY(rect(x, y, w, h), 14, 14), paint("#ffffff", a))
    # barra de título com o nome do arquivo
    c.save(); c.clipRRect(skia.RRect.MakeRectXY(rect(x, y, w, h), 14, 14), True)
    c.drawRect(rect(x, y, w, 56), paint("#1d6f42", a))
    icon(c, "sheet", x + 16, y + 10, 30, 36, alpha=a)
    text(c, "matriculas-51-2026.xlsx", x + 60, y + 37, 22, 650, "#ffffff", a)
    # grade
    gx, gy = x + 18, y + 80
    tot = sum(WIDTH[k] for k in COLS)
    cw = [(w - 36) * WIDTH[k] / tot for k in COLS]
    rh = 58
    hp = paint("#1d6f42", 0.12 * a)
    c.drawRect(rect(gx, gy, w - 36, rh), hp)
    cx = gx
    for i, k in enumerate(COLS):
        text(c, k, cx + 10, gy + 36, 16, 700, "#1d6f42", a, family="Menlo")
        cx += cw[i]
    # a linha da Ana se preenche coluna a coluna
    row = dict(zip(_HEAD, _ROW))
    cx = gx
    for i, k in enumerate(COLS):
        ki = clamp(fill * len(COLS) - i)
        v = str(row.get(k) or "")
        if ki > 0:
            c.drawRect(rect(cx, gy + rh, cw[i], rh), paint(MINT, 0.25 * (1 - ki) * a))
            n = int(len(v) * ki)
            sz = 21
            while text_width(v, sz, 500) > cw[i] - 14 and sz > 10: sz -= 0.5
            text(c, v[:n], cx + 10, gy + rh + 38, sz, 500, "#222222", a)
        cx += cw[i]
    # linhas da grade e as linhas vazias abaixo
    gp = paint("#c8d2cc", a, style="stroke", stroke=1)
    for j in range(6):
        c.drawLine(gx, gy + j * rh, gx + w - 36, gy + j * rh, gp)
    cx = gx
    for i in range(len(COLS) + 1):
        c.drawLine(cx, gy, cx, gy + 5 * rh, gp)
        if i < len(COLS): cx += cw[i]
    text(c, f"… e mais {len(_HEAD) - len(COLS)} colunas no modelo de importação", gx, gy + 5 * rh + 40, 18, 500, "#5b6b62", a)
    # aba da planilha
    tw = text_width(SHEET_NAME, 16, 600, family="Menlo") + 30
    c.drawRect(rect(x + 18, y + h - 44, tw, 34), paint("#e8f1ec", a))
    c.drawRect(rect(x + 18, y + h - 12, tw, 3), paint("#1d6f42", a))
    text(c, SHEET_NAME, x + 33, y + h - 21, 16, 600, "#1d6f42", a, family="Menlo")
    c.restore()

def sistema(c, x, y, w, h, a, k):
    if a <= 0.01: return
    rrect(c, x, y, w, h, 18, "#0f2a1d", a)
    rrect(c, x, y, w, h, 18, GREEN, 0.9 * a, style="stroke", stroke=2)
    # um cilindro: banco de dados
    cx, cy, rw, rh = x + w / 2, y + 70, 70, 20
    body = skia.Path(); body.addRect(rect(cx - rw, cy, 2 * rw, 80))
    c.drawRect(rect(cx - rw, cy, 2 * rw, 80), paint(GREEN, 0.25 * a))
    for yy in (cy, cy + 40, cy + 80):
        c.drawOval(rect(cx - rw, yy - rh, 2 * rw, 2 * rh), paint(GREEN, 0.9 * a, style="stroke", stroke=3))
    c.drawLine(cx - rw, cy, cx - rw, cy + 80, paint(GREEN, 0.9 * a, style="stroke", stroke=3))
    c.drawLine(cx + rw, cy, cx + rw, cy + 80, paint(GREEN, 0.9 * a, style="stroke", stroke=3))
    text(c, "Registro Acadêmico", cx, y + 210, 22, 650, INK, a, "center")
    text(c, "importa a planilha", cx, y + 244, 18, 450, MUTED, a, "center")
    if k > 0:
        c.drawCircle(cx + rw - 6, cy - 30, 22 * e_outback(k, 1.4), paint(GREEN, a))
        pth = skia.Path(); pth.moveTo(cx + rw - 16, cy - 30); pth.lineTo(cx + rw - 9, cy - 22); pth.lineTo(cx + rw + 4, cy - 38)
        c.drawPath(pth, paint("#ffffff", a * clamp(k * 2), style="stroke", stroke=4))

def flow(c, p0, p1, k):
    if k <= 0: return
    bezier(c, p0, (lerp(p0[0], p1[0], 0.5), p0[1]), (lerp(p0[0], p1[0], 0.5), p1[1]), p1, GREEN, 0.95, 4, k=e_out3(k))
    if k >= 1:
        path = skia.Path(); path.moveTo(p1[0], p1[1]); path.lineTo(p1[0] - 14, p1[1] - 9); path.lineTo(p1[0] - 14, p1[1] + 9); path.close()
        c.drawPath(path, paint(GREEN, 1))
