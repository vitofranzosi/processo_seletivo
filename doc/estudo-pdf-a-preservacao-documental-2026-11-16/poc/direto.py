"""Simula a geração direta: acrescenta ao PDF do GPS só o que a ISO 19005-2 cobra, sem reescrever o conteúdo.
/ID determinístico, XMP com pdfaid, OutputIntent sRGB e /F 4 (imprimível) nas anotações."""
import hashlib, sys
from pathlib import Path
import pikepdf
icc = Path("/usr/share/color/icc/ghostscript/srgb.icc").read_bytes()
Path("saida/direto").mkdir(exist_ok=True)
for nome, nivel in [("I1-edital-gps", "B"), ("I1-edital-gps", "U"), ("I4-relatorio-gps", "U"), ("I2-comprovante-gps", "B")]:
    origem = Path(f"amostras/{nome}.pdf")
    with pikepdf.open(origem) as pdf:
        perfil = pdf.make_stream(icc); perfil.N = 3
        pdf.Root.OutputIntents = pikepdf.Array([pikepdf.Dictionary(Type=pikepdf.Name.OutputIntent, S=pikepdf.Name.GTS_PDFA1,
            OutputConditionIdentifier=pikepdf.String("sRGB"), DestOutputProfile=perfil)])
        for pagina in pdf.pages:
            for anotacao in pagina.get("/Annots", []):
                anotacao.F = 4
        with pdf.open_metadata(set_pikepdf_as_editor=False) as m:
            m["pdfaid:part"] = "2"; m["pdfaid:conformance"] = nivel
        destino = Path(f"saida/direto/{nome}-2{nivel.lower()}.pdf")
        pdf.save(destino, static_id=True, deterministic_id=True)
    print(destino, origem.stat().st_size, "→", destino.stat().st_size)
