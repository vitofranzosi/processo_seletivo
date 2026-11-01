"""PNG, manifesto e ZIP — a última camada, e a única que pede algo de fora do projeto.

**O rasterizador é experimental.** `resvg-py` não está no `pyproject.toml`: a POC o carrega por
`uv run --with resvg-py`, que monta um ambiente efêmero e não toca o `uv.lock`. Decidir a
dependência é a D-7 do estudo.

**As fontes são as do Edital, e só elas.** `skip_system_fonts=True` impede que o resvg complete um
glifo com a fonte da máquina — que seria uma no Mac da equipe e outra no servidor, e o PNG mudaria
de um para o outro.

**O ZIP é reproduzível.** Datas fixas e ordem fixa: os mesmos dados dão os mesmos bytes, e o
resumo do pacote pode ser comparado entre duas gerações.
"""

import hashlib
import importlib.metadata
import io
import json
import zipfile

from processo_seletivo.publicacoes.infrastructure import fonte

TEMPLATE = "feed-4x5 · poc-1"
FONTES = [str(fonte.PASTA / arquivo) for arquivo in fonte.ARQUIVOS.values()]
DATA_FIXA = (1980, 1, 1, 0, 0, 0)


def versao_do_rasterizador():
    try:
        return f"resvg-py {importlib.metadata.version('resvg-py')}"
    except importlib.metadata.PackageNotFoundError:
        return "ausente"


def rasterizar(svg):
    import resvg_py

    return bytes(resvg_py.svg_to_bytes(svg_string=svg, font_files=FONTES, skip_system_fonts=True))


def manifesto(ficha, *, gerado_em, svg=None, png=None, omissoes=()):
    """O mínimo para saber de onde veio o material e até quando a versão usada é a vigente.

    Três instantes, e cada um diz uma coisa diferente: quando o material foi gerado, desde quando
    vale a versão que ele descreve, e o próximo marco **conhecido** — uma Retificação já publicada a
    vigorar, ou o fim do período. Nenhum deles é "validade": uma Retificação publicada amanhã muda
    tudo, e o manifesto não promete o contrário.
    """
    proximos = []
    if ficha["retificacao_a_vigorar"]:
        proximos.append(
            {"marco": "Retificação publicada passa a valer", "em": ficha["retificacao_a_vigorar"]}
        )
    if ficha["fim"]:
        proximos.append({"marco": "Término do período de inscrições", "em": ficha["fim"]})
    return {
        "edital": ficha["identificacao"],
        "edital_id": ficha["edital_id"],
        "gerado_em": gerado_em,
        "instante_de_referencia": ficha["referencia"],
        "versao": {
            "id": ficha["versao_id"],
            "content_hash": ficha["versao_hash"],
            "vigente_desde": ficha["versao_desde"],
            "ato": ficha["versao_ato"],
        },
        "impressao_da_ficha": ficha["impressao"],
        "proximos_marcos_conhecidos": sorted(proximos, key=lambda item: item["em"]),
        "aviso": (
            "Uma Retificação publicada depois desta geração pode mudar os dados. A publicação "
            "oficial prevalece."
        ),
        "peca": None
        if svg is None
        else {
            "template": TEMPLATE,
            "rasterizador": versao_do_rasterizador(),
            "fontes": {arquivo: fonte.SHA256[arquivo] for arquivo in fonte.ARQUIVOS.values()},
            "svg_sha256": hashlib.sha256(svg.encode()).hexdigest(),
            "png_sha256": hashlib.sha256(png).hexdigest() if png else None,
            "omissoes": list(omissoes),
        },
    }


def empacotar(arquivos):
    """`{nome: bytes | str}` num ZIP de bytes estáveis."""
    saida = io.BytesIO()
    with zipfile.ZipFile(saida, "w", compression=zipfile.ZIP_DEFLATED) as zip_:
        for nome in sorted(arquivos):
            conteudo = arquivos[nome]
            if isinstance(conteudo, str):
                conteudo = conteudo.encode()
            info = zipfile.ZipInfo(nome, date_time=DATA_FIXA)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zip_.writestr(info, conteudo)
    return saida.getvalue()


def json_bonito(dados):
    return json.dumps(dados, ensure_ascii=False, indent=2, sort_keys=False) + "\n"
