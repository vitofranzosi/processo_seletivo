"""T048 — o percurso da seção 49 da spec, ponta a ponta, com dois atores.

Gestor constitui → designa presidente → aloca → o membro entra e vê → quem não foi alocado não
acessa. E a última parte é metade da entrega: um percurso feliz sem os 404 não demonstra o
contrato arquitetural da 011.
"""

import pytest
from django.test import Client
from django.urls import reverse

from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.acceptance]


def test_o_percurso_completo_da_organizacao_do_trabalho(
    client, seletor_ligado, processo_a, edital_a, edital_b, etapa_a1, etapa_a2, etapa_b1
):
    # --- O gestor constitui a comissão ---------------------------------------------------
    identificar(client, "carlos", ["gestor"])
    comissao = reverse("interface:comissao", args=[processo_a.id])

    for subject, funcao in (("maria", "PRESIDENTE"), ("joao", "MEMBRO")):
        conferencia = client.post(
            comissao, {"acao": "incluir", "identity_subject": subject, "funcao": funcao}
        )
        assert conferencia.status_code == 200, "o primeiro envio confere, e não grava"
        chave = _chave(conferencia.content.decode())
        criado = client.post(
            comissao,
            {
                "acao": "incluir",
                "confirmado": "1",
                "identity_subject": subject,
                "funcao": funcao,
                "chave_idempotencia": chave,
            },
        )
        assert criado.status_code == 302

    # --- E aloca João à Etapa A1 ---------------------------------------------------------
    from processo_seletivo.comissoes.models import MembroComissao

    joao = MembroComissao.objects.get(processo=processo_a, identity_subject="joao")
    alocacoes = reverse("interface:alocacoes", args=[processo_a.id])
    resposta = client.post(
        alocacoes,
        {
            "acao": "incluir",
            "membro_id": str(joao.id),
            "edital_id": str(edital_a.id),
            "etapa_id": etapa_a1,
            "chave_idempotencia": "aceitacao-aloca-joao-0001",
        },
    )
    assert resposta.status_code == 302

    # --- João entra, e vê a Etapa dele ---------------------------------------------------
    do_joao = Client()
    identificar(do_joao, "joao", [])
    minhas = do_joao.get(reverse("interface:minhas-etapas")).content.decode()
    assert "Análise documental" in minhas
    assert "Prova didática" not in minhas

    assert (
        do_joao.get(reverse("interface:minha-etapa", args=[edital_a.id, etapa_a1])).status_code
        == 200
    )

    # --- E não acessa o que não é dele ---------------------------------------------------
    assert (
        do_joao.get(reverse("interface:minha-etapa", args=[edital_a.id, etapa_a2])).status_code
        == 404
    )
    assert (
        do_joao.get(reverse("interface:minha-etapa", args=[edital_b.id, etapa_b1])).status_code
        == 404
    )
    adulterada = reverse(
        "interface:minha-etapa", args=[edital_a.id, "00000000-0000-0000-0000-000000000999"]
    )
    assert do_joao.get(adulterada).status_code == 404

    # --- Nem administra o Processo -------------------------------------------------------
    assert do_joao.get(comissao).status_code == 404

    # --- Remover a alocação revoga o acesso, sem tocar em papel global -------------------
    from processo_seletivo.comissoes.models import AlocacaoEtapa

    alocacao = AlocacaoEtapa.objects.get(membro=joao, ativo=True)
    client.post(
        alocacoes,
        {
            "acao": "remover",
            "alocacao_id": str(alocacao.id),
            "chave_idempotencia": "aceitacao-remove-joao-0001",
        },
    )

    assert (
        do_joao.get(reverse("interface:minha-etapa", args=[edital_a.id, etapa_a1])).status_code
        == 404
    )
    depois = do_joao.get(reverse("interface:minhas-etapas")).content.decode()
    assert "Você não possui Etapas atribuídas" in depois


def _chave(corpo):
    import re

    achado = re.search(r'name="chave_idempotencia" value="([^"]+)"', corpo)
    assert achado, corpo[:400]
    return achado.group(1)
