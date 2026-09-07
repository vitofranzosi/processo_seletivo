"""O custo de mostrar o Resultado da Etapa não cresce com o número de marcos publicados.

Contagem de consultas, e não tempo de parede: o que importa detectar é o custo **crescer com o
histórico**. Um Edital com marco intermediário e marco final publica dois; um Edital maduro pode
publicar três. Uma leitura por marco parece barata com um e some com três — e a norma de cada um
mora no JSON do Edital inteiro, de modo que a versão errada de fazer isto carrega uma cópia do
conteúdo publicado por marco.

São três consultas, sempre: as publicações vigentes do Perfil, os conteúdos das versões
**distintas** que os atos citam, e os Resultados vigentes da Inscrição nas Etapas autorizadas
(018, T-009).

`conteudos_das_versoes` é o que faz a segunda ser uma só. `select_related("versao")` traria a
mesma resposta com o mesmo número de consultas — e uma cópia do Edital em JSON por linha, que
nenhum teste de contagem denunciaria (013, D-1).
"""

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from processo_seletivo.resultados.application.selectors import resultados_visiveis
from tests.fixtures.divulgacao import emitir, montar_marco, pontuar, publicar_o_ato

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.performance]


def consultas(inscricao):
    with CaptureQueriesContext(connection) as capturadas:
        resultados_visiveis(inscricao)
    return len(capturadas)


@pytest.fixture
def com_um_marco(gestor, api_client, manager_headers, process_payload):
    cenario = montar_marco(
        gestor, api_client, manager_headers, process_payload, seed=85, codigo="0785"
    )
    cenario["inscricoes"] = pontuar(
        cenario, gestor, ["90.0000", "70.0000"], primeiro=851, sufixo="85"
    )
    cenario["ato"] = emitir(cenario, gestor, chave="emitir-perf-018")
    publicar_o_ato(cenario, chave="publicar-perf-018")
    return cenario


@pytest.fixture
def com_dois_marcos(gestor, api_client, manager_headers, process_payload):
    """O mesmo Edital com marco intermediário **e** final, os dois publicados."""
    cenario = montar_marco(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=86,
        codigo="0786",
        com_intermediario=True,
    )
    cenario["inscricoes"] = pontuar(
        cenario, gestor, ["90.0000", "70.0000"], primeiro=861, sufixo="86"
    )
    cenario["ato"] = emitir(cenario, gestor, chave="emitir-perf-018-a")
    publicar_o_ato(cenario, chave="publicar-perf-018-a")
    intermediario = cenario.get("marco_intermediario")
    if intermediario:
        ato = emitir(cenario, gestor, marco=intermediario, chave="emitir-perf-018-b")
        publicar_o_ato(cenario, chave="publicar-perf-018-b", ato=ato)
    return cenario


def test_o_custo_e_constante_entre_um_e_dois_marcos(com_um_marco, com_dois_marcos):
    """Dois marcos publicados custam o mesmo que um.

    É a propriedade que `conteudos_das_versoes` garante e que uma leitura por marco não teria — e
    ela é a diferença entre uma tela que serve um Edital e uma que serve um Edital maduro.
    """
    com_um = consultas(com_um_marco["inscricoes"][0])
    com_dois = consultas(com_dois_marcos["inscricoes"][0])

    assert com_dois == com_um


def test_o_custo_e_de_tres_consultas(com_um_marco):
    """O número declarado: uma regressão silenciosa aparece como número, e não como lentidão."""
    assert consultas(com_um_marco["inscricoes"][0]) == 3


def test_sem_publicacao_o_custo_e_de_uma_consulta(
    gestor, api_client, manager_headers, process_payload
):
    """Sem publicação a leitura para na primeira: não há norma a ler nem Resultado a buscar."""
    cenario = montar_marco(
        gestor, api_client, manager_headers, process_payload, seed=87, codigo="0787"
    )
    inscricoes = pontuar(cenario, gestor, ["90.0000"], primeiro=871, sufixo="87")

    assert consultas(inscricoes[0]) == 1
