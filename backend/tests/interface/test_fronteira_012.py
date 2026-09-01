"""T076 e T076a — a fronteira com a 012, nas telas e nos dados.

A 011 organiza o trabalho e para antes de executá-lo. Isso tem duas consequências verificáveis:
nenhuma tela dela mostra dado de candidato, e nenhum comando dela toca uma inscrição.
"""

import pytest
from django.urls import reverse

from processo_seletivo.comissoes.application.alocacao import remover_alocacao
from processo_seletivo.comissoes.application.comissao import alterar_funcao, remover_membro
from processo_seletivo.inscricoes.models import Inscricao
from tests.fixtures.comissao import alocar_em
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def telas(processo, edital, etapa_id):
    return [
        reverse("interface:comissao", args=[processo.id]),
        reverse("interface:alocacoes", args=[processo.id]),
        reverse("interface:minhas-etapas"),
        reverse("interface:atribuicao", args=[edital.id, etapa_id]),
    ]


def test_nenhuma_tela_da_011_exibe_dado_de_candidato(
    client, seletor_ligado, gestor, processo_a, edital_a, comissao_de_a, etapa_a1
):
    """O que se procura é o **dado**, e não a palavra: a página fala em candidatos para dizer
    justamente que a avaliação deles ainda não está aqui."""
    from django.utils import timezone

    inscricao = Inscricao.objects.create(
        created_at=timezone.now(),
        identity_subject="cpf:11144477735",
        edital=edital_a,
        profile_id="00000000-0000-0000-0000-000000000401",
        nome="Candidata Fulana",
        cpf="111.444.777-35",
        cpf_normalizado="11144477735",
        email="fulana@exemplo.br",
    )
    alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)
    identificar(client, "carlos", ["gestor"])

    for tela in telas(processo_a, edital_a, etapa_a1):
        corpo = client.get(tela).content.decode()
        for proibido in (inscricao.nome, inscricao.cpf, inscricao.email, str(inscricao.id)):
            assert proibido not in corpo, f"{tela}: {proibido}"


def test_os_cinco_comandos_nao_alteram_inscricoes(
    gestor, processo_a, edital_a, comissao_de_a, etapa_a1, etapa_a2
):
    """FR-082: mudar a comissão não é mexer em quem se inscreveu."""
    antes = _retrato_das_inscricoes()

    joao = comissao_de_a["joao"]
    alocacao = alocar_em(gestor, processo_a, joao, edital_a, etapa_a1)
    alocar_em(gestor, processo_a, joao, edital_a, etapa_a2)
    remover_alocacao(
        actor=gestor,
        processo_id=processo_a.id,
        alocacao_id=alocacao.id,
        idempotency_key="k1",
        correlation_id="c",
    )
    alterar_funcao(
        actor=gestor,
        processo_id=processo_a.id,
        membro_id=joao.id,
        funcao="PRESIDENTE",
        idempotency_key="k2",
        correlation_id="c",
    )
    remover_membro(
        actor=gestor,
        processo_id=processo_a.id,
        membro_id=joao.id,
        idempotency_key="k3",
        correlation_id="c",
    )

    assert _retrato_das_inscricoes() == antes


def _retrato_das_inscricoes():
    return sorted(Inscricao.objects.values_list("id", "status", "revision"))
