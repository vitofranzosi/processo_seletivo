"""A matriz da distribuição: pessoas nas linhas, Etapas nas colunas.

A tela anterior era indexada por Etapa e repetia a lista inteira de avaliadores dentro de cada
uma — com cinquenta pessoas e quatro Etapas, duzentos rótulos para cinquenta nomes. Estes testes
preservam as garantias daquela tela e acrescentam a que ela não tinha: o estado inteiro visível.
"""

import pytest
from django.urls import reverse

from processo_seletivo.comissoes.models import AlocacaoEtapa
from tests.fixtures.comissao import alocar_em, constituir
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def url(processo):
    return reverse("interface:alocacoes", args=[processo.id])


def linha_de(corpo, subject):
    return corpo.split(f">{subject}<")[1].split("</tr>")[0]


def test_a_matriz_mostra_a_distribuicao_inteira_de_uma_vez(
    client, seletor_ligado, gestor, processo_a, edital_a, comissao_de_a, etapa_a1, etapa_a2
):
    """A pergunta que nenhuma tela respondia: esta é a distribuição?"""
    alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)
    identificar(client, "carlos", ["gestor"])

    corpo = client.get(url(processo_a)).content.decode()

    assert "Análise documental" in corpo and "Prova didática" in corpo
    assert corpo.count('name="celula"') == 4  # duas pessoas × duas Etapas
    marcada = f'value="{edital_a.id}:{etapa_a1}:{comissao_de_a["joao"].id}"'
    vazia = f'value="{edital_a.id}:{etapa_a2}:{comissao_de_a["joao"].id}"'
    assert "checked" in corpo.split(marcada)[1].split(">")[0]
    assert "checked" not in corpo.split(vazia)[1].split(">")[0]


def test_a_etapa_sem_ninguem_e_identificavel_sem_depender_de_cor(
    client, seletor_ligado, gestor, processo_a, edital_a, comissao_de_a, etapa_a1
):
    alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)
    identificar(client, "carlos", ["gestor"])

    corpo = client.get(url(processo_a)).content.decode()

    assert "sem ninguém" in corpo


def test_salvar_a_matriz_cria_e_remove_no_mesmo_ato(
    client, seletor_ligado, gestor, processo_a, edital_a, comissao_de_a, etapa_a1, etapa_a2
):
    """A distribuição é um desenho, não uma sequência de inclusões e remoções."""
    alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)
    identificar(client, "carlos", ["gestor"])
    maria, joao = comissao_de_a["maria"], comissao_de_a["joao"]

    client.post(
        url(processo_a),
        {
            "acao": "distribuir",
            "escopo_membro": [str(maria.id), str(joao.id)],
            "escopo_etapa": [f"{edital_a.id}:{etapa_a1}", f"{edital_a.id}:{etapa_a2}"],
            # João sai de A1 e entra em A2; Maria entra em A1.
            "celula": [
                f"{edital_a.id}:{etapa_a2}:{joao.id}",
                f"{edital_a.id}:{etapa_a1}:{maria.id}",
            ],
            "chave_idempotencia": "matriz-salvar-0001",
        },
        follow=True,
    )

    ativas = {(str(a.etapa_id), a.membro_id) for a in AlocacaoEtapa.objects.filter(ativo=True)}
    assert ativas == {(etapa_a2, joao.id), (etapa_a1, maria.id)}


def test_a_busca_nao_apaga_quem_ficou_fora_da_tela(
    client, seletor_ligado, gestor, processo_a, edital_a, comissao_de_a, etapa_a1
):
    """A armadilha da matriz filtrada: sem escopo declarado, salvar removeria os escondidos."""
    maria, joao = comissao_de_a["maria"], comissao_de_a["joao"]
    alocar_em(gestor, processo_a, maria, edital_a, etapa_a1)
    alocar_em(gestor, processo_a, joao, edital_a, etapa_a1)
    identificar(client, "carlos", ["gestor"])

    # A tela filtrada por "joao" desenha só ele — e é só ele que o envio pode afetar.
    client.post(
        url(processo_a),
        {
            "acao": "distribuir",
            "escopo_membro": [str(joao.id)],
            "escopo_etapa": [f"{edital_a.id}:{etapa_a1}"],
            "celula": [],
            "q": "joao",
            "chave_idempotencia": "matriz-filtrada-0001",
        },
        follow=True,
    )

    assert not AlocacaoEtapa.objects.filter(membro=joao, ativo=True).exists()
    assert AlocacaoEtapa.objects.filter(membro=maria, ativo=True).exists()


def test_a_tela_avisa_que_o_filtro_limita_o_que_sera_salvo(
    client, seletor_ligado, processo_a, comissao_de_a
):
    identificar(client, "carlos", ["gestor"])

    corpo = client.get(url(processo_a) + "?q=joao").content.decode()

    assert "salvar altera" in corpo
    assert "apenas quem está listado" in corpo


def test_a_coluna_inteira_e_um_clique_e_o_inverso_tambem(
    client, seletor_ligado, processo_a, edital_a, comissao_de_a, etapa_a1
):
    """Pôr a banca toda numa etapa documental não pode custar cinquenta caixas."""
    identificar(client, "carlos", ["gestor"])
    escopo = {
        "acao": "distribuir",
        "escopo_membro": [str(m.id) for m in comissao_de_a.values()],
        "escopo_etapa": [f"{edital_a.id}:{etapa_a1}"],
        "celula": [],
    }

    client.post(
        url(processo_a),
        {**escopo, "coluna_todos": f"{edital_a.id}:{etapa_a1}", "chave_idempotencia": "col-1"},
        follow=True,
    )
    assert AlocacaoEtapa.objects.filter(ativo=True, etapa_id=etapa_a1).count() == 2

    marcadas = [f"{edital_a.id}:{etapa_a1}:{m.id}" for m in comissao_de_a.values()]
    client.post(
        url(processo_a),
        {
            **escopo,
            "celula": marcadas,
            "coluna_nenhum": f"{edital_a.id}:{etapa_a1}",
            "chave_idempotencia": "col-2",
        },
        follow=True,
    )
    assert AlocacaoEtapa.objects.filter(ativo=True, etapa_id=etapa_a1).count() == 0


def test_comissao_sem_presidente_nao_deixa_distribuir(client, seletor_ligado, gestor, processo_a):
    constituir(gestor, processo_a, [("joao", "MEMBRO")])
    identificar(client, "carlos", ["gestor"])

    corpo = client.get(url(processo_a)).content.decode()

    assert "Designe a presidência antes de distribuir" in corpo
    assert "Salvar distribuição" not in corpo
    assert "disabled" in corpo


def test_edital_nao_publicado_diz_por_que_nao_ha_o_que_distribuir(
    client, seletor_ligado, api_client, manager_headers, processo_a, comissao_de_a
):
    api_client.post(
        f"/api/v1/admin/processos/{processo_a.id}/editais",
        {"number": "88", "year": 2026, "title": "Em elaboração"},
        format="json",
        **{**manager_headers, "HTTP_IDEMPOTENCY_KEY": "interface-edital-88-0001"},
    )
    identificar(client, "carlos", ["gestor"])

    corpo = client.get(url(processo_a)).content.decode()

    assert "não publicado" in corpo


def test_processo_sem_edital_publicado_tem_estado_vazio_proprio(
    client, seletor_ligado, api_client, manager_headers, processo_a
):
    from tests.fixtures.edital import complete_draft
    from tests.fixtures.publicacao import publish_original

    outro = publish_original(
        api_client,
        {**manager_headers, "HTTP_IDEMPOTENCY_KEY": "interface-sem-etapas-0001"},
        {
            "institutionalCode": "PS-2026-777",
            "title": "Sem Etapas",
            "firstEdital": {"number": "77", "year": 2026, "title": "Sem Etapas"},
        },
        draft=complete_draft(2),
    )
    identificar(client, "carlos", ["gestor"])

    corpo = client.get(url(outro.processo)).content.decode()

    assert "Nenhum Edital declara Etapas de Avaliação" in corpo


def test_cada_celula_diz_de_quem_e_de_qual_etapa(
    client, seletor_ligado, processo_a, edital_a, comissao_de_a, etapa_a1
):
    """Duzentas caixas idênticas seriam ilegíveis por leitor de tela."""
    identificar(client, "carlos", ["gestor"])

    corpo = client.get(url(processo_a)).content.decode()

    assert 'aria-label="joao em Análise documental' in corpo
    assert 'aria-label="maria em Prova didática' in corpo
