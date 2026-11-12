"""A publicação das inscrições como documento oficial — o quarto a entrar pela mesma costura (148).

Timbre, autoridade e resumo de integridade são os do documento do resultado, importados e não
copiados: os dois atos são da mesma unidade, assinados do mesmo jeito, e conferidos pelo mesmo
resumo. O que é próprio daqui é a moldura (natureza, Etapa, prazo, sucessão) e as tabelas por
Perfil.

**Nada aqui consulta banco, e nada lê o relógio** — a mesma composição produz os mesmos bytes, e o
documento é gerado uma vez, na publicação, a partir dos bytes que a página também lê (FR-5424).
"""

from processo_seletivo.divulgacao.domain.inscricoes import (
    FRASE_DAS_LISTAS,
    grupos_publicados,
    tem_lista_reservada,
)
from processo_seletivo.divulgacao.infrastructure.documento import (
    ENTRE_SECOES,
    _autoridade,
    _instante,
    _integridade,
    _par,
    _timbre,
)
from processo_seletivo.publicacoes.infrastructure.pdf import (
    ANTES_DE_LINHA,
    CORPO_NOTA,
    CORPO_SECAO,
    CORPO_TEXTO,
    ESQUERDA,
    NEGRITO,
    Composicao,
    _tabela,
    render_documento,
)


def render_inscricoes_pdf(conteudo: dict) -> bytes:
    """O documento do ato, a partir dos bytes canônicos.

    Lê os dois formatos dos bytes (FR-5447): o documento de um ato gravado não é regerado, mas a
    composição que o gerou precisa continuar reproduzível a partir daqueles bytes.
    """
    cabecalho = conteudo["cabecalho"]
    grupos = grupos_publicados(conteudo)
    composicao = Composicao()
    _timbre(composicao, cabecalho)
    _moldura(composicao, cabecalho)
    _explicacao(composicao, cabecalho, grupos)
    for grupo in grupos:
        _perfil(composicao, grupo, conteudo)
    _autoridade(composicao, cabecalho)
    _integridade(composicao, conteudo)
    return render_documento(
        composicao, identificacao=f"{cabecalho['edital']} · {cabecalho['titulo']}"
    )


def _moldura(composicao, cabecalho):
    """O que o documento afirma ser: processo, Edital, Etapa, prazo, sucessão e instante."""
    with composicao.bloco(moldura=True):
        composicao.espaco(4.0)
        for rotulo, valor in (
            ("PROCESSO", cabecalho["processo"]),
            ("EDITAL", cabecalho["edital"]),
            ("ETAPA DE ANÁLISE", cabecalho.get("etapa") or ""),
            ("PRAZO DE RECURSO", frase_do_prazo(cabecalho.get("prazo"))),
            ("SUCEDE", frase_da_sucessao(cabecalho.get("sucede"))),
            ("PUBLICADO EM", _instante(cabecalho["publicado_em"])),
        ):
            if valor:
                _par(composicao, rotulo, valor)
        composicao.espaco(4.0)


def _explicacao(composicao, cabecalho, grupos):
    frase = frase_da_natureza(cabecalho["natureza"])
    if tem_lista_reservada(grupos):
        frase = f"{frase} {FRASE_DAS_LISTAS}"
    composicao.escrever(frase, tamanho=CORPO_NOTA, antes=ENTRE_SECOES, justificar=True)


def _perfil(composicao, grupo, conteudo):
    composicao.escrever(
        grupo["perfil"] or "Perfil",
        tamanho=CORPO_SECAO,
        fonte=NEGRITO,
        antes=ENTRE_SECOES,
        junto=True,
    )
    for lista in grupo["listas"]:
        _lista(composicao, lista, conteudo)


def _lista(composicao, lista, conteudo):
    """Uma lista de concorrência do Perfil — ou o Perfil inteiro, no ato anterior à revisão.

    **O título da lista só existe quando a lista tem nome** (FR-5447): o ato gravado antes de 12/11
    não declarou lista nenhuma, e o documento dele não ganha uma.
    """
    natureza = conteudo["cabecalho"]["natureza"]
    if lista["lista"]:
        composicao.escrever(
            f"{lista['lista']} ({len(lista['constam'])})",
            tamanho=CORPO_TEXTO,
            fonte=NEGRITO,
            antes=ANTES_DE_LINHA + 5,
            junto=True,
        )
    if lista["constam"]:
        _tabela(
            composicao,
            ["Candidato", "Protocolo"],
            [[linha["candidato"], linha["protocolo"]] for linha in lista["constam"]],
            recuo=0.0,
            alinhamentos=[ESQUERDA, ESQUERDA],
        )
    else:
        composicao.escrever(
            frase_da_lista_vazia(natureza) if lista["lista"] else frase_do_perfil_vazio(natureza),
            tamanho=CORPO_TEXTO,
            antes=ANTES_DE_LINHA + 3,
        )
    if conteudo.get("rotulo_nao_constam") and lista["nao_constam"]:
        onde = "nesta lista" if lista["lista"] else "neste Perfil"
        composicao.escrever(
            f"{conteudo['rotulo_nao_constam'].capitalize()} {onde}: "
            f"{lista['nao_constam']} — não nomeadas; cada candidato consulta a própria situação "
            "e o motivo na área do candidato.",
            tamanho=CORPO_NOTA,
            antes=ANTES_DE_LINHA,
        )


# ---------------------------------------------------------------------------
# As frases — uma vez, para o documento e para as duas telas
# ---------------------------------------------------------------------------


def frase_da_natureza(natureza):
    """O que o ato é, e o que ele não é — dito em uma frase (UX-462)."""
    return {
        "RECEBIDAS": "Esta relação lista as inscrições enviadas dentro do prazo. Constar nela "
        "significa que a inscrição foi recebida, e não que foi deferida ou homologada.",
        "PRELIMINAR": "Este é o resultado preliminar da análise das inscrições: pode mudar em "
        "razão de recurso, e só a homologação das inscrições é definitiva.",
        "HOMOLOGACAO": "Esta é a homologação das inscrições: a relação final das inscrições "
        "aceitas, depois da análise e dos recursos. Ela não é classificação.",
    }[natureza]


def frase_do_perfil_vazio(natureza):
    return {
        "RECEBIDAS": "Nenhuma inscrição recebida neste Perfil.",
        "PRELIMINAR": "Nenhuma inscrição deferida neste Perfil.",
        "HOMOLOGACAO": "Nenhuma inscrição homologada neste Perfil.",
    }[natureza]


def frase_da_lista_vazia(natureza):
    return {
        "RECEBIDAS": "Nenhuma inscrição recebida nesta lista.",
        "PRELIMINAR": "Nenhuma inscrição deferida nesta lista.",
        "HOMOLOGACAO": "Nenhuma inscrição homologada nesta lista.",
    }[natureza]


def frase_do_prazo(prazo):
    if not prazo:
        return ""
    if not prazo.get("admite"):
        return "O Edital não prevê recurso contra este resultado"
    return f"Até {_instante(prazo['ate'])} — {prazo['evento']}"


def frase_da_sucessao(sucede):
    if not sucede:
        return ""
    frase = f"{sucede['natureza_rotulo']} de {_instante(sucede['publicado_em'])}"
    if sucede.get("motivo"):
        frase += f". Motivo: {sucede['motivo']}"
    return frase


__all__ = [
    "frase_da_lista_vazia",
    "frase_da_natureza",
    "frase_da_sucessao",
    "frase_do_perfil_vazio",
    "frase_do_prazo",
    "render_inscricoes_pdf",
]
