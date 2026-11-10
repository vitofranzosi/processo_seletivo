"""Depois do ato, a tela diz o próximo passo da lista (127, US6, FR-4090 a FR-4092, SC-1238).

A transição confirmava e não conduzia (`J-08` do estudo): depois de emitir o corte, o botão de maior
peso era outro "Emitir corte". O "Próximo nesta lista" sai da mesma derivação do detalhe do Edital,
e só aparece no retorno de um ato — abrir a tela não o mostra, nem paga a derivação.

O resultado do ato é posto na sessão como a view o põe depois do POST: o que se prova aqui é o GET
que mostra a mensagem, e não o comando, que tem os testes dele.
"""

import pytest
from django.urls import reverse

from processo_seletivo.interface import andamento as a
from tests.fixtures.convocacao import convocar, montar_cenario_da_convocacao
from tests.fixtures.corte import MARCO, emitir, montar_cenario_do_corte
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

PROXIMO = '<p class="proximo-nesta-lista">'


def com_resultado(client, chave, valor, **extra):
    sessao = client.session
    sessao[chave] = valor
    for nome, conteudo in extra.items():
        sessao[nome] = conteudo
    sessao.save()


def test_depois_do_corte_o_proximo_e_a_etapa_governada_e_nao_outro_corte(
    client, gestor, api_client, manager_headers, process_payload, seletor_ligado
):
    """SC-1238: no P2, depois do corte vem a Etapa que a faixa governa, antes da apuração."""
    edital, _, _ = montar_cenario_do_corte(
        gestor, api_client, manager_headers, process_payload, prefixo="transicao-127-corte"
    )
    resultado = emitir(edital, gestor, chave="transicao-127-corte")
    identificar(client, "carlos", ["gestor"])
    com_resultado(client, "resultado_do_corte", {"emitido": True, **(resultado or {})})

    corpo = client.get(reverse("interface:corte", args=[edital.id, MARCO])).content.decode()

    assert PROXIMO in corpo
    proximo = corpo.split(PROXIMO, 1)[1].split("</p>", 1)[0]
    assert "Distribuir" in proximo and "/distribuicao/" in proximo, proximo


def test_abrir_a_tela_nao_mostra_o_proximo(
    client, gestor, api_client, manager_headers, process_payload, seletor_ligado
):
    """FR-4090: só no retorno de um ato."""
    edital, _, _ = montar_cenario_do_corte(
        gestor, api_client, manager_headers, process_payload, prefixo="transicao-127-abrir"
    )
    identificar(client, "carlos", ["gestor"])
    corpo = client.get(reverse("interface:corte", args=[edital.id, MARCO])).content.decode()
    assert PROXIMO not in corpo


def test_depois_de_convocar_o_proximo_e_da_mesma_lista(
    client, gestor, api_client, manager_headers, process_payload, seletor_ligado
):
    """SC-1236, SC-1238: a convocação sem comunicação passa a ser a providência da lista."""
    edital, _, inscricoes = montar_cenario_da_convocacao(
        gestor, api_client, manager_headers, process_payload, prefixo="transicao-127-conv"
    )
    convocar(edital, gestor, inscricoes[0], idempotency_key="transicao-127-conv")
    identificar(client, "carlos", ["gestor"])
    com_resultado(
        client, "resultado_da_convocacao", {"protocolo": "x"}, acao_da_convocacao="convocacao"
    )

    corpo = client.get(reverse("interface:convocacao", args=[edital.id, MARCO])).content.decode()

    proximo = corpo.split(PROXIMO, 1)[1].split("</p>", 1)[0]
    assert "<strong>Próximo nesta lista:</strong>" in proximo
    assert "/convocacao" in proximo, proximo


def test_depois_da_ordem_o_proximo_aparece_na_ordenacao(
    client, gestor, api_client, manager_headers, process_payload, seletor_ligado
):
    """Item 6 do code review: as seis telas, e não só corte e convocação."""
    from tests.fixtures.recortes import montar_cenario_7_1_2

    edital, _, _ = montar_cenario_7_1_2(
        gestor, api_client, manager_headers, process_payload, prefixo="transicao-127-ordem"
    )
    identificar(client, "carlos", ["gestor"])
    com_resultado(client, "resultado_da_ordenacao", {"comPosicao": 5, "semPosicao": 1})
    corpo = client.get(reverse("interface:ordenacao", args=[edital.id, MARCO])).content.decode()
    assert PROXIMO in corpo


def test_depois_da_apuracao_o_proximo_aparece_na_ocupacao(
    client, gestor, api_client, manager_headers, process_payload, seletor_ligado
):
    edital, _, _ = montar_cenario_da_convocacao(
        gestor, api_client, manager_headers, process_payload, prefixo="transicao-127-ocup"
    )
    identificar(client, "carlos", ["gestor"])
    com_resultado(client, "resultado_da_ocupacao", {"listaId": None, "efetivas": 2})
    corpo = client.get(reverse("interface:ocupacao", args=[edital.id, MARCO])).content.decode()
    proximo = corpo.split(PROXIMO, 1)[1].split("</p>", 1)[0]
    assert "Convocar" in proximo, proximo


def test_depois_de_congelar_o_proximo_aparece_no_sorteio(
    client, gestor, api_client, manager_headers, process_payload, seletor_ligado
):
    from tests.fixtures.sorteio import certame_de_sorteio

    certame = certame_de_sorteio(gestor, api_client, manager_headers, process_payload)
    identificar(client, "carlos", ["gestor"])
    com_resultado(
        client,
        "resultado_do_sorteio",
        {"tipo": "relacao", "listaId": "", "quantidade": 3, "resumo": "x", "advertencias": []},
    )
    corpo = client.get(
        reverse("interface:sorteio", args=[certame["edital"].id, certame["marco"]])
    ).content.decode()
    assert PROXIMO in corpo


def test_sem_nada_em_aberto_a_lista_diz_isso():
    """FR-4091: não inventa passo."""
    marco = {"id": "m", "name": "Final", "orderProduction": "POR_PONTUACAO", "stages": []}
    pontos = a._pontos_do_marco(marco)
    for ponto in pontos:
        ponto.celulas = {"": a.Celula(a.FEITO)}
    perfil = a.PerfilNoAndamento(
        perfil={}, forma="", listas=[(None, "Ampla")], pontos=pontos, inscritos=1
    )
    andamento = a.Andamento(perfis=[perfil], providencias=[], atencoes=[], inscricoes={})
    desta, outras, _ = a.da_lista(andamento, "m", None)
    assert desta is None and outras == []


# --- a volta ao Centro e o próximo que chega ao ato (139) --------------------------------------

RETORNO = '<p class="retorno-ao-centro">'


def test_depois_do_ato_o_bloco_termina_no_centro_e_abrir_a_tela_nao_o_mostra(
    client, gestor, api_client, manager_headers, process_payload, seletor_ligado
):
    """FR-4768, SC-1492: um clique de volta ao Centro, e só depois de um ato."""
    edital, _, _ = montar_cenario_do_corte(
        gestor, api_client, manager_headers, process_payload, prefixo="transicao-139-retorno"
    )
    identificar(client, "carlos", ["gestor"])
    url = reverse("interface:corte", args=[edital.id, MARCO])
    assert RETORNO not in client.get(url).content.decode()

    resultado = emitir(edital, gestor, chave="transicao-139-retorno")
    com_resultado(client, "resultado_do_corte", {"emitido": True, **(resultado or {})})
    corpo = client.get(url).content.decode()

    centro = reverse("interface:detalhe", args=[edital.id])
    retorno = corpo.split(RETORNO, 1)[1].split("</p>", 1)[0]
    assert f'<a href="{centro}">Voltar ao Centro de Controle do Edital</a>' in retorno
    # O retorno fecha o bloco: vem depois do próximo, e não antes.
    assert corpo.index(PROXIMO) < corpo.index(RETORNO)
    assert client.get(centro).status_code == 200


def test_depois_de_convocar_o_proximo_leva_a_secao_das_pendentes(
    client, gestor, api_client, manager_headers, process_payload, seletor_ligado
):
    """FR-4765: a providência que nasce do ato leva à seção dela na mesma tela, que está lá."""
    edital, _, inscricoes = montar_cenario_da_convocacao(
        gestor, api_client, manager_headers, process_payload, prefixo="transicao-139-conv"
    )
    convocar(edital, gestor, inscricoes[0], idempotency_key="transicao-139-conv")
    identificar(client, "carlos", ["gestor"])
    com_resultado(
        client, "resultado_da_convocacao", {"protocolo": "x"}, acao_da_convocacao="convocacao"
    )

    corpo = client.get(reverse("interface:convocacao", args=[edital.id, MARCO])).content.decode()

    proximo = corpo.split(PROXIMO, 1)[1].split("</p>", 1)[0]
    assert "#pendentes" in proximo, proximo
    assert 'id="pendentes"' in corpo
