"""As três formas de impedimento, cada uma com o seu código — e o que elas **não** fazem.

A parte final é a que mais importa e a menos óbvia: recusar a publicação não pode ter tornado nada
menos consultável. O ato recusado continua abrindo na tela da 015, com a proveniência inteira,
inclusive o desempate e o que cada critério comparou. Publicar é um ato **a mais** sobre o ato de
ordenação; ele não retira nada do que já existia (SC-012, SC-023).
"""

import pytest
from django.urls import reverse

from processo_seletivo.divulgacao.domain.publicabilidade import (
    DESATUALIZADO,
    IMPEDIMENTO,
    INFORMACAO,
    MARCO_REMOVIDO,
    SUCEDIDO,
    aferir,
)
from tests.fixtures.divulgacao import emitir, marco_de, montar_ato_publicavel
from tests.fixtures.edital import caminho_perfil
from tests.fixtures.publicacao import retify
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


@pytest.fixture
def cenario(gestor, api_client, manager_headers, process_payload):
    return montar_ato_publicavel(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=51,
        codigo="0751",
        pontuacoes=("90.0000", "70.0000"),
        primeiro=201,
    )


def test_o_ato_vigente_e_intacto_e_publicavel(cenario):
    aferida = aferir(edital=cenario["edital"], marco_id=cenario["marco"], ato=cenario["ato"])

    assert aferida.nivel == INFORMACAO
    assert aferida.publicavel


def test_o_ato_sucedido_e_recusado_com_o_seu_codigo(cenario, gestor):
    """Divulgar um ato que outro já sucedeu publicaria uma ordem revogada (FR-004)."""
    antigo = cenario["ato"]
    emitir(cenario, gestor, chave="emitir-0751-b", motivo="Resultado tardio.")

    aferida = aferir(edital=cenario["edital"], marco_id=cenario["marco"], ato=antigo)

    assert aferida.nivel == IMPEDIMENTO
    assert aferida.codigo == SUCEDIDO
    assert aferida.status == 409
    assert not aferida.publicavel


def test_o_ato_divergente_e_recusado_com_o_seu_codigo(cenario, api_client, gestor):
    """A regra mudou depois da emissão: divulgar publicaria ordem que o Edital já não produz."""
    from processo_seletivo.resultados.application.ocorrencia import registrar_ocorrencia

    # O universo muda: uma terceira participante entra com Resultado por Ocorrência, e o ato
    # emitido deixa de descrever o conjunto que a regra vigente considera.
    from tests.fixtures.comissao import inscrever

    tardia = inscrever(cenario["edital"], 1, primeiro=299, perfil=cenario["perfil"])[0]
    registrar_ocorrencia(
        actor=gestor,
        processo_id=cenario["edital"].processo_id,
        edital_id=cenario["edital"].id,
        etapa_id=cenario["etapa"],
        inscricao_ids=[tardia.id],
        motivo="Não compareceu à Etapa.",
        idempotency_key="ocorrencia-0751",
        correlation_id="teste",
    )

    aferida = aferir(edital=cenario["edital"], marco_id=cenario["marco"], ato=cenario["ato"])

    assert aferida.nivel == IMPEDIMENTO
    assert aferida.codigo == DESATUALIZADO
    assert aferida.status == 422
    assert aferida.divergencias, "a recusa precisa dizer o que divergiu"


def test_o_marco_removido_e_recusado_com_o_seu_codigo(cenario, api_client):
    """Retificação removeu o marco: não há regra vigente com que comparar (FR-004)."""
    retify(
        api_client,
        cenario["edital"],
        [
            {
                "targetPath": f"{caminho_perfil('classificationMilestones', 51)}/id={marco_de(51)}",
                "operation": "REMOVE",
            }
        ],
        suffix="rm0751",
    )

    aferida = aferir(edital=cenario["edital"], marco_id=cenario["marco"], ato=cenario["ato"])

    assert aferida.nivel == IMPEDIMENTO
    assert aferida.codigo == MARCO_REMOVIDO
    assert aferida.status == 422


def test_as_tres_recusas_nomeiam_o_caminho(cenario, gestor):
    """Uma recusa que não diz o que fazer a seguir devolve a pessoa à tela anterior sem nada."""
    from processo_seletivo.divulgacao.domain.publicabilidade import MENSAGENS

    for mensagem in MENSAGENS.values():
        assert "ato sucessor" in mensagem, (
            "cada recusa aponta para emitir o ato sucessor na tela da 015 (FR-006)"
        )


def test_recusar_a_publicacao_nao_torna_o_ato_menos_consultavel(
    cenario, gestor, client, seletor_ligado
):
    """SC-012 e SC-023: publicar é ato **a mais**, e não retira nada do que já existia.

    O ato recusado continua abrindo na tela da 015, com a proveniência inteira — inclusive o
    desempate e o que cada critério comparou. Se divulgar passasse a ser condição de consultar,
    a 017 teria quebrado a 015 ao acrescentar-se a ela.
    """
    antigo = cenario["ato"]
    emitir(cenario, gestor, chave="emitir-0751-c", motivo="Resultado tardio.")
    assert not aferir(edital=cenario["edital"], marco_id=cenario["marco"], ato=antigo).publicavel

    identificar(client, "maria", ["gestor"])
    resposta = client.get(
        reverse(
            "interface:ato-de-ordenacao", args=[cenario["edital"].id, cenario["marco"], antigo.id]
        )
    )
    corpo = resposta.content.decode()

    assert resposta.status_code == 200
    assert "Proveniência do ato" in corpo
    assert "Posições e valores de desempate" in corpo
    assert str(antigo.versao_id) in corpo


def test_o_marco_ja_divulgado_e_aviso_e_nao_impedimento(cenario):
    """O terceiro degrau da FR-005 — e a razão de ele existir de verdade.

    Suceder é o caminho normal da correção (FR-041): publicar sobre um marco já divulgado não
    impede nada. Mas é o que a autoridade precisa ler antes de confirmar, porque a divulgação de
    hoje passa a dizer que foi sucedida — e é isso que separa `aviso` de `informacao`.

    Sem este caso, `AVISO` seria um nível declarado e nunca alcançado, e a classificação em três
    degraus que a FR-005 pede teria, na prática, dois.
    """
    from processo_seletivo.divulgacao.domain.publicabilidade import AVISO, SUCEDERA
    from tests.fixtures.divulgacao import publicar_o_ato

    publicada = publicar_o_ato(cenario, chave="publicar-0751-aviso")

    aferida = aferir(
        edital=cenario["edital"],
        marco_id=cenario["marco"],
        ato=cenario["ato"],
        sucede=publicada,
    )

    assert aferida.nivel == AVISO
    assert aferida.codigo == SUCEDERA
    assert aferida.publicavel, "aviso não impede: ele informa"
    assert "sucede" in aferida.mensagem


def test_sem_publicacao_anterior_o_nivel_e_informacao(cenario):
    """E o comando, que só precisa saber se recusa, decide igual nos dois casos."""
    from processo_seletivo.divulgacao.domain.publicabilidade import AVISO

    aferida = aferir(edital=cenario["edital"], marco_id=cenario["marco"], ato=cenario["ato"])

    assert aferida.nivel == INFORMACAO
    assert aferida.nivel != AVISO
    assert aferida.publicavel


def test_os_tres_degraus_da_classificacao_sao_todos_alcancaveis(cenario, gestor):
    """A varredura que impede um nível declarado e nunca produzido (FR-005)."""
    from processo_seletivo.divulgacao.domain.publicabilidade import AVISO
    from tests.fixtures.divulgacao import publicar_o_ato

    alcancados = {
        aferir(edital=cenario["edital"], marco_id=cenario["marco"], ato=cenario["ato"]).nivel
    }
    publicada = publicar_o_ato(cenario, chave="publicar-0751-tres")
    alcancados.add(
        aferir(
            edital=cenario["edital"],
            marco_id=cenario["marco"],
            ato=cenario["ato"],
            sucede=publicada,
        ).nivel
    )
    antigo = cenario["ato"]
    emitir(cenario, gestor, chave="emitir-0751-tres", motivo="Resultado tardio.")
    alcancados.add(aferir(edital=cenario["edital"], marco_id=cenario["marco"], ato=antigo).nivel)

    assert alcancados == {INFORMACAO, AVISO, IMPEDIMENTO}
