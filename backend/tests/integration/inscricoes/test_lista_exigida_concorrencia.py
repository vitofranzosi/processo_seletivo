"""O envio e uma Retificação que muda o recorte, ao mesmo tempo (044, FR-714).

Os dois desfechos são legítimos, e a combinação proibida é uma só: a inscrição apontando uma
versão e a lista gravada de outra. Ou o envio chega primeiro e grava sob a versão que leu — e a
Retificação espera o `FOR SHARE` —, ou a Retificação vence e o envio recusa com `edital_updated`,
sem gravar lista nenhuma. O gatilho de coerência é a segunda barreira, e este teste não o
atravessa: ele prova a primeira.
"""

import threading

import pytest
from django.db import connection, connections

from processo_seletivo.inscricoes.application.submissao import enviar_inscricao
from processo_seletivo.inscricoes.models import Inscricao, ItemDaListaExigida
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.candidato import MARIA, MODALIDADE_AC, PERFIL_DOCENTE, pdf
from tests.fixtures.publicacao import retify
from tests.fixtures.selecao import DOCUMENTO_DE_TODOS, DOCUMENTO_DO_PERFIL

pytestmark = [
    pytest.mark.integration,
    pytest.mark.django_db(transaction=True),
    pytest.mark.skipif(connection.vendor != "postgresql", reason="corrida só em PostgreSQL"),
]

DECLARACOES = {"veracidade": True, "ciencia": True}


def _pronta(edital):
    from processo_seletivo.inscricoes.application.rascunho import (
        abrir_inscricao,
        anexar_documento,
        gravar_dados,
    )

    inscricao = abrir_inscricao(identidade=MARIA, edital_id=edital.id, profile_id=PERFIL_DOCENTE)
    inscricao = gravar_dados(
        identidade=MARIA,
        inscricao=inscricao,
        dados={
            "nome": MARIA.nome,
            "cpf": MARIA.cpf,
            "email": MARIA.email,
            "modality_id": MODALIDADE_AC,
        },
    )
    for requisito in (DOCUMENTO_DE_TODOS, DOCUMENTO_DO_PERFIL):
        anexar_documento(
            identidade=MARIA, inscricao=inscricao, requirement_id=requisito, arquivo=pdf()
        )
    inscricao.refresh_from_db()
    return inscricao


def test_a_lista_e_da_versao_que_o_envio_registrou(api_client, selecao, candidatos_registrados):
    inscricao = _pronta(selecao)
    antes = VersaoConsolidada.objects.filter(edital=selecao).latest("materialized_at")
    barreira = threading.Barrier(2, timeout=10)
    desfechos = {}

    def enviar():
        try:
            barreira.wait()
            enviar_inscricao(
                identidade=MARIA,
                inscricao=inscricao,
                declaracoes=DECLARACOES,
                idempotency_key="corrida-da-lista",
            )
            desfechos["envio"] = "enviada"
        except DomainError as exc:
            desfechos["envio"] = exc.code
        finally:
            connections.close_all()

    def retificar():
        try:
            barreira.wait()
            retify(
                api_client,
                selecao,
                [
                    {
                        "targetPath": f"/documentRequirements/id={DOCUMENTO_DO_PERFIL}/required",
                        "operation": "REPLACE",
                        "newValue": False,
                    }
                ],
                suffix="corrida-lista",
            )
            desfechos["retificacao"] = "publicada"
        finally:
            connections.close_all()

    fios = [threading.Thread(target=enviar), threading.Thread(target=retificar)]
    for fio in fios:
        fio.start()
    for fio in fios:
        fio.join(timeout=30)

    itens = list(ItemDaListaExigida.objects.filter(inscricao=inscricao))
    if desfechos["envio"] == "enviada":
        enviada = Inscricao.objects.get(pk=inscricao.pk)
        assert enviada.versao_aceita_id == antes.pk, desfechos
        assert {item.versao_id for item in itens} == {antes.pk}, desfechos
        diploma = next(item for item in itens if str(item.requisito_id) == DOCUMENTO_DO_PERFIL)
        assert diploma.situacao == "OBRIGATORIO", "pedido sob a versão que o envio leu"
    else:
        assert desfechos["envio"] == "edital_updated", desfechos
        assert itens == [], "envio recusado não grava lista"
