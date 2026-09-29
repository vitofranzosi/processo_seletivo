"""T011 e T012 — o catálogo de Seções, declarado e fixo.

A `007` acrescenta três seções institucionais e renumera a ordem; a `009` acrescenta a décima
primeira, gerada, com os documentos exigidos do candidato; a `054` o amplia para 22, pelas famílias
da amostra, e tira a redação padrão. O que estes testes protegem é que o
catálogo continua sendo **catálogo**: conjunto e ordem definidos pelo sistema (FR-009), e
identidade derivada da chave — não da posição (D-007).
"""

import uuid

from processo_seletivo.editais.domain import secoes

# A ordem declarada pela `054` (FR-980): a união das seções que se repetem nas quatro famílias da
# amostra do Cefor, a oferta antes da inscrição. As 12 de antes mantêm a chave (FR-981).
ORDEM_ESPERADA = [
    ("apresentacao", "Apresentação", secoes.TEXTUAL),
    ("disposicoes-preliminares", "Disposições Preliminares", secoes.TEXTUAL),
    ("informacoes-gerais", "Informações Gerais sobre o Curso", secoes.TEXTUAL),
    ("publico-alvo", "Público-Alvo", secoes.TEXTUAL),
    ("requisitos-gerais", "Requisitos Gerais de Participação", secoes.TEXTUAL),
    ("perfis", "Perfis de Vaga", secoes.GERADA),
    ("inscricao", "Da Inscrição", secoes.TEXTUAL),
    ("documentos-exigidos", "Documentos Exigidos para a Inscrição", secoes.GERADA),
    ("verificacao-autodeclaracao", "Da Verificação da Autodeclaração", secoes.TEXTUAL),
    ("atendimento-pcd", "Do Atendimento à Pessoa com Deficiência", secoes.TEXTUAL),
    ("etapas", "Etapas de Avaliação", secoes.GERADA),
    ("classificacao", "Critérios de Classificação", secoes.TEXTUAL),
    ("cronograma", "Cronograma", secoes.GERADA),
    ("recursos", "Dos Recursos", secoes.TEXTUAL),
    ("convocacao", "Da Convocação", secoes.TEXTUAL),
    ("matricula", "Da Matrícula", secoes.TEXTUAL),
    ("acesso-ao-curso", "Do Acesso ao Curso", secoes.TEXTUAL),
    ("homologacao-matricula", "Da Homologação da Matrícula", secoes.TEXTUAL),
    ("certificado", "Do Certificado", secoes.TEXTUAL),
    ("prazo-de-validade", "Do Prazo de Validade", secoes.TEXTUAL),
    # A `020` acrescenta a relação dos Anexos, e ela é **gerada**: o catálogo lista os anexos que o
    # Edital publica, e quem os declara é a etapa própria, não um texto redigido aqui.
    ("anexos", "Anexos", secoes.GERADA),
    ("disposicoes-finais", "Disposições Finais", secoes.TEXTUAL),
]


def test_o_catalogo_tem_as_secoes_declaradas_na_ordem():
    assert [(s.key, s.title, s.type) for s in secoes.CATALOGO] == ORDEM_ESPERADA


def test_a_ordem_declarada_e_uma_sequencia_sem_buraco():
    """`order` é conteúdo normativo e o documento o respeita; buraco ou repetição seria defeito."""
    assert [s.order for s in secoes.CATALOGO] == list(range(1, len(ORDEM_ESPERADA) + 1))


def test_as_posicoes_cumprem_a_leitura_de_um_edital():
    """FR-008 da 007 e FR-980 da 054, verificados por posição relativa e não por número mágico."""
    posicao = {s.key: s.order for s in secoes.CATALOGO}

    assert posicao["apresentacao"] < posicao["perfis"], "a apresentação vem antes dos Perfis"
    assert posicao["requisitos-gerais"] < posicao["inscricao"], (
        "os requisitos gerais vêm antes da inscrição"
    )
    assert posicao["perfis"] < posicao["inscricao"], (
        "a oferta vem antes da inscrição, como nos quinze Editais da amostra (054, FR-980)"
    )
    assert posicao["classificacao"] > posicao["etapas"], (
        "a classificação vem depois das Etapas de Avaliação"
    )
    assert posicao["disposicoes-finais"] == len(secoes.CATALOGO), "as disposições finais fecham"


def test_nenhuma_secao_tem_redacao_padrao():
    """FR-983 da 054: a textual nasce vazia, e o documento só publica o que alguém escreveu."""
    for secao in secoes.CATALOGO:
        assert not hasattr(secao, "default_text"), secao.key


def test_secao_textual_nao_declara_origem_e_a_gerada_declara():
    for secao in secoes.CATALOGO:
        if secao.gerada:
            assert secao.source, secao.key
        else:
            assert not secao.source, secao.key
            assert secoes.e_textual(secao.key)


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
