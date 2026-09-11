"""A emissão do corte: o ato, os itens, as recusas e a sucessão de geração (014).

O cenário, a regra e os atalhos de emissão moram no `conftest.py` desta pasta, porque três arquivos
os exercitam.
"""

import pytest
from django.db import DatabaseError, connection, transaction

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.classificacao.application.calculo import calcular_ordem
from processo_seletivo.classificacao.application.corte import calcular_corte, geracao_vigente
from processo_seletivo.classificacao.application.emissao import assinatura_da_proposta, emitir_ordem
from processo_seletivo.classificacao.application.emissao_do_corte import (
    EMITIR,
    continuar_corte,
    emitir_corte,
)
from processo_seletivo.classificacao.models import Corte, ItemDoCorte
from processo_seletivo.comissoes.domain.funcoes import Funcao
from processo_seletivo.resultados.application.consolidacao import consolidar
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.comissao import alocar_em, constituir, inscrever
from tests.fixtures.corte import ENTREVISTA, MARCO, emitir, rascunho, regra
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.mesa import concluir_como, distribuir_para
from tests.fixtures.publicacao import publish_original

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

# --- T044 · todos os considerados constam, com posição e causa (FR-194) ----------------------


def test_a_emissao_enumera_todos_os_considerados_e_nao_so_quem_progrediu(cenario, gestor):
    edital, _, inscricoes = cenario

    desfecho = emitir(edital, gestor)

    corte = Corte.objects.get()
    assert desfecho["id"] == str(corte.id)
    assert corte.itens.count() == 4, "os quatro considerados, e não os dois que progrediram"
    progrediram = corte.itens.filter(consequencia=ItemDoCorte.Consequencia.PROGREDIU)
    assert progrediram.count() == 2
    assert {item.inscricao_id for item in progrediram} == {inscricoes[0].id, inscricoes[1].id}


def test_quem_fica_fora_tem_causa_legivel(cenario, gestor):
    edital, _, inscricoes = cenario

    emitir(edital, gestor)

    terceiro = ItemDoCorte.objects.get(inscricao=inscricoes[2])
    sem_posicao = ItemDoCorte.objects.get(inscricao=inscricoes[3])
    assert terceiro.consequencia == ItemDoCorte.Consequencia.FORA_DA_FAIXA
    assert "posição 3" in terceiro.motivo
    assert sem_posicao.posicao is None
    assert sem_posicao.motivo, "quem não tinha posição na ordem também é nomeado"


def test_o_ato_declara_o_universo_e_a_etapa_governada(cenario, gestor):
    edital, _, _ = cenario

    emitir(edital, gestor)

    corte = Corte.objects.get()
    assert corte.universo["orderingActId"] == str(corte.ato_id)
    assert corte.universo["cutRule"]["targetCount"] == 2
    assert corte.universo["target"] == {"count": 2, "source": "FIXED"}
    assert str(corte.etapa_governada_id) == ENTREVISTA
    assert (corte.primeira_posicao, corte.ultima_posicao) == (1, 2)


def test_a_emissao_gera_uma_auditoria(cenario, gestor):
    edital, _, _ = cenario

    emitir(edital, gestor)

    assert RegistroAuditoria.objects.filter(operation=EMITIR).count() == 1


# --- T045 · as recusas da emissão (FR-197, FR-198, SC-058) -----------------------------------


def test_emitir_sem_ordem_vigente_recusa(cenario, gestor):
    edital, _, _ = cenario
    outro_marco = "00000000-0000-4000-8000-000000000999"

    with pytest.raises(DomainError) as erro:
        calcular_corte(edital=edital, perfil_id=PROFILE_ID, marco_id=outro_marco)

    assert erro.value.code == "sem_ato_vigente"


def test_emitir_em_marco_sem_regra_de_corte_recusa(
    gestor, api_client, manager_headers, process_payload
):
    """Nenhum corte existe sem regra publicada, em 100% das tentativas (SC-058)."""
    draft, pontuada = rascunho(cut=False)
    draft["profiles"][0]["classificationMilestones"][0].pop("cutRule")
    edital = publish_original(api_client, manager_headers, process_payload, draft=draft)

    with pytest.raises(DomainError) as erro:
        calcular_corte(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)

    assert erro.value.code in {"sem_ato_vigente", "marco_sem_regra_de_corte"}


def test_a_confirmacao_divergente_recusa(cenario, gestor):
    edital, _, _ = cenario

    with pytest.raises(DomainError) as erro:
        emitir_corte(
            actor=gestor,
            processo_id=edital.processo_id,
            edital_id=edital.id,
            perfil_id=PROFILE_ID,
            marco_id=MARCO,
            idempotency_key="corte-014-divergente",
            correlation_id="teste-corte-014",
            confirmacao_do_calculo="sha256:outra-coisa",
        )

    assert erro.value.code == "calculo_divergente"


def test_a_confirmacao_vazia_recusa(cenario, gestor):
    edital, _, _ = cenario

    with pytest.raises(DomainError) as erro:
        emitir_corte(
            actor=gestor,
            processo_id=edital.processo_id,
            edital_id=edital.id,
            perfil_id=PROFILE_ID,
            marco_id=MARCO,
            idempotency_key="corte-014-vazia",
            correlation_id="teste-corte-014",
            confirmacao_do_calculo="",
        )

    assert erro.value.code == "confirmacao_do_corte_exigida"


# --- T047 · a sucessão é de geração (FR-200, FR-227) -----------------------------------------


def test_a_sucessao_sem_motivo_recusa(cenario, gestor):
    edital, _, _ = cenario
    emitir(edital, gestor)
    vigente = geracao_vigente(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)

    with pytest.raises(DomainError) as erro:
        emitir(edital, gestor, chave="corte-014-sucessao", geracao=vigente)

    assert erro.value.code == "sucessao_sem_motivo"


def test_a_sucessao_cria_geracao_nova_e_a_anterior_permanece_legivel(cenario, gestor):
    edital, _, _ = cenario
    emitir(edital, gestor)
    anterior = Corte.objects.get()
    vigente = geracao_vigente(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)

    emitir(
        edital,
        gestor,
        chave="corte-014-sucessao-ok",
        motivo="a comissão revisou o alvo",
        geracao=vigente,
    )

    sucessora = Corte.objects.exclude(pk=anterior.pk).get()
    assert sucessora.corte_anterior_id == anterior.id
    assert sucessora.raiz_id is None, "o sucessor é raiz da geração nova"
    assert Corte.objects.filter(pk=anterior.pk).exists(), "a sucedida continua legível"
    assert geracao_vigente(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO) == [sucessora]


# --- T048 · a idempotência devolve o desfecho anterior ---------------------------------------


def test_a_repeticao_com_a_mesma_chave_nao_produz_um_segundo_ato(cenario, gestor):
    edital, _, _ = cenario
    primeiro = emitir(edital, gestor)

    repetido = emitir(edital, gestor)

    assert repetido == primeiro
    assert Corte.objects.count() == 1


# --- T042a · o marco que declara não governar Etapa alguma (FR-224) --------------------------


def test_o_marco_terminal_emite_e_o_gate_nao_incide(
    gestor, api_client, manager_headers, process_payload
):
    """A Assumption da spec que declara esse corte legítimo não tinha teste nenhum.

    E ele **não** é o caso dos suplentes: no 77, no 57 e no 28 os suplentes são a parte excedente da
    mesma faixa, no mesmo marco que alimenta a análise documental.
    """
    draft, pontuada = rascunho(cut=regra(governedStage="NONE"))
    edital = publish_original(api_client, manager_headers, process_payload, draft=draft)
    membros = constituir(
        gestor,
        edital.processo,
        [("maria", Funcao.PRESIDENTE), ("joao", Funcao.MEMBRO)],
        prefixo="corte-014-terminal",
    )
    alocar_em(gestor, edital.processo, membros["joao"], edital, pontuada["id"])
    contexto = {
        "edital": edital,
        "processo": edital.processo,
        "membros": membros,
        "etapa": pontuada["id"],
    }
    inscricoes = inscrever(edital, 2, primeiro=701)
    distribuir_para(contexto, gestor, ["joao"], inscricoes, chave="corte-014-terminal-lote")
    for indice, pontuacao in enumerate(["90.0000", "80.0000"]):
        concluir_como(contexto, "joao", inscricoes[indice], pontuacao=pontuacao)
    consolidar(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        etapa_id=pontuada["id"],
        inscricao_ids=[item.id for item in inscricoes],
        idempotency_key="corte-014-terminal-consolidar",
        correlation_id="teste-corte-014",
    )
    emitir_ordem(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        idempotency_key="corte-014-terminal-ordem",
        correlation_id="teste-corte-014",
        confirmacao_do_calculo=assinatura_da_proposta(
            calcular_ordem(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)
        ),
    )

    emitir(edital, gestor, chave="corte-014-terminal-emitir")

    corte = Corte.objects.get()
    assert corte.etapa_governada_id is None
    assert corte.itens.count() == 2


# --- FR-204 · a continuação onde a regra não a admite ----------------------------------------


def test_continuar_onde_o_edital_nao_publicou_continuacao_recusa(cenario, gestor):
    edital, _, _ = cenario
    emitir(edital, gestor)

    with pytest.raises(DomainError) as erro:
        continuar_corte(
            actor=gestor,
            processo_id=edital.processo_id,
            edital_id=edital.id,
            perfil_id=PROFILE_ID,
            marco_id=MARCO,
            idempotency_key="corte-014-continuar",
            correlation_id="teste-corte-014",
            quantidade=1,
            motivo="indeferimento de uma inscrição",
        )

    assert erro.value.code == "continuacao_nao_publicada"


def test_continuar_sem_motivo_recusa(cenario, gestor):
    edital, _, _ = cenario
    emitir(edital, gestor)

    with pytest.raises(DomainError) as erro:
        continuar_corte(
            actor=gestor,
            processo_id=edital.processo_id,
            edital_id=edital.id,
            perfil_id=PROFILE_ID,
            marco_id=MARCO,
            idempotency_key="corte-014-continuar-sem-motivo",
            correlation_id="teste-corte-014",
            quantidade=1,
            motivo="  ",
        )

    assert erro.value.code == "continuacao_sem_motivo"


# --- T043 · a trigger recusa o caminho que o ORM não fiscaliza (FR-223) ----------------------


@pytest.mark.skipif(
    connection.vendor != "postgresql",
    reason="As triggers são de PostgreSQL; em sqlite a garantia não existe.",
)
def test_a_trigger_recusa_o_update_direto_no_corte(cenario, gestor):
    """O caminho pelo qual o histórico seria reescrito sem que ninguém pedisse."""
    edital, _, _ = cenario
    emitir(edital, gestor)

    with pytest.raises(DatabaseError, match="immutable"), transaction.atomic():
        Corte.objects.filter(edital=edital).update(motivo="reescrita indevida")


@pytest.mark.skipif(
    connection.vendor != "postgresql",
    reason="As triggers são de PostgreSQL; em sqlite a garantia não existe.",
)
def test_a_trigger_recusa_o_delete_direto_no_item(cenario, gestor):
    edital, _, _ = cenario
    emitir(edital, gestor)

    with pytest.raises(DatabaseError, match="immutable"), transaction.atomic():
        ItemDoCorte.objects.filter(corte__edital=edital).delete()
