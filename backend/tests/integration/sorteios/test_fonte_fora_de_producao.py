"""A semente de demonstração não chega a um Processo real (046, `FR-757`, `FR-759`, `SC-279`).

**O `RC-72` da auditoria de consolidação**: a *"Fonte de demonstração"* — semente fixa, sem rede —
era oferecida no seletor de fonte e aceita na publicação em qualquer ambiente. Um Edital de
produção que a declarasse publicaria um sorteio cujo resultado se conhece antes da extração.

**Um vocabulário, cinco pontos.** O seletor da composição, a gravação do rascunho, a publicação, a
Retificação e a observação da ocorrência leem a mesma função. Este arquivo desliga a configuração
como produção a desliga e confere os pontos um a um — e religa para conferir que a suíte, o
`seed_demo` e o `quickstart` continuam com ela.
"""

import copy

import pytest
from django.test import override_settings

from processo_seletivo.editais.application.reaproveitamento import reaproveitar_edital
from processo_seletivo.editais.domain.validation import (
    ATO_DE_PUBLICACAO,
    ATO_DE_RETIFICACAO,
    validate_for_publication,
)
from processo_seletivo.interface.forms import opcoes_do_metodo
from processo_seletivo.processos.models import Edital
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.sorteios.infrastructure.fontes import fonte_declarada, fontes_publicadas
from tests.conftest import ator_institucional
from tests.fixtures.edital import actor_headers, complete_draft
from tests.fixtures.publicacao import publish_original

DEMONSTRACAO = "Fonte de demonstração"
COMO_PRODUCAO = override_settings(SORTEIO_FONTE_DE_DEMONSTRACAO=False)


def _rascunho_com_a_demonstracao():
    """O rascunho mínimo sorteia, e o método dele já declara a fonte de demonstração."""
    rascunho = complete_draft()
    metodo = rascunho["profiles"][0]["classificationMilestones"][0]["drawMethod"]
    assert metodo["source"] == DEMONSTRACAO, "a premissa: o rascunho mínimo usa a demonstração"
    return rascunho


def _achados_da_fonte(conteudo, ato):
    return [
        item
        for item in validate_for_publication(conteudo, ato=ato)
        if item.code == "draw_method_invalid" and DEMONSTRACAO in item.message
    ]


# --- o vocabulário, onde a demonstração existe e onde não existe ------------------------------


def test_na_suite_a_demonstracao_pertence_ao_vocabulario():
    """`FR-759`: desenvolvimento e testes continuam sorteando sem rede, pelo mesmo nome."""
    assert DEMONSTRACAO in fontes_publicadas()
    assert fonte_declarada(DEMONSTRACAO) is not None


@COMO_PRODUCAO
def test_em_producao_o_vocabulario_e_so_a_loteria_federal():
    assert set(fontes_publicadas()) == {"Loteria Federal"}


@COMO_PRODUCAO
def test_em_producao_o_seletor_nao_oferece_a_demonstracao():
    fontes = [valor for valor, _ in opcoes_do_metodo()["drawMethod/source"]]

    assert fontes == ["Loteria Federal"]


@COMO_PRODUCAO
def test_em_producao_a_execucao_recusa_a_demonstracao():
    with pytest.raises(DomainError, match="draw_source_not_supported") as recusa:
        fonte_declarada(DEMONSTRACAO)

    assert DEMONSTRACAO not in str(recusa.value).split("As publicadas são:")[1]


# --- a validação, nos dois atos ---------------------------------------------------------------


@pytest.mark.parametrize("ato", [ATO_DE_PUBLICACAO, ATO_DE_RETIFICACAO])
def test_em_producao_a_publicacao_e_a_retificacao_acusam_a_demonstracao(ato):
    """Na Retificação também: o sorteio de um Edital de produção com semente fixa não sai."""
    conteudo = _rascunho_com_a_demonstracao()

    assert _achados_da_fonte(conteudo, ato) == [], "a contraprova: na suíte, a fonte é aceita"
    with COMO_PRODUCAO:
        acusados = _achados_da_fonte(conteudo, ato)

    assert acusados and all(item.severity == "BLOCKING_ERROR" for item in acusados)


# --- a gravação e o reaproveitamento ----------------------------------------------------------


def _processo(api_client, manager_headers, process_payload, *, chave):
    payload = copy.deepcopy(process_payload)
    payload["institutionalCode"] = f"PS-046-{chave}"
    payload["firstEdital"] = {**payload["firstEdital"], "number": f"46{len(chave):02d}"}
    criado = api_client.post(
        "/api/v1/admin/processos",
        payload,
        format="json",
        **{**manager_headers, "HTTP_IDEMPOTENCY_KEY": f"046-fonte-{chave}"},
    )
    assert criado.status_code == 201, criado.content
    return Edital.objects.get(processo_id=criado.json()["id"])


@pytest.mark.django_db
@pytest.mark.integration
def test_em_producao_a_gravacao_recusa_a_demonstracao(api_client, manager_headers, process_payload):
    edital = _processo(api_client, manager_headers, process_payload, chave="gravacao")

    with COMO_PRODUCAO:
        gravado = api_client.put(
            f"/api/v1/admin/editais/{edital.id}/rascunho",
            _rascunho_com_a_demonstracao(),
            format="json",
            **{
                **actor_headers("preparador", ["edital:elaborar"], key="046-fonte-put"),
                "HTTP_IF_MATCH": f'"{edital.revision}"',
            },
        )

    assert gravado.status_code in (400, 422), gravado.content
    assert DEMONSTRACAO in gravado.content.decode()


@pytest.mark.django_db
@pytest.mark.integration
def test_em_producao_o_reaproveitamento_nao_copia_a_demonstracao(
    api_client, manager_headers, process_payload
):
    """Reaproveitar copia a cláusula antiga — é o caminho que mais facilmente escaparia (`D-G3`)."""
    origem = publish_original(
        api_client, manager_headers, process_payload, draft=_rascunho_com_a_demonstracao()
    )
    destino = _processo(api_client, manager_headers, process_payload, chave="destino")

    with COMO_PRODUCAO, pytest.raises(DomainError) as recusa:
        reaproveitar_edital(
            actor=ator_institucional("preparadora", "edital:elaborar"),
            edital_id=destino.id,
            origem_id=origem.id,
            expected_revision=destino.revision,
            idempotency_key="046-fonte-reaproveitar",
            correlation_id="046-fonte",
        )

    assert DEMONSTRACAO in str(recusa.value)
