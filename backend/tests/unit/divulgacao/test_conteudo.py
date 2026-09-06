"""A projeção do ato: o que atravessa a fronteira pública, e o que fica do lado de cá.

O que estes testes prendem é a **separação**, e não a serialização: quem recebeu posição vai para
as duas projeções, quem não recebeu vai só para a individual, e nenhuma delas carrega identificador
ou valor de desempate.
"""

import pytest

from processo_seletivo.divulgacao.domain.conteudo import compor
from processo_seletivo.divulgacao.models import SituacaoDivulgada
from tests.fixtures.divulgacao import MODALIDADE_NOME, montar_ato_publicavel

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


@pytest.fixture
def com_empate(gestor, api_client, manager_headers, process_payload):
    """1º, 2º, 3º, 3º — e uma quinta considerada **sem** Resultado, portanto sem posição.

    O empate é residual de verdade: o marco não declara critério de desempate, e por isso duas
    pontuações iguais permanecem empatadas. Inventar um desempate para separá-las seria o defeito
    que a FR-014 nomeia.
    """
    return montar_ato_publicavel(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=50,
        codigo="0750",
        pontuacoes=("90.0000", "80.0000", "70.0000", "70.0000", None),
        primeiro=101,
    )


def test_os_rotulos_vem_resolvidos_do_conteudo_publicado(com_empate):
    """Nada na renderização traduz enum nem resolve identificador (FR-012, FR-013)."""
    projecao = compor(com_empate["ato"])
    cabecalho = projecao["cabecalho"]

    assert cabecalho["marco"] == "Classificação final"
    assert cabecalho["perfil"] == "Perfil"
    assert cabecalho["edital"].startswith("Edital ")
    assert cabecalho["processo"]
    assert all(item["modalidade"] == MODALIDADE_NOME for item in projecao["posicoes"])


def test_o_empate_residual_vira_posicao_compartilhada(com_empate):
    """1º, 2º, 3º, 3º — o grupo empatado consome as posições que ocupa (FR-014, FR-026)."""
    posicoes = compor(com_empate["ato"])["posicoes"]

    assert [item["posicao"] for item in posicoes] == [1, 2, 3, 3]
    assert [item["compartilhada"] for item in posicoes] == [False, False, True, True]


def test_a_natureza_e_o_titulo_sao_texto_e_nao_enum(com_empate):
    """`PRELIMINAR` é grafia interna; o que se divulga é "Resultado preliminar" (FR-013)."""
    from processo_seletivo.divulgacao.domain.conteudo import conteudo_divulgado
    from processo_seletivo.publicacoes.domain.autoridades import escolher

    projecao = compor(com_empate["ato"])
    conteudo = conteudo_divulgado(
        projecao,
        natureza="PRELIMINAR",
        publicado_em=com_empate["ato"].emitido_em,
        signatario=escolher("diretoria-cefor"),
    )

    assert conteudo["cabecalho"]["natureza_rotulo"] == "Resultado preliminar"
    assert conteudo["cabecalho"]["titulo"] == "Resultado preliminar — Perfil"


def test_quem_nao_recebeu_posicao_fica_fora_da_publica_e_dentro_da_individual(com_empate):
    """A tensão entre FR-017 e FR-059, resolvida por **separação** e não por filtro.

    A quinta inscrição foi considerada pelo ato — ela está no universo — e não recebeu posição. Ela
    não é nomeada publicamente, e ainda assim é informada na própria Área. As duas coisas ao mesmo
    tempo só são possíveis porque as projeções são duas.
    """
    projecao = compor(com_empate["ato"])
    sem_posicao = com_empate["inscricoes"][4]

    assert len(projecao["posicoes"]) == 4
    assert len(projecao["situacoes"]) == 5
    assert sem_posicao.nome not in [item["candidato"] for item in projecao["posicoes"]]
    assert sem_posicao.protocolo not in [item["protocolo"] for item in projecao["posicoes"]]

    dela = next(
        item for item in projecao["situacoes"] if str(item["inscricao_id"]) == str(sem_posicao.id)
    )
    assert dela["situacao"] == SituacaoDivulgada.Situacao.SEM_POSICAO
    assert dela["posicao"] is None
    assert dela["motivo"], "sem posição precisa dizer por quê — é o que a pessoa lê (FR-059)"


def test_a_projecao_publica_nao_carrega_identificador_nem_desempate(com_empate):
    """As chaves são as do contrato, e nenhuma a mais (FR-018, FR-019, FR-020)."""
    posicoes = compor(com_empate["ato"])["posicoes"]

    esperadas = {"posicao", "compartilhada", "candidato", "protocolo", "modalidade", "pontuacao"}
    assert all(set(item) == esperadas for item in posicoes)


def test_a_coluna_de_desempate_nao_e_lida(com_empate):
    """A FR-020 deixa de depender de disciplina: o valor não chega a estar em mãos.

    Afirmar sobre a **consulta emitida**, e não sobre o dicionário devolvido, é o que separa "o
    código não copiou o campo" de "o campo não foi buscado". A primeira volta com o próximo
    refactor; a segunda não.
    """
    from django.db import connection
    from django.test.utils import CaptureQueriesContext

    with CaptureQueriesContext(connection) as consultas:
        compor(com_empate["ato"])

    das_posicoes = [
        item["sql"]
        for item in consultas.captured_queries
        if "classificacao_posicaonaordem" in item["sql"]
    ]
    assert das_posicoes, "o teste precisa ver a consulta das posições para afirmar sobre ela"
    assert not any("desempate" in sql for sql in das_posicoes), (
        "a consulta trouxe `desempate`: a coluna não é lida, e é assim que a FR-020 se sustenta"
    )


def test_a_pontuacao_sai_na_apresentacao_institucional(com_empate):
    """`185,00` — texto já formatado, com as casas que o **marco** declarou.

    Reformatar na renderização seria decidir de novo, e faria a página e o documento poderem
    divergir sobre o mesmo número.
    """
    posicoes = compor(com_empate["ato"])["posicoes"]

    assert [item["pontuacao"] for item in posicoes] == ["90,00", "80,00", "70,00", "70,00"]
