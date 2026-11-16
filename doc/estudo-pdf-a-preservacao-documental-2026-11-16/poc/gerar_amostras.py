"""Amostras sintéticas de documentos 'de candidato' — nenhum dado pessoal real."""
import io, random, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import pikepdf

D = Path(sys.argv[1]); random.seed(7)
TEXTO = ("DECLARAÇÃO DE EXPERIÊNCIA PROFISSIONAL — FICTÍCIA. Declaramos, para os devidos fins, que "
         "FULANA DE TAL EXEMPLO, CPF 000.000.000-00, atuou como tutora a distância no período de "
         "março de 2020 a dezembro de 2023, com carga horária de 20 horas semanais. Ação, coração, "
         "útil, pôr, à, ç, ã, õ, ü.").split()

def paragrafos(c, x, y, fonte, tam, largura=480):
    linha = ""
    for p in TEXTO * 3:
        t = (linha + " " + p).strip()
        if c.stringWidth(t, fonte, tam) > largura:
            c.drawString(x, y, linha); y -= tam * 1.4; linha = p
        else:
            linha = t
    c.drawString(x, y, linha)

# C1: textual convencional, Helvetica NÃO embutida (como muitos geradores 'leves')
c = canvas.Canvas(str(D / "C1-textual-helvetica.pdf"), pagesize=A4)
c.setFont("Helvetica-Bold", 14); c.drawString(56, 780, "Declaração (amostra sintética)")
c.setFont("Helvetica", 11); paragrafos(c, 56, 750, "Helvetica", 11); c.save()

# C1b: textual com fonte embutida (como Word/LibreOffice exportam)
pdfmetrics.registerFont(TTFont("DejaVu", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
c = canvas.Canvas(str(D / "C1b-textual-fonte-embutida.pdf"), pagesize=A4)
c.setFont("DejaVu", 14); c.drawString(56, 780, "Declaração (amostra sintética)")
c.setFont("DejaVu", 11); paragrafos(c, 56, 750, "DejaVu", 11); c.save()

# C2: digitalizado — página rasterizada, ruído, leve rotação, JPEG (foto de celular / scanner)
subprocess.run(["pdftoppm", "-r", "200", "-gray", "-png", "-singlefile", str(D / "C1b-textual-fonte-embutida.pdf"), "/tmp/scan"], check=True)
im = Image.open("/tmp/scan.png").convert("L").rotate(0.7, fillcolor=235, expand=False)
px = im.load()
for _ in range(60000):
    x, y = random.randrange(im.width), random.randrange(im.height); px[x, y] = max(0, px[x, y] - random.randrange(60))
im = im.filter(ImageFilter.GaussianBlur(0.6))
buf = io.BytesIO(); im.save(buf, "JPEG", quality=70, dpi=(200, 200))
import img2pdf
(D / "C2-digitalizado.pdf").write_bytes(img2pdf.convert(buf.getvalue()))

# C3: múltiplas páginas com imagens coloridas (fotos sintéticas) e texto
c = canvas.Canvas(str(D / "C3-multipagina-imagens.pdf"), pagesize=A4)
for pagina in range(6):
    img = Image.new("RGB", (1600, 1100))
    d = ImageDraw.Draw(img)
    for _ in range(400):
        x, y = random.randrange(1600), random.randrange(1100)
        d.ellipse([x, y, x + random.randrange(20, 200), y + random.randrange(20, 200)], fill=tuple(random.randrange(256) for _ in range(3)))
    img = img.filter(ImageFilter.GaussianBlur(3))
    b = io.BytesIO(); img.save(b, "JPEG", quality=85); b.seek(0)
    from reportlab.lib.utils import ImageReader
    c.setFont("Helvetica", 12); c.drawString(56, 800, f"Certificado fictício — página {pagina + 1}")
    c.drawImage(ImageReader(b), 56, 380, width=480, height=330)
    c.setFillColorRGB(0.1, 0.3, 0.7, alpha=0.4); c.rect(56, 300, 200, 60, fill=1, stroke=0)  # transparência
    c.setFillColorRGB(0, 0, 0, alpha=1)
    c.showPage()
c.save()

# C5: com JavaScript e formulário (problemático para PDF/A)
from reportlab.lib.colors import black
c = canvas.Canvas(str(D / "C5-js-formulario.pdf"), pagesize=A4)
c.setFont("Helvetica", 12); c.drawString(56, 780, "Formulário fictício com campo e script")
c.acroForm.textfield(name="nome", tooltip="Nome", x=56, y=700, width=300, height=20, value="Fulana Exemplo")
c.save()
with pikepdf.open(D / "C5-js-formulario.pdf", allow_overwriting_input=True) as p:
    p.Root.OpenAction = pikepdf.Dictionary(S=pikepdf.Name.JavaScript, JS=pikepdf.String("app.alert('oi');"))
    p.save(D / "C5-js-formulario.pdf")

# C6: protegido por senha de abertura
subprocess.run(["qpdf", "--encrypt", "senha", "dono", "256", "--", str(D / "C1-textual-helvetica.pdf"), str(D / "C6-protegido-senha.pdf")], check=True)
# C6b: com restrição de permissões, sem senha de abertura (comum em documentos de instituições)
subprocess.run(["qpdf", "--encrypt", "", "dono", "256", "--modify=none", "--extract=n", "--", str(D / "C1b-textual-fonte-embutida.pdf"), str(D / "C6b-restricao-sem-senha.pdf")], check=True)
# C7: corrompido (truncado na metade)
dados = (D / "C3-multipagina-imagens.pdf").read_bytes(); (D / "C7-truncado.pdf").write_bytes(dados[: len(dados) // 2])
# C8: declara PDF/A no XMP sem ser (alegação falsa)
with pikepdf.open(D / "C1-textual-helvetica.pdf") as p:
    with p.open_metadata(set_pikepdf_as_editor=False) as m:
        m["pdfaid:part"] = "2"; m["pdfaid:conformance"] = "B"
    p.save(D / "C8-falso-pdfa.pdf")
print("ok")
