"""T028, T028a e T060 — a tela da Comissão: conferência antes de gravar, e rótulos distinguíveis."""

import pytest
from django.urls import reverse

from processo_seletivo.comissoes.models import MembroComissao
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def url(processo):
    return reverse("interface:comissao", args=[processo.id])


def test_a_tela_lista_a_composicao(client, seletor_ligado, processo_a, comissao_de_a):
    identificar(client, "carlos", ["gestor"])

    corpo = client.get(url(processo_a)).content.decode()

    assert "maria" in corpo and "joao" in corpo
    assert "Presidente" in corpo


def test_a_tela_avisa_que_o_identificador_nao_e_verificado(client, seletor_ligado, processo_a):
    """FR-020: sem diretório, a interface não pode fingir que confere."""
    identificar(client, "carlos", ["gestor"])

    corpo = client.get(url(processo_a)).content.decode()

    assert "não é verificado pelo sistema" in corpo


def test_o_primeiro_envio_nao_grava_e_devolve_a_conferencia(client, seletor_ligado, processo_a):
    """FR-022: o erro de digitação precisa aparecer antes da gravação, e não depois."""
    identificar(client, "carlos", ["gestor"])

    resposta = client.post(
        url(processo_a),
        {"acao": "incluir", "identity_subject": "joao.silva", "funcao": "MEMBRO"},
    )

    assert resposta.status_code == 200
    corpo = resposta.content.decode()
    assert "joao.silva" in corpo and "Confirmar inclusão" in corpo
    assert MembroComissao.objects.count() == 0


def test_so_o_segundo_envio_cria_o_membro(client, seletor_ligado, processo_a):
    identificar(client, "carlos", ["gestor"])
    primeiro = client.post(
        url(processo_a),
        {"acao": "incluir", "identity_subject": "joao.silva", "funcao": "MEMBRO"},
    )
    chave = _chave(primeiro.content.decode())

    resposta = client.post(
        url(processo_a),
        {
            "acao": "incluir",
            "confirmado": "1",
            "identity_subject": "joao.silva",
            "funcao": "MEMBRO",
            "chave_idempotencia": chave,
        },
    )

    assert resposta.status_code == 302
    assert MembroComissao.objects.filter(identity_subject="joao.silva", ativo=True).count() == 1


def test_as_duas_remocoes_tem_nomes_acessiveis_distintos(
    client, seletor_ligado, gestor, processo_a, edital_a, comissao_de_a, etapa_a1
):
    """SC-UX-002 e FR-077: "da comissão" e "desta Etapa" não podem se confundir."""
    from tests.fixtures.comissao import alocar_em

    alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)
    identificar(client, "carlos", ["gestor"])

    da_comissao = client.get(url(processo_a)).content.decode()
    da_etapa = client.get(reverse("interface:alocacoes", args=[processo_a.id])).content.decode()

    assert "Remover da comissão" in da_comissao
    assert "Remover desta Etapa" not in da_comissao
    assert "Remover desta Etapa" in da_etapa


def test_a_tela_mostra_as_etapas_de_cada_membro(
    client, seletor_ligado, gestor, processo_a, edital_a, comissao_de_a, etapa_a1
):
    """FR-040: dá para ver a distribuição a partir da pessoa, e não só a partir da Etapa."""
    from tests.fixtures.comissao import alocar_em

    alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)
    identificar(client, "carlos", ["gestor"])

    corpo = client.get(url(processo_a)).content.decode()

    assert "Análise documental" in corpo
    assert "Atua em:" in corpo


def _chave(corpo):
    import re

    achado = re.search(r'name="chave_idempotencia" value="([^"]+)"', corpo)
    assert achado, corpo[:400]
    return achado.group(1)
