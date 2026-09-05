"""A leitura monta o universo uma vez e entrega dados puros ao motor (015, T082)."""

import pytest

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.classificacao.application.calculo import calcular_ordem
from processo_seletivo.classificacao.application.emissao import EMITIR, emitir_ordem
from processo_seletivo.classificacao.models import AtoDeOrdenacao, PosicaoNaOrdem
from processo_seletivo.comissoes.domain.funcoes import Funcao
from processo_seletivo.resultados.application.consolidacao import consolidar
from tests.fixtures.comissao import alocar_em, constituir, inscrever, rascunho_com_etapas
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.mesa import concluir_como, distribuir_para
from tests.fixtures.publicacao import publish_original

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

MARCO = "00000000-0000-4000-8000-000000000451"


@pytest.fixture
def cenario(gestor, api_client, manager_headers, process_payload):
    rascunho = rascunho_com_etapas(avaliacoes=1, maxima="100.0000", minima="60.0000")
    etapa = rascunho["stages"][1]
    etapa["weight"] = "1.0000"
    rascunho["profiles"][0]["classificationMilestones"] = [
        {
            "id": MARCO,
            "code": "FINAL",
            "name": "Classificação final",
            "stages": [etapa["id"]],
            "operation": "SOMA_PONDERADA",
            "normalization": "NENHUMA",
            "rounding": {"scale": 2, "mode": "MEIO_PARA_CIMA"},
            "tiebreakers": [],
        }
    ]
    edital = publish_original(
        api_client,
        manager_headers,
        process_payload,
        draft=rascunho,
    )
    membros = constituir(
        gestor,
        edital.processo,
        [("maria", Funcao.PRESIDENTE), ("joao", Funcao.MEMBRO)],
        prefixo="calculo-015",
    )
    alocar_em(gestor, edital.processo, membros["joao"], edital, etapa["id"])
    contexto = {
        "edital": edital,
        "processo": edital.processo,
        "membros": membros,
        "etapa": etapa["id"],
    }
    inscricoes = inscrever(edital, 3, primeiro=501)
    distribuir_para(contexto, gestor, ["joao"], inscricoes[:2], chave="calculo-015-lote")
    concluir_como(contexto, "joao", inscricoes[0], pontuacao="70.0000")
    concluir_como(contexto, "joao", inscricoes[1], pontuacao="90.0000")
    consolidar(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        etapa_id=etapa["id"],
        inscricao_ids=[item.id for item in inscricoes[:2]],
        idempotency_key="calculo-015-consolidar",
        correlation_id="teste-calculo-015",
    )
    return edital, etapa, inscricoes


def test_calcula_a_ordem_e_nomeia_quem_nao_tem_pontuacao(cenario):
    edital, etapa, inscricoes = cenario

    proposta = calcular_ordem(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)

    assert [item["inscricao_id"] for item in proposta["posicoes"]] == [
        str(inscricoes[1].id),
        str(inscricoes[0].id),
    ]
    assert [item["pontuacao"] for item in proposta["posicoes"]] == [90, 70]
    assert proposta["sem_posicao"][0]["inscricao_id"] == str(inscricoes[2].id)
    assert etapa["name"] in proposta["sem_posicao"][0]["motivo"]
    assert len(proposta["universo"]["participants"]) == 3
    assert len(proposta["universo"]["stageResults"]) == 2


def test_emite_um_ato_com_tres_posicoes_e_uma_unica_auditoria(cenario, gestor):
    edital, _, _ = cenario

    desfecho = emitir_ordem(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        idempotency_key="emitir-ordem-015",
        correlation_id="teste-emissao-015",
    )

    ato = AtoDeOrdenacao.objects.get()
    assert desfecho["ids"] == [str(ato.id)]
    assert PosicaoNaOrdem.objects.filter(ato=ato).count() == 3
    assert (
        RegistroAuditoria.objects.filter(
            operation=EMITIR,
            aggregate_type="AtoDeOrdenacao",
            aggregate_id=ato.id,
        ).count()
        == 1
    )

    repetido = emitir_ordem(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        idempotency_key="emitir-ordem-015",
        correlation_id="outra-correlacao",
    )

    assert repetido == desfecho
    assert AtoDeOrdenacao.objects.count() == 1
    assert PosicaoNaOrdem.objects.count() == 3
    assert RegistroAuditoria.objects.filter(operation=EMITIR).count() == 1
