"""O resultado dentro da própria Inscrição — o gate de produto da feature (US3).

**A prova está na ordem inversa**, e é o primeiro teste: o mesmo acompanhamento, antes de publicar,
não menciona resultado por caminho nenhum. Sem ele, "aparece depois de publicar" não distinguiria a
feature de uma tela que sempre mostrou alguma coisa.
"""

import re

import pytest
from django.urls import reverse

from tests.fixtures.divulgacao import (
    emitir,
    entrar_como_titular,
    montar_ato_publicavel,
    pontuar,
    publicar_o_ato,
)

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

# O que a tela diz quando há resultado. Se alguma destas frases aparecer antes de publicar, a
# ausência da I-004 deixou de valer.
MARCAS_DE_RESULTADO = (
    "Classificação por lista",
    "lugar",
    "Resultado preliminar",
    "Resultado definitivo",
)


@pytest.fixture
def cenario(gestor, api_client, manager_headers, process_payload):
    """Duas classificadas e uma considerada sem posição — as três situações da spec."""
    return montar_ato_publicavel(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=60,
        codigo="0760",
        pontuacoes=("90.0000", "70.0000", None),
        primeiro=901,
    )


def abrir(client, inscricao):
    """O conteúdo do acompanhamento, **pela titular** — a identidade é a da própria inscrição.

    Devolve só o `<main>`: o cabeçalho do portal traz o nome de quem está identificado e a folha de
    estilo traz prosa, e uma asserção sobre o documento inteiro casaria com os dois sem que a tela
    tivesse dito nada.
    """
    entrar_como_titular(client, inscricao)
    resposta = client.get(reverse("portal:acompanhamento", args=[inscricao.id]))
    return _conteudo(resposta)


def _conteudo(resposta):
    corpo = resposta.content.decode()
    return re.search(r"<main[^>]*>(.*)</main>", corpo, re.DOTALL).group(1)


def cartoes(corpo):
    """Os cartões da classificação por lista (063, FR-1181), cada um com o seu texto.

    As asserções sobre o resultado divulgado leem **o cartão**, e não a página: desde a 063 o topo
    também cita a lista, o marco e a posição no porquê, e uma contagem sobre a página inteira
    contaria as duas menções do mesmo ato.
    """
    return re.findall(r'<section class="cartao-de-lista".*?</section>', corpo, re.DOTALL)


def test_sem_publicacao_o_acompanhamento_nao_menciona_resultado(client, cenario):
    """SC-008: o ato **está emitido** e mesmo assim nada aparece — divulgar é outro ato (FR-056).

    É este teste que dá sentido ao seguinte. Emitir a ordem não informa ninguém; a informação nasce
    da divulgação, e antes dela a tela não pode antecipá-la.
    """
    corpo = abrir(client, cenario["inscricoes"][0])

    for marca in MARCAS_DE_RESULTADO:
        assert marca not in corpo, (
            f"a tela mencionou resultado antes de existir divulgação: {marca}"
        )


def test_a_classificada_ve_natureza_posicao_pontuacao_e_o_caminho(client, cenario):
    """SC-009: o que a pessoa foi buscar, dentro da inscrição dela."""
    publicacao = publicar_o_ato(cenario, chave="publicar-0760")
    primeira = cenario["inscricoes"][0]

    corpo = abrir(client, primeira)

    assert "Classificação por lista" in corpo
    [cartao] = cartoes(corpo)
    assert "Ampla concorrência — Classificação final" in cartao, (
        "o cartão é nomeado pela lista e pelo marco (FR-057, FR-1181)"
    )
    assert "Resultado preliminar" in cartao
    assert "1º lugar" in cartao
    assert "pontuação 90,00" in cartao, (
        "a pontuação é rotulada: ela chega como texto já formatado, e `pluralize` sobre texto "
        "daria 'ponto' para qualquer valor"
    )
    assert "90,00 ponto" not in corpo
    assert reverse("portal:resultado", args=[publicacao.id]) in cartao


def test_a_nao_classificada_ve_a_propria_situacao_e_o_motivo(client, cenario):
    """SC-020: informada na Área, e **não** nomeada na lista pública (FR-017, FR-059)."""
    publicacao = publicar_o_ato(cenario, chave="publicar-0760-b")
    sem_posicao = cenario["inscricoes"][2]

    corpo = abrir(client, sem_posicao)

    [cartao] = cartoes(corpo)
    assert "Sem posição nesta lista" in cartao, "a ausência de posição é da lista (FR-1182)"
    assert "Classificação final" in cartao

    # A página pública, por **outro** cliente: com a sessão da candidata aberta, o cabeçalho do
    # portal traz o nome dela em toda página, e a asserção casaria com o cabeçalho em vez de com a
    # lista. Público quer dizer sem sessão nenhuma.
    from django.test import Client

    publica = _conteudo(Client().get(reverse("portal:resultado", args=[publicacao.id])))
    assert sem_posicao.nome not in publica
    assert sem_posicao.protocolo not in publica


def test_o_caminho_leva_sempre_a_publicacao_vigente(client, cenario, gestor):
    """FR-061: publicada a segunda, a Área aponta para ela — e não para a que foi sucedida."""
    primeira = publicar_o_ato(cenario, chave="publicar-0760-p1")
    segunda = publicar_o_ato(cenario, chave="publicar-0760-p2", natureza="DEFINITIVA")

    corpo = abrir(client, cenario["inscricoes"][0])

    assert reverse("portal:resultado", args=[segunda.id]) in corpo
    assert reverse("portal:resultado", args=[primeira.id]) not in corpo
    [cartao] = cartoes(corpo)
    assert "Resultado definitivo" in cartao
    assert "Resultado preliminar" not in corpo, (
        "um cartão por lista e marco, e não um por publicação: a sucedida não aparece"
    )


def test_os_dois_marcos_aparecem_na_ordem_normativa_e_nao_na_de_publicacao(
    gestor, api_client, manager_headers, process_payload, client
):
    """SC-022: dois marcos divulgados, **o final primeiro** — e os dois aparecem, na ordem certa.

    A ordem é a de `marco_codigo`, congelado em cada publicação: é a ordem em que os marcos se
    sucedem no certame, e não a ordem em que a instituição os divulgou. Publicar o final antes do
    intermediário é possível, e a Área não deve inverter a sequência do certame por causa disso.

    Nenhum dos dois é escolhido em lugar do outro: cada um é ato pleno, e decidir qual interessa à
    pessoa não é do sistema (FR-057, FR-058).
    """
    from tests.fixtures.divulgacao import montar_marco

    cenario = montar_marco(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=61,
        codigo="0761",
        com_intermediario=True,
    )
    inscricoes = pontuar(cenario, gestor, ["90.0000", "70.0000"], primeiro=951, sufixo="61")
    cenario["inscricoes"] = inscricoes
    # A primeira Etapa também é consolidada, para que o marco intermediário tenha universo.
    pontuar(
        cenario,
        gestor,
        [],
        primeiro=999,
        etapa=cenario["primeira"],
        sufixo="61-vazio",
    )
    _consolidar_a_primeira(cenario, gestor, inscricoes)

    final = emitir(cenario, gestor, marco=cenario["marco"], chave="emitir-0761-final")
    intermediario = emitir(
        cenario,
        gestor,
        marco=cenario["marco_intermediario"],
        chave="emitir-0761-inter",
    )
    # **O final primeiro**, em ordem temporal inversa à normativa.
    publicar_o_ato(cenario, chave="publicar-0761-final", ato=final)
    publicar_o_ato(cenario, chave="publicar-0761-inter", ato=intermediario)

    corpo = abrir(client, inscricoes[0])

    titulos = [re.search(r"<h3[^>]*>(.*?)</h3>", cartao).group(1) for cartao in cartoes(corpo)]
    assert len(titulos) == 2
    assert "Classificação da análise documental" in titulos[0]
    assert "Classificação final" in titulos[1], (
        "a ordem é a normativa (`marco_codigo`), e não a ordem em que se publicou"
    )


def _consolidar_a_primeira(cenario, gestor, inscricoes):
    """As mesmas inscrições, agora com Resultado também na primeira Etapa."""
    from processo_seletivo.resultados.application.consolidacao import consolidar
    from tests.fixtures.mesa import concluir_como, distribuir_para

    anterior = cenario["etapa"]
    cenario["etapa"] = cenario["primeira"]
    distribuir_para(cenario, gestor, ["joao"], inscricoes, chave="lote-0761-primeira")
    for indice, inscricao in enumerate(inscricoes):
        concluir_como(cenario, "joao", inscricao, pontuacao=f"{80 - indice * 10}.0000")
    consolidar(
        actor=gestor,
        processo_id=cenario["edital"].processo_id,
        edital_id=cenario["edital"].id,
        etapa_id=cenario["primeira"],
        inscricao_ids=[item.id for item in inscricoes],
        idempotency_key="consolidar-0761-primeira",
        correlation_id="fixture",
    )
    cenario["etapa"] = anterior


def test_o_bloco_do_resultado_nao_entra_na_lista_de_fatos_da_participacao(client, cenario):
    """FR-060: `_fatos_da_participacao` descreve o que **a pessoa fez**; divulgar é ato de terceiro.

    Misturá-los devolveria à tela a confusão que a 010 passou uma feature inteira desfazendo — a
    lista pessoal afirmando coisas que ninguém fez.
    """
    publicar_o_ato(cenario, chave="publicar-0760-c")
    corpo = abrir(client, cenario["inscricoes"][0])

    pessoal = re.search(r'class="linha-do-tempo pessoal"(.*?)</ul>', corpo, re.DOTALL).group(1)
    assert "lugar" not in pessoal
    assert "Resultado preliminar" not in pessoal
