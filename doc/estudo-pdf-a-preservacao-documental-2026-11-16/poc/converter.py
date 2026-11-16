"""Converte cada amostra para PDF/A-2b com Ghostscript e mede fidelidade (página, imagem, texto, assinatura)."""
import difflib, hashlib, json, os, re, subprocess, time
from pathlib import Path
import pikepdf
from PIL import Image, ImageChops

A, S = Path("amostras"), Path("saida")
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def texto(p):
    r = subprocess.run(["pdftotext", "-q", str(p), "-"], capture_output=True, text=True)
    return re.sub(r"\s+", " ", r.stdout).strip()
def paginas_png(p, prefixo):
    for f in Path("/tmp").glob(prefixo + "*"): f.unlink()
    subprocess.run(["pdftoppm", "-q", "-r", "72", "-png", str(p), f"/tmp/{prefixo}"], capture_output=True)
    return sorted(Path("/tmp").glob(prefixo + "*.png"))
def inspecionar(p):
    info = {"cifrado": False, "assinaturas": 0, "alega_pdfa": None, "paginas": None, "erro": None}
    try:
        with pikepdf.open(p) as d:
            info["cifrado"] = d.is_encrypted
            info["paginas"] = len(d.pages)
            campos = d.Root.get("/AcroForm", {}).get("/Fields", []) if "/AcroForm" in d.Root else []
            info["assinaturas"] = sum(1 for c in campos if c.get("/FT") == "/Sig")
            try:
                m = d.open_metadata()
                parte = m.get("pdfaid:part")
                info["alega_pdfa"] = f"{parte}{m.get('pdfaid:conformance','')}" if parte else None
            except Exception:
                pass
    except pikepdf.PasswordError:
        info["cifrado"] = True; info["erro"] = "senha de abertura"
    except Exception as e:
        info["erro"] = type(e).__name__ + ": " + str(e)[:80]
    return info
def validar_assinatura(p):
    try:
        from pyhanko.pdf_utils.reader import PdfFileReader
        from pyhanko.sign.validation import validate_pdf_signature
        from pyhanko_certvalidator import ValidationContext
        from pyhanko.keys import load_cert_from_pemder
        vc = ValidationContext(trust_roots=[load_cert_from_pemder("saida/cert-teste.pem")])
        with open(p, "rb") as f:
            r = PdfFileReader(f, strict=False)
            return [{"intacta": s.intact, "valida": s.valid, "cobre": str(s.coverage).split(".")[-1]} for s in (validate_pdf_signature(e, vc) for e in r.embedded_signatures)]
    except Exception as e:
        return [{"erro": type(e).__name__}]

def converter(origem, destino, politica=1, env=None):
    cmd = ["gs", "-q", "-dPDFA=2", "-dBATCH", "-dNOPAUSE", "-dSAFER", "--permit-file-read=/usr/share/color/icc/ghostscript/srgb.icc", "--permit-file-read=/poc/PDFA_def.ps",
           f"-dPDFACompatibilityPolicy={politica}", "-sColorConversionStrategy=RGB", "-sDEVICE=pdfwrite",
           f"-sOutputFile={destino}", "/poc/PDFA_def.ps", str(origem)]
    t = time.perf_counter()
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300, env=env)
    return r.returncode, round(time.perf_counter() - t, 3), (r.stdout + r.stderr).strip().splitlines()[-6:]

resultados = []
for origem in sorted(A.glob("*.pdf")):
    destino = S / (origem.stem + ".pdfa.pdf")
    linha = {"amostra": origem.name, "bytes": origem.stat().st_size, "sha256": sha(origem)[:16], **inspecionar(origem)}
    if linha["assinaturas"]:
        linha["assinatura_antes"] = validar_assinatura(origem)
    rc, seg, msgs = converter(origem, destino)
    linha.update(gs_rc=rc, gs_segundos=seg, gs_msgs=msgs)
    if rc == 0 and destino.exists() and destino.stat().st_size:
        linha["bytes_pdfa"] = destino.stat().st_size
        linha["variacao_tamanho"] = round(destino.stat().st_size / origem.stat().st_size, 2)
        depois = inspecionar(destino); linha["paginas_pdfa"] = depois["paginas"]; linha["assinaturas_pdfa"] = depois["assinaturas"]
        if linha["assinaturas"]:
            linha["assinatura_depois"] = validar_assinatura(destino)
        ta, tb = texto(origem), texto(destino)
        linha["texto_chars"] = (len(ta), len(tb)); linha["texto_igual"] = round(difflib.SequenceMatcher(None, ta, tb).ratio(), 4) if (ta or tb) else None
        pa, pb = paginas_png(origem, "a_"), paginas_png(destino, "b_")
        difs = []
        for x, y in zip(pa, pb):
            ia, ib = Image.open(x).convert("RGB"), Image.open(y).convert("RGB")
            if ia.size != ib.size: difs.append(("tamanho", ia.size, ib.size)); continue
            d = ImageChops.difference(ia, ib).convert("L")
            hist = d.histogram(); total = sum(hist)
            difs.append(round(sum(hist[33:]) / total * 100, 3))  # % de pixels com diferença > 32/255
        linha["pixels_diferentes_pct_max"] = max([v for v in difs if isinstance(v, float)], default=None)
        linha["paginas_renderizadas"] = (len(pa), len(pb))
    elif destino.exists():
        destino.unlink()
    resultados.append(linha)
    print(origem.name, rc, seg, flush=True)

# Determinismo: a mesma entrada dá os mesmos bytes?
i2 = A / "I2-comprovante-gps.pdf"
converter(i2, "/tmp/d1.pdf"); time.sleep(1.1); converter(i2, "/tmp/d2.pdf")
env = dict(os.environ, SOURCE_DATE_EPOCH="1767225600")
converter(i2, "/tmp/d3.pdf", env=env); time.sleep(1.1); converter(i2, "/tmp/d4.pdf", env=env)
det = {"sem_epoch_iguais": sha("/tmp/d1.pdf") == sha("/tmp/d2.pdf"), "com_SOURCE_DATE_EPOCH_iguais": sha("/tmp/d3.pdf") == sha("/tmp/d4.pdf")}
# Política 2 (abortar) no caso com JavaScript, para ver o que a política 1 descartou em silêncio
det["js_politica_2"] = converter(A / "C5-js-formulario.pdf", "/tmp/js2.pdf", politica=2)[0::2]
Path("saida/conversao.json").write_text(json.dumps({"resultados": resultados, "determinismo": det}, ensure_ascii=False, indent=1))
print(json.dumps(det))
