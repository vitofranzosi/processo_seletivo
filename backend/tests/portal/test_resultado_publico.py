"""A página pública do resultado: sem conta, num endereço estável, e histórica quando sucedida.

Todo teste aqui usa um cliente **sem sessão nenhuma** — é o que "público" quer dizer, e é também o
que impede que o cabeçalho do portal, que traz o nome de quem está identificado, entre nas
asserções sobre a lista.
"""

import re

import pytest
from django.urls import reverse

from tests.fixtures.divulgacao import (
    MODALIDADE_NOME,
    montar_ato_publicavel,
    publicar_o_ato,
)

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

UUID_EM_QUALQUER_LUGAR = re.compile(
    r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"
)


@pytest.fixture
def cenario(gestor, api_client, manager_headers, process_payload):
    """1º, 2º, 3º, 3º e uma quinta considerada sem posição — o empate e a fronteira juntos."""
    return montar_ato_publicavel(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=62,
        codigo="0762",
        pontuacoes=("90.0000", "80.0000", "70.0000", "70.0000", None),
        primeiro=1001,
    )


@pytest.fixture
def publicada(cenario):
    return publicar_o_ato(cenario, chave="publicar-0762")


def _conteudo(resposta):
    return re.search(r"<main[^>]*>(.*)</main>", resposta.content.decode(), re.DOTALL).group(1)


def abrir(client, publicacao):
    resposta = client.get(reverse("portal:resultado", args=[publicacao.id]))
    assert resposta.status_code == 200
    return _conteudo(resposta)


def test_sem_autenticacao_a_pagina_mostra_o_resultado(client, cenario, publicada):
    """SC-007: nome, protocolo, posição, rótulos institucionais e o instante — sem conta."""
    corpo = abrir(client, publicada)

    assert "Resultado preliminar" in corpo
    assert "Classificação final" in corpo
    assert "Candidata 1001" in corpo
    assert "1001" in corpo, "o protocolo é a identificação pública"
    assert MODALIDADE_NOME in corpo
    assert "90,00" in corpo
    assert publicada.publicado_em.astimezone().strftime("%d/%m/%Y") in corpo
    assert "Diretora do Cefor" in corpo


def test_a_pagina_nao_exibe_uuid_como_informacao(client, publicada):
    """FR-049: nenhum código interno é apresentado a quem lê.

    Os identificadores continuam existindo em `href` — é assim que se chega ao documento e à
    sucessora —, e o que se proíbe é UUID como **texto lido**.
    """
    corpo = abrir(client, publicada)
    sem_atributos = re.sub(r"<[^>]+>", " ", corpo)

    assert not UUID_EM_QUALQUER_LUGAR.search(sem_atributos)


def test_a_lista_tem_estrutura_semantica_com_cabecalho_de_coluna(client, publicada):
    """FR-054: quem ouve a página precisa saber a que coluna cada valor pertence."""
    corpo = abrir(client, publicada)

    assert "<table" in corpo
    assert corpo.count('<th scope="col">') == 5
    assert "<thead>" in corpo and "<tbody>" in corpo


def test_a_pagina_nao_oferece_acao_de_recurso(client, publicada):
    """FR-055: divulgar não abre canal transacional; recurso é ato de outra feature."""
    corpo = abrir(client, publicada)

    assert "recurso" not in corpo.lower()
    assert "<form" not in corpo


def test_o_empate_aparece_como_posicao_compartilhada(client, publicada):
    """FR-014: 1º, 2º, 3º, 3º — e o empate dito em texto, não por cor nem por ordem."""
    corpo = abrir(client, publicada)
    linhas = re.findall(r'<td data-rotulo="Posição">(.*?)</td>', corpo, re.DOTALL)

    assert [re.sub(r"<[^>]+>", "", item).strip().split("º")[0] for item in linhas] == [
        "1",
        "2",
        "3",
        "3",
    ]
    assert corpo.count("posição compartilhada") == 2


def test_a_publicacao_sucedida_diz_em_texto_que_foi_sucedida(client, cenario, publicada):
    """SC-005, SC-006 e FR-052: o mesmo endereço, o conteúdo intacto, e o aviso em texto."""
    antes = abrir(client, publicada)
    sucessora = publicar_o_ato(cenario, chave="publicar-0762-b", natureza="DEFINITIVA")

    depois = abrir(client, publicada)

    assert "foi sucedido" in depois, "a sucessão é dita em texto, e não só por cor (FR-052)"
    assert reverse("portal:resultado", args=[sucessora.id]) in depois, (
        "o aviso oferece o caminho para a vigente (FR-044)"
    )
    # O conteúdo divulgado permanece: o que mudou foi o aviso, e não a lista (FR-043, FR-048).
    lista_antes = re.search(r"<tbody>(.*?)</tbody>", antes, re.DOTALL).group(1)
    lista_depois = re.search(r"<tbody>(.*?)</tbody>", depois, re.DOTALL).group(1)
    assert lista_antes == lista_depois


def test_a_vigente_nao_diz_que_foi_sucedida(client, cenario, publicada):
    sucessora = publicar_o_ato(cenario, chave="publicar-0762-c", natureza="DEFINITIVA")

    corpo = abrir(client, sucessora)

    assert "foi sucedido" not in corpo


def test_quem_conhece_so_o_edital_chega_a_publicacao_vigente(client, cenario, publicada):
    """SC-018 e FR-050: a descobribilidade pela página que a pessoa já abre."""
    resposta = client.get(reverse("portal:selecao", args=[cenario["edital"].id]))
    corpo = _conteudo(resposta)

    assert "Resultados divulgados" in corpo
    assert reverse("portal:resultado", args=[publicada.id]) in corpo
    assert "Classificação final" in corpo


def test_a_vitrine_do_edital_anuncia_so_a_vigente(client, cenario, publicada):
    """Anunciar a sucedida como atual ofereceria como vigente o que já não é."""
    sucessora = publicar_o_ato(cenario, chave="publicar-0762-d", natureza="DEFINITIVA")

    corpo = _conteudo(client.get(reverse("portal:selecao", args=[cenario["edital"].id])))

    assert reverse("portal:resultado", args=[sucessora.id]) in corpo
    assert reverse("portal:resultado", args=[publicada.id]) not in corpo


def test_abrir_a_pagina_nao_recalcula_a_ordem(client, cenario, publicada, api_client, monkeypatch):
    """SC-011 e FR-010: a página histórica mostra o que foi divulgado, e não o que sairia hoje.

    Não porque alguém congele a leitura: porque **não há cálculo na leitura**. `calcular_ordem` é
    substituída por uma função que explode — se a página a chamasse, o teste quebraria em vez de
    passar por acaso.
    """
    from tests.fixtures.edital import caminho_perfil
    from tests.fixtures.publicacao import retify

    antes = abrir(client, publicada)

    retify(
        api_client,
        cenario["edital"],
        [
            {
                "targetPath": f"{caminho_perfil('classificationMilestones', 62)}"
                f"/id={cenario['marco']}/rounding/scale",
                "operation": "REPLACE",
                "newValue": 4,
            }
        ],
        suffix="ret0762",
    )

    def explodir(*args, **kwargs):
        raise AssertionError("a página pública recalculou a ordem")

    monkeypatch.setattr(
        "processo_seletivo.classificacao.application.calculo.calcular_ordem", explodir
    )
    depois = abrir(client, publicada)

    assert antes == depois


TABELAS_PROIBIDAS = (
    "inscricoes_inscricao",
    "classificacao_posicaonaordem",
    "publicacoes_versaoconsolidada",
    "divulgacao_situacaodivulgada",
)


def test_a_pagina_nao_emite_consulta_as_tabelas_de_dado_individual(client, publicada):
    """T-013: a fronteira é a **ausência da consulta**, e não um filtro na serialização.

    Um filtro protegeria a mesma coisa e dependeria de ninguém o remover. A ausência da consulta é
    verificável, e é o que este teste verifica.
    """
    from django.db import connection
    from django.test.utils import CaptureQueriesContext

    with CaptureQueriesContext(connection) as consultas:
        client.get(reverse("portal:resultado", args=[publicada.id]))

    alcancadas = [
        tabela
        for tabela in TABELAS_PROIBIDAS
        if any(tabela in item["sql"] for item in consultas.captured_queries)
    ]
    assert alcancadas == [], f"a página pública alcançou {alcancadas}"


def test_a_pagina_nao_tem_largura_fixa_que_force_rolagem_horizontal(client, publicada):
    """FR-051 e SC-016: a 375 px a página não rola de lado.

    O que dá para prender sem navegador é a **causa**: nenhuma largura cravada em pixel, e a lista
    longa dentro do seu próprio contêiner rolável. O `scrollWidth === 375` é medido no navegador, e
    está no quickstart como verificação manual.
    """
    resposta = client.get(reverse("portal:resultado", args=[publicada.id]))
    corpo = resposta.content.decode()
    conteudo = _conteudo(resposta)

    assert 'class="tabela-rolavel"' in conteudo, (
        "a tabela larga rola dentro do próprio contêiner, e não empurra a página"
    )
    folha = corpo[corpo.index("<style>") : corpo.index("</style>")]
    assert not re.search(r"\bmain\{[^}]*width:\d+px", folha)
    assert "--pagina" in folha


def test_a_publicacao_mais_antiga_leva_a_vigente_e_nao_a_sucessora_imediata(
    client, cenario, publicada, gestor
):
    """FR-044 e SC-006: o caminho é para **a vigente**, e não para a próxima da fila.

    Com dois elos a distinção não aparece — a sucessora imediata *é* a vigente —, e foi por isso
    que ela passou despercebida. Com três, P1 apontava para P2, que já fora sucedida: quem abrisse
    o resultado mais antigo seria levado a outro resultado histórico e continuaria sem saber o que
    vale hoje.
    """
    from tests.fixtures.divulgacao import emitir

    p2 = publicar_o_ato(cenario, chave="publicar-0762-cadeia-2", natureza="DEFINITIVA")
    # A terceira exige ato novo: `(ato, natureza)` é único, e as duas naturezas já se esgotaram.
    sucessor = emitir(cenario, gestor, chave="emitir-0762-cadeia", motivo="Correção da ordem.")
    p3 = publicar_o_ato(
        cenario, chave="publicar-0762-cadeia-3", natureza="DEFINITIVA", ato=sucessor
    )

    corpo = abrir(client, publicada)

    assert "foi sucedido" in corpo
    assert reverse("portal:resultado", args=[p3.id]) in corpo, (
        "o caminho precisa levar à ponta da cadeia, que é a que vale hoje"
    )
    assert reverse("portal:resultado", args=[p2.id]) not in corpo, (
        "P2 também já foi sucedida: oferecê-la levaria de um histórico a outro"
    )
