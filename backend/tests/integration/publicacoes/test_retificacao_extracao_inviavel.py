"""Na Retificação a extração inviável só adverte, e se cala sobre o marco já sorteado (102).

**FR-2656.**

**Por que advertência, e não recusa** (D-003, D-005). A Retificação é a saída do Edital que já está
condenado: recusar a que corrige uma vírgula tiraria dele também a saída. E o caminho pelo qual um
Edital publicado chega ao estado condenado é justamente uma Retificação — a que prorroga as
inscrições até o dia da extração —, e quem a confirma precisa ver o aviso **na confirmação**, que é
o que `advertencias_do_ato` mostra, e não só na lista bruta de achados (R-004).
"""

import copy
from datetime import datetime, time, timedelta

import pytest
from django.utils import timezone

from processo_seletivo.publicacoes.application.retificacoes import advertencias_do_ato
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from processo_seletivo.shared.tempo import ZONA
from processo_seletivo.sorteios.application.ocorrencia import observar_ocorrencia
from processo_seletivo.sorteios.application.relacao import publicar_relacao
from processo_seletivo.sorteios.application.selectors import (
    marcos_sorteados_em_todos_os_recortes,
)
from processo_seletivo.sorteios.application.sorteio import constituir_sorteio
from processo_seletivo.sorteios.infrastructure.fontes import Observacao
from tests.fixtures.edital import DRAW_METHOD, complete_draft
from tests.fixtures.publicacao import (
    create_retification,
    encerrar_inscricoes,
    publish_original,
    publish_retification,
)
from tests.fixtures.sorteio import METODO, certame_de_sorteio, presidente

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

CODIGO = "draw_occurrence_not_after_registration_on_retification"


class _Caixa:
    """A Loteria Federal sem rede: a extração publicada, com o limite inferior de agora."""

    def observar(self, *, fonte, referencia):
        return Observacao(
            material_bruto="012345 678901 234567 890123 456789",
            ocorrida_nao_antes_de=timezone.now(),
        )


def _codigos(retificacao):
    return {item.code for item in advertencias_do_ato(retificacao)}


def _caminho_do_marco(conteudo, campo):
    perfil = conteudo["profiles"][0]
    marco = perfil["classificationMilestones"][0]
    return f"/profiles/id={perfil['id']}/classificationMilestones/id={marco['id']}/{campo}"


def _versao(edital):
    return VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")


# --- a prorrogação que condena o sorteio ----------------------------------------------------


def test_prorrogar_as_inscricoes_ate_o_dia_da_extracao_adverte_e_publica(
    api_client, manager_headers, process_payload
):
    dia = timezone.localdate(timezone.now(), ZONA) + timedelta(days=30)
    fim = datetime.combine(dia, time(9, 0), tzinfo=ZONA)
    rascunho = complete_draft()
    rascunho["schedule"][0].update(
        {
            "startAt": (fim - timedelta(days=20)).isoformat(),
            "endAt": fim.isoformat(),
            "isRegistrationPeriod": True,
        }
    )
    metodo = copy.deepcopy(DRAW_METHOD)
    metodo.update(
        {
            "source": "Loteria Federal",
            "occurrence": "6113",
            "occurrenceAt": datetime.combine(
                dia + timedelta(days=1), time(20, 5), tzinfo=ZONA
            ).isoformat(),
        }
    )
    rascunho["profiles"][0]["classificationMilestones"][0]["drawMethod"] = metodo
    edital = publish_original(api_client, manager_headers, process_payload, draft=rascunho)
    evento = _versao(edital).content["schedule"][0]

    retificacao = create_retification(
        api_client,
        edital,
        [
            {
                "targetPath": f"/schedule/id={evento['id']}/endAt",
                "operation": "REPLACE",
                "newValue": (fim + timedelta(days=1)).isoformat(),
            }
        ],
    )

    assert CODIGO in _codigos(retificacao), "a advertência chega à confirmação"
    publish_retification(api_client, retificacao)


# --- o marco já sorteado --------------------------------------------------------------------


def _certame_com_a_caixa(gestor, api_client, manager_headers, process_payload):
    """Inscrições encerradas há um minuto, e a extração declarada para daqui a três dias."""
    metodo = copy.deepcopy(METODO)
    metodo.update(
        {
            "source": "Loteria Federal",
            "occurrence": "6113",
            "occurrenceAt": (timezone.now() + timedelta(days=3)).astimezone(ZONA).isoformat(),
        }
    )
    certame = certame_de_sorteio(
        gestor, api_client, manager_headers, process_payload, metodo=metodo, periodo_aberto=True
    )
    encerrar_inscricoes(api_client, certame["edital"], timezone.now() - timedelta(minutes=1))
    return certame


def _sortear(certame):
    relacao = publicar_relacao(
        actor=presidente(),
        processo_id=certame["processo"].id,
        edital_id=certame["edital"].id,
        perfil_id=certame["perfil"],
        marco_id=certame["marco"],
        idempotency_key="inviavel-relacao",
        correlation_id="teste-102",
    )["relacao"]
    ocorrencia = observar_ocorrencia(
        actor=presidente(),
        processo_id=certame["processo"].id,
        fonte="Loteria Federal",
        referencia="6113",
        idempotency_key="inviavel-obs",
        correlation_id="teste-102",
        fonte_externa=_Caixa(),
    )["ocorrencia"]
    constituir_sorteio(
        actor=presidente(),
        processo_id=certame["processo"].id,
        edital_id=certame["edital"].id,
        relacao_id=relacao,
        ocorrencia_id=ocorrencia,
        idempotency_key="inviavel-sorteio",
        correlation_id="teste-102",
    )


def _retificar_a_extracao_para_hoje(api_client, edital):
    conteudo = _versao(edital).content
    hoje = datetime.combine(timezone.localdate(timezone.now(), ZONA), time(20, 5), tzinfo=ZONA)
    return create_retification(
        api_client,
        edital,
        [
            {
                "targetPath": _caminho_do_marco(conteudo, "drawMethod/occurrenceAt"),
                "operation": "REPLACE",
                "newValue": hoje.isoformat(),
            }
        ],
        suffix="hoje",
    )


def test_sem_sorteio_a_extracao_retificada_para_hoje_adverte(
    gestor, api_client, manager_headers, process_payload
):
    certame = _certame_com_a_caixa(gestor, api_client, manager_headers, process_payload)

    retificacao = _retificar_a_extracao_para_hoje(api_client, certame["edital"])

    assert CODIGO in _codigos(retificacao)


def test_o_marco_ja_sorteado_nao_e_advertido(gestor, api_client, manager_headers, process_payload):
    certame = _certame_com_a_caixa(gestor, api_client, manager_headers, process_payload)
    _sortear(certame)

    assert marcos_sorteados_em_todos_os_recortes(
        certame["edital"], _versao(certame["edital"]).content
    ) == frozenset({str(certame["marco"])})
    retificacao = _retificar_a_extracao_para_hoje(api_client, certame["edital"])

    assert CODIGO not in _codigos(retificacao)


def test_antes_do_sorteio_nenhum_marco_esta_sorteado(
    gestor, api_client, manager_headers, process_payload
):
    certame = _certame_com_a_caixa(gestor, api_client, manager_headers, process_payload)

    assert (
        marcos_sorteados_em_todos_os_recortes(certame["edital"], _versao(certame["edital"]).content)
        == frozenset()
    )
