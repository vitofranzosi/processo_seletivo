"""A 011 numa comissão do tamanho que mil candidatos exigem.

Mil candidatos não acrescentam uma linha às tabelas desta feature — as telas dela nunca tocam
`inscricoes`. O que o volume de candidatos determina é o **tamanho da comissão**: duas avaliações
por candidato numa etapa documental são duas mil avaliações, e a cinquenta por avaliador isso é
uma banca de quarenta pessoas.

O que estes testes prendem é que a leitura não pode custar por pessoa. A tela de Comissão chegou a
206 consultas com quarenta membros, porque perguntava as Etapas de cada um dentro do laço.
"""

import pytest
from django.urls import reverse

from processo_seletivo.comissoes.application.alocacao import alocar
from processo_seletivo.comissoes.application.comissao import adicionar_membro
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.performance]

TAMANHO = 25


@pytest.fixture
def comissao_grande(gestor, processo_a, edital_a, etapa_a1, etapa_a2):
    membros = []
    for i in range(TAMANHO):
        membro, _ = adicionar_membro(
            actor=gestor,
            processo_id=processo_a.id,
            identity_subject=f"servidor{i:03d}",
            display_label=f"Servidor Sobrenome {i:03d}",
            funcao="PRESIDENTE" if i == 0 else "MEMBRO",
            idempotency_key=f"escala-membro-{i:03d}",
            correlation_id="escala",
        )
        membros.append(membro)
    for membro in membros:
        for etapa in (etapa_a1, etapa_a2):
            alocar(
                actor=gestor,
                processo_id=processo_a.id,
                membro_id=membro.id,
                edital_id=edital_a.id,
                etapa_id=etapa,
                idempotency_key=f"escala-aloc-{membro.id}-{etapa}",
                correlation_id="escala",
            )
    return membros


def test_a_comissao_e_lida_em_numero_constante_de_consultas(
    client, seletor_ligado, django_assert_max_num_queries, processo_a, comissao_grande
):
    """Se voltar a custar por membro, este teste é o que avisa."""
    identificar(client, "carlos", ["gestor"])

    with django_assert_max_num_queries(15):
        resposta = client.get(reverse("interface:comissao", args=[processo_a.id]))

    assert resposta.status_code == 200
    assert resposta.content.decode().count("Servidor Sobrenome") >= TAMANHO


def test_a_alocacao_e_lida_em_numero_constante_de_consultas(
    client, seletor_ligado, django_assert_max_num_queries, processo_a, comissao_grande
):
    identificar(client, "carlos", ["gestor"])

    with django_assert_max_num_queries(20):
        resposta = client.get(reverse("interface:alocacoes", args=[processo_a.id]))

    assert resposta.status_code == 200


def test_minhas_etapas_nao_custa_pelo_tamanho_da_comissao(
    client, seletor_ligado, django_assert_max_num_queries, comissao_grande
):
    """A área pessoal é de uma pessoa: o tamanho da banca não pode aparecer nela."""
    identificar(client, "servidor001", [])

    with django_assert_max_num_queries(10):
        resposta = client.get(reverse("interface:minhas-etapas"))

    assert resposta.status_code == 200
