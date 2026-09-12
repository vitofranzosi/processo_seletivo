"""Apoio comum às telas: identidade, o seletor que substitui a autenticação institucional, e o
Edital em elaboração que mais de um teste do assistente precisa.

As duas fixtures do rascunho moraram em `test_compor_classificacao.py` enquanto só ele as usava.
Passaram para cá quando o assistente da janela recursal precisou do mesmo estado: importar fixture
de um módulo de teste para outro funciona, mas faz o parâmetro da função sombrear o nome importado —
e o mesmo estado passa a ter dois donos. Aqui ele não tem nenhum, que é o certo para apoio comum.
"""

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
    # `.linha` desenha o bloco; o sufixo marca **qual** foi acrescentado agora no formulário de
    # Retificação — e desde a divisão da tela em seções ele carrega a borda tracejada que separa a
    # proposta do conteúdo que já vige. Continua aqui porque também é o nome pelo qual o htmx
    # troca a linha certa e pelo qual os testes a encontram.
    "evento-novo",
    "perfil-novo",
    # O mesmo gancho, para o Anexo acrescentado por Retificação (020).
    "anexo-novo",
    # E para a linha do quadro de vagas acrescentada por Retificação (025).
    "linha-do-quadro-nova",
    # E para a linha do Anexo já existente, pela mesma razão que `evento` e `secao` estão aqui.
    "anexo",
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


ETAPA_CLASSIFICATORIA = "aaaaaaaa-0000-4000-8000-00000000e021"
ETAPA_SO_ELIMINATORIA = "aaaaaaaa-0000-4000-8000-00000000e023"
FATO_DO_DESEMPATE = "aaaaaaaa-0000-4000-8000-00000000e071"


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    from processo_seletivo.processos.models import Edital

    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)
    return Edital.objects.get()


@pytest.fixture
def com_etapas(client, seletor_ligado, edital):
    """Rascunho com uma Etapa classificatória e uma só eliminatória — o que o marco enumera.

    O fato declarado entra aqui porque o desempate o consome: sem ele, o select "O que ele compara"
    teria só Etapas, e metade da lista que o critério oferece ficaria fora do teste.
    """
    from tests.interface.test_compor import EVENTO, eventos, perfis

    identificar(client, "ana.elaboradora", ["elaborador"])
    compor_rascunho(
        client,
        edital,
        perfis=perfis(
            **{
                "fato-0-0-id": FATO_DO_DESEMPATE,
                "fato-0-0-code": "EXPERIENCIA",
                "fato-0-0-label": "Meses de experiência em EaD",
                "fato-0-0-type": "INTEIRO",
            }
        ),
        eventos=eventos(),
    )
    edital.refresh_from_db()
    resposta = client.post(
        reverse("interface:compor-etapa", args=[edital.id, "etapas"]),
        {
            "etapa-0-id": ETAPA_CLASSIFICATORIA,
            "etapa-0-name": "Prova didática",
            "etapa-0-order": "1",
            "etapa-0-weight": "2",
            "etapa-0-classificatory": "on",
            "etapa-0-scheduleEventId": EVENTO,
            "etapa-1-id": ETAPA_SO_ELIMINATORIA,
            "etapa-1-name": "Análise documental",
            "etapa-1-order": "2",
            "etapa-1-weight": "1",
            "etapa-1-eliminatory": "on",
            "etapa-1-scheduleEventId": "",
        },
    )
    assert resposta.status_code == 302, resposta.content
    edital.refresh_from_db()
    return edital


@pytest.fixture
def cenario(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    """O cenário da ocupação (016): Edital com quadro publicado, ordem e corte emitidos.

    A fixture é declarada aqui **e** no `conftest` da integração, de propósito: importar fixture de
    outro módulo de teste a redefine no importador. O que se importa é a função.
    """
    from tests.fixtures.ocupacao import montar_cenario_da_ocupacao

    # **Com cota, de propósito**: a tela lista um bloco por recorte, e um cenário de recorte único
    # não exercitaria a listagem — que é o que evita publicar dois e esquecer o terceiro.
    return montar_cenario_da_ocupacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="ocupacao-016-tela",
        geral=3,
        ppi=2,
    )
