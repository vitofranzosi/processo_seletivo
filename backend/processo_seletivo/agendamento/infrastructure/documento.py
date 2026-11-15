"""A agenda publicada como documento oficial (167, T086, FR-7224, SC-2399, `D-012`).

No molde de `convocacao/infrastructure/documento.py` (`149`): `Composicao`, `render_documento` e
`_tabela`, nenhuma biblioteca nova. **Nada aqui consulta banco.** A função recebe o conteúdo já
composto — o mesmo objeto que virou `conteudo_publico` do ato — e devolve bytes: a página e o
documento dizem o mesmo porque saem da mesma origem.

**O que não está no conteúdo não pode estar no documento**: nem o endereço da sala, nem CPF,
e-mail, telefone, Modalidade ou motivo (FR-7226). Na Etapa restrita por Modalidade, a pessoa é só o
protocolo (`D-009`), porque o conteúdo já chega assim.

**Determinismo.** O instante impresso é o da publicação, gravado no conteúdo, e não o relógio da
geração: o mesmo conteúdo produz sempre o mesmo arquivo. E o arquivo é gravado uma vez, no ato
(`DocumentoDoAtoDaAgenda`): um compositor que mude depois não muda o que foi publicado.
"""

from datetime import date

from django.utils.dateparse import parse_datetime

from processo_seletivo.agendamento.domain import nomes
from processo_seletivo.agendamento.domain.horarios import dia_por_extenso, hora
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
TITULOS = {
    nomes.PUBLICACAO: "Agenda da Etapa",
    nomes.REMARCACAO: "Remarcação na agenda da Etapa",
    nomes.INCLUSAO: "Inclusão na agenda da Etapa",
    nomes.CANCELAMENTO: "Cancelamento na agenda da Etapa",
}


def titulo(conteudo):
    return TITULOS.get(
        conteudo["cabecalho"].get("especie") or nomes.PUBLICACAO, TITULOS[nomes.PUBLICACAO]
    )


def render_agenda_pdf(conteudo: dict) -> bytes:
    """O documento de um ato da agenda, do conteúdo que a página também lê."""
    cabecalho = conteudo["cabecalho"]
    composicao = Composicao()
    _timbre(composicao, cabecalho, titulo(conteudo))
    _identificacao(composicao, cabecalho)
    _nota(composicao, cabecalho)
    so_protocolo = cabecalho.get("identificacao") == nomes.PROTOCOLO
    varias = len(conteudo.get("bancas") or []) > 1
    for dia in conteudo["dias"]:
        _dia(composicao, dia, so_protocolo=so_protocolo, varias=varias)
    _locais(composicao, conteudo)
    _orientacoes(composicao, cabecalho)
    _autoridade(composicao, cabecalho)
    _integridade(composicao, conteudo)
    return render_documento(
        composicao,
        identificacao=f"{cabecalho['edital']} · {titulo(conteudo)}: {cabecalho['etapa']}",
    )


def _timbre(composicao, cabecalho, titulo_):
    # A unidade do conteúdo congelado, e não a do registro de hoje (060, FR-1112).
    unidade = UnidadeDoAto(cabecalho=tuple(cabecalho["unidade"]["cabecalho"]), local="")
    composicao.espaco(ALTURA_DO_BRASAO - 10)
    for indice, linha in enumerate(linhas_do_orgao(unidade)):
        composicao.escrever(
            linha, tamanho=CORPO_TEXTO, alinhamento=CENTRO, antes=0.0 if indice else 4.0
        )
    composicao.escrever(
        titulo_.upper(), tamanho=CORPO_ATO, fonte=NEGRITO, antes=16, alinhamento=CENTRO
    )


def _identificacao(composicao, cabecalho):
    forma = "por videoconferência" if cabecalho.get("forma") == nomes.REMOTA else "presencial"
    with composicao.bloco(moldura=True):
        composicao.espaco(4.0)
        for rotulo, valor in (
            ("EDITAL", cabecalho["edital"]),
            ("ETAPA", cabecalho["etapa"]),
            ("ATENDIMENTO", f"{cabecalho['duracao']} minutos, {forma}"),
            (_rotulo_do_instante(cabecalho), _instante(cabecalho.get("publicadoEm"))),
            ("VEÍCULO", _veiculo(cabecalho)),
        ):
            if valor:
                _par(composicao, rotulo, valor)
        composicao.espaco(4.0)


def _rotulo_do_instante(cabecalho):
    """ "Publicada em" na publicação; nos atos individuais, o instante do ato (entrega C)."""
    if (cabecalho.get("especie") or nomes.PUBLICACAO) == nomes.PUBLICACAO:
        return "PUBLICADA EM"
    return "REGISTRADO EM"


def _nota(composicao, cabecalho):
    """O que o ato individual muda, numa frase; nunca o motivo, que fica na trilha (FR-7246)."""
    texto = (cabecalho.get("nota") or "").strip()
    if texto:
        composicao.escrever(texto, tamanho=CORPO_TEXTO, antes=ENTRE_SECOES, justificar=True)


def _veiculo(cabecalho):
    detalhe = cabecalho.get("veiculoDetalhe") or ""
    if cabecalho.get("veiculo") == nomes.VEICULO_GPS:
        return "Página pública da seleção, no GPS" + (f" ({detalhe})" if detalhe else "")
    if cabecalho.get("veiculo") == nomes.VEICULO_EXTERNO:
        return f"Fora do GPS: {detalhe}" if detalhe else "Fora do GPS"
    return ""


def _par(composicao, rotulo, valor):
    composicao.escrever(rotulo, tamanho=CORPO_NOTA, antes=4.5)
    composicao.escrever(valor, tamanho=CORPO_TEXTO, recuo=RECUO_DO_VALOR, antes=SUBIR_PARA_A_LINHA)


def _dia(composicao, dia, *, so_protocolo, varias):
    composicao.escrever(
        dia_por_extenso(date.fromisoformat(dia["dia"])),
        tamanho=CORPO_SECAO,
        fonte=NEGRITO,
        antes=ENTRE_SECOES,
        junto=True,
    )
    colunas = ["Horário"]
    if varias:
        colunas.append("Banca")
    colunas += ["Protocolo"] if so_protocolo else ["Nome", "Protocolo"]
    linhas = []
    for item in dia["horarios"]:
        linha = [hora(parse_datetime(item["inicio"]))]
        if varias:
            linha.append(item.get("banca", ""))
        if not so_protocolo:
            linha.append(item["pessoa"].get("nome", ""))
        linha.append(item["pessoa"]["protocolo"])
        linhas.append(linha)
    _tabela(composicao, colunas, linhas, recuo=0.0, alinhamentos=[ESQUERDA] * len(colunas))


def _locais(composicao, conteudo):
    """O local de cada banca, só no presencial: o conteúdo nunca traz o endereço da sala."""
    locais = [banca for banca in conteudo.get("bancas") or [] if banca.get("local")]
    if not locais:
        return
    composicao.escrever(
        "Locais", tamanho=CORPO_SECAO, fonte=NEGRITO, antes=ENTRE_SECOES, junto=True
    )
    for banca in locais:
        composicao.escrever(
            f"{banca['nome']}: {banca['local']}", tamanho=CORPO_TEXTO, antes=ANTES_DE_LINHA
        )


def _orientacoes(composicao, cabecalho):
    texto = (cabecalho.get("orientacoes") or "").strip()
    if not texto:
        return
    composicao.escrever(
        "Orientações", tamanho=CORPO_SECAO, fonte=NEGRITO, antes=ENTRE_SECOES, junto=True
    )
    for paragrafo in [p.strip() for p in texto.splitlines() if p.strip()]:
        composicao.escrever(paragrafo, tamanho=CORPO_TEXTO, antes=ANTES_DE_LINHA, justificar=True)


def _autoridade(composicao, cabecalho):
    """Nome e cargo, como o resultado: sem nome, o cargo ocupa a linha do nome (054, FR-992)."""
    signatario = cabecalho.get("signatario")
    if not signatario:
        return
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
        "Este documento reproduz a agenda publicada na página pública da seleção, na data e hora "
        "indicadas. O resumo acima é calculado sobre esse conteúdo, e permite confirmar que nada "
        "foi alterado. O endereço da sala virtual de cada pessoa não é público: está na área dela.",
        tamanho=CORPO_NOTA,
        antes=ANTES_DE_LINHA,
        justificar=True,
    )


def _instante(texto):
    """O instante congelado no fuso da instituição — a mesma conversão do documento do resultado."""
    from django.utils import timezone

    from processo_seletivo.publicacoes.infrastructure import humano

    momento = parse_datetime(texto or "")
    if momento is None:
        return texto or ""
    return humano.instante(timezone.localtime(momento) if timezone.is_aware(momento) else momento)


__all__ = ["render_agenda_pdf", "titulo"]
