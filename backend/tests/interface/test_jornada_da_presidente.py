"""A jornada de quem preside sem papel sistêmico — o ator central da 011.

Estes testes nasceram de um percurso manual: a presidente conseguia fazer tudo, e o sistema lhe
dizia que ela não podia nada. As telas herdadas decidiam por `ator.permissions`, e a base
contextual que a 011 criou não existia para elas.
"""

import pytest
from django.urls import reverse

from tests.fixtures.comissao import alocar_em
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


@pytest.fixture
def presidente(client, seletor_ligado, comissao_de_a):
    identificar(client, "maria", [])
    return client


def test_a_lista_nao_diz_que_a_presidente_nao_tem_papel(presidente, processo_a):
    """L1: "Sua conta não possui nenhum papel de responsabilidade" era falso para ela."""
    corpo = presidente.get(reverse("interface:lista")).content.decode()

    assert "Sem permissões" not in corpo
    assert "Você preside a comissão" in corpo


def test_a_lista_oferece_a_comissao_a_quem_a_integra(presidente, processo_a):
    corpo = presidente.get(reverse("interface:lista")).content.decode()

    assert reverse("interface:comissao", args=[processo_a.id]) in corpo


def test_quem_nao_tem_vinculo_continua_recebendo_a_orientacao(client, seletor_ligado, processo_a):
    """A garantia da 002 permanece para quem de fato não tem nada."""
    identificar(client, "servidor.novo", [])

    corpo = client.get(reverse("interface:lista")).content.decode()

    assert "Sem permissões" in corpo


def test_a_presidente_sem_alocacao_nao_e_mandada_pedir_acesso(presidente):
    """L2: ela já integra a comissão — mandá-la pedir para ser registrada é dizer o oposto."""
    corpo = presidente.get(reverse("interface:minhas-etapas")).content.decode()

    assert "não possui papel de responsabilidade nem atribuição" not in corpo
    assert "Comissões que você integra" in corpo


def test_minhas_etapas_leva_a_presidente_ate_a_comissao_dela(presidente, processo_a):
    """L3: o acesso existia; a rota não."""
    corpo = presidente.get(reverse("interface:minhas-etapas")).content.decode()

    assert reverse("interface:comissao", args=[processo_a.id]) in corpo
    assert reverse("interface:alocacoes", args=[processo_a.id]) in corpo


def test_quem_nao_tem_nada_continua_recebendo_a_orientacao_em_minhas_etapas(
    client, seletor_ligado
):
    identificar(client, "servidor.novo", [])

    corpo = client.get(reverse("interface:minhas-etapas")).content.decode()

    assert "não possui papel de responsabilidade nem atribuição" in corpo


def test_a_escolha_nao_oferece_quem_ja_esta_alocado(
    presidente, gestor, processo_a, edital_a, comissao_de_a, etapa_a1
):
    """L4: oferecer quem já está era a tela produzindo o próprio 409."""
    alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)

    corpo = presidente.get(
        reverse("interface:alocacoes", args=[processo_a.id])
    ).content.decode()

    bloco = corpo.split(f'value="{etapa_a1}"')[1].split("</form>")[0]
    assert f'value="{comissao_de_a["joao"].id}"' not in bloco
    assert f'value="{comissao_de_a["maria"].id}"' in bloco


def test_etapa_com_a_comissao_toda_alocada_diz_isso(
    presidente, gestor, processo_a, edital_a, comissao_de_a, etapa_a1
):
    for membro in comissao_de_a.values():
        alocar_em(gestor, processo_a, membro, edital_a, etapa_a1)

    corpo = presidente.get(
        reverse("interface:alocacoes", args=[processo_a.id])
    ).content.decode()

    assert "Toda a comissão já está alocada nesta Etapa" in corpo


def test_as_remocoes_dizem_de_quem_e_de_onde(
    presidente, gestor, processo_a, edital_a, comissao_de_a, etapa_a1
):
    """L5: quatro botões com o mesmo nome acessível são indistinguíveis por leitor de tela."""
    alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)

    alocacoes = presidente.get(
        reverse("interface:alocacoes", args=[processo_a.id])
    ).content.decode()
    comissao = presidente.get(
        reverse("interface:comissao", args=[processo_a.id])
    ).content.decode()

    assert 'aria-label="Remover joao da Etapa Análise documental"' in alocacoes
    assert 'aria-label="Remover joao da comissão"' in comissao


def test_a_confirmacao_de_atribuicao_nao_usa_estilo_de_alerta(
    client, seletor_ligado, gestor, processo_a, edital_a, comissao_de_a, etapa_a1
):
    """L8: a frase que confirma a atribuição parecia um problema a resolver."""
    alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)
    identificar(client, "joao", [])

    corpo = client.get(
        reverse("interface:atribuicao", args=[edital_a.id, etapa_a1])
    ).content.decode()

    trecho = corpo.split("Você está alocado nesta Etapa")[0][-120:]
    assert 'class="sucesso"' in trecho


def test_alocar_a_comissao_inteira_numa_submissao(
    presidente, processo_a, edital_a, comissao_de_a, etapa_a1
):
    """O item que corta 160 envios a 4: uma submissão, várias pessoas."""
    from processo_seletivo.comissoes.models import AlocacaoEtapa

    resposta = presidente.post(
        reverse("interface:alocacoes", args=[processo_a.id]),
        {
            "acao": "incluir",
            "edital_id": str(edital_a.id),
            "etapa_id": etapa_a1,
            "membro_id": [str(m.id) for m in comissao_de_a.values()],
            "chave_idempotencia": "interface-lote-0001",
        },
        follow=True,
    )

    assert resposta.status_code == 200
    assert AlocacaoEtapa.objects.filter(ativo=True).count() == 2


def test_a_alocacao_abre_com_o_resumo(presidente, processo_a, comissao_de_a):
    """Sem ele, a resposta que a tela existe para dar tem de ser contada nos cartões."""
    corpo = presidente.get(
        reverse("interface:alocacoes", args=[processo_a.id])
    ).content.decode()

    assert "Etapas com equipe" in corpo or "Etapa com equipe" in corpo
    assert "sem ninguém" in corpo
    assert "sem atribuição" in corpo


def test_a_comissao_pode_ser_filtrada_por_nome(presidente, processo_a, comissao_de_a):
    corpo = presidente.get(
        reverse("interface:comissao", args=[processo_a.id]) + "?q=joao"
    ).content.decode()

    assert "joao" in corpo
    assert "maria" not in corpo.split("Membros da comissão")[1].split("Adicionar membro")[0]


def test_a_comissao_pode_mostrar_so_quem_esta_sem_etapa(
    presidente, gestor, processo_a, edital_a, comissao_de_a, etapa_a1
):
    """A pergunta que o presidente faz de verdade numa banca grande."""
    alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)

    corpo = presidente.get(
        reverse("interface:comissao", args=[processo_a.id]) + "?sem_etapa=1"
    ).content.decode()

    lista = corpo.split("Membros da comissão")[1].split("Adicionar membro")[0]
    assert "maria" in lista
    assert "joao" not in lista


def test_a_trilha_filtra_por_pessoa_e_por_operacao(
    client, seletor_ligado, gestor, processo_a, edital_a, comissao_de_a, etapa_a1
):
    """19 páginas de vinte não respondem “quem perdeu acesso a esta Etapa”."""
    alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)
    identificar(client, "auditora", ["auditor"])
    url = reverse("interface:auditoria-comissao", args=[processo_a.id])

    def atos(corpo):
        # Só a lista: o seletor de filtro contém todos os rótulos, e procurá-los na página
        # inteira testaria o formulário em vez do filtro.
        return corpo.split('aria-label="Atos registrados"')[1]

    por_operacao = atos(client.get(url + "?operacao=ALOCACAO_INCLUIR").content.decode())
    por_pessoa = atos(client.get(url + "?pessoa=maria").content.decode())

    assert "Alocação em Etapa" in por_operacao
    assert "Inclusão na comissão" not in por_operacao
    assert "maria" in por_pessoa
    assert "joao" not in por_pessoa
