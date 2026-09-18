"""O Edital publicado basta para reconstruir a ordem que o sistema calculou (E2E15-004/005/008).

O ato de classificação sempre foi reprodutível *por dentro*. O que a auditoria exploratória da
`015` mostrou é que ele não era reconstituível **a partir do papel**: o documento imprimia
"2º maior valor declarado" sem dizer de quê, nunca lia `declaredFacts`, e trazia "soma ponderada"
sem a escala, o modo de arredondamento, a normalização nem os pesos das Etapas que combina. Um
candidato — ou um juiz — que lesse só o documento oficial não chegava ao mesmo resultado.

O que se prova aqui é isso, e nada mais forte: que cada parâmetro que fecha a conta está no
documento, junto da regra que o usa, escrito com os **nomes publicados**. As garantias que este
trabalho não pode quebrar — nenhum identificador técnico no papel, decimais em português —
continuam afirmadas em `test_pdf.py` e em `tests/contract/test_documento_publicado.py`; aqui elas
reaparecem apenas sobre o conteúdo novo, que é onde passariam a poder vazar.
"""

import re

import pytest

from tests.unit.publicacoes.test_pdf import documento, snapshot, texto_de

PERFIL = "33333333-3333-3333-3333-333333333333"
DIDATICA = "77777777-7777-7777-7777-777777777777"
TITULOS = "88888888-8888-8888-8888-888888888888"
ENTREVISTA = "99999999-9999-9999-9999-999999999999"
NASCIMENTO = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
EXPERIENCIA = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
MARCO = "cccccccc-cccc-cccc-cccc-cccccccccccc"

FATOS = [
    {"id": NASCIMENTO, "code": "NASCIMENTO", "label": "Data de nascimento", "type": "DATA"},
    {
        "id": EXPERIENCIA,
        "code": "EXPERIENCIA",
        "label": "Meses de experiência em EaD",
        "type": "INTEIRO",
    },
]

ETAPAS = [
    {
        "id": DIDATICA,
        "name": "Prova didática",
        "order": 1,
        "weight": "2.0000",
        "eliminatory": True,
        "classificatory": True,
        "minimumScore": "7.0000",
        "scheduleEventId": None,
    },
    {
        "id": TITULOS,
        "name": "Análise de títulos",
        "order": 2,
        "weight": "1.0000",
        "eliminatory": False,
        "classificatory": True,
        "minimumScore": None,
        "scheduleEventId": None,
    },
]


def criterio(ordem, tipo, parametros, quando_ausente="ULTIMO_NO_CRITERIO"):
    return {
        "id": f"dddddddd-dddd-dddd-dddd-00000000000{ordem}",
        "order": ordem,
        "type": tipo,
        "parameters": parametros,
        "whenMissing": quando_ausente,
    }


CRITERIOS = [
    criterio(1, "MAIOR_PONTUACAO_NA_ETAPA", {"stageId": DIDATICA}),
    criterio(2, "MAIOR_VALOR_DE_FATO", {"factId": EXPERIENCIA}),
    criterio(3, "MENOR_VALOR_DE_FATO", {"factId": NASCIMENTO}, "CRITERIO_NAO_SE_APLICA"),
]


def marco(**alteracoes):
    base = {
        "id": MARCO,
        "code": "FINAL",
        "name": "Classificação final",
        "stages": [DIDATICA, TITULOS],
        "orderProduction": "POR_PONTUACAO",
        "operation": "SOMA_PONDERADA",
        "normalization": "NENHUMA",
        "rounding": {"scale": 2, "mode": "MEIO_PARA_CIMA"},
        "tiebreakers": list(CRITERIOS),
    }
    return {**base, **alteracoes}


def com_classificacao(*, marcos=None, fatos=None, etapas=None):
    """O cenário-base da `015`: um Perfil que declara fatos e publica um marco sobre duas Etapas."""
    base = snapshot()
    perfil = {
        **base["profiles"][0],
        "declaredFacts": FATOS if fatos is None else fatos,
        "classificationMilestones": [marco()] if marcos is None else marcos,
    }
    return snapshot(profiles=[perfil], stages=ETAPAS if etapas is None else etapas)


def texto(conteudo):
    """O texto desenhado, com as quebras de refluxo desfeitas.

    `texto_de` devolve uma linha por linha **desenhada**, e uma frase normativa longa — o critério
    com o alvo e a regra de ausência, a combinação com os pesos — atravessa duas. Afirmá-la contra
    o texto cru faria o teste depender da largura da página, e não do que o documento diz.

    Colapsar espaço em branco só pode criar coincidência, nunca escondê-la: as afirmações de
    ausência ficam mais estritas, não menos.
    """
    return re.sub(r"\s+", " ", texto_de(documento(conteudo)))


# ---------------------------------------------------------------------------
# E2E15-004 — o critério diz o que compara
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("trecho", "porque"),
    [
        ("1º maior pontuação na Etapa Prova didática", "o alvo de Etapa vira o nome publicado"),
        (
            "2º maior valor declarado em Meses de experiência em EaD",
            "o alvo de fato vira o rótulo publicado",
        ),
        (
            "3º menor valor declarado em Data de nascimento",
            "e o de menor valor também — o tipo muda a frase, não a resolução do alvo",
        ),
    ],
)
def test_cada_criterio_de_desempate_nomeia_o_que_compara(trecho, porque):
    """ "2º maior valor declarado" não é regra: é a metade dela.

    `parameters` carrega `stageId` ou `factId` conforme o tipo, e era descartado na tradução do
    enum. O desempate aplicado pelo sistema não era o que o Edital deixava reconstituir.
    """
    assert trecho in texto(com_classificacao()), porque


def test_a_ordem_impressa_e_a_declarada_e_nao_a_posicao_no_conteudo():
    """A norma declara `order`; a posição no array é acidente de gravação.

    Uma Retificação que reordene os critérios endereça por identidade e pode deixar a lista fora
    de ordem. Imprimir a posição faria o documento dizer uma coisa e o cálculo fazer outra.
    """
    invertidos = list(reversed(CRITERIOS))

    escrito = texto(com_classificacao(marcos=[marco(tiebreakers=invertidos)]))

    posicoes = [escrito.index(f"{ordem}º ") for ordem in (1, 2, 3)]
    assert posicoes == sorted(posicoes)
    assert "1º maior pontuação na Etapa Prova didática" in escrito


@pytest.mark.parametrize(
    ("quando_ausente", "frase"),
    [
        ("ULTIMO_NO_CRITERIO", "sem o valor, fica por último neste critério"),
        ("CRITERIO_NAO_SE_APLICA", "sem o valor, o critério não se aplica"),
    ],
)
def test_o_criterio_declara_o_que_fazer_na_ausencia_do_valor(quando_ausente, frase):
    """Sem isto, dois candidatos em que um não tem o valor não são separáveis no papel."""
    unico = [criterio(1, "MAIOR_VALOR_DE_FATO", {"factId": EXPERIENCIA}, quando_ausente)]

    assert frase in texto(com_classificacao(marcos=[marco(tiebreakers=unico)]))


# ---------------------------------------------------------------------------
# E2E15-005 — os fatos exigidos são anunciados antes do envio
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("trecho", "porque"),
    [
        ("Dados exigidos na inscrição", "o bloco se anuncia"),
        ("Data de nascimento (data)", "o fato sai com rótulo e tipo publicados"),
        ("Meses de experiência em EaD (número inteiro)", "e o tipo inteiro também tem nome"),
    ],
)
def test_o_perfil_anuncia_os_dados_que_a_inscricao_vai_exigir(trecho, porque):
    """O candidato os descobria na tela de revisão, no instante do envio — e são irreversíveis."""
    assert trecho in texto(com_classificacao()), porque


def test_os_dados_exigidos_vem_antes_das_modalidades_e_dos_marcos_que_os_consomem():
    """Quem decide se concorre lê o que a vaga exige antes de ler como ela ordena."""
    escrito = texto(com_classificacao())

    assert (
        escrito.index("Dados exigidos na inscrição")
        < escrito.index("Modalidades de concorrência")
        < escrito.index("Marcos classificatórios")
    )


def test_perfil_sem_fato_declarado_nao_compoe_o_bloco():
    """Título sobre nada afirmaria que a inscrição exige dados que este Edital não declara."""
    assert "Dados exigidos na inscrição" not in texto(com_classificacao(fatos=[]))


# ---------------------------------------------------------------------------
# E2E15-008 — os parâmetros que fecham a conta
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("trecho", "porque"),
    [
        (
            "soma ponderada das Etapas Prova didática (peso 2) e Análise de títulos (peso 1)",
            "o peso de cada Etapa aparece junto da regra que o usa, e não só na seção da Etapa",
        ),
        ("Normalização:", "a normalização é declarada, e não deduzida da operação"),
        ("Arredondamento:", "a escala e o modo saem do snapshot para o papel"),
        ("2 casas decimais, meio para cima", "e saem por extenso, não como enum"),
    ],
)
def test_o_marco_publica_o_que_basta_para_refazer_a_conta(trecho, porque):
    """Com duas Etapas de peso 1 e 2, a nota combinada não era reconstruível a partir do papel."""
    assert trecho in texto(com_classificacao()), porque


@pytest.mark.parametrize(
    ("normalizacao", "frase"),
    [("NENHUMA", "nenhuma"), ("PELA_SOMA_DOS_PESOS", "pela soma dos pesos")],
)
def test_a_normalizacao_sai_por_extenso(normalizacao, frase):
    escrito = texto(com_classificacao(marcos=[marco(normalization=normalizacao)]))

    assert f"Normalização: {frase}" in escrito
    assert normalizacao not in escrito


@pytest.mark.parametrize(
    ("arredondamento", "frase"),
    [
        ({"scale": 0, "mode": "TRUNCAR"}, "sem casas decimais, truncamento"),
        ({"scale": 1, "mode": "MEIO_PARA_PAR"}, "1 casa decimal, meio para par"),
        ({"scale": 4, "mode": "MEIO_PARA_CIMA"}, "4 casas decimais, meio para cima"),
    ],
)
def test_a_escala_e_o_modo_do_arredondamento_saem_em_portugues(arredondamento, frase):
    """`ROUND_HALF_UP` é da biblioteca e `MEIO_PARA_CIMA` é do snapshot: o Edital escreve a
    frase."""
    escrito = texto(com_classificacao(marcos=[marco(rounding=arredondamento)]))

    assert frase in escrito
    assert arredondamento["mode"] not in escrito


def test_o_peso_fracionario_do_marco_sai_com_virgula():
    """A forma canônica de quatro casas é do snapshot; o peso repetido aqui segue a mesma
    régua."""
    fracionaria = [{**ETAPAS[0], "weight": "1.7500"}, ETAPAS[1]]

    escrito = texto(com_classificacao(etapas=fracionaria))

    assert "Prova didática (peso 1,75)" in escrito
    assert not re.search(r"\d\.\d{4}\b", escrito)


def test_etapa_decisoria_enumerada_e_porta_e_nao_ganha_peso():
    """Ela não produz número e não contribui com grandeza (FR-074) — dizer "peso" seria inventar."""
    porta = [
        {**ETAPAS[0], "weight": None, "forma": "DECISORIA", "rotuloFavoravel": "Deferida"},
        ETAPAS[1],
    ]

    escrito = texto(com_classificacao(etapas=porta))

    assert "Prova didática (não pontua)" in escrito
    assert "Prova didática (peso" not in escrito


def test_perfil_sem_marco_nao_compoe_o_bloco():
    assert "Marcos classificatórios" not in texto(com_classificacao(marcos=[]))


# ---------------------------------------------------------------------------
# O que a resolução dos alvos não pode produzir
# ---------------------------------------------------------------------------


def test_alvo_inexistente_nao_derruba_o_documento_e_nao_imprime_identificador():
    """A publicação recusa o critério pendurado (FR-017); a prévia de um rascunho, não.

    Compor tinha de continuar possível, e a lacuna tinha de ficar legível: trocar um alvo ausente
    pelo UUID que o snapshot guarda seria substituir uma falta que se lê por uma que ninguém sabe
    ler — e violaria a garantia de que nenhum estado interno de entidade chega ao papel.
    """
    perdidos = [
        criterio(1, "MAIOR_PONTUACAO_NA_ETAPA", {"stageId": ENTREVISTA}),
        criterio(2, "MAIOR_VALOR_DE_FATO", {"factId": ENTREVISTA}),
        criterio(3, "MENOR_VALOR_DE_FATO", {}),
    ]

    escrito = texto(com_classificacao(marcos=[marco(tiebreakers=perdidos)]))

    assert "1º maior pontuação na Etapa não identificada neste Edital" in escrito
    assert "2º maior valor declarado em dado não identificado neste Edital" in escrito
    assert "3º menor valor declarado em dado não identificado neste Edital" in escrito
    assert ENTREVISTA not in escrito


def test_etapa_enumerada_que_o_edital_nao_carrega_e_dita_como_ausente():
    """Deixá-la cair em silêncio faria o documento anunciar uma combinação menor do que a regra."""
    escrito = texto(com_classificacao(marcos=[marco(stages=[DIDATICA, ENTREVISTA])]))

    assert "Prova didática (peso 2) e Etapa não identificada neste Edital" in escrito
    assert ENTREVISTA not in escrito


def test_nenhum_identificador_tecnico_da_classificacao_chega_ao_papel():
    """A garantia de `test_a_declaracao_de_integridade_identifica_sem_expor_uuid`, sobre o novo.

    O marco, os critérios e os fatos entraram no documento carregando `id` — que é exatamente o
    caminho por onde um UUID passaria a vazar sem que nenhum teste anterior notasse.
    """
    escrito = texto(com_classificacao())

    assert not re.search(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", escrito)


def test_nenhuma_grafia_de_enum_do_marco_chega_ao_papel():
    escrito = texto(com_classificacao())

    for enumeracao in (
        "SOMA_PONDERADA",
        "MEDIA_PONDERADA",
        "NENHUMA",
        "PELA_SOMA_DOS_PESOS",
        "MEIO_PARA_CIMA",
        "MAIOR_PONTUACAO_NA_ETAPA",
        "MAIOR_VALOR_DE_FATO",
        "MENOR_VALOR_DE_FATO",
        "ULTIMO_NO_CRITERIO",
        "CRITERIO_NAO_SE_APLICA",
    ):
        assert enumeracao not in escrito, enumeracao


def test_nenhuma_linha_da_classificacao_ultrapassa_a_margem():
    """FR-029, no recuo onde este trabalho é mais capaz de quebrá-lo.

    O par rótulo-valor escreve o valor a partir da largura do rótulo, e aqui ele começa 32 pontos
    para dentro — mais fundo que os pares da Etapa, e com um valor que pode enumerar Etapas até
    encher a linha. Um rótulo longo empurrando um valor longo é exatamente o caso em que o refluxo
    passaria da margem sem nenhum teste existente notar.
    """
    from processo_seletivo.publicacoes.infrastructure.pdf import LARGURA, MARGEM, largura
    from tests.unit.publicacoes.test_pdf import linhas_desenhadas

    muitas = [
        {**ETAPAS[0], "id": f"{indice:08d}-0000-0000-0000-000000000000", "name": f"Etapa {indice}"}
        for indice in range(1, 13)
    ]
    conteudo = com_classificacao(
        etapas=muitas, marcos=[marco(stages=[etapa["id"] for etapa in muitas])]
    )

    util = LARGURA - 2 * MARGEM
    for linha, fonte, tamanho, recuo in linhas_desenhadas(documento(conteudo)):
        assert largura(linha, tamanho, fonte) + recuo <= util + 0.5, f"{linha!r} passa da margem"


def test_com_mais_de_um_perfil_o_bloco_diz_de_qual_perfil_e_o_marco():
    """Dois Perfis publicam marcos homônimos, e a regra de um não é a do outro.

    O bloco deixou de ser tabela e perdeu a legenda que o nomeava; o Perfil volta ao título por
    isso — o documento não pode ter dois "Marcos classificatórios" indistinguíveis quando a
    Etapa que cada um combina, e o peso com que a combina, são outros.
    """
    base = snapshot()["profiles"][0]
    segundo = {
        **base,
        "id": "eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee",
        "code": "DOC-MAT",
        "name": "Professor de Matemática",
        "declaredFacts": [],
        "classificationMilestones": [marco(stages=[TITULOS])],
    }
    primeiro = {**base, "declaredFacts": FATOS, "classificationMilestones": [marco()]}

    escrito = texto(snapshot(profiles=[primeiro, segundo], stages=ETAPAS))

    assert "Marcos classificatórios — DOC-INFO" in escrito
    assert "Marcos classificatórios — DOC-MAT" in escrito
    assert "soma ponderada da Etapa Análise de títulos (peso 1)" in escrito


# ---------------------------------------------------------------------------
# 032 — a seção do marco diz como a ordem nasce, e publica o método do sorteio
# ---------------------------------------------------------------------------
#
# **O `ACH-50`, visto do papel.** O documento de um Edital de sorteio imprimia "soma ponderada da
# Etapa…" — uma regra que aquele marco não aplica — e não imprimia nada do método que ele aplica.
# Quem recebia o Edital lia um método falso e não tinha como conferir o sorteio contra a norma.
#
# **O documento publica a norma, e não o resultado.** Ele imprime a ocorrência que **fixará** a
# semente, e nunca a semente: no dia da publicação ela ainda não existe. Quem publica a semente é o
# documento do resultado do sorteio (`Algoritmo`, `Semente`), e a verificação pública compara os
# dois — é essa comparação que a `FR-465` torna possível.

METODO_DO_EDITAL = {
    "algorithm": "IFES-SORTEIO-SHA256-v1",
    "source": "Loteria Federal",
    "occurrence": "concurso 6100 da Loteria Federal",
    "occurrenceAt": "2026-11-20T20:00:00-03:00",
    "derivation": "o primeiro concurso realizado após a data programada do sorteio",
    "normalization": {
        "rule": "DIGITOS_EM_SEQUENCIA",
        "text": "os dígitos das cinco dezenas, em sequência",
    },
    "substitutionRule": {
        "rule": "OCORRENCIA_SEGUINTE_DA_MESMA_FONTE",
        "text": "a ocorrência seguinte da mesma fonte",
    },
}

METODO_PROPRIO = {
    **METODO_DO_EDITAL,
    "occurrence": "concurso 6101 da Loteria Federal",
    "derivation": "o segundo concurso realizado após a data programada do sorteio",
}


def sorteado(**alteracoes):
    """O marco que ordena por sorteio. Sem `stages`: sortear não exige Etapa (030, `FR-432`)."""
    return marco(
        **{
            "code": "SORT-X",
            "name": "Sorteio público",
            "orderProduction": "POR_SORTEIO",
            "stages": [],
            "tiebreakers": [],
            **alteracoes,
        }
    )


def documento_de_sorteio(*, no_marco=None, no_edital=None):
    """O conteúdo de um Edital cujo único marco sorteia, com o método onde o chamador o puser."""
    base = com_classificacao(marcos=[sorteado(drawMethod=no_marco)] if no_marco else [sorteado()])
    if no_marco is None:
        base["profiles"][0]["classificationMilestones"][0].pop("drawMethod", None)
    if no_edital is not None:
        base["drawMethod"] = no_edital
    return texto(base)


def test_o_marco_declara_como_a_ordem_dele_e_produzida():
    """`FR-464`: a primeira coisa que a seção do marco diz é de onde a ordem vem."""
    assert "Ordem: pela pontuação combinada das Etapas" in texto(com_classificacao())
    assert "Ordem: por sorteio" in documento_de_sorteio(no_edital=METODO_DO_EDITAL)


def test_o_marco_do_acervo_sem_forma_declarada_sai_exatamente_como_hoje():
    """A outra metade da `FR-464`, e a que protege o acervo.

    Marco composto antes da `030` não declara `orderProduction`, e a ausência **é** a afirmação:
    dela os leitores derivam o comportamento de sempre. O documento dele não ganha o par `Ordem`, e
    tudo o mais continua onde estava — inclusive a combinação, que é o que ele sempre imprimiu.
    """
    do_acervo = marco()
    do_acervo.pop("orderProduction")

    escrito = texto(com_classificacao(marcos=[do_acervo]))

    assert "Ordem:" not in escrito
    assert "soma ponderada das Etapas Prova didática (peso 2) e Análise de títulos (peso 1)" in (
        escrito
    )


@pytest.mark.parametrize(
    ("rotulo", "trecho"),
    [
        ("Algoritmo", "IFES-SORTEIO-SHA256-v1"),
        ("Fonte", "Loteria Federal"),
        ("Ocorrência", "concurso 6100 da Loteria Federal"),
        ("Quando", "20/11/2026, às 20h"),
        ("Derivação", "o primeiro concurso realizado após a data programada do sorteio"),
        ("Semente", "os dígitos das cinco dezenas, em sequência"),
        ("Se faltar", "a ocorrência seguinte da mesma fonte"),
    ],
)
def test_o_documento_imprime_os_sete_dados_do_metodo(rotulo, trecho):
    """`FR-465` e `SC-158`: os sete que tornam a semente reproduzível por terceiro.

    O instante sai como um Edital escreve data e hora — `20/11/2026, às 20h` —, e não como um banco
    a armazena. A normalização e a substituição saem pela **frase publicada**: o identificador é o
    que a máquina aplica, e ele mora no manifesto do sorteio, não no Edital.
    """
    escrito = documento_de_sorteio(no_edital=METODO_DO_EDITAL)

    assert f"{rotulo}: {trecho}" in escrito


def test_os_rotulos_do_metodo_saem_do_vocabulario_do_dominio():
    """Princípio I: o documento e a tela de composição dizem a mesma coisa com as mesmas palavras.

    A varredura é sobre a **fonte**, e não sobre a grafia: se `CAMPOS_DO_METODO` ganhar um oitavo
    campo, ou perder um, este teste falha antes de o documento passar a omitir algo que a norma
    declara. É o que impede o renderizador de inventar um oitavo nome para a mesma coisa.
    """
    from processo_seletivo.editais.domain.perfis import CAMPOS_DO_METODO

    escrito = documento_de_sorteio(no_edital=METODO_DO_EDITAL)

    assert len(CAMPOS_DO_METODO) == 7
    for _, _, rotulo in CAMPOS_DO_METODO:
        assert f"{rotulo}:" in escrito, rotulo


@pytest.mark.parametrize(
    ("no_marco", "no_edital", "grafia"),
    [
        (None, METODO_DO_EDITAL, "Método: comum a este Edital"),
        (
            METODO_PROPRIO,
            METODO_DO_EDITAL,
            "Método: próprio deste marco — diverge do comum deste Edital",
        ),
        (METODO_PROPRIO, None, "Método: próprio deste marco"),
    ],
)
def test_o_documento_diz_qual_metodo_governa_o_marco(no_marco, no_edital, grafia):
    """`FR-466`, e são três grafias — a quarta não chega ao documento porque `FR-467` a recusa."""
    assert grafia in documento_de_sorteio(no_marco=no_marco, no_edital=no_edital)


def test_o_proprio_identico_ao_comum_nao_e_anunciado_como_divergente():
    """A `FR-466` nomeia a divergência **quando ela existe**.

    Um marco que declara o próprio idêntico ao comum não diverge de nada, e escrever que diverge
    seria o documento afirmando uma diferença que ninguém publicou.
    """
    escrito = documento_de_sorteio(no_marco=METODO_DO_EDITAL, no_edital=METODO_DO_EDITAL)

    assert "Método: próprio deste marco" in escrito
    assert "diverge" not in escrito


def test_o_marco_que_sorteia_nao_imprime_combinacao_de_pontuacoes():
    """`FR-468`: aquela ordem não vem de nota, e imprimi-la era o que afirmava um método falso."""
    escrito = documento_de_sorteio(no_edital=METODO_DO_EDITAL)

    assert "Combinação" not in escrito
    assert "Normalização:" not in escrito
    assert "soma ponderada" not in escrito


def test_o_marco_que_ordena_por_pontuacao_nao_ganha_bloco_de_sorteio():
    """A contraprova simétrica: o Edital comum não passa a falar de sorteio."""
    escrito = texto(com_classificacao())

    assert "Sorteio" not in escrito
    assert "Método:" not in escrito
    assert "soma ponderada das Etapas Prova didática (peso 2)" in escrito
