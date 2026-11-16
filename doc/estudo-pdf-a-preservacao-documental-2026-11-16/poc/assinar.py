"""Assina com certificado autoassinado de teste (PAdES B-B via pyHanko). Não é ICP-Brasil."""
import subprocess, sys
from pyhanko.sign import signers
from pyhanko.sign.fields import SigSeedSubFilter
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
subprocess.run("openssl req -x509 -newkey rsa:2048 -nodes -keyout /tmp/k.pem -out saida/cert-teste.pem -days 30 -subj '/CN=Assinante de Teste POC/O=Teste'", shell=True, check=True, capture_output=True)
signer = signers.SimpleSigner.load("/tmp/k.pem", "saida/cert-teste.pem")
for origem, destino in [(sys.argv[1], sys.argv[2])] + ([(sys.argv[3], sys.argv[4])] if len(sys.argv) > 4 else []):
    with open(origem, "rb") as f:
        w = IncrementalPdfFileWriter(f)
        meta = signers.PdfSignatureMetadata(field_name="Assinatura", subfilter=SigSeedSubFilter.PADES)
        with open(destino, "wb") as out:
            signers.sign_pdf(w, meta, signer=signer, output=out)
print("assinado")
