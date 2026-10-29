"""A tela da Agenda dos Editais (101): o mês, o dia, os próximos marcos, os filtros e o orçamento.

Três Editais publicados cujos cronogramas se cruzam no terceiro dia a partir de hoje: duas provas,
uma abertura de período e uma prova cancelada. É o dia de concentração que a grade tem de destacar
— e o cancelado que ela não pode contar.
"""

import re
import uuid

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from processo_seletivo.interface import agenda
from tests.fixtures.agenda import em, evento, publicar
from tests.fixtures.publicacao import create_retification, publish_retification
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

URL = reverse("interface:agenda")
PALAVRAS_DE_EXECUCAO = ("concluído", "concluido", "cumprido", "realizado", "pendente", "atrasado")


@pytest.fixture
def pessoa(client, seletor_ligado):
    """Uma identidade sem papel nenhum: a agenda é de toda identidade da gestão (`D-004`)."""
    identificar(client, "pessoa.agenda", [])
    return client


@pytest.fixture
def cenario(api_client, manager_headers, process_payload):
    a = publicar(
        api_client,
        manager_headers,
        process_payload,
        21,
        [
            evento(21, 0, "Período de inscrições", em(1), em(10, 18), isRegistrationPeriod=True),
            evento(21, 1, "Prova objetiva", em(3, 14), location="Campus Serra, bloco 2"),
            evento(21, 2, "Prova prática", em(3, 15), status="CANCELADO"),
            evento(21, 3, "Resultado preliminar", em(12, 10)),
            evento(21, 4, "Período de análise", em(-2), em(5, 18)),
        ],
    )
    b = publicar(
        api_client,
        manager_headers,
        process_payload,
        22,
        [
            evento(22, 0, "Período de inscrições", em(2), em(20, 18), isRegistrationPeriod=True),
            evento(22, 1, "Prova escrita", em(3, 9)),
        ],
    )
    c = publicar(
        api_client,
        manager_headers,
        process_payload,
        23,
        [
            evento(23, 0, "Período de inscrições", em(3), em(4, 18), isRegistrationPeriod=True),
            evento(23, 1, "Entrevista", em(40, 10)),
        ],
    )
    return a, b, c


def principal(resposta):
    assert resposta.status_code == 200
    return resposta.content.decode().split('<main id="conteudo"')[1].split("</main>")[0]


def texto(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def celula(html, dia):
    """A célula do mês que leva àquele dia."""
    alvo = f"dia={dia.isoformat()}"
    for td in re.findall(r"<td class=\"dia-do-mes[^\"]*\"[^>]*>.*?</td>", html, re.S):
        if alvo in td:
            return td
    raise AssertionError(f"sem célula para {dia}")


def mes_de(instante):
    return instante.strftime("%Y-%m")


# ---- acesso e estado vazio (FR-2609, FR-2611, FR-2644) -------------------------------------------


def test_sem_edital_publicado_a_pagina_diz_e_nao_desenha_a_grade(pessoa):
    html = principal(pessoa.get(URL))
    assert "Nenhum Edital da unidade tem cronograma publicado." in html
    assert "grade-do-mes" not in html


def test_so_leitura_o_unico_formulario_e_o_dos_filtros(pessoa, cenario):
    for parametros in (
        {},
        {"visao": "proximos"},
        {"visao": "mes", "dia": em(3).date().isoformat()},
    ):
        html = principal(pessoa.get(URL, parametros))
        formularios = re.findall(r"<form[^>]*>", html)
        assert formularios == [
            '<form method="get" class="filtros-da-agenda" aria-label="Filtros da agenda">'
        ]


# ---- o mês (FR-2623 a FR-2627, FR-2635, SC-951) --------------------------------------------------


def test_o_mes_conta_destaca_e_nomeia_dois_sem_o_cancelado(pessoa, cenario):
    html = principal(pessoa.get(URL, {"mes": mes_de(em(3))}))
    assert html.count('<th scope="col">') == 7
    assert "<caption>" in html

    dia = celula(html, em(3).date())
    assert "varios" in dia.split(">")[0]
    assert "3 marcos" in texto(dia)
    nomes = re.findall(r"<li>(.*?)</li>", dia, re.S)
    assert [texto(n).strip() for n in nomes] == [
        "22/2026 Prova escrita",
        "23/2026 Abre · Período de inscrições",
    ]
    assert "mais 1" in dia
    assert "Prova prática" not in dia, "o cancelado não ocupa a grade (FR-2621)"


def test_o_periodo_nao_ocupa_os_dias_do_meio_e_aparece_uma_vez_na_lista(pessoa, cenario):
    mes = mes_de(em(3))
    html = principal(pessoa.get(URL, {"mes": mes}))
    for dias in (6, 7, 8):
        if mes_de(em(dias)) == mes:
            assert "Período de inscrições" not in celula(html, em(dias).date())
    periodos = html.split('class="periodos-do-mes"')[1]
    intervalo_de_a = f"{em(1):%d/%m} a {em(10):%d/%m}"
    assert periodos.count(intervalo_de_a) == 1


def test_a_soma_das_celulas_e_a_sintese(pessoa, cenario):
    html = principal(pessoa.get(URL, {"mes": mes_de(em(3))}))
    celulas = sum(int(n) for n in re.findall(r'quantidade-do-dia">(\d+)<', html))
    sintese = int(re.search(r"<dt>Marcos previstos</dt><dd>(\d+)</dd>", html).group(1))
    assert celulas == sintese > 0


def test_o_dia_de_um_marco_so_nao_e_destacado_e_hoje_e_marcado(pessoa, cenario):
    hoje = em(0).date()
    assert 'aria-current="date"' in celula(principal(pessoa.get(URL)), hoje)
    html = principal(pessoa.get(URL, {"mes": mes_de(em(12))}))
    um_so = celula(html, em(12).date())
    assert " 1 marco " in texto(um_so) and "varios" not in um_so.split(">")[0]


def test_o_acesso_ao_dia_diz_a_data_por_extenso(pessoa, cenario):
    dia = em(3).date()
    html = principal(pessoa.get(URL, {"mes": mes_de(em(3))}))
    assert agenda.por_extenso(dia) in celula(html, dia)


def test_mes_invalido_cai_no_corrente_e_a_navegacao_leva_aos_vizinhos(pessoa, cenario):
    html = principal(pessoa.get(URL, {"mes": "2026-13"}))
    hoje = em(0).date()
    assert f"{agenda.MESES[hoje.month - 1]} de {hoje.year}".capitalize() in html
    assert 'rel="prev"' in html and 'rel="next"' in html


# ---- o dia (FR-2628 a FR-2630) -------------------------------------------------------------------


def test_o_dia_lista_todos_os_marcos_com_os_dois_destinos(pessoa, cenario):
    a, b, c = cenario
    html = principal(pessoa.get(URL, {"visao": "mes", "dia": em(3).date().isoformat()}))
    assert html.count('<li class="marco-da-agenda') == 4
    assert "3 marcos previstos · 1 cancelado" in texto(html)
    assert "Cancelado" in html
    assert "Local: Campus Serra, bloco 2" in html
    for edital in (a, b, c):
        assert reverse("interface:detalhe", args=[edital.id]) in html
        assert f"{reverse('portal:selecao', args=[edital.id])}#cronograma-titulo" in html
    em_curso = texto(html.split("Períodos em curso neste dia")[1])
    assert "Período de análise" in em_curso
    assert em_curso.count("Período de inscrições") == 2, "o de C começa neste dia: é marco"
    assert "Voltar a" in html


def test_dia_invalido_e_ignorado(pessoa, cenario):
    html = principal(pessoa.get(URL, {"visao": "mes", "dia": "ontem"}))
    assert "grade-do-mes" in html


# ---- próximos marcos (FR-2631 a FR-2634) ---------------------------------------------------------


def test_proximos_sete_dias_com_o_periodo_em_curso_uma_vez(pessoa, cenario):
    html = principal(pessoa.get(URL, {"visao": "proximos"}))
    em_curso = html.split('class="em-curso"')[1].split("</section>")[0]
    assert "Período de análise" in em_curso
    assert "encerra em 5 dias" in em_curso
    dias = html.split('class="titulo-da-janela"')[1]
    assert "Prova escrita" in dias and "Cancelado" in dias
    assert "Resultado preliminar" not in dias, "fora dos sete dias"


def test_trinta_dias_alcanca_mais_e_nao_tudo(pessoa, cenario):
    html = principal(pessoa.get(URL, {"visao": "proximos", "janela": "30"}))
    assert "Resultado preliminar" in html
    assert "Entrevista" not in html


def test_a_sintese_de_proximos_nao_conta_o_cancelado(pessoa, cenario):
    html = principal(pessoa.get(URL, {"visao": "proximos"}))
    marcos = [m for m in re.findall(r'<li class="marco-da-agenda[^"]*"', html)]
    cancelados = [m for m in marcos if "cancelado" in m]
    sintese = int(re.search(r"<dt>Marcos previstos</dt><dd>(\d+)</dd>", html).group(1))
    assert cancelados and sintese == len(marcos) - len(cancelados)


def test_janela_vazia_nomeia_o_proximo_marco_com_os_filtros(pessoa, cenario):
    _, _, c = cenario
    html = principal(
        pessoa.get(URL, {"visao": "proximos", "edital": str(c.id), "especie": agenda.DEMAIS})
    )
    assert "Nenhum marco previsto" in html
    assert f"O próximo é em {em(40):%d/%m/%Y}: Entrevista" in html


# ---- filtros (FR-2637 a FR-2639) -----------------------------------------------------------------


def test_o_filtro_segue_nas_abas_nos_dias_e_na_sintese(pessoa, cenario):
    a, _, _ = cenario
    filtro = f"edital={a.id}"
    html = principal(pessoa.get(URL, {"mes": mes_de(em(3)), "edital": str(a.id)}))
    abas = html.split('class="abas-da-agenda"')[1].split("</nav>")[0]
    assert abas.count(filtro) == 2
    assert re.search(r'aria-current="page">Mês<', abas), "a aba ativa é a página atual (FR-2645)"
    assert filtro in celula(html, em(3).date())
    assert "Prova escrita" not in html
    assert "Limpar filtros" in html

    proximos = re.search(r'href="([^"]*visao=proximos[^"]*)"', abas).group(1).replace("&amp;", "&")
    seguinte = principal(pessoa.get(proximos))
    assert f'<option value="{a.id}" selected>' in seguinte
    assert "Prova escrita" not in seguinte


def test_identificador_alheio_e_ignorado_sem_recusa(pessoa, cenario):
    html = principal(pessoa.get(URL, {"edital": str(uuid.uuid4())}))
    assert "Limpar filtros" not in html
    assert " selected>" not in html.split('id="f-edital"')[1].split("</select>")[0]


def test_nao_ha_filtro_de_unidade_modalidade_ou_categoria(pessoa, cenario):
    formulario = (
        principal(pessoa.get(URL)).split('class="filtros-da-agenda"')[1].split("</form>")[0]
    )
    assert sorted(re.findall(r'<select name="([^"]+)"', formulario)) == ["edital", "especie"]


# ---- previsto × efetivo e Retificação (FR-2614, FR-2636, FR-2640 a FR-2642) ----------------------


def test_nenhuma_visualizacao_afirma_execucao(pessoa, cenario):
    for parametros in (
        {},
        {"visao": "proximos", "janela": "30"},
        {"dia": em(3).date().isoformat()},
    ):
        visivel = texto(principal(pessoa.get(URL, parametros))).lower()
        assert not [p for p in PALAVRAS_DE_EXECUCAO if p in visivel], parametros
        assert "datas são as previstas" in visivel
        assert "lido em" in visivel, "o instante da leitura é declarado (FR-2643)"
        assert "podem diferir das datas previstas" in visivel


def test_o_aviso_da_retificacao_a_vigorar(pessoa, api_client, manager_headers, process_payload):
    edital = publicar(api_client, manager_headers, process_payload, 24)
    retificacao = create_retification(
        api_client,
        edital,
        [
            {
                "targetPath": f"/schedule/id={evento(24, 1, 'x', em(3))['id']}/startAt",
                "operation": "REPLACE",
                "newValue": em(8, 14).isoformat(),
            }
        ],
        effective_at=em(4, 0).isoformat(),
    )
    publish_retification(api_client, retificacao)
    html = texto(principal(pessoa.get(URL, {"visao": "proximos"})))
    assert "Retificação publicada que ainda não vigora" in html
    assert f"Edital 24/2026 — Processo da agenda 24: vigora a partir de {em(4):%d/%m/%Y}" in html


# ---- orçamento (FR-2646, SC-950) -----------------------------------------------------------------


def consultas(client, parametros):
    with CaptureQueriesContext(connection) as capturadas:
        assert client.get(URL, parametros).status_code == 200
    return len(capturadas.captured_queries)


def test_as_consultas_nao_crescem_com_os_editais(
    pessoa, api_client, manager_headers, process_payload
):
    visoes = ({}, {"visao": "proximos", "janela": "30"}, {"dia": em(3).date().isoformat()})
    publicar(api_client, manager_headers, process_payload, 31)
    com_um = [consultas(pessoa, v) for v in visoes]
    for seed in range(32, 36):
        publicar(api_client, manager_headers, process_payload, seed)
    com_cinco = [consultas(pessoa, v) for v in visoes]
    assert com_cinco == com_um, "a agenda passou a consultar por Edital"
    assert len(set(com_um)) == 1, "as visualizações leem o mesmo conjunto"


def test_o_marco_de_edital_encerrado_se_diz_encerrado():
    """`FR-2629`: o marco de Edital encerrado diz que o Edital parou por ato."""
    from datetime import date, datetime

    from django.template.loader import render_to_string

    from processo_seletivo.shared.tempo import ZONA

    edital = agenda.EditalDaAgenda(
        id=str(uuid.uuid4()), numero="7", ano=2026, processo="Processo C", status="ENCERRADO"
    )
    marco = agenda.Marco(
        dia=date(2026, 11, 2),
        instante=datetime(2026, 11, 2, 9, tzinfo=ZONA),
        hora="9h",
        tipo=agenda.PONTUAL,
        evento_id="e",
        nome="Prova objetiva",
        local="",
        intervalo="",
        especie=agenda.DEMAIS,
        fase=agenda.PASSADA,
        cancelado=False,
        edital=edital,
    )
    html = texto(render_to_string("interface/_agenda_marco.html", {"marco": marco}))
    assert "Edital encerrado" in html
    assert "data passada" in html
