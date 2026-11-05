"""O PNG da peça e o pacote do kit (111, D-007, FR-3435, FR-3437, FR-3438).

O rasterizador é a única camada do kit que pede algo de fora do projeto. O pacote reúne, num ZIP
montado na memória, o que as outras exportações entregam uma a uma, e o manifesto que diz de onde o
material veio e quando.

**O rasterizador é o `resvg-py`**, dependência de execução desde a P-4 (aprovada em 01/11), com a
verificação em `specs/111-kit-de-divulgacao/verificacao-do-motor.md`. `disponivel()` sobra como
defesa: num ambiente montado sem ele, a tela diz que a peça não tem PNG, e o SVG e os textos
continuam.

**As fontes são as da família do template, e só elas** (119, `D-005`). `skip_system_fonts=True`
impede que o resvg complete um glifo com a fonte da máquina — uma no Mac da equipe, outra no
servidor —, e o PNG mudaria de um para o outro. Nenhum recurso externo é resolvido: a marca vai no
SVG, em `data:`. A peça Institucional continua com a Edital Sans, a fonte do Edital.
"""

import hashlib
import importlib.metadata
import importlib.util
import io
import json
import zipfile

from processo_seletivo.inscricoes.domain import periodo
from processo_seletivo.interface import kit_familias, kit_fontes, kit_peca

#: As fontes da peça Institucional, a de produção da `111`: o padrão de quem não diz a peça.
FONTES_DA_INSTITUCIONAL = kit_familias.familia(kit_peca.INSTITUCIONAL.familia).chaves_das_fontes()


def disponivel():
    return importlib.util.find_spec("resvg_py") is not None


def versao_do_rasterizador():
    try:
        return f"resvg-py {importlib.metadata.version('resvg-py')}"
    except importlib.metadata.PackageNotFoundError:
        return ""


def rasterizar(svg, fontes=FONTES_DA_INSTITUCIONAL):
    """Os bytes do PNG. O SVG é sempre o que o compositor gerou, nunca entrada de quem pede.

    `fontes` são as chaves de `kit_fontes` da família da peça (`kit_peca.fontes_da_peca`): o
    rasterizador recebe esses arquivos e nenhum outro.
    """
    import resvg_py

    arquivos = list(kit_fontes.arquivos(fontes))
    return bytes(resvg_py.svg_to_bytes(svg_string=svg, font_files=arquivos, skip_system_fonts=True))


# ---------------------------------------------------------------------------
# O pacote: o ZIP e o manifesto (`FR-3435`, `FR-3437`, `FR-3438`)
# ---------------------------------------------------------------------------

#: Os arquivos do pacote, na ordem em que entram. A ordem é parte do determinismo (`FR-3438`): o
#: mesmo material no mesmo instante de referência sai o mesmo ZIP, byte a byte.
ARQUIVOS = (
    "kit.md",
    "kit.txt",
    "peca-feed-1080x1350.png",
    "peca-feed-1080x1350.svg",
    "texto-alternativo.txt",
    "ficha.json",
    "manifesto.json",
)
PNG, SVG, ALTERNATIVO = ARQUIVOS[2:5]

#: Os arquivos do ZIP de uma família da comunicação (119, FR-3829, `D-015`): os textos, depois
#: post, story e banner, cada um em PNG, SVG e texto alternativo, depois a ficha e o manifesto. O
#: ZIP da Institucional continua com `ARQUIVOS`.
FORMATOS_DO_PACOTE = ("post", "story", "banner")


def arquivos_do_formato(formato):
    return (f"peca-{formato}.png", f"peca-{formato}.svg", f"peca-{formato}-alternativo.txt")


ARQUIVOS_DA_FAMILIA = (
    "kit.md",
    "kit.txt",
    *(nome for formato in FORMATOS_DO_PACOTE for nome in arquivos_do_formato(formato)),
    "ficha.json",
    "manifesto.json",
)
#: A versão do manifesto do ZIP de família; o da `111`, sem o campo, é a versão 1.
VERSAO_DO_MANIFESTO = 2

#: A data de cada entrada do ZIP. **Não é o instante da geração**: com ele, dois downloads do mesmo
#: material dariam arquivos diferentes, e o resumo gravado na trilha não serviria para reconhecer o
#: arquivo que circula. O instante está no manifesto, onde é lido; a data do ZIP é a menor que o
#: formato admite.
DATA_FIXA = (1980, 1, 1, 0, 0, 0)
PERMISSOES = 0o644 << 16

MARCO_DA_RETIFICACAO = "Retificação publicada passa a valer"
MARCO_DO_TERMINO = "Término do período de inscrições"
SEM_ENDERECO = (
    "Acesso por endereço local: o endereço público não é conhecido neste acesso, e os textos saem "
    "sem link absoluto."
)


def _json(dados):
    return (json.dumps(dados, ensure_ascii=False, indent=2) + "\n").encode()


def _proximos_marcos(ficha):
    """Os marcos já conhecidos depois da geração (`FR-3437`, `FR-3440`).

    Nenhum é chamado de prazo de validade do material: dizem quando o Edital muda, e quem decide o
    que fazer é quem divulga.
    """
    marcos = []
    if ficha.retificacao_a_vigorar:
        marcos.append({"marco": MARCO_DA_RETIFICACAO, "instante": ficha.retificacao_a_vigorar})
    if ficha.fim and ficha.periodo_estado in {periodo.FUTURO, periodo.ABERTO}:
        marcos.append({"marco": MARCO_DO_TERMINO, "instante": ficha.fim})
    return sorted(marcos, key=lambda marco: marco["instante"])


def manifesto(ficha, *, arquivos, peca, motivo_sem_peca):
    """O que o pacote é, de onde veio e quando — sem nenhum instante chamado de validade."""
    return {
        "kit": f"Kit de divulgação — {ficha.identificacao}",
        "edital": {
            "id": ficha.edital_id,
            "identificacao": ficha.identificacao,
            "unidade": ficha.unidade_sigla,
        },
        "instantes": {
            "gerado_em": ficha.referencia,
            "versao_vigente_desde": {"instante": ficha.versao_desde, "ato": ficha.versao_ato},
            "proximos_marcos": _proximos_marcos(ficha),
        },
        "versao": {"id": ficha.versao_id, "content_hash": ficha.versao_hash},
        "impressao": {"resumo": ficha.impressao, "versao": ficha.versao_da_impressao},
        "template": peca.template.identificador if peca is not None else None,
        "rasterizador": versao_do_rasterizador() or None,
        # As da Institucional mesmo sem peça, como na `111`: o manifesto não muda de forma.
        "fontes": kit_fontes.resumos(
            kit_peca.fontes_da_peca(peca) if peca is not None else FONTES_DA_INSTITUCIONAL
        ),
        "endereco_publico": ficha.endereco,
        "notas": [] if ficha.endereco else [SEM_ENDERECO],
        "peca": {
            "incluida": peca is not None,
            "motivo": motivo_sem_peca or None,
            "manchete": peca.manchete if peca is not None else None,
        },
        "arquivos": [
            {"nome": nome, "sha256": hashlib.sha256(dados).hexdigest()}
            for nome, dados in arquivos.items()
        ],
    }


def zipar(arquivos, ordem=ARQUIVOS):
    """Os bytes do ZIP, montado na memória (`FR-3441`) com data e permissões fixas."""
    memoria = io.BytesIO()
    with zipfile.ZipFile(memoria, "w") as pacote:
        for nome in ordem:
            if nome not in arquivos:
                continue
            info = zipfile.ZipInfo(nome, date_time=DATA_FIXA)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = PERMISSOES
            info.create_system = 3
            pacote.writestr(info, arquivos[nome])
    return memoria.getvalue()


def montar(ficha, *, markdown, texto, peca, svg, png, motivo_sem_peca):
    """O ZIP do material. `peca` nulo, ou `motivo_sem_peca`, tira os arquivos da peça.

    `svg` e `png` chegam prontos de quem chama; sem o rasterizador, `png` é nulo e o pacote sai
    com o SVG, e o motivo diz que falta o PNG.
    """
    arquivos = {"kit.md": markdown.encode(), "kit.txt": texto.encode()}
    if peca is not None:
        if png is not None:
            arquivos[PNG] = png
        arquivos[SVG] = svg
        arquivos[ALTERNATIVO] = (peca.alternativo + "\n").encode()
    arquivos["ficha.json"] = _json(ficha.como_dict())
    arquivos["manifesto.json"] = _json(
        manifesto(
            ficha,
            arquivos=arquivos,
            peca=peca,
            motivo_sem_peca=motivo_sem_peca,
        )
    )
    return zipar(arquivos)


# ---------------------------------------------------------------------------
# O pacote de uma família da comunicação (119, FR-3829, `D-015`)
# ---------------------------------------------------------------------------


def _resumo(dados):
    return hashlib.sha256(dados).hexdigest()


def montar_da_familia(ficha, *, markdown, texto, escolhida, formatos):
    """O ZIP da família, com uma entrada no manifesto por formato, incluído ou não.

    `formatos` é a lista, na ordem do pacote, de `{formato, template, peca, svg, png, motivo,
    detalhe}`: `peca` nula quando o formato não entra, e `motivo` dizendo por quê (`nao_liberado`,
    `versao_divergente`, `recusa`), ou `sem_rasterizador` quando entra sem o PNG. Devolve os bytes
    e a lista `pecas`, que o evento leva igual à do manifesto.
    """
    arquivos = {"kit.md": markdown.encode(), "kit.txt": texto.encode()}
    pecas, fontes, ativos = [], {}, {}
    for item in formatos:
        template, peca = item["template"], item["peca"]
        png, svg, alternativo = arquivos_do_formato(item["formato"])
        incluidos = {}
        if peca is not None:
            if item["png"] is not None:
                incluidos[png] = item["png"]
            incluidos[svg] = item["svg"]
            incluidos[alternativo] = (peca.alternativo + "\n").encode()
            arquivos.update(incluidos)
            fontes.update(kit_fontes.resumos(kit_peca.fontes_da_peca(peca)))
            familia = kit_familias.familia(template.familia)
            for ativo in familia.ativos.values():
                ativos[ativo.arquivo] = ativo.sha256
            if peca.imagem is not None:
                formato = template.formato.chave
                ativos[peca.imagem.arquivo(formato)] = peca.imagem.sha256(formato)
        pecas.append(
            {
                "formato_da_peca": item["formato"],
                "template": template.identificador,
                "template_versao": template.versao,
                "template_resumo": kit_familias.resumo(template),
                "incluida": peca is not None,
                "motivo": item["motivo"] or None,
                **({"recusa": item["recusa"]} if item.get("recusa") else {}),
                "manchete": peca.manchete if peca is not None else None,
                "arquivos": [
                    {"nome": nome, "sha256": _resumo(dados)} for nome, dados in incluidos.items()
                ],
            }
        )
    arquivos["ficha.json"] = _json(ficha.como_dict())
    base = manifesto(ficha, arquivos=arquivos, peca=None, motivo_sem_peca="")
    imagem = escolhida.imagem_do_banco()
    arquivos["manifesto.json"] = _json(
        {
            **base,
            # Os campos singulares da `111` significam a Institucional; aqui vêm nulos, e quem lê
            # usa `pecas` (FR-3829).
            "template": None,
            "peca": None,
            "versao_do_manifesto": VERSAO_DO_MANIFESTO,
            "familia": {
                "chave": escolhida.familia.chave,
                "versao": escolhida.familia.versao,
                "variante": escolhida.variante,
            },
            "imagem": (
                {"chave": imagem.chave, "sha256": {f: imagem.sha256(f) for f in imagem.arquivos}}
                if imagem
                else None
            ),
            "pecas": pecas,
            "fontes": fontes,
            "ativos": ativos,
            "arquivos": [
                {"nome": nome, "sha256": _resumo(dados)} for nome, dados in arquivos.items()
            ],
        }
    )
    return zipar(arquivos, ARQUIVOS_DA_FAMILIA), pecas
