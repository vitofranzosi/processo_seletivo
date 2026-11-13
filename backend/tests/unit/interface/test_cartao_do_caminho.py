"""Do caminho normativo ao cartão da tela Retificar (123, R-004, R-005).

O achado da conferência e a Alteração da proposta falam por caminho; a tela fala por cartão. A
tradução decide **para onde** o «Ir ao cartão» leva e **qual** cartão ganha «na proposta» — e o erro
dela é silencioso: o Perfil que ninguém tocou marcado, ou o link do quadro levando ao Perfil, e não
à linha que soma errado.
"""

from processo_seletivo.interface.retificacao import cartao_do_caminho, referencias_na_proposta

PERFIL = "/profiles/id=P1"
GRUPOS = [
    {"referencia": "g1", "caminho": ""},
    {"referencia": "g2", "caminho": PERFIL},
    {"referencia": "g3", "caminho": f"{PERFIL}/competitionModalities/id=AC"},
    {"referencia": "g4", "caminho": f"{PERFIL}/vacancyTable/id=L1"},
    {"referencia": "g5", "caminho": f"{PERFIL}/vacancyTable/id=L2"},
    {"referencia": "g6", "caminho": "/profiles/id=P12"},
    {"referencia": "g7", "caminho": "/schedule/id=E1"},
]


def test_o_caminho_exato_e_o_proprio_cartao():
    assert cartao_do_caminho(GRUPOS, PERFIL) == "cartao-g2"


def test_a_colecao_leva_a_primeira_linha_dela():
    # O achado da soma do quadro mora em `…/vacancyTable`: volta-se à linha, e não ao Perfil.
    assert cartao_do_caminho(GRUPOS, f"{PERFIL}/vacancyTable") == "cartao-g4"


def test_o_campo_leva_ao_ancestral_mais_fundo():
    assert cartao_do_caminho(GRUPOS, f"{PERFIL}/immediateVacancies") == "cartao-g2"
    assert cartao_do_caminho(GRUPOS, f"{PERFIL}/vacancyTable/id=L2/immediateVacancies") == (
        "cartao-g5"
    )


def test_prefixo_so_em_fronteira_de_segmento():
    assert cartao_do_caminho(GRUPOS, "/profiles/id=P12/name") == "cartao-g6"
    assert cartao_do_caminho(GRUPOS, "/profiles/id=P1/name") == "cartao-g2"


def test_campo_da_raiz_leva_a_identificacao():
    assert cartao_do_caminho(GRUPOS, "/title") == "cartao-g1"
    assert cartao_do_caminho(GRUPOS, "/drawMethod") == "cartao-g1"
    assert cartao_do_caminho(GRUPOS, "/drawMethod/algorithm") == "cartao-g1"


def test_colecao_sem_cartao_leva_a_secao_so_se_ela_esta_na_pagina():
    assert cartao_do_caminho(GRUPOS, "/stages", secoes={"etapas"}) == "s-etapas"
    assert cartao_do_caminho(GRUPOS, "/stages", secoes={"perfis", "cronograma"}) is None


def test_entidade_acrescentada_nesta_tela_leva_a_linha_nova():
    novas = {"NOVO-E": "novo-evento-0"}
    assert cartao_do_caminho(GRUPOS, "/schedule/id=NOVO-E/startAt", novas) == "cartao-novo-evento-0"


def test_replace_marca_o_cartao_do_campo():
    alteracoes = [
        {"targetPath": f"{PERFIL}/vacancyTable/id=L1/immediateVacancies", "operation": "REPLACE"},
        {"targetPath": "/title", "operation": "REPLACE"},
    ]
    assert referencias_na_proposta(GRUPOS, alteracoes) == ({"g4", "g1"}, 0)


def test_acrescentar_linha_aninhada_nao_marca_o_perfil():
    alteracoes = [
        {
            "targetPath": f"{PERFIL}/vacancyTable/-",
            "operation": "ADD",
            "newValue": {"id": "L9", "modalityId": None, "immediateVacancies": 1},
        },
        {
            "targetPath": f"{PERFIL}/competitionModalities/-",
            "operation": "ADD",
            "newValue": {"id": "EP", "code": "EP"},
        },
    ]
    novas = {"L9": "novo-linha-do-quadro-0", "EP": "novo-modalidade-0"}
    assert referencias_na_proposta(GRUPOS, alteracoes, novas) == (
        {"novo-linha-do-quadro-0", "novo-modalidade-0"},
        0,
    )


def test_a_ampla_que_a_modalidade_nova_declara_marca_o_perfil():
    alteracoes = [
        {"targetPath": f"{PERFIL}/generalCompetitionModalityId", "operation": "REPLACE"},
    ]
    assert referencias_na_proposta(GRUPOS, alteracoes) == ({"g2"}, 0)


def test_acrescido_ja_desenhado_marca_o_proprio_cartao():
    # A edição: o Evento acrescido pelo rascunho já está no proposto, com cartão.
    alteracoes = [
        {"targetPath": "/schedule/-", "operation": "ADD", "newValue": {"id": "E1"}},
    ]
    assert referencias_na_proposta(GRUPOS, alteracoes) == ({"g7"}, 0)


def test_remocao_marca_o_proprio_cartao_e_sem_ele_conta_a_parte():
    alteracoes = [
        {"targetPath": f"{PERFIL}/competitionModalities/id=AC", "operation": "REMOVE"},
        # A edição: a Modalidade removida já não está no proposto, e não marca o Perfil dela.
        {"targetPath": f"{PERFIL}/competitionModalities/id=PPI", "operation": "REMOVE"},
    ]
    assert referencias_na_proposta(GRUPOS, alteracoes) == ({"g3"}, 1)
