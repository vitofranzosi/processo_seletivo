"""A Retificação confere só a referência que ela introduz (116, US4, FR-3633, FR-3635, SC-1100).

**A Retificação é a saída do Edital com defeito** (6ª decisão do usuário): bloqueá-la por um
problema que ela não causou tiraria a saída. Por isso a que só muda o cronograma de um Edital cujo
concurso já foi realizado é publicada sem consulta nenhuma, e a que troca o concurso para um
realizado é recusada.
"""

import copy
from datetime import timedelta

import pytest
from django.utils import timezone

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from processo_seletivo.sorteios.application.ocorrencia import observar_ocorrencia
from processo_seletivo.sorteios.application.relacao import publicar_relacao
from processo_seletivo.sorteios.application.sorteio import constituir_sorteio
from processo_seletivo.sorteios.domain import conferencia as dominio
from processo_seletivo.sorteios.infrastructure.fontes import Observacao
from tests.fixtures.edital import DRAW_METHOD, complete_draft
from tests.fixtures.publicacao import (
    create_retification,
    publish_original,
    publish_retification,
    try_publish_retification,
)
from tests.fixtures.sorteio import METODO, certame_de_sorteio, presidente

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

LF = "Loteria Federal"


def _futuro(dias=40):
    return (timezone.now() + timedelta(days=dias)).isoformat()


def _rascunho(ocorrencia, fonte=LF):
    rascunho = complete_draft()
    metodo = copy.deepcopy(DRAW_METHOD)
    metodo.update({"source": fonte, "occurrence": ocorrencia, "occurrenceAt": _futuro()})
    rascunho["profiles"][0]["classificationMilestones"][0]["drawMethod"] = metodo
    return rascunho


def _versao(edital):
    return VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")


def _caminho_do_metodo(edital, campo):
    perfil = _versao(edital).content["profiles"][0]
    marco = perfil["classificationMilestones"][0]
    return (
        f"/profiles/id={perfil['id']}/classificationMilestones/id={marco['id']}/drawMethod/{campo}"
    )


def _trocar(edital, campo, valor):
    return [
        {
            "targetPath": _caminho_do_metodo(edital, campo),
            "operation": "REPLACE",
            "newValue": valor,
        }
    ]


def _publicado(api_client, manager_headers, process_payload, ocorrencia, fonte=LF):
    return publish_original(
        api_client, manager_headers, process_payload, draft=_rascunho(ocorrencia, fonte)
    )


def test_troca_para_realizado_e_recusada(api_client, manager_headers, process_payload, caixa):
    edital = _publicado(api_client, manager_headers, process_payload, "6116")
    caixa.usar_gravacao().zerar()
    retificacao = create_retification(api_client, edital, _trocar(edital, "occurrence", "6113"))

    resposta = try_publish_retification(api_client, retificacao)

    assert resposta.status_code == 422, resposta.content
    corpo = resposta.content.decode("utf-8")
    assert "O concurso 6113 da Loteria Federal já foi realizado, em 28/10/2026" in corpo
    assert caixa.chamadas_ao_ultimo == 1


def test_so_o_cronograma_muda_e_nada_e_consultado(
    api_client, manager_headers, process_payload, caixa, monkeypatch
):
    """Cenário E: o 5000 consolidado, e a Retificação que só prorroga não é bloqueada por ele."""
    from processo_seletivo.sorteios.infrastructure.fontes.loteria_federal import LoteriaFederal

    # O acervo: publicado quando a Caixa ainda não acusava o 5000 — aqui, sem conferência.
    with monkeypatch.context() as antes_da_116:
        antes_da_116.setattr(LoteriaFederal, "SABE_CONFERIR", False)
        edital = _publicado(api_client, manager_headers, process_payload, "5000")
    caixa.usar_gravacao().zerar()
    evento = _versao(edital).content["schedule"][0]
    retificacao = create_retification(
        api_client,
        edital,
        [
            {
                "targetPath": f"/schedule/id={evento['id']}/description",
                "operation": "REPLACE",
                "newValue": "Inscrições, prorrogadas",
            }
        ],
    )

    publish_retification(api_client, retificacao)

    assert caixa.chamadas == 0
    registro = RegistroAuditoria.objects.get(
        aggregate_type="Retificacao", aggregate_id=retificacao.pk, operation="PUBLICAR"
    )
    assert registro.detalhe is None


def test_troca_de_fonte_para_a_loteria_e_conferida(
    api_client, manager_headers, process_payload, caixa
):
    # O 6113 é "ainda não realizado" na tabela da demonstração (último 5000), e realizado na Caixa.
    edital = _publicado(
        api_client, manager_headers, process_payload, "6113", "Fonte de demonstração"
    )
    caixa.usar_gravacao()
    retificacao = create_retification(api_client, edital, _trocar(edital, "source", LF))

    resposta = try_publish_retification(api_client, retificacao)

    assert resposta.status_code == 422, resposta.content
    assert "O concurso 6113 da Loteria Federal já foi realizado" in resposta.content.decode()


def test_troca_para_forma_invalida_e_impeditiva(
    api_client, manager_headers, process_payload, caixa
):
    edital = _publicado(api_client, manager_headers, process_payload, "6116")
    caixa.zerar()
    retificacao = create_retification(api_client, edital, _trocar(edital, "occurrence", "6106-9"))

    resposta = try_publish_retification(api_client, retificacao)

    assert resposta.status_code == 422, resposta.content
    assert "informe só o número do concurso" in resposta.content.decode()
    assert caixa.chamadas == 0


def test_inconclusivo_adverte_e_publica_com_o_registro(
    api_client, manager_headers, process_payload, caixa
):
    edital = _publicado(api_client, manager_headers, process_payload, "6116")
    caixa.fora_do_ar()
    retificacao = create_retification(api_client, edital, _trocar(edital, "occurrence", "6120"))

    publish_retification(api_client, retificacao)

    (registro,) = RegistroAuditoria.objects.get(
        aggregate_type="Retificacao", aggregate_id=retificacao.pk, operation="PUBLICAR"
    ).detalhe["conferenciaDaReferencia"]
    assert (registro["referencia"], registro["situacao"]) == ("6120", dominio.INCONCLUSIVO)
    assert registro["decisao"] == "PROSSEGUIU_COM_ADVERTENCIA"


def test_acervo_nao_e_reconferido(api_client, manager_headers, process_payload, caixa, monkeypatch):
    """`Concurso 6100` publicado antes da `116`: a Retificação de outra coisa não o reconfere."""
    from processo_seletivo.sorteios.infrastructure import fontes

    with monkeypatch.context() as antes_da_116:
        antes_da_116.setattr(fontes, "forma_da_referencia", lambda nome: None)
        edital = _publicado(api_client, manager_headers, process_payload, "Concurso 6100")
    caixa.zerar()
    retificacao = create_retification(
        api_client, edital, _trocar(edital, "occurrenceAt", _futuro(41))
    )

    publish_retification(api_client, retificacao)

    assert caixa.chamadas == 0


class _Extracao:
    def observar(self, *, fonte, referencia):
        return Observacao(
            material_bruto="012345 678901 234567 890123 456789",
            ocorrida_nao_antes_de=timezone.now(),
        )


def test_o_marco_ja_sorteado_fica_fora(gestor, api_client, manager_headers, process_payload, caixa):
    metodo = copy.deepcopy(METODO)
    metodo.update({"source": LF, "occurrence": "6116", "occurrenceAt": _futuro(3)})
    certame = certame_de_sorteio(
        gestor, api_client, manager_headers, process_payload, metodo=metodo
    )
    relacao = publicar_relacao(
        actor=presidente(),
        processo_id=certame["processo"].id,
        edital_id=certame["edital"].id,
        perfil_id=certame["perfil"],
        marco_id=certame["marco"],
        idempotency_key="116-relacao",
        correlation_id="teste-116",
    )["relacao"]
    ocorrencia = observar_ocorrencia(
        actor=presidente(),
        processo_id=certame["processo"].id,
        fonte=LF,
        referencia="6116",
        idempotency_key="116-obs",
        correlation_id="teste-116",
        fonte_externa=_Extracao(),
    )["ocorrencia"]
    constituir_sorteio(
        actor=presidente(),
        processo_id=certame["processo"].id,
        edital_id=certame["edital"].id,
        relacao_id=relacao,
        ocorrencia_id=ocorrencia,
        idempotency_key="116-sorteio",
        correlation_id="teste-116",
    )
    caixa.usar_gravacao()
    chamadas = caixa.chamadas
    edital = certame["edital"]
    retificacao = create_retification(api_client, edital, _trocar(edital, "occurrence", "6113"))

    publish_retification(api_client, retificacao)

    assert caixa.chamadas == chamadas, "o 6113 está realizado na gravação e não foi consultado"
