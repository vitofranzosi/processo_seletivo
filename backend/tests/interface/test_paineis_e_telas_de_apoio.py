"""Os painéis e as telas de apoio da gestão, nono incremento (087).

Na Visão Geral, nas Autoridades da unidade, na Supervisão, nas duas telas do assistente, em Criar
Processo Seletivo e nas conferências dos atos do Processo e do Edital a trilha mora no cabeçalho de
contexto, e só lá — a das telas do Edital é a do Edital com a tela no fim, e a dos dois painéis de
seção é a própria seção. "Perguntar" é a ação principal do Assistente. Nenhum número entra nos
painéis. O desenho em si é provado no navegador e pelo inventário visual refeito (quickstart): aqui
fica o que a marcação garante.
"""

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from processo_seletivo.processos.models import ProcessoSeletivo
from tests.fixtures.publicacao import publish_original
from tests.interface.conftest import identificar
from tests.interface.test_shell_da_gestao import barra
from tests.interface.test_telas_da_presidencia import (
    abrir,
    ate_o_processo,
    comeca_pelo_titulo,
    niveis_em_ordem,
)
from tests.interface.test_telas_de_uso_diario import conteudo, trilha_unica_no_cabecalho

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

GESTOR = ["gestor"]
PILOTO = ["gestor", "participante-piloto-assistente"]


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    return publish_original(api_client, manager_headers, process_payload)


def ate_o_edital(edital):
    return [
        *ate_o_processo(edital.processo),
        f'<a href="{reverse("interface:detalhe", args=[edital.id])}">'
        f"Edital {edital.number}/{edital.year}</a> ›",
    ]


def rotulo_do_h1(corpo):
    return conteudo(corpo).split("<h1>")[1].split("</h1>")[0]


def termina_em(trilha, atual):
    assert trilha.rstrip().endswith(f'<span aria-current="page">{atual}</span>'), trilha


# ---- a trilha no cabeçalho -------------------------------------------------------------------


@pytest.mark.parametrize(
    ("rota", "secao"),
    [("interface:visao-geral", "Visão Geral"), ("interface:autoridades", "Autoridades da unidade")],
)
def test_nos_paineis_de_secao_a_trilha_e_a_propria_secao(client, seletor_ligado, rota, secao):
    """`FR-1970`, `FR-1971`, `FR-1973`, `SC-772`: GPS › a seção, como página atual, sem link —
    como a lista e Minhas Etapas —, e a barra marca o item como a página."""
    identificar(client, "gustavo.gestor", GESTOR)
    corpo = abrir(client, rota)

    trilha = trilha_unica_no_cabecalho(corpo)
    termina_em(trilha, secao)
    assert "<a " not in trilha
    assert comeca_pelo_titulo(corpo)
    assert f'<a href="{reverse(rota)}" aria-current="page">' in barra(corpo)


def test_na_supervisao_a_trilha_passa_pelo_processo(client, seletor_ligado, edital):
    """`FR-1970`, `FR-1972`, `FR-1973`, `FR-1974`: GPS › Processos Seletivos › código ›
    Supervisão, e a barra continua em Processos Seletivos."""
    identificar(client, "gustavo.gestor", GESTOR)
    corpo = abrir(client, "interface:supervisao", edital.processo.id)

    trilha = trilha_unica_no_cabecalho(corpo)
    niveis_em_ordem(trilha, ate_o_processo(edital.processo))
    termina_em(trilha, "Supervisão")
    assert comeca_pelo_titulo(corpo)
    assert f'<a href="{reverse("interface:lista")}" aria-current="true">' in barra(corpo)


@pytest.mark.parametrize("acao", ["encerrar", "cancelar"])
def test_na_conferencia_do_ato_do_processo_a_trilha_termina_no_ato(
    client, seletor_ligado, edital, acao
):
    """`FR-1970`, `FR-1972`, `FR-1973`: o Processo, e o ato — o rótulo do título — como página
    atual."""
    identificar(client, "gustavo.gestor", GESTOR)
    corpo = abrir(client, "interface:processo-ato", edital.processo.id, acao)

    trilha = trilha_unica_no_cabecalho(corpo)
    niveis_em_ordem(trilha, ate_o_processo(edital.processo))
    assert trilha.count("<a ") == 2
    termina_em(trilha, rotulo_do_h1(corpo))
    assert comeca_pelo_titulo(corpo)


@pytest.mark.parametrize(
    ("rota", "papeis", "atual"),
    [
        ("interface:duvidas", GESTOR, "Respostas do assistente de dúvidas"),
        ("interface:assistente", PILOTO, "Assistente do Edital (piloto)"),
    ],
)
def test_nas_telas_do_assistente_a_trilha_e_a_do_edital(
    client, seletor_ligado, edital, rota, papeis, atual
):
    """`FR-1970`, `FR-1972`, `FR-1973`, `SC-773`: GPS › Processos Seletivos › código › Edital ›
    a tela. A trilha do conteúdo pulava o Processo (087, D-001)."""
    identificar(client, "gustavo.gestor", papeis)
    corpo = abrir(client, rota, edital.id)

    trilha = trilha_unica_no_cabecalho(corpo)
    niveis_em_ordem(trilha, ate_o_edital(edital))
    termina_em(trilha, atual)
    assert comeca_pelo_titulo(corpo)


def test_na_conferencia_do_ato_do_edital_a_trilha_passa_pelo_processo(
    client, seletor_ligado, edital
):
    """`FR-1970`, `FR-1972`, `FR-1973`, `SC-773`: o Processo, o Edital e o ato."""
    identificar(client, "gustavo.gestor", GESTOR)
    corpo = abrir(client, "interface:ato", edital.id, "encerrar")

    trilha = trilha_unica_no_cabecalho(corpo)
    niveis_em_ordem(trilha, ate_o_edital(edital))
    termina_em(trilha, rotulo_do_h1(corpo))
    assert comeca_pelo_titulo(corpo)


def test_em_criar_processo_a_trilha_e_a_da_lista(client, seletor_ligado):
    """`FR-1970`, `FR-1972`, `FR-1973`: GPS › Processos Seletivos › Criar."""
    identificar(client, "gustavo.gestor", GESTOR)
    corpo = abrir(client, "interface:processo-criar")

    trilha = trilha_unica_no_cabecalho(corpo)
    assert f'<a href="{reverse("interface:lista")}">Processos Seletivos</a> ›' in trilha
    assert trilha.count("<a ") == 1
    termina_em(trilha, "Criar")
    assert comeca_pelo_titulo(corpo)


@pytest.mark.parametrize(
    ("rota", "papeis", "acao"),
    [
        ("interface:duvidas", GESTOR, None),
        ("interface:assistente", PILOTO, None),
        ("interface:ato", GESTOR, "encerrar"),
    ],
)
def test_o_processo_da_trilha_nao_custa_consulta(
    client, seletor_ligado, edital, rota, papeis, acao
):
    """`FR-1978`: o código do Processo vem do Edital, que a view já carrega com ele — nenhuma
    consulta lê o Processo sozinho."""
    identificar(client, "gustavo.gestor", papeis)
    args = [edital.id, acao] if acao else [edital.id]
    tabela = ProcessoSeletivo._meta.db_table
    with CaptureQueriesContext(connection) as consultas:
        client.get(reverse(rota, args=args))

    sozinho = [
        q["sql"] for q in consultas if q["sql"].split(" WHERE ")[0].endswith(f'FROM "{tabela}"')
    ]
    assert sozinho == []


# ---- a hierarquia das ações ------------------------------------------------------------------


def test_no_assistente_perguntar_e_a_acao_principal(client, seletor_ligado, edital):
    """`FR-1976`: "Perguntar" com o desenho de ação principal; "Começar outra conversa", não."""
    identificar(client, "gustavo.gestor", PILOTO)
    corpo = conteudo(abrir(client, "interface:assistente", edital.id))

    assert '<button type="submit" class="botao">Perguntar</button>' in corpo
    assert '<button type="submit" class="acao">Começar outra conversa</button>' in corpo
    assert corpo.count('class="botao"') == 1


def test_nas_respostas_a_acao_principal_continua_ver_a_resposta(client, seletor_ligado, edital):
    """`FR-1976`, D-003: um botão principal só, e "Consultar neste instante" secundário."""
    identificar(client, "gustavo.gestor", GESTOR)
    corpo = conteudo(abrir(client, "interface:duvidas", edital.id))

    assert '<button type="submit" class="botao">Ver a resposta</button>' in corpo
    assert '<button type="submit" class="acao">Consultar neste instante</button>' in corpo
    assert corpo.count('class="botao"') == 1


def test_a_conferencia_do_edital_continua_com_o_mesmo_confirmar(client, seletor_ligado, edital):
    """`FR-1977`: o cancelamento interrompe, e "Confirmar" continua `botao perigoso`, depois das
    consequências, com "Cancelar e voltar" ao lado."""
    identificar(client, "gustavo.gestor", GESTOR)
    corpo = conteudo(abrir(client, "interface:ato", edital.id, "cancelar"))

    assert corpo.index('id="consequencias-titulo"') < corpo.index('<button type="submit"')
    assert '<button type="submit" class="botao perigoso">' in corpo
    assert ">Cancelar e voltar</a>" in corpo


def test_a_conferencia_do_processo_com_recusa_certa_continua_sem_confirmar(
    client, seletor_ligado, edital
):
    """`FR-1977`, casos-limite: com um Edital ainda publicado, cancelar o Processo é recusa certa —
    o aviso vem antes das consequências, não há "Confirmar", e "Cancelar e voltar" continua."""
    identificar(client, "gustavo.gestor", GESTOR)
    corpo = conteudo(abrir(client, "interface:processo-ato", edital.processo.id, "cancelar"))

    assert corpo.index("Este ato será recusado.") < corpo.index('id="consequencias-titulo"')
    assert '<button type="submit"' not in corpo
    assert ">Cancelar e voltar</a>" in corpo


@pytest.mark.parametrize("template", ["confirmar.html", "processo_confirmar.html"])
def test_o_confirmar_dos_atos_tem_o_desenho_de_antes(template):
    """`FR-1977`: `botao`, com o desenho de perigo quando o ato interrompe."""
    from tests.interface.test_telas_de_uso_diario import TEMPLATES

    folha = (TEMPLATES / template).read_text()
    assert (
        '<button type="submit" class="botao {% if ato.interrupcao %}perigoso{% endif %}">' in folha
    )


def test_encerrar_a_vigencia_continua_perigoso():
    """`FR-1977`: a única ação que não se desfaz nas Autoridades, com o desenho de antes."""
    from tests.interface.test_telas_de_uso_diario import TEMPLATES

    folha = (TEMPLATES / "autoridades.html").read_text()
    assert 'class="acao perigoso" aria-label="Encerrar a vigência de {{ item.rotulo }}"' in folha
    assert '<button type="submit" class="botao">Cadastrar autoridade</button>' in folha


# ---- nenhum número novo nos painéis ----------------------------------------------------------


def test_a_visao_geral_tem_os_mesmos_quatro_indicadores(client, seletor_ligado, edital):
    """`FR-1978`: os quatro números, nesta ordem, e a declaração do que a página não mede."""
    identificar(client, "gustavo.gestor", GESTOR)
    corpo = conteudo(abrir(client, "interface:visao-geral"))

    indicadores = corpo.split('<ul class="consolidado"')[1].split("</ul>")[0]
    assert indicadores.count("<li>") == 4
    rotulos = [
        "Edita",
        "Vagas imediatas publicadas",
        "Inscrições submetidas",
        "Inscrições por vaga",
    ]
    niveis_em_ordem(indicadores, rotulos)
    assert "O que esta página não mede" in corpo


def test_a_supervisao_tem_o_mesmo_pulso(client, seletor_ligado, edital):
    """`FR-1978`: o Pulso e a Atenção, com o instante da leitura, e nenhum percentual."""
    identificar(client, "gustavo.gestor", GESTOR)
    corpo = conteudo(abrir(client, "interface:supervisao", edital.processo.id))

    niveis_em_ordem(corpo, ['id="pulso-titulo"', "Lido em ", 'id="atencao-titulo"'])
    resumo = corpo.split('<ul class="resumo"')[1].split("</ul>")[0]
    assert 2 <= resumo.count("<li>") <= 3
    assert "%" not in resumo
