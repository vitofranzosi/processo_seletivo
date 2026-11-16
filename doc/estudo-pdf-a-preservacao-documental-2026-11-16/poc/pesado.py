import io, random, subprocess, time
from PIL import Image, ImageDraw, ImageFilter
import img2pdf
random.seed(3); paginas = []
for i in range(20):
    im = Image.new("L", (2480, 3508), 240); d = ImageDraw.Draw(im)
    for l in range(90):
        y = 200 + l * 36
        for x in range(200, 2200, 22):
            if random.random() > 0.15: d.rectangle([x, y, x + 14 + random.randrange(6), y + 18], fill=random.randrange(10, 80))
    px = im.load()
    for _ in range(40000):
        x, y = random.randrange(2480), random.randrange(3508); px[x, y] = random.randrange(150, 255)
    b = io.BytesIO(); im.filter(ImageFilter.GaussianBlur(0.8)).convert("RGB").save(b, "JPEG", quality=80, dpi=(300, 300)); paginas.append(b.getvalue())
open("amostras/C9-digitalizado-20p-300dpi.pdf", "wb").write(img2pdf.convert(paginas))
cmd = ["gs", "-q", "-dPDFA=2", "-dBATCH", "-dNOPAUSE", "-dSAFER", "--permit-file-read=/usr/share/color/icc/ghostscript/srgb.icc", "--permit-file-read=/poc/PDFA_def.ps",
       "-dPDFACompatibilityPolicy=1", "-sColorConversionStrategy=RGB", "-sDEVICE=pdfwrite", "-sOutputFile=saida/C9.pdfa.pdf", "/poc/PDFA_def.ps", "amostras/C9-digitalizado-20p-300dpi.pdf"]
t = time.perf_counter(); subprocess.run(cmd, check=True); dt = time.perf_counter() - t
import os
print(f"C9: {os.path.getsize('amostras/C9-digitalizado-20p-300dpi.pdf')/1e6:.2f} MB → {os.path.getsize('saida/C9.pdfa.pdf')/1e6:.2f} MB em {dt:.2f}s")
