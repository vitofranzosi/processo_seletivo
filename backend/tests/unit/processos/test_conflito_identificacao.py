"""T055/T056 — a recusa aponta a entidade e o campo do conflito (FR-022, achado 26).

`Edital` é único por `(escopo, número, ano)` — **não** por Processo. Criar um Processo cujo
primeiro Edital repita o número de qualquer outro Edital do escopo falhava com "Identificação
institucional já utilizada": a identificação estava correta, e quem recebia o erro corrigia o campo
que não tinha problema.

A causa era um `try` só para dois `create`, com um `except IntegrityError` que sempre devolvia a
mensagem do Processo.
"""

import pytest

from processo_seletivo.processos.application.commands import (
    add_edital,
    create_process_with_first_edital,
)
from processo_seletivo.processos.models import Edital, ProcessoSeletivo
from processo_seletivo.seguranca.domain import Actor
from processo_seletivo.shared.api.problems import DomainError

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def manager_actor():
    return Actor("gestora", "cefor", frozenset({"processo:criar", "edital:criar"}))


def _dados(codigo, numero, ano=2027):
    return {
        "institutionalCode": codigo,
        "title": f"Processo {codigo}",
        "firstEdital": {"number": numero, "year": ano, "title": f"Edital {numero}/{ano}"},
    }


def _criar(ator, codigo, numero, ano=2027, chave=None):
    return create_process_with_first_edital(
        actor=ator,
        data=_dados(codigo, numero, ano),
        idempotency_key=chave or f"k-{codigo}-{numero}-{ano}",
        correlation_id=f"c-{codigo}-{numero}",
    )


def test_conflito_do_edital_aponta_numero_e_ano(manager_actor):
    """O caso do achado 26: identificação do Processo nova, número do Edital repetido."""
    _criar(manager_actor, "PS-PRIMEIRO", "21")

    with pytest.raises(DomainError) as erro:
        _criar(manager_actor, "PS-SEGUNDO", "21")

    assert erro.value.code == "edital_identifier_conflict"
    assert "21/2027" in erro.value.detail
    assert "Identificação institucional" not in erro.value.detail


def test_conflito_do_processo_continua_apontando_a_identificacao(manager_actor):
    """A recusa que já estava certa não pode ter sido trocada pela outra."""
    _criar(manager_actor, "PS-UNICO", "30")

    with pytest.raises(DomainError) as erro:
        _criar(manager_actor, "PS-UNICO", "31")

    assert erro.value.code == "institutional_identifier_conflict"
    assert "Identificação institucional" in erro.value.detail


def test_o_conflito_do_edital_nao_deixa_processo_orfao(manager_actor):
    """A transação do command desfaz o Processo criado antes da falha do Edital.

    Separar os dois `try` não pode ter separado a atomicidade: um Processo sem Edital violaria a
    invariante da Constituição de que nenhum Processo existe sem ao menos um Edital.
    """
    _criar(manager_actor, "PS-BASE", "40")
    antes = ProcessoSeletivo.objects.count()

    with pytest.raises(DomainError):
        _criar(manager_actor, "PS-NOVO", "40")

    assert ProcessoSeletivo.objects.count() == antes
    assert not ProcessoSeletivo.objects.filter(institutional_code="PS-NOVO").exists()


def test_o_codigo_de_erro_e_o_mesmo_que_create_edital_ja_devolvia(manager_actor):
    """Nenhum erro novo foi inventado: é o código que `add_edital` já usa desde a `001`."""
    processo, _ = _criar(manager_actor, "PS-COMPARA", "50")

    with pytest.raises(DomainError) as erro:
        add_edital(
            actor=manager_actor,
            processo_id=processo.id,
            data={"number": "50", "year": 2027, "title": "Repetido"},
            idempotency_key="k-repetido",
            correlation_id="c-repetido",
        )

    assert erro.value.code == "edital_identifier_conflict"


def test_editais_de_anos_distintos_com_o_mesmo_numero_convivem(manager_actor):
    """A unicidade é de `(escopo, número, ano)` — o ano faz parte dela."""
    _criar(manager_actor, "PS-2027", "60", ano=2027)
    _criar(manager_actor, "PS-2028", "60", ano=2028)

    assert Edital.objects.filter(number="60").count() == 2
