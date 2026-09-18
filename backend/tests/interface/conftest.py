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


def marco_de_sorteio_no_formulario(perfil_id, *, indice=0, marco_id=None):
    """O marco mínimo, na grafia que o formulário da etapa Classificação envia (032, FR-457).

    **Ele passou a ser parte do percurso, e não um passo opcional.** Desde a `FR-457` um Edital com
    Perfil sem marco não publica — sem marco ninguém é classificado por aquele Perfil —, e por isso
    um roteiro que atravessa o assistente e submete precisa percorrer também esta etapa. Quem não
    submete não precisa dela.

    Sorteia porque sortear não exige Etapa (030, `FR-432`), e publica o método inteiro porque a
    `FR-467` recusa quem sorteia sem publicá-lo.
    """
    from uuid import NAMESPACE_URL, uuid5

    base = f"marco-{perfil_id}-{indice}"
    return {
        "perfil_id": perfil_id,
        f"{base}-id": marco_id or str(uuid5(NAMESPACE_URL, f"marco-do-formulario:{perfil_id}")),
        f"{base}-code": "SORT",
        f"{base}-name": "Sorteio público",
        f"{base}-orderProduction": "POR_SORTEIO",
        f"{base}-operation": "SOMA_PONDERADA",
        f"{base}-normalization": "NENHUMA",
        f"{base}-scale": "2",
        f"{base}-mode": "MEIO_PARA_CIMA",
        f"{base}-draw-algorithm": "IFES-SORTEIO-SHA256-v1",
        f"{base}-draw-source": "Fonte de demonstração",
        f"{base}-draw-occurrence": "5900",
        f"{base}-draw-occurrenceAt": "2020-01-01T20:00:00-03:00",
        f"{base}-draw-derivation": "A extração de sábado imediatamente anterior.",
        f"{base}-draw-normalizationRule": "DIGITOS_EM_SEQUENCIA",
        f"{base}-draw-normalizationText": "Os cinco números sorteados, na ordem dos prêmios.",
        f"{base}-draw-substitutionRule": "OCORRENCIA_SEGUINTE_DA_MESMA_FONTE",
        f"{base}-draw-substitutionText": "Não havendo extração, vale a seguinte da mesma fonte.",
        f"{base}-cutTargetKind": "FIXED",
        f"{base}-cutTargetCount": "1",
        f"{base}-cutSurplusCount": "0",
        f"{base}-cutTieOutcome": "STRICT",
        f"{base}-cutGovernedStage": "NONE",
        f"{base}-cutContinuation": "NONE",
    }


def compor_rascunho(client, edital, perfis=None, eventos=None, marcos=None):
    """Percorre o assistente: Perfis, Classificação e Cronograma são etapas salvas em separado.

    `marcos` é o passo que a `032` tornou obrigatório para quem vai **submeter**: sem marco o
    Edital não publica (`FR-457`). Continua opcional aqui porque nem todo roteiro submete.
    """
    from django.urls import reverse

    if perfis is not None:
        resposta = client.post(
            reverse("interface:compor-etapa", args=[edital.id, "perfis"]), perfis
        )
        assert resposta.status_code == 302, resposta.content
    if marcos is not None:
        edital.refresh_from_db()
        resposta = client.post(
            reverse("interface:compor-etapa", args=[edital.id, "classificacao"]), marcos
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


# --- O Requerimento de Matrícula (029) ---------------------------------------------------------
# As funções moram em `tests/fixtures/requerimento.py`, e estas fixtures são as mesmas que
# `tests/integration/requerimentos/conftest.py` declara. **Declaradas duas vezes de propósito**:
# importar uma fixture de outro módulo de teste a redefine no importador, que é o que o `F811`
# acusa. A regra está escrita em `tests/fixtures/corte.py`.


@pytest.fixture
def selecao_na_inscricao(raiz_de_arquivos, api_client, manager_headers, process_payload):
    """Seleção publicada que coleta o requerimento **na inscrição** — o caso do 77 e do 58."""
    from tests.fixtures.requerimento import publicar_com_requerimento

    return publicar_com_requerimento(api_client, manager_headers, process_payload, "AT_ENROLLMENT")


@pytest.fixture
def selecao_na_convocacao(raiz_de_arquivos, api_client, manager_headers, process_payload):
    """Seleção publicada que coleta **na convocação** — o caso do 69 e do 46."""
    from tests.fixtures.requerimento import publicar_com_requerimento

    return publicar_com_requerimento(api_client, manager_headers, process_payload, "AT_CALL")


@pytest.fixture
def campos_declarados():
    from tests.fixtures.requerimento import campos_de_exemplo

    return campos_de_exemplo()
