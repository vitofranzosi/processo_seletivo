"""T011 e T012 — o catálogo de Seções, declarado e fixo.

A `007` acrescenta três seções institucionais e renumera a ordem; a `009` acrescenta a décima
primeira, gerada, com os documentos exigidos do candidato. O que estes testes protegem é que o
catálogo continua sendo **catálogo**: conjunto e ordem definidos pelo sistema (FR-009), e
identidade derivada da chave — não da posição (D-007).
"""

import uuid

import pytest

from processo_seletivo.editais.domain import secoes

# A ordem declarada no contrato `specs/007-edital-institucional/contracts/institucional.md`, A.3.
ORDEM_ESPERADA = [
    ("apresentacao", "Apresentação", secoes.TEXTUAL),
    ("disposicoes-preliminares", "Disposições Preliminares", secoes.TEXTUAL),
    ("requisitos-gerais", "Requisitos Gerais de Participação", secoes.TEXTUAL),
    ("inscricao", "Da Inscrição", secoes.TEXTUAL),
    ("documentos-exigidos", "Documentos Exigidos para a Inscrição", secoes.GERADA),
    ("perfis", "Perfis de Vaga", secoes.GERADA),
    ("etapas", "Etapas de Avaliação", secoes.GERADA),
    ("classificacao", "Critérios de Classificação", secoes.TEXTUAL),
    ("cronograma", "Cronograma", secoes.GERADA),
    ("recursos", "Dos Recursos", secoes.TEXTUAL),
    ("disposicoes-finais", "Disposições Finais", secoes.TEXTUAL),
]


def test_o_catalogo_tem_as_onze_secoes_na_ordem_declarada():
    assert [(s.key, s.title, s.type) for s in secoes.CATALOGO] == ORDEM_ESPERADA


def test_a_ordem_declarada_e_uma_sequencia_sem_buraco():
    """`order` é conteúdo normativo e o documento o respeita; buraco ou repetição seria defeito."""
    assert [s.order for s in secoes.CATALOGO] == list(range(1, len(ORDEM_ESPERADA) + 1))


def test_as_posicoes_cumprem_a_leitura_de_um_edital():
    """FR-008, verificado por posição relativa e não por número mágico."""
    posicao = {s.key: s.order for s in secoes.CATALOGO}

    assert posicao["apresentacao"] < posicao["perfis"], "a apresentação vem antes dos Perfis"
    assert posicao["requisitos-gerais"] < posicao["inscricao"], (
        "os requisitos gerais vêm antes da inscrição"
    )
    assert posicao["classificacao"] > posicao["etapas"], (
        "a classificação vem depois das Etapas de Avaliação"
    )


@pytest.mark.parametrize("chave", ["apresentacao", "requisitos-gerais", "classificacao"])
def test_as_tres_novas_sao_textuais_com_redacao_inicial(chave):
    secao = secoes.POR_CHAVE[chave]

    assert secao.type == secoes.TEXTUAL
    assert not secao.gerada
    assert secao.default_text.strip(), "seção textual sem redação inicial nasceria vazia"
    assert not secao.source, "seção textual não declara origem"
    assert secoes.e_textual(chave)


def test_seção_gerada_declara_origem_e_nao_traz_texto():
    for secao in secoes.CATALOGO:
        if secao.gerada:
            assert secao.source, secao.key
            assert not secao.default_text, secao.key


def test_a_identidade_deriva_da_chave_e_nao_muda_com_a_renumeracao():
    """D-007: renumerar `order` foi seguro por isto, e este teste é o que o mantém verdadeiro.

    Os valores são os que `uuid5(NAMESPACE, f"{edital}:{chave}")` produzia **antes** da `007`,
    quando `perfis` era a seção 2 e `disposicoes-finais` era a 7. Se alguém trocar a identidade por
    algo que dependa da posição, estes números mudam e o teste acusa — junto com o endereçamento de
    toda Retificação já publicada.
    """
    edital = uuid.UUID("6b83e44e-f63b-41bb-9231-0c754db388f6")

    esperado = {
        chave: str(uuid.uuid5(secoes.NAMESPACE, f"{edital}:{chave}"))
        for chave, _, _ in ORDEM_ESPERADA
    }
    for chave, identidade in esperado.items():
        assert str(secoes.identidade(edital, chave)) == identidade

    # E a identidade é distinta entre Editais, para a mesma chave.
    outro = uuid.UUID("6dddda31-71c9-4a9d-80ee-03e1b5c1d0ba")
    assert secoes.identidade(outro, "perfis") != secoes.identidade(edital, "perfis")


def test_a_identidade_e_estavel_entre_chamadas():
    edital = uuid.uuid4()
    assert secoes.identidade(edital, "apresentacao") == secoes.identidade(edital, "apresentacao")


def test_chaves_textuais_e_por_chave_cobrem_o_catalogo():
    assert set(secoes.POR_CHAVE) == {chave for chave, _, _ in ORDEM_ESPERADA}
    assert secoes.CHAVES_TEXTUAIS == {
        chave for chave, _, tipo in ORDEM_ESPERADA if tipo == secoes.TEXTUAL
    }
