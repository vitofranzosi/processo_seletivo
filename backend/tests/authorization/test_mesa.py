"""A autorização composta, pelo canal do ator (US2, FR-043 a FR-046).

```text
pode_atuar_na_etapa (011)  →  Atribuição ativa desta pessoa  →  sim
```

As duas condições, e a demonstração de cada uma pela recusa. A que mais importa é a última:
**perder a alocação revoga o acesso sem que nenhuma linha de Atribuição seja tocada**, e devolvê-la
restaura — que é o que torna reparável o engano da presidência (D-004, FR-046, FR-069).
"""

import pytest
from django.urls import reverse

from processo_seletivo.avaliacoes.application.distribuicao import distribuir
from processo_seletivo.avaliacoes.models import Atribuicao
from processo_seletivo.comissoes.application.alocacao import alocar, remover_alocacao
from tests.fixtures.comissao import alocar_em, inscrever
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.authorization]


@pytest.fixture
def mesa(edital_a, etapa_a1):
    return reverse("interface:minha-etapa", args=[edital_a.id, etapa_a1])


@pytest.fixture
def joao_com_trabalho(gestor, processo_a, edital_a, comissao_de_a, etapa_a1):
    membro = comissao_de_a["joao"]
    alocacao = alocar_em(gestor, processo_a, membro, edital_a, etapa_a1)
    inscricoes = inscrever(edital_a, 2)
    distribuir(
        actor=gestor,
        processo_id=processo_a.id,
        edital_id=edital_a.id,
        etapa_id=etapa_a1,
        membro_ids=[membro.id],
        inscricao_ids=[i.id for i in inscricoes],
        idempotency_key="para-joao",
        correlation_id="teste",
    )
    return {"membro": membro, "alocacao": alocacao, "inscricoes": inscricoes}


def test_quem_tem_alocacao_e_atribuicao_ve_a_mesa(client, seletor_ligado, mesa, joao_com_trabalho):
    identificar(client, "joao", [])

    corpo = client.get(mesa).content.decode()

    assert joao_com_trabalho["inscricoes"][0].protocolo in corpo


def test_alocado_sem_atribuicao_alcanca_a_mesa_vazia(
    client, seletor_ligado, gestor, processo_a, edital_a, comissao_de_a, etapa_a1, mesa
):
    """Alocação abre a porta da Etapa: responder 404 negaria o que a 011 concedeu (FR-023)."""
    alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)
    identificar(client, "joao", [])

    assert client.get(mesa).status_code == 200


def test_sem_alocacao_a_etapa_e_inexistente(client, seletor_ligado, comissao_de_a, mesa):
    """Sem a primeira condição, nem a porta abre — e a recusa não enumera a Etapa (FR-044)."""
    identificar(client, "joao", [])

    assert client.get(mesa).status_code == 404


def test_perder_a_alocacao_revoga_o_acesso(
    client, seletor_ligado, gestor, processo_a, mesa, joao_com_trabalho
):
    """SC-010, e a prova de que a revogação é **computada**.

    A conjunção é avaliada a cada acesso: falhando a primeira condição, as Atribuições continuam
    ativas e inertes. Nenhuma linha desta feature é escrita para revogar (FR-069).
    """
    identificar(client, "joao", [])
    assert client.get(mesa).status_code == 200
    ativas_antes = Atribuicao.objects.filter(ativo=True).count()

    remover_alocacao(
        actor=gestor,
        processo_id=processo_a.id,
        alocacao_id=joao_com_trabalho["alocacao"].id,
        idempotency_key="tirar-joao",
        correlation_id="teste",
    )

    assert client.get(mesa).status_code == 404
    assert Atribuicao.objects.filter(ativo=True).count() == ativas_antes


def test_devolver_a_alocacao_restaura_as_mesmas_atribuicoes(
    client, seletor_ligado, gestor, processo_a, edital_a, etapa_a1, mesa, joao_com_trabalho
):
    """O engano da presidência é reparável, e é para isso que a Atribuição não pende da alocação.

    Se ela pendesse, remover alguém da Etapa por engano deixaria as atribuições dele órfãs para
    sempre — e a correção seria redistribuir tudo à mão (D-004, EC-003).
    """
    identificar(client, "joao", [])
    remover_alocacao(
        actor=gestor,
        processo_id=processo_a.id,
        alocacao_id=joao_com_trabalho["alocacao"].id,
        idempotency_key="tirar",
        correlation_id="teste",
    )
    assert client.get(mesa).status_code == 404

    alocar(
        actor=gestor,
        processo_id=processo_a.id,
        membro_id=joao_com_trabalho["membro"].id,
        edital_id=edital_a.id,
        etapa_id=etapa_a1,
        idempotency_key="devolver",
        correlation_id="teste",
    )

    corpo = client.get(mesa).content.decode()
    for inscricao in joao_com_trabalho["inscricoes"]:
        assert inscricao.protocolo in corpo


def test_escopo_divergente_e_inexistente(client, seletor_ligado, mesa, joao_com_trabalho):
    identificar(client, "joao", [], escopo="outra-unidade")

    assert client.get(mesa).status_code == 404
