"""A Caixa fora do ar não paralisa o certame (116, US3, FR-3641, SC-1096, SC-1097).

**As oito falhas da POC, nos quatro atos.** O adaptador real roda sobre `urlopen` substituído
(`caixa.pela_rede`): é o parse dele e a classificação dos motivos que se testam, e nada sai da
máquina. Em cada caso o ato conclui, a advertência diz um dos quatro motivos do contrato, o registro
diz `conclusiva: false`, e nada da resposta crua chega a lugar nenhum.
"""

import copy
import re
from datetime import datetime, time, timedelta
from urllib import error

import pytest
from django.utils import timezone

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.processos.models import Edital
from processo_seletivo.shared.tempo import ZONA
from processo_seletivo.sorteios.application.relacao import PUBLICAR, publicar_relacao
from processo_seletivo.sorteios.domain import conferencia as dominio
from tests.fixtures.caixa_gravada import Servidor, gravada
from tests.fixtures.edital import DRAW_METHOD, actor_headers, complete_draft
from tests.fixtures.publicacao import (
    SIGNATORY,
    create_retification,
    publish_original,
    publish_retification,
)
from tests.fixtures.sorteio import METODO, certame_de_sorteio, presidente

pytestmark = [pytest.mark.integration]

LF = "Loteria Federal"


def _ultimo_com(**campos):
    resposta = copy.deepcopy(gravada("ultimo"))
    resposta["corpo"].update(campos)
    return resposta


# O que a Caixa pode fazer, e o motivo que quem opera lê. **Nenhum deles é "ainda não realizado".**
FALHAS = {
    "tempo esgotado": (TimeoutError("timed out"), dominio.SEM_RESPOSTA_A_TEMPO),
    "rede fora": (error.URLError("Name or service not known"), dominio.SEM_CONEXAO),
    "500": ({"status": 500, "corpo": {"message": "An error has occurred."}}, dominio.COM_ERRO),
    "503": ({"status": 503, "corpo": b"Service Unavailable"}, dominio.COM_ERRO),
    "html": ({"status": 200, "corpo": b"<html><body>Acesso negado</body></html>"}, None),
    "sem bilhetes": (_ultimo_com(listaDezenas=[]), None),
    "data noutro formato": (_ultimo_com(dataApuracao="2026-11-01"), None),
    "numero como texto": (_ultimo_com(numero="6114"), None),
}
# Pedaços da resposta crua que não podem aparecer em mensagem nem registro (FR-3641, FR-3648).
CRUS = ("html", "Service Unavailable", "An error has occurred", "URLError", "TimeoutError")
# O código HTTP cru se procura como número inteiro, e não como substring: o registro leva o
# `consultadaEm` com microssegundos, e "…00.255037…" contém "503". Como substring, o teste caía
# uma vez a cada tantas execuções — no CI da #372 e na integração de 04/11 —, sempre no horário e
# nunca num vazamento. Nenhum grupo de dígitos do isoformat tem três algarismos, de modo que a
# fronteira de palavra não perde o código solto ("HTTP 503", "503 Service Unavailable").
CODIGOS_CRUS = ("503",)


def _tem_codigo_cru(texto, codigo):
    return re.search(rf"\b{codigo}\b", texto) is not None


def _motivo(nome):
    return FALHAS[nome][1] or dominio.SEM_O_ULTIMO


def _cair(caixa, nome):
    caixa.pela_rede(Servidor(federal=FALHAS[nome][0]))


def _sem_resposta_crua(*textos):
    for texto in textos:
        for cru in CRUS:
            assert cru not in texto, (cru, texto)
        for codigo in CODIGOS_CRUS:
            assert not _tem_codigo_cru(texto, codigo), (codigo, texto)


@pytest.mark.parametrize(
    "texto, vazou",
    [
        ("'consultadaEm': '2026-11-04T14:55:00.255037-03:00'", False),
        ("'consultadaEm': '2026-11-04T10:20:54.250324-03:00'", False),
        ("'consultadaEm': '2026-11-04T10:20:54.503000-03:00'", False),
        ("a Caixa respondeu HTTP 503", True),
        ("503 Service Unavailable", True),
        ("{'status': 503}", True),
    ],
)
def test_o_codigo_cru_nao_se_confunde_com_o_horario_da_consulta(texto, vazou):
    assert _tem_codigo_cru(texto, "503") is vazou


def _metodo(ocorrencia="6116", ocorre_em=None):
    metodo = copy.deepcopy(DRAW_METHOD)
    metodo.update(
        {
            "source": LF,
            "occurrence": ocorrencia,
            "occurrenceAt": ocorre_em or (timezone.now() + timedelta(days=40)).isoformat(),
        }
    )
    return metodo


def _rascunho(ocorrencia="6116"):
    rascunho = complete_draft()
    rascunho["profiles"][0]["classificationMilestones"][0]["drawMethod"] = _metodo(ocorrencia)
    return rascunho


def _registro(aggregate, operacao):
    (registro,) = RegistroAuditoria.objects.get(
        aggregate_id=aggregate.pk, operation=operacao
    ).detalhe["conferenciaDaReferencia"]
    return registro


def _em_elaboracao(api_client, manager_headers, process_payload, rascunho):
    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    assert criado.status_code == 201, criado.content
    edital = Edital.objects.get(processo_id=criado.json()["id"])
    preparador = actor_headers("preparador", ["edital:elaborar", "edital:submeter"])
    gravado = api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        rascunho,
        format="json",
        **{**preparador, "HTTP_IF_MATCH": f'"{edital.revision}"'},
    )
    assert gravado.status_code < 400, gravado.content
    edital.refresh_from_db()
    return edital


def _submeter(api_client, edital):
    edital.refresh_from_db()
    return api_client.post(
        f"/api/v1/admin/editais/{edital.id}/submissoes",
        format="json",
        **{
            **actor_headers("preparador", ["edital:elaborar", "edital:submeter"]),
            "HTTP_IF_MATCH": f'"{edital.revision}"',
        },
    )


@pytest.mark.django_db
@pytest.mark.parametrize("falha", FALHAS)
def test_a_submissao_conclui_com_a_advertencia(
    api_client, manager_headers, process_payload, caixa, falha
):
    edital = _em_elaboracao(api_client, manager_headers, process_payload, _rascunho())
    _cair(caixa, falha)

    resposta = _submeter(api_client, edital)

    assert resposta.status_code == 200, resposta.content
    (advertencia,) = [
        achado
        for achado in resposta.json()["validationFindings"]
        if achado["code"] == "draw_occurrence_not_checked"
    ]
    assert advertencia["severity"] == "WARNING"
    assert _motivo(falha) in advertencia["message"]
    registro = _registro(edital, "SUBMETER")
    assert (registro["conclusiva"], registro["motivo"]) == (False, _motivo(falha))
    _sem_resposta_crua(advertencia["message"], repr(registro))


@pytest.mark.django_db
@pytest.mark.parametrize("falha", FALHAS)
def test_a_publicacao_conclui_com_a_advertencia(
    api_client, manager_headers, process_payload, caixa, falha
):
    edital = _em_elaboracao(api_client, manager_headers, process_payload, _rascunho())
    assert _submeter(api_client, edital).status_code == 200
    edital.refresh_from_db()
    api_client.post(
        f"/api/v1/admin/editais/{edital.id}/homologacoes",
        {"reason": "OK"},
        format="json",
        **{
            **actor_headers("homologador", ["edital:homologar"]),
            "HTTP_IF_MATCH": f'"{edital.revision}"',
        },
    )
    edital.refresh_from_db()
    _cair(caixa, falha)

    resposta = api_client.post(
        f"/api/v1/admin/editais/{edital.id}/publicacoes",
        {"signatory": SIGNATORY},
        format="json",
        **{
            **actor_headers("publicador", ["edital:publicar"]),
            "HTTP_IF_MATCH": f'"{edital.revision}"',
        },
    )

    assert resposta.status_code == 201, resposta.content
    registro = _registro(edital, "PUBLICAR")
    assert (registro["conclusiva"], registro["decisao"]) == (False, "PROSSEGUIU_COM_ADVERTENCIA")
    assert registro["motivo"] == _motivo(falha)
    _sem_resposta_crua(repr(registro))


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("falha", FALHAS)
def test_a_retificacao_conclui_com_a_advertencia(
    api_client, manager_headers, process_payload, caixa, falha
):
    edital = publish_original(api_client, manager_headers, process_payload, draft=_rascunho())
    from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada

    perfil = (
        VersaoConsolidada.objects.filter(edital=edital)
        .latest("materialized_at")
        .content["profiles"][0]
    )
    marco = perfil["classificationMilestones"][0]
    retificacao = create_retification(
        api_client,
        edital,
        [
            {
                "targetPath": (
                    f"/profiles/id={perfil['id']}/classificationMilestones/id={marco['id']}"
                    "/drawMethod/occurrence"
                ),
                "operation": "REPLACE",
                "newValue": "6120",
            }
        ],
    )
    _cair(caixa, falha)

    publish_retification(api_client, retificacao)

    registro = _registro(retificacao, "PUBLICAR")
    assert (registro["referencia"], registro["conclusiva"]) == ("6120", False)
    assert registro["motivo"] == _motivo(falha)
    _sem_resposta_crua(repr(registro))


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("falha", FALHAS)
def test_o_congelamento_conclui_com_a_advertencia(
    gestor, api_client, manager_headers, process_payload, caixa, falha
):
    metodo = copy.deepcopy(METODO)
    metodo.update(_metodo())
    certame = certame_de_sorteio(
        gestor, api_client, manager_headers, process_payload, metodo=metodo
    )
    _cair(caixa, falha)

    declarado = publicar_relacao(
        actor=presidente(),
        processo_id=certame["processo"].id,
        edital_id=certame["edital"].id,
        perfil_id=certame["perfil"],
        marco_id=certame["marco"],
        idempotency_key="caixa-fora-do-ar",
        correlation_id="teste-116",
    )

    (advertencia,) = declarado["advertencias"]
    assert _motivo(falha) in advertencia
    assert "A relação foi publicada." in advertencia
    (registro,) = RegistroAuditoria.objects.get(
        operation=PUBLICAR, aggregate_id=declarado["relacao"]
    ).detalhe["conferenciaDaReferencia"]
    assert registro["conclusiva"] is False
    _sem_resposta_crua(advertencia, repr(registro))


@pytest.mark.django_db
def test_a_102_continua_impedindo_com_a_caixa_fora_do_ar(
    api_client, manager_headers, process_payload, caixa
):
    """As regras locais não se suspendem: a extração no dia do fim das inscrições (SC-1096)."""
    dia = timezone.localdate(timezone.now(), ZONA) + timedelta(days=30)
    fim = datetime.combine(dia, time(9, 0), tzinfo=ZONA)
    rascunho = _rascunho()
    rascunho["schedule"][0].update(
        {
            "startAt": (fim - timedelta(days=20)).isoformat(),
            "endAt": fim.isoformat(),
            "isRegistrationPeriod": True,
        }
    )
    rascunho["profiles"][0]["classificationMilestones"][0]["drawMethod"]["occurrenceAt"] = (
        datetime.combine(dia, time(20, 5), tzinfo=ZONA).isoformat()
    )
    edital = _em_elaboracao(api_client, manager_headers, process_payload, rascunho)
    _cair(caixa, "tempo esgotado")

    resposta = _submeter(api_client, edital)

    assert resposta.status_code == 422, resposta.content
    assert "o sorteio será sempre recusado" in resposta.content.decode("utf-8")


class _Relogio:
    """O tempo que a fonte que dorme custaria, sem dormir: cada chamada gasta o tempo limite."""

    def __init__(self):
        self.agora = 0.0
        self.chamadas = 0

    def monotonic(self):
        return self.agora

    def urlopen(self, url, timeout=None):
        self.chamadas += 1
        if url.endswith("/federal"):
            # A principal responde: é o pior caso, porque abre as consultas por número.
            return Servidor(federal="ultimo")(url, timeout=timeout)
        self.agora += timeout
        raise TimeoutError("timed out")


def test_a_espera_com_a_fonte_que_dorme_nao_passa_de_quinze_segundos(caixa, monkeypatch):
    """Quatro concursos realizados, e cada consulta de data esgota o tempo: a soma tem teto."""
    from processo_seletivo.sorteios.infrastructure import fontes
    from processo_seletivo.sorteios.infrastructure.fontes.loteria_federal import LoteriaFederal

    relogio = _Relogio()
    caixa.pela_rede(relogio.urlopen)
    monkeypatch.setattr(fontes.time, "monotonic", relogio.monotonic)

    situacoes = LoteriaFederal().conferir_referencias(
        ["5000", "6000", "6100", "6113"],
        fonte=LF,
        agora=timezone.now(),
    )

    assert relogio.agora <= 15
    assert {s.estado for s in situacoes.values()} == {dominio.REALIZADO}
    assert relogio.chamadas < 5, "as datas que não cabem no teto não são pedidas"


def test_a_principal_que_dorme_custa_uma_chamada(caixa, monkeypatch):
    from processo_seletivo.sorteios.infrastructure import fontes
    from processo_seletivo.sorteios.infrastructure.fontes.loteria_federal import LoteriaFederal

    relogio = _Relogio()

    def dormir(url, timeout=None):
        relogio.chamadas += 1
        relogio.agora += timeout
        raise TimeoutError("timed out")

    caixa.pela_rede(dormir)
    monkeypatch.setattr(fontes.time, "monotonic", relogio.monotonic)

    situacoes = LoteriaFederal().conferir_referencias(["5000", "6116"], fonte=LF, agora=None)

    assert relogio.chamadas == 1
    assert relogio.agora == 5
    assert {s.estado for s in situacoes.values()} == {dominio.INCONCLUSIVO}
