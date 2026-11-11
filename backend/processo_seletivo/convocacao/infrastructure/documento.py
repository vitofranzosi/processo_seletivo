"""A publicação de convocados como documento oficial — o quarto a entrar pela costura (148, D-013).

O Edital, o comprovante e o resultado já passam por `Composicao` e `render_documento`; este entra
pelo mesmo lugar, com `_tabela` para cada grupo. Nenhuma biblioteca nova.

**Nada aqui consulta banco.** A função recebe o conteúdo já composto — o mesmo objeto que virou
`conteudo_publico` — e devolve bytes: a página e o documento dizem o mesmo porque saem da mesma
origem, e não por coincidência a conferir (FR-5426).

**Determinismo.** O instante impresso é o da publicação, gravado no conteúdo, e não o relógio da
geração: o mesmo conteúdo produz sempre o mesmo arquivo.
"""

from processo_seletivo.convocacao.domain import publicacao as dominio
from processo_seletivo.publicacoes.infrastructure.pdf import (
    ALTURA_DO_BRASAO,
    ANTES_DE_LINHA,
    CENTRO,
    CORPO_ATO,
    CORPO_NOTA,
    CORPO_SECAO,
    CORPO_TEXTO,
    ESQUERDA,
    NEGRITO,
    Composicao,
    UnidadeDoAto,
    _tabela,
    linhas_do_orgao,
    render_documento,
)
from processo_seletivo.shared.canonical import canonical_sha256

ENTRE_SECOES = 12.0
RECUO_DO_VALOR = 118.0
SUBIR_PARA_A_LINHA = -11.5


def render_convocados_pdf(conteudo: dict) -> bytes:
    """O documento da publicação de convocados, dos bytes que a página também lê."""
    cabecalho = conteudo["cabecalho"]
    composicao = Composicao()
    _timbre(composicao, cabecalho)
    _identificacao(composicao, cabecalho)
    for grupo in conteudo["grupos"]:
        _grupo(composicao, grupo)
    _orientacoes(composicao, cabecalho)
    _autoridade(composicao, cabecalho)
    _integridade(composicao, conteudo)
    return render_documento(
        composicao, identificacao=f"{cabecalho['edital']} · {cabecalho['titulo']}"
    )


def _timbre(composicao, cabecalho):
    # A unidade do conteúdo congelado, e não a do registro de hoje (060, FR-1112).
    unidade = UnidadeDoAto(cabecalho=tuple(cabecalho["unidade"]["cabecalho"]), local="")
    composicao.espaco(ALTURA_DO_BRASAO - 10)
    for indice, linha in enumerate(linhas_do_orgao(unidade)):
        composicao.escrever(
            linha, tamanho=CORPO_TEXTO, alinhamento=CENTRO, antes=0.0 if indice else 4.0
        )
    composicao.escrever(
        cabecalho["titulo"].upper(), tamanho=CORPO_ATO, fonte=NEGRITO, antes=16, alinhamento=CENTRO
    )


def _identificacao(composicao, cabecalho):
    with composicao.bloco(moldura=True):
        composicao.espaco(4.0)
        for rotulo, valor in (
            ("PROCESSO", cabecalho["processo"]),
            ("EDITAL", cabecalho["edital"]),
            ("PUBLICADA EM", _instante(cabecalho["publicadoEm"])),
        ):
            if valor:
                _par(composicao, rotulo, valor)
        composicao.espaco(4.0)


def _par(composicao, rotulo, valor):
    composicao.escrever(rotulo, tamanho=CORPO_NOTA, antes=4.5)
    composicao.escrever(valor, tamanho=CORPO_TEXTO, recuo=RECUO_DO_VALOR, antes=SUBIR_PARA_A_LINHA)


def _grupo(composicao, grupo):
    """Um grupo: a vaga e a lista, o que ele é, o prazo, e as pessoas (FR-5414, FR-5415)."""
    titulo = f"{grupo['perfil']} — {grupo['lista']}"
    if grupo["marco"]:
        titulo += f" ({grupo['marco']})"
    composicao.escrever(titulo, tamanho=CORPO_SECAO, fonte=NEGRITO, antes=ENTRE_SECOES, junto=True)
    composicao.escrever(
        dominio.nota_do_grupo(grupo),
        tamanho=CORPO_NOTA,
        antes=ANTES_DE_LINHA,
        justificar=True,
        junto=True,
    )
    if grupo["vencimentoUnico"]:
        composicao.escrever(
            f"Prazo para atender: {_prazo(grupo['vencimento'])}.",
            tamanho=CORPO_TEXTO,
            antes=ANTES_DE_LINHA,
            junto=True,
        )
    colunas = ["Nome", "Protocolo"]
    if not grupo["vencimentoUnico"]:
        colunas.append("Prazo")
    if not grupo["canalUnico"]:
        colunas.append("Convocação oficial")
    corrige = any(pessoa["corrige"] for pessoa in grupo["pessoas"])
    if corrige:
        colunas.append("Observação")
    linhas = []
    for pessoa in grupo["pessoas"]:
        linha = [pessoa["nome"], pessoa["protocolo"]]
        if not grupo["vencimentoUnico"]:
            linha.append(_prazo(pessoa["vencimento"]))
        if not grupo["canalUnico"]:
            linha.append(pessoa["canal"] or "—")
        if corrige:
            linha.append(_correcao(pessoa["corrige"]))
        linhas.append(linha)
    _tabela(composicao, colunas, linhas, recuo=0.0, alinhamentos=[ESQUERDA] * len(colunas))


def _correcao(numero):
    return f"corrige a convocação divulgada na {dominio.titulo(numero)}" if numero else "—"


def _orientacoes(composicao, cabecalho):
    composicao.escrever(
        "Orientações", tamanho=CORPO_SECAO, fonte=NEGRITO, antes=ENTRE_SECOES, junto=True
    )
    for frase in dominio.orientacoes(
        requerimento_na_convocacao=cabecalho.get("requerimentoNaConvocacao", False)
    ):
        composicao.escrever(frase, tamanho=CORPO_TEXTO, antes=ANTES_DE_LINHA, justificar=True)


def _autoridade(composicao, cabecalho):
    """Nome e cargo, como o resultado: sem nome, o cargo ocupa a linha do nome (054, FR-992)."""
    signatario = cabecalho["signatario"]
    composicao.espaco(ENTRE_SECOES)
    nome = str(signatario.get("nome") or "").strip()
    if nome:
        composicao.escrever(nome, tamanho=CORPO_TEXTO, fonte=NEGRITO, alinhamento=CENTRO)
        composicao.escrever(signatario["cargo"], tamanho=CORPO_NOTA, alinhamento=CENTRO, antes=2.0)
    else:
        composicao.escrever(
            signatario["cargo"], tamanho=CORPO_TEXTO, fonte=NEGRITO, alinhamento=CENTRO
        )
    ato = str(signatario.get("atoDeNomeacao") or "").strip()
    if ato:
        composicao.escrever(ato, tamanho=CORPO_NOTA, alinhamento=CENTRO)


def _integridade(composicao, conteudo):
    composicao.espaco(ENTRE_SECOES)
    composicao.regua()
    composicao.escrever(
        f"SHA-256 do conteúdo publicado: {canonical_sha256(conteudo)}",
        tamanho=CORPO_NOTA,
        antes=ANTES_DE_LINHA + 3,
    )
    composicao.escrever(
        "Este documento reproduz o conteúdo publicado na página pública da seleção, na data e hora "
        "indicadas. O resumo acima é calculado sobre esse conteúdo, e permite confirmar que nada "
        "foi alterado.",
        tamanho=CORPO_NOTA,
        antes=ANTES_DE_LINHA,
        justificar=True,
    )


def _prazo(texto):
    """`até 18/11/2026, às 23h59` — ou o do Edital, quando o ato não informou vencimento."""
    return f"até {_instante(texto)}" if texto else dominio.SEM_VENCIMENTO


def _instante(texto):
    """O instante congelado no fuso da instituição — a mesma conversão do documento do resultado."""
    from django.utils import timezone
    from django.utils.dateparse import parse_datetime

    from processo_seletivo.publicacoes.infrastructure import humano

    momento = parse_datetime(texto or "")
    if momento is None:
        return texto or "—"
    return humano.instante(timezone.localtime(momento) if timezone.is_aware(momento) else momento)


__all__ = ["render_convocados_pdf"]
