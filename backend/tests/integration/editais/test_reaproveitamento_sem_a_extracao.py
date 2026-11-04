"""Reaproveitar um Edital anterior não traz o concurso dele (116, US7, FR-3715–FR-3720, SC-1115).

**Pelo comando real, e com as regras de hoje no destino.** A origem pode ser do acervo — o 91/2026
do corpus declara a Loteria Federal com `Concurso 6010`, e é reconstituído por `antes_da_116()`,
como todo acervo da suíte —, mas o reaproveitamento roda **fora** desse mecanismo: o Edital novo é
de hoje, com a forma e a conferência ligadas (FR-3720). Os testes de compatibilidade histórica — a
republicação do corpus, o congelamento e a Retificação do acervo — ficam nos arquivos deles.

**O que a cópia preserva, e o que não.** O método do sorteio é regra — algoritmo, fonte, derivação,
normalização, substituição e a Etapa de habilitação —, e vem. O concurso e o instante dele são o que
aconteceu no certame anterior, e não vêm (D-009).
"""

import copy
from datetime import timedelta

import pytest
from django.utils import timezone

from processo_seletivo.editais.application.reaproveitamento import reaproveitar_edital
from processo_seletivo.editais.domain.reaproveitamento import payload_do_conteudo
from processo_seletivo.editais.domain.validation import blocking_findings, validate_for_publication
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.application.publish_edital import edital_snapshot
from processo_seletivo.publicacoes.application.selectors import effective_version
from tests.conftest import ator_institucional
from tests.fixtures.corpus import publicar_do_corpus
from tests.fixtures.edital import DRAW_METHOD, actor_headers, complete_draft
from tests.fixtures.legado import publicar_como_acervo
from tests.fixtures.publicacao import levar_a_publicacao, publish_original, retify
from tests.integration.editais.test_reaproveitamento import (
    ETAPA,
    _vincular_anexo_e_fechar_cronograma,
    rascunho_rico,
)

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

LF = "Loteria Federal"
EXTRACAO = ("occurrence", "occurrenceAt")
ESTRUTURA = ("algorithm", "source", "derivation", "normalization", "substitutionRule")
INDICACAO = "ainda não declara a extração"


def _futuro(dias=40):
    return (timezone.now() + timedelta(days=dias)).isoformat()


def _metodo(ocorrencia):
    metodo = copy.deepcopy(DRAW_METHOD)
    metodo.update({"source": LF, "occurrence": ocorrencia, "occurrenceAt": _futuro()})
    return metodo


def _com_metodo_proprio(ocorrencia):
    rascunho = complete_draft()
    rascunho["profiles"][0]["classificationMilestones"][0]["drawMethod"] = _metodo(ocorrencia)
    return rascunho


def _com_metodo_comum(ocorrencia):
    rascunho = complete_draft()
    rascunho["profiles"][0]["classificationMilestones"][0].pop("drawMethod")
    rascunho["drawMethod"] = _metodo(ocorrencia)
    return rascunho


@pytest.fixture
def destino(api_client, manager_headers):
    """Edital novo e vazio, em Processo próprio: a nova oferta."""
    criado = api_client.post(
        "/api/v1/admin/processos",
        {
            "institutionalCode": "PS-2027-116",
            "title": "Processo Seletivo 2027",
            "firstEdital": {"number": "16", "year": 2027, "title": "Edital da nova oferta"},
        },
        format="json",
        **{**manager_headers, "HTTP_IDEMPOTENCY_KEY": "destino-116-chave-0001"},
    )
    assert criado.status_code == 201, criado.content
    return Edital.objects.get(processo_id=criado.json()["id"])


def _reaproveitar(destino, origem):
    return reaproveitar_edital(
        actor=ator_institucional("preparadora", "edital:elaborar"),
        edital_id=destino.id,
        origem_id=origem.id,
        expected_revision=destino.revision,
        idempotency_key="reaproveitar-116-0001",
        correlation_id="teste-116",
    )


def _metodos(snapshot):
    """O comum, se houver, e o de cada marco que declara o próprio."""
    metodos = [snapshot["drawMethod"]] if snapshot.get("drawMethod") else []
    return metodos + [
        marco["drawMethod"]
        for perfil in snapshot.get("profiles") or []
        for marco in perfil.get("classificationMilestones") or []
        if marco.get("drawMethod")
    ]


def _sem_a_extracao(destino):
    destino.refresh_from_db()
    metodos = _metodos(edital_snapshot(destino))
    for metodo in metodos:
        for campo in EXTRACAO:
            assert not metodo.get(campo), (campo, metodo)
    return metodos


def _put(api_client, edital, payload, *, chave):
    edital.refresh_from_db()
    return api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        payload,
        format="json",
        **{
            **actor_headers("preparador", ["edital:elaborar"], key=chave),
            "HTTP_IF_MATCH": f'"{edital.revision}"',
        },
    )


def _submeter(api_client, edital):
    edital.refresh_from_db()
    return api_client.post(
        f"/api/v1/admin/editais/{edital.id}/submissoes",
        format="json",
        **{
            **actor_headers(
                "preparador",
                ["edital:elaborar", "edital:submeter"],
                key="submeter-reaproveitado-116",
            ),
            "HTTP_IF_MATCH": f'"{edital.revision}"',
        },
    )


# --- o que a cópia traz --------------------------------------------------------------------------


def test_o_historico_com_concurso_6010_e_reaproveitado_sem_a_extracao(api_client, destino):
    """O 91/2026 do corpus: método comum da Loteria Federal com `Concurso 6010`, do acervo."""
    origem, _ = publicar_do_corpus(api_client, "91", ate=1, chave="reaproveitar116")
    do_acervo = effective_version(edital_id=origem.id).content["drawMethod"]
    assert do_acervo["occurrence"] == "Concurso 6010"

    copiado = _reaproveitar(destino, origem)

    (metodo,) = _sem_a_extracao(copiado)
    for campo in ESTRUTURA:
        assert metodo[campo] == do_acervo[campo], campo


def test_o_numero_valido_tambem_nao_vem(api_client, manager_headers, process_payload, destino):
    """`6010` passa na forma; não é por isso que ele vem. O que aconteceu não se copia."""
    origem = publish_original(
        api_client, manager_headers, process_payload, draft=_com_metodo_proprio("6010")
    )

    (metodo,) = _sem_a_extracao(_reaproveitar(destino, origem))

    for campo in ESTRUTURA:
        assert metodo[campo] == _metodo("6010")[campo], campo


def test_o_metodo_comum_vem_sem_a_extracao_e_os_marcos_continuam_sem_o_proprio(
    api_client, manager_headers, process_payload, destino
):
    origem = publish_original(
        api_client, manager_headers, process_payload, draft=_com_metodo_comum("6010")
    )

    copiado = _reaproveitar(destino, origem)

    snapshot = edital_snapshot(copiado)
    assert snapshot["drawMethod"]["source"] == LF
    assert not any(
        marco.get("drawMethod")
        for perfil in snapshot["profiles"]
        for marco in perfil["classificationMilestones"]
    )
    _sem_a_extracao(copiado)


def test_os_metodos_proprios_vem_sem_a_extracao_e_com_a_etapa_do_destino(
    api_client, manager_headers, process_payload, destino
):
    """Identificadores e Etapas consistentes: a habilitação e as Etapas do marco são do destino."""
    rascunho = rascunho_rico()
    marco = rascunho["profiles"][0]["classificationMilestones"][0]
    marco["drawMethod"] = {**_metodo("6010"), "qualifyingStageId": ETAPA}
    origem = publicar_como_acervo(
        api_client,
        manager_headers,
        process_payload,
        draft=rascunho,
        anexos=1,
        antes_de_submeter=_vincular_anexo_e_fechar_cronograma,
    )

    copiado = _reaproveitar(destino, origem)

    (metodo,) = _sem_a_extracao(copiado)
    etapas_do_destino = {str(etapa) for etapa in copiado.etapas.values_list("id", flat=True)}
    etapas_da_origem = {str(etapa) for etapa in origem.etapas.values_list("id", flat=True)}
    assert metodo["qualifyingStageId"] in etapas_do_destino
    assert metodo["qualifyingStageId"] not in etapas_da_origem
    marco_copiado = copiado.perfis.get().marcos.get()
    assert {str(etapa) for etapa in marco_copiado.etapas} <= etapas_do_destino


def test_sem_sorteio_nada_muda(api_client, destino):
    origem, _ = publicar_do_corpus(api_client, "92", ate=1, chave="reaproveitar116-92")

    copiado = _reaproveitar(destino, origem)

    assert _metodos(edital_snapshot(copiado)) == []
    assert copiado.perfis.exists()


# --- o rascunho, a recusa e a publicação ---------------------------------------------------------


def test_sem_a_extracao_edita_mas_nao_submete_nem_publica(
    api_client, manager_headers, process_payload, destino, caixa
):
    origem = publish_original(
        api_client, manager_headers, process_payload, draft=_com_metodo_proprio("6010")
    )
    copiado = _reaproveitar(destino, origem)
    caixa.zerar()

    # Editar outra etapa antes de declarar a extração: a gravação conclui.
    payload = payload_do_conteudo(edital_snapshot(copiado))
    payload["schedule"][0]["description"] = "Inscrições da nova oferta"
    editado = _put(api_client, copiado, payload, chave="editar-reaproveitado-116")
    assert editado.status_code < 400, editado.content

    # Submeter sem ela: recusa com a indicação, sem perguntar nada à Caixa.
    resposta = _submeter(api_client, copiado)
    assert resposta.status_code == 422, resposta.content
    assert INDICACAO in resposta.content.decode("utf-8")
    assert caixa.chamadas == 0
    # E a publicação recusaria pelo mesmo motivo: é a mesma validação, no ato dela.
    copiado.refresh_from_db()
    impeditivos = blocking_findings(validate_for_publication(edital_snapshot(copiado)))
    assert any(INDICACAO in achado.message for achado in impeditivos)
    assert Edital.objects.get(pk=copiado.pk).status == Edital.Status.EM_ELABORACAO


def test_com_a_extracao_futura_declarada_o_edital_publica(
    api_client, manager_headers, process_payload, destino, caixa
):
    """SC-1116: a mesma cópia, com a extração deste certame, chega à publicação."""
    origem = publish_original(
        api_client, manager_headers, process_payload, draft=_com_metodo_proprio("6010")
    )
    copiado = _reaproveitar(destino, origem)
    caixa.usar_gravacao()

    payload = payload_do_conteudo(edital_snapshot(copiado))
    metodo = payload["profiles"][0]["classificationMilestones"][0]["drawMethod"]
    metodo.update({"occurrence": "6116", "occurrenceAt": _futuro(45)})
    assert _put(api_client, copiado, payload, chave="extracao-reaproveitado-116").status_code < 400

    publicado = levar_a_publicacao(
        api_client, copiado, regravar_rascunho=False, chave="publicar-reaproveitado-116"
    )

    assert publicado.status == Edital.Status.PUBLICADO
    vigente = effective_version(edital_id=publicado.id).content
    assert vigente["profiles"][0]["classificationMilestones"][0]["drawMethod"]["occurrence"] == (
        "6116"
    )


# --- a origem -----------------------------------------------------------------------------------


def test_a_origem_continua_consultavel_e_retificavel(api_client, destino):
    """FR-3719: o acervo não é tocado, e a Retificação que não toca o concurso dele publica."""
    origem, _ = publicar_do_corpus(api_client, "91", ate=1, chave="reaproveitar116-origem")
    antes = effective_version(edital_id=origem.id).content

    _reaproveitar(destino, origem)

    depois = effective_version(edital_id=origem.id).content
    assert depois == antes
    assert depois["drawMethod"]["occurrence"] == "Concurso 6010"
    evento = depois["schedule"][0]
    retify(
        api_client,
        origem,
        [
            {
                "targetPath": f"/schedule/id={evento['id']}/description",
                "operation": "REPLACE",
                "newValue": f"{evento.get('description') or 'Evento'} (retificado)",
            }
        ],
        suffix="origem116",
    )
    vigente = effective_version(edital_id=origem.id).content
    assert vigente["drawMethod"]["occurrence"] == "Concurso 6010"
