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


def test_a_remocao_da_comissao_e_a_da_etapa_nao_se_confundem(
    client, seletor_ligado, gestor, processo_a, edital_a, comissao_de_a, etapa_a1
):
    """SC-UX-002 com a matriz: sair da comissão é um botão; sair de uma Etapa é desmarcar."""
    from tests.fixtures.comissao import alocar_em

    alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)
    identificar(client, "carlos", ["gestor"])

    da_comissao = client.get(url(processo_a)).content.decode()
    distribuicao = client.get(
        reverse("interface:alocacoes", args=[processo_a.id])
    ).content.decode()

    assert 'aria-label="Remover joao da comissão"' in da_comissao
    assert "Remover da comissão" not in distribuicao
    assert 'aria-label="joao em Análise documental' in distribuicao


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


def test_alteracao_bem_sucedida_produz_aviso_perceptivel(client, seletor_ligado, processo_a):
    """UX-006: sem o sinal, a única evidência de que deu certo é a lista ter mudado."""
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
        follow=True,
    )

    corpo = resposta.content.decode()
    assert "Membro incluído na comissão" in corpo
    assert 'role="status"' in corpo


def test_distribuicao_salva_produz_aviso_perceptivel(
    client, seletor_ligado, processo_a, edital_a, comissao_de_a, etapa_a1
):
    identificar(client, "carlos", ["gestor"])

    resposta = client.post(
        reverse("interface:alocacoes", args=[processo_a.id]),
        {
            "acao": "distribuir",
            "escopo_membro": [str(m.id) for m in comissao_de_a.values()],
            "escopo_etapa": [f"{edital_a.id}:{etapa_a1}"],
            "celula": [f"{edital_a.id}:{etapa_a1}:{comissao_de_a['joao'].id}"],
            "chave_idempotencia": "interface-distribuir-sucesso-0001",
        },
        follow=True,
    )

    assert "Distribuição salva" in resposta.content.decode()


def test_formulario_sem_o_campo_funcao_nao_rebaixa_ninguem(
    client, seletor_ligado, processo_a, comissao_de_a
):
    """"Não informado" e "informado como MEMBRO" são coisas diferentes.

    Um formulário truncado — cliente próprio, campo renomeado num refactor — não pode rebaixar
    a presidente por omissão.
    """
    identificar(client, "carlos", ["gestor"])

    client.post(
        url(processo_a),
        {"acao": "alterar_funcao", "membro_id": str(comissao_de_a["maria"].id)},
    )

    comissao_de_a["maria"].refresh_from_db()
    assert comissao_de_a["maria"].funcao == "PRESIDENTE"
