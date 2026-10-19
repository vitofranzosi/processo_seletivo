"""Coleta autorizada A2: GET de manifestos públicos, sem Docker, blobs ou camadas.

Tokens anônimos de escopo público ficam apenas em memória. Não lê configuração Docker,
proxies, credenciais locais nem arquivos do ambiente funcional. Saída exclusiva documental.
"""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request

FONTES = (
    ("postgres", "registry-1.docker.io", "library/postgres", "18", "auth.docker.io", "registry.docker.io"),
    ("python", "registry-1.docker.io", "library/python", "3.13-slim-bookworm", "auth.docker.io", "registry.docker.io"),
    ("uv", "ghcr.io", "astral-sh/uv", "0.9", "ghcr.io", "ghcr.io"),
)
ACEITAR = ", ".join(("application/vnd.oci.image.index.v1+json",
                     "application/vnd.docker.distribution.manifest.list.v2+json",
                     "application/vnd.oci.image.manifest.v1+json",
                     "application/vnd.docker.distribution.manifest.v2+json"))


class SemRedirecionamento(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise RuntimeError("Redirecionamento inesperado: interromper sem ampliar origens")


def consultar():
    destino = Path(__file__).with_name("metadados-publicos.json")
    if destino.exists():
        raise RuntimeError("Evidência existente: não sobrescrever consulta anterior")
    cliente = urllib.request.build_opener(urllib.request.ProxyHandler({}), SemRedirecionamento())
    registros = []

    def obter(url, token=None):
        parsed = urllib.parse.urlsplit(url)
        if (parsed.scheme != "https" or parsed.hostname not in
            {"registry-1.docker.io", "auth.docker.io", "ghcr.io"}
            or parsed.username or parsed.password or "/blobs/" in parsed.path):
            raise RuntimeError("Destino fora do escopo de metadados")
        if not (parsed.path.endswith("/token") or "/manifests/" in parsed.path):
            raise RuntimeError("Rota não autorizada")
        headers = {"User-Agent": "cefor-auditoria-metadados/5B.2-A.2", "Accept": ACEITAR}
        if token:
            headers["Authorization"] = "Bearer " + token
        request = urllib.request.Request(url, headers=headers, method="GET")
        with cliente.open(request, timeout=15) as resposta:
            corpo = resposta.read(2 * 1024 * 1024 + 1)
            if len(corpo) > 2 * 1024 * 1024:
                raise RuntimeError("Resposta excedeu limite de metadados")
            return corpo, {k: resposta.headers.get(k) for k in ("Docker-Content-Digest", "Content-Type", "Date")}

    for nome, host, repositorio, tag, host_token, servico in FONTES:
        registro = {"nome": nome, "registry": host, "repositorio": repositorio, "tag_consultada": tag,
                    "instante_utc": datetime.now(timezone.utc).isoformat()}
        try:
            query = urllib.parse.urlencode({"service": servico, "scope": f"repository:{repositorio}:pull"})
            corpo_token, _ = obter(f"https://{host_token}/token?{query}")
            credencial_publica = json.loads(corpo_token)
            token = credencial_publica.get("token") or credencial_publica.get("access_token")
            if not isinstance(token, str) or not token:
                raise RuntimeError("Autenticação anônima pública indisponível")
            corpo, headers = obter(f"https://{host}/v2/{repositorio}/manifests/{tag}", token)
            indice = json.loads(corpo)
            digest = "sha256:" + hashlib.sha256(corpo).hexdigest()
            if headers["Docker-Content-Digest"] != digest:
                raise RuntimeError("Digest publicado diverge dos bytes do manifesto")
            registro.update({"digest_indice": digest, "headers_publicos": headers, "indice_bytes_utf8": corpo.decode("utf-8"),
                             "indice": indice, "plataformas_verificadas": []})
            for descritor in indice.get("manifests", []):
                plataforma = descritor.get("platform", {})
                if plataforma.get("os") != "linux" or plataforma.get("architecture") not in {"amd64", "arm64"}:
                    continue
                ref = descritor["digest"]
                bruto, cabecalhos = obter(f"https://{host}/v2/{repositorio}/manifests/{ref}", token)
                observado = "sha256:" + hashlib.sha256(bruto).hexdigest()
                if observado != ref or cabecalhos["Docker-Content-Digest"] != ref:
                    raise RuntimeError("Manifesto de plataforma divergente")
                registro["plataformas_verificadas"].append({"plataforma": plataforma,
                    "digest": observado, "headers_publicos": cabecalhos, "manifesto_bytes_utf8": bruto.decode("utf-8"), "manifesto": json.loads(bruto)})
            if not registro["plataformas_verificadas"]:
                raise RuntimeError("Plataformas candidatas não encontradas")
            registro["estado"] = "metadados e SHA-256 verificados; imagem não adquirida nem aprovada"
            del token, credencial_publica, corpo_token
        except Exception as erro:
            registro["estado"] = "consulta interrompida"
            registro["erro_sanitizado"] = type(erro).__name__
            if isinstance(erro, urllib.error.HTTPError):
                registro["http_status"] = erro.code
        registros.append(registro)
    with destino.open("x", encoding="utf-8") as arquivo:
        json.dump({"fase": "5B.2-A.2", "escopo": "somente manifestos públicos; nenhuma camada/config blob",
                   "registros": registros}, arquivo, ensure_ascii=True, indent=2)
        arquivo.write("\n")
    for registro in registros:
        print(json.dumps({k: registro[k] for k in ("nome", "estado", "digest_indice", "erro_sanitizado") if k in registro}))


if __name__ == "__main__":
    consultar()
