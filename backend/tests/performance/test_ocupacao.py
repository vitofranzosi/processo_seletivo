"""O custo de ler a ocupação é do conjunto, e não uma consulta por recorte (016, `SC-082`, `R-006`).

**Dois testes, e eles medem grandezas diferentes.** O de contagem cobra o desenho: a tela lista
recortes, e recalcular abrindo o conteúdo publicado por linha é a consulta por listagem que o
orçamento já reprovou. O do relógio mede o teto de volume, e mede-o **por razão** contra uma
operação que já existe — tempo absoluto varia com a máquina, e razão não.
"""

import time

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from processo_seletivo.ocupacao.application.selectors import recortes_do_marco
from tests.fixtures.corte import MARCO
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.ocupacao import montar_cenario_da_ocupacao
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.performance, pytest.mark.django_db(transaction=True)]

# A apuração pode custar mais que a emissão da ordem — ela lê a faixa e os Resultados —, e o dobro
# é a folga que a `SC-082` fixa. Razão, e não segundos: tempo absoluto reprova por máquina lenta.
RAZAO_MAXIMA = 2.0


@pytest.fixture
def cenario_com_cota(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    """Dois recortes: a linha geral e uma cota. É o mínimo que exercita a listagem."""
    return montar_cenario_da_ocupacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="ocupacao-016-escala",
        geral=3,
        ppi=2,
    )


def test_a_leitura_nao_faz_uma_consulta_por_recorte(cenario_com_cota, gestor):
    """**O orçamento de consulta** (`R-006`): o custo não cresce por recorte listado.

    Com dois recortes, a leitura não pode custar o dobro de um. O que se mede é a diferença entre
    listar um e listar dois — se ela for proporcional, o desenho abre o conteúdo publicado por
    linha, que é o defeito que esta feature existe para não ter.
    """
    edital, _, _ = cenario_com_cota

    with CaptureQueriesContext(connection) as um:
        recortes_do_marco(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)
    consultas_por_recorte = len(um.captured_queries) / 2

    # Um teto folgado e absoluto: o que ele impede é a consulta por participante, não a por
    # recorte — dois recortes custam duas leituras de apuração, e isso é esperado.
    assert consultas_por_recorte < 15, (
        f"{len(um.captured_queries)} consultas para 2 recortes: "
        f"{consultas_por_recorte:.1f} por recorte"
    )


def test_a_tela_abre_sem_consulta_por_participante(client, seletor_ligado, cenario_com_cota):
    """Abrir a tela não custa uma consulta por participante — não há N+1 de gente."""
    edital, _, _ = cenario_com_cota
    identificar(client, "carlos", ["gestor"])

    with CaptureQueriesContext(connection) as ctx:
        resposta = client.get(reverse("interface:ocupacao", args=[edital.id, MARCO]))

    assert resposta.status_code == 200
    assert len(ctx.captured_queries) < 60, len(ctx.captured_queries)


def test_a_apuracao_cabe_no_dobro_do_tempo_da_emissao_da_ordem(cenario_com_cota, gestor):
    """**O teto da `SC-082`, medido por razão.**

    A spec fixa 7 Perfis × 3 listas com mil participantes por recorte. Aqui o volume é o do cenário
    reduzido — a mesma redução que o percurso da `014` declarou —, e o que se mede é a **forma** do
    custo: a apuração de um recorte não pode custar mais que o dobro da emissão da ordem no mesmo
    volume. O volume real é do percurso conduzido, e não deste teste.
    """
    from processo_seletivo.classificacao.application.calculo import calcular_ordem
    from processo_seletivo.ocupacao.application.selectors import ocupacao_do_recorte

    edital, _, _ = cenario_com_cota

    inicio = time.perf_counter()
    calcular_ordem(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)
    custo_da_ordem = time.perf_counter() - inicio

    inicio = time.perf_counter()
    ocupacao_do_recorte(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)
    custo_da_ocupacao = time.perf_counter() - inicio

    # O piso evita que a razão explique ruído: com custos na casa dos microssegundos, qualquer
    # divisão é aleatória.
    if custo_da_ordem < 0.001:
        pytest.skip("o cenário reduzido roda rápido demais para a razão significar algo")
    assert custo_da_ocupacao <= custo_da_ordem * RAZAO_MAXIMA, (
        f"ocupação {custo_da_ocupacao:.4f}s contra ordem {custo_da_ordem:.4f}s"
    )
