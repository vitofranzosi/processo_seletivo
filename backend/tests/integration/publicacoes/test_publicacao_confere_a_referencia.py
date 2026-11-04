"""A submissão e a publicação conferem o concurso declarado na Caixa (116, US1, FR-3634, FR-3647).

**O caso é o concurso 5000, de 26/08/2015, declarado para dezembro de 2026.** Pelo caminho real —
rascunho, submissão, homologação e publicação pela API —, com a Caixa da suíte respondendo o que a
Caixa respondeu em 03/11/2026: último 6114, de 01/11/2026. A tela chama os mesmos comandos
(`interface/atos.py`), e o desfecho dela está em `tests/interface/test_desfecho_da_conferencia.py`.
"""

import copy
import logging
from datetime import date, timedelta

import pytest
from django.utils import timezone

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.processos.models import Edital
from processo_seletivo.sorteios.domain import conferencia as dominio
from tests.fixtures.edital import (
    DRAW_METHOD,
    actor_headers,
    complete_draft,
    identidade_do_marco,
    identificador,
)

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

LF = "Loteria Federal"


def _metodo(ocorrencia):
    metodo = copy.deepcopy(DRAW_METHOD)
    metodo.update(
        {
            "source": LF,
            "occurrence": ocorrencia,
            "occurrenceAt": (timezone.now() + timedelta(days=40)).isoformat(),
        }
    )
    return metodo


def _rascunho(*ocorrencias, comum=None):
    rascunho = complete_draft()
    modelo = rascunho["profiles"][0]
    rascunho["profiles"] = []
    for indice, ocorrencia in enumerate(ocorrencias):
        perfil = copy.deepcopy(modelo)
        perfil["id"] = identificador(401, 30 + indice)
        perfil["code"] = f"P{indice}"
        marco = perfil["classificationMilestones"][0]
        marco["id"] = identidade_do_marco(perfil["id"])
        marco["code"] = f"M{indice}"
        if ocorrencia is None:
            marco.pop("drawMethod", None)
        else:
            marco["drawMethod"] = _metodo(ocorrencia)
        rascunho["profiles"].append(perfil)
    if comum is not None:
        rascunho["drawMethod"] = _metodo(comum)
    return rascunho


@pytest.fixture
def em_elaboracao(api_client, manager_headers, process_payload):
    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    assert criado.status_code == 201, criado.content
    return Edital.objects.get(processo_id=criado.json()["id"])


def _gravar(api_client, edital, rascunho):
    preparador = actor_headers("preparador", ["edital:elaborar", "edital:submeter"])
    gravado = api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        rascunho,
        format="json",
        **{**preparador, "HTTP_IF_MATCH": f'"{edital.revision}"'},
    )
    assert gravado.status_code < 400, gravado.content
    edital.refresh_from_db()


def _submeter(api_client, edital, *, chave="submeter-116-0001"):
    preparador = actor_headers("preparador", ["edital:elaborar", "edital:submeter"], key=chave)
    return api_client.post(
        f"/api/v1/admin/editais/{edital.id}/submissoes",
        format="json",
        **{**preparador, "HTTP_IF_MATCH": f'"{edital.revision}"'},
    )


def _homologar(api_client, edital):
    edital.refresh_from_db()
    resposta = api_client.post(
        f"/api/v1/admin/editais/{edital.id}/homologacoes",
        {"reason": "OK"},
        format="json",
        **{
            **actor_headers("homologador", ["edital:homologar"]),
            "HTTP_IF_MATCH": f'"{edital.revision}"',
        },
    )
    assert resposta.status_code < 400, resposta.content
    edital.refresh_from_db()


def _publicar(api_client, edital, *, chave="publicar-116-0001"):
    from tests.fixtures.publicacao import SIGNATORY

    edital.refresh_from_db()
    return api_client.post(
        f"/api/v1/admin/editais/{edital.id}/publicacoes",
        {"signatory": SIGNATORY},
        format="json",
        **{
            **actor_headers("publicador", ["edital:publicar"], key=chave),
            "HTTP_IF_MATCH": f'"{edital.revision}"',
        },
    )


def _conferencias(edital, operacao):
    registro = RegistroAuditoria.objects.get(
        aggregate_type="Edital", aggregate_id=edital.pk, operation=operacao
    )
    return registro.detalhe["conferenciaDaReferencia"]


# --- cenário A: o concurso histórico ---------------------------------------------------------


def test_o_concurso_5000_e_recusado_na_submissao(api_client, em_elaboracao, caixa):
    caixa.usar_gravacao()
    _gravar(api_client, em_elaboracao, _rascunho("5000"))

    resposta = _submeter(api_client, em_elaboracao)

    assert resposta.status_code == 422, resposta.content
    corpo = resposta.content.decode("utf-8")
    assert "O concurso 5000 da Loteria Federal já foi realizado, em 26/08/2015" in corpo
    assert "6114, de 01/11/2026" in corpo
    em_elaboracao.refresh_from_db()
    assert em_elaboracao.status == Edital.Status.EM_ELABORACAO
    assert caixa.chamadas_ao_ultimo == 1
    assert caixa.chamadas_por_numero == [5000]


def test_homologado_sob_ainda_nao_e_recusado_na_publicacao(api_client, em_elaboracao, caixa):
    """Submissão e publicação são atos distintos, em instantes distintos (a FR-358 da `028`)."""
    caixa.usar_gravacao()
    _gravar(api_client, em_elaboracao, _rascunho("6116"))
    assert _submeter(api_client, em_elaboracao).status_code == 200
    _homologar(api_client, em_elaboracao)
    # Entre a homologação e a publicação, a Caixa realiza o 6116.
    caixa.realizado_ate(6116, date(2026, 11, 7))

    resposta = _publicar(api_client, em_elaboracao)

    assert resposta.status_code == 422, resposta.content
    assert "O concurso 6116 da Loteria Federal já foi realizado, em 07/11/2026" in (
        resposta.content.decode("utf-8")
    )
    em_elaboracao.refresh_from_db()
    assert em_elaboracao.status == Edital.Status.HOMOLOGADO


# --- cenários B e F: o futuro passa, com a informação ----------------------------------------


def test_o_6116_passa_com_a_informacao(api_client, em_elaboracao, caixa):
    caixa.usar_gravacao()
    _gravar(api_client, em_elaboracao, _rascunho("6116"))

    resposta = _submeter(api_client, em_elaboracao)

    assert resposta.status_code == 200, resposta.content
    (informacao,) = [
        achado
        for achado in resposta.json()["validationFindings"]
        if achado["code"] == "draw_occurrence_not_drawn_yet"
    ]
    assert informacao["severity"] == "INFO"
    assert "ainda não realizado na consulta de" in informacao["message"]
    assert "2 concurso(s) adiante" in informacao["message"]


def test_o_registro_do_ato_traz_a_conferencia(api_client, em_elaboracao, caixa):
    """As seis perguntas da SC-1098, lidas só do registro de cada ato (FR-3647)."""
    caixa.usar_gravacao()
    _gravar(api_client, em_elaboracao, _rascunho("6116"))
    assert _submeter(api_client, em_elaboracao).status_code == 200
    _homologar(api_client, em_elaboracao)
    assert _publicar(api_client, em_elaboracao).status_code == 201

    for operacao in ("SUBMETER", "PUBLICAR"):
        (registro,) = _conferencias(em_elaboracao, operacao)
        assert registro["fonte"] == LF
        assert registro["referencia"] == "6116"
        assert registro["consultadaEm"].endswith("-03:00")
        assert (registro["ultimo"], registro["ultimoEm"]) == (6114, "2026-11-01")
        assert registro["situacao"] == dominio.AINDA_NAO_REALIZADO
        assert registro["conclusiva"] is True
        assert registro["decisao"] == "PROSSEGUIU"
        assert "listaDezenas" not in repr(registro)


# --- cenário G: vários marcos, uma consulta --------------------------------------------------


def test_dois_marcos_e_o_comum_fazem_uma_consulta_e_um_impeditivo(api_client, em_elaboracao, caixa):
    caixa.usar_gravacao()
    _gravar(api_client, em_elaboracao, _rascunho("6116", "6113", None, comum="6117"))

    resposta = _submeter(api_client, em_elaboracao)

    assert resposta.status_code == 422, resposta.content
    corpo = resposta.content.decode("utf-8")
    assert corpo.count("já foi realizado") == 1
    assert "O marco M1: O concurso 6113 da Loteria Federal já foi realizado" in corpo
    assert caixa.chamadas_ao_ultimo == 1
    assert caixa.chamadas_por_numero == [6113]


# --- o guardião contra o `situacoes=None` esquecido ------------------------------------------


def test_cada_comando_consulta_a_fonte(api_client, em_elaboracao, caixa):
    _gravar(api_client, em_elaboracao, _rascunho("6116"))
    assert caixa.chamadas_ao_ultimo == 0, "a gravação do rascunho não consulta (D-007)"
    assert _submeter(api_client, em_elaboracao).status_code == 200
    assert caixa.chamadas_ao_ultimo == 1
    _homologar(api_client, em_elaboracao)
    assert caixa.chamadas_ao_ultimo == 1, "a homologação não confere"
    assert _publicar(api_client, em_elaboracao).status_code == 201
    assert caixa.chamadas_ao_ultimo == 2


def test_a_repeticao_nao_consulta_de_novo(api_client, em_elaboracao, caixa):
    _gravar(api_client, em_elaboracao, _rascunho("6116"))
    revisao = em_elaboracao.revision
    assert _submeter(api_client, em_elaboracao).status_code == 200
    em_elaboracao.revision = revisao
    repetida = _submeter(api_client, em_elaboracao)
    assert repetida.status_code == 200, repetida.content
    assert caixa.chamadas_ao_ultimo == 1


# --- FR-3632 e FR-3649 -----------------------------------------------------------------------


def test_referencia_travada_sem_consulta_e_inconclusiva(
    api_client, em_elaboracao, caixa, monkeypatch
):
    """O rascunho mudou entre a consulta e a trava: a referência travada é inconclusiva."""
    from processo_seletivo.sorteios.application import conferencia

    _gravar(api_client, em_elaboracao, _rascunho("6116"))
    monkeypatch.setattr(conferencia, "conferir", lambda referencias, agora=None: {})

    resposta = _submeter(api_client, em_elaboracao)

    assert resposta.status_code == 200, resposta.content
    codigos = {achado["code"] for achado in resposta.json()["validationFindings"]}
    assert "draw_occurrence_not_checked" in codigos
    (registro,) = _conferencias(em_elaboracao, "SUBMETER")
    assert (registro["situacao"], registro["conclusiva"]) == (dominio.INCONCLUSIVO, False)
    assert registro["decisao"] == "PROSSEGUIU_COM_ADVERTENCIA"


class _Coletor(logging.Handler):
    def __init__(self):
        super().__init__(logging.INFO)
        self.registros = []

    def emit(self, record):
        self.registros.append(record)


def test_a_recusa_vai_ao_log_e_nao_a_trilha(api_client, em_elaboracao, caixa):
    caixa.usar_gravacao()
    _gravar(api_client, em_elaboracao, _rascunho("5000"))
    # O logger do projeto não propaga até o `caplog`; o coletor se pendura nele direto.
    logger = logging.getLogger("processo_seletivo.sorteios.application.conferencia")
    coletor = _Coletor()
    logger.addHandler(coletor)
    try:
        resposta = _submeter(api_client, em_elaboracao)
    finally:
        logger.removeHandler(coletor)

    assert resposta.status_code == 422
    assert not RegistroAuditoria.objects.filter(
        aggregate_id=em_elaboracao.pk, operation="SUBMETER"
    ).exists()
    (linha,) = [
        r for r in coletor.registros if r.getMessage().startswith("conferencia_da_referencia")
    ]
    assert '"desfecho": "RECUSADO"' in linha.getMessage()
    assert '"decisao": "RECUSOU"' in linha.getMessage()
    assert linha.correlationId
