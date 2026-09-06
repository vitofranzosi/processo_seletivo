"""Apoio comum às telas: identidade e o seletor que substitui a autenticação institucional."""

import re

import pytest
from django.urls import reverse


def identificar(client, subject, papeis, escopo=None):
    """Identidade institucional pela própria tela.

    `escopo` existe para os testes de isolamento: o seletor não o oferece — ele identifica sempre
    no escopo padrão —, e forçá-lo aqui é o que permite exercitar o que acontece quando o ator é
    de outra unidade.
    """
    resposta = client.post(reverse("interface:identificar"), {"subject": subject, "papeis": papeis})
    assert resposta.status_code == 302, resposta.content
    if escopo is not None:
        from processo_seletivo.interface.identidade import CHAVE_SESSAO

        sessao = client.session
        sessao[CHAVE_SESSAO] = {**sessao[CHAVE_SESSAO], "escopo": escopo}
        sessao.save()
    return resposta


@pytest.fixture
def seletor_ligado(settings):
    settings.INTERFACE_SELETOR_IDENTIDADE = True


def compor_rascunho(client, edital, perfis=None, eventos=None):
    """Percorre o assistente: Perfis e Cronograma são etapas distintas, salvas em separado."""
    from django.urls import reverse

    if perfis is not None:
        resposta = client.post(
            reverse("interface:compor-etapa", args=[edital.id, "perfis"]), perfis
        )
        assert resposta.status_code == 302, resposta.content
    if eventos is not None:
        edital.refresh_from_db()
        resposta = client.post(
            reverse("interface:compor-etapa", args=[edital.id, "cronograma"]), eventos
        )
        assert resposta.status_code == 302, resposta.content
    return edital


# Ganchos, e não desenho: nomes que a marcação carrega para o JavaScript ou para as consultas dos
# testes acharem o elemento. A folha não decide nada sobre eles, e por isso a varredura de classes
# órfãs os dispensa — declarados aqui, um a um, para que a dispensa seja escolha e não descuido.
CLASSES_SEM_DESENHO = {
    "alvo",
    "base",
    "confirmacao",
    "conteudo-vigente",
    "etapa",
    "evento",
    "identidades",
    "modalidade",
    # O marco e o critério são ganchos pela mesma razão da modalidade: a linha é desenhada por
    # `.linha`, e o nome serve para achá-la em teste e para o htmx trocar a certa.
    "marco",
    "criterio",
    "fato",
    "pessoa",
    "quem",
    "secao",
    "tamanho",
    # A grade da lista de documentos posiciona por ordem, e não por nome: o `span` do requisito é
    # célula da grade do `ul`, e a classe serve para achá-lo em teste.
    "requisito",
    # `.linha` já desenha o bloco; o sufixo marca **qual** foi acrescentado agora no formulário de
    # Retificação, e hoje não carrega desenho próprio nem é lido por script algum.
    "evento-novo",
    "perfil-novo",
    "perfil",
    # Envolve um `.botao`, que é quem tem o peso; a classe nomeia o lugar, não o desenho.
    "proximo-passo",
    # --- portal ---
    # O par de `.linha-do-tempo.pessoal`: aquela é a exceção e tem regra; esta é a linha comum, e
    # o nome existe para dizer qual é qual na marcação.
    "processo",
    # Nomeia **qual** `.sub` é esta — a notícia de que o código foi enviado. O desenho é o de
    # `.sub`; se um dia a notícia precisar de mais peso, é aqui que ela ganha.
    "aviso-do-envio",
}


# --- leitura das listagens ---------------------------------------------------------------------

_LINHA = re.compile(r"<tr[^>]*>(.*?)</tr>", re.DOTALL)
_CELULA = re.compile(r"<td[^>]*>(.*?)</td>", re.DOTALL)
_MARCACAO = re.compile(r"<[^>]+>")


def protocolos_listados(corpo):
    """Os protocolos que a tela **lista**, lidos das linhas da tabela.

    Protocolo é número curto e preenchido com zeros — `0740` —, e a página é cheia de UUID
    sorteado: o `id` de um membro da banca, de uma Atribuição, do Edital. Procurar `"0740"` no
    documento inteiro acha `bf107404-b1ad-…` e responde "está listada" sem que linha alguma
    exista. Foi assim que o filtro de avaliação pendente falhou num CI que não tocava em
    distribuição — e passou, no mesmo commit, no `push` que sorteou outros UUID.

    A coluna que identifica a linha é a primeira que tem texto: nas telas de distribuição a
    primeira célula carrega só a caixa de seleção. Lendo dali, tanto o "está" quanto o "não está"
    dizem o que o teste quer dizer.
    """
    listados = []
    for linha in _LINHA.findall(corpo):
        celulas = (_MARCACAO.sub("", celula).strip() for celula in _CELULA.findall(linha))
        identificador = next((texto for texto in celulas if texto), None)
        if identificador is not None:
            listados.append(identificador)
    return listados
