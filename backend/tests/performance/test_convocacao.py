"""O custo de abrir a tela do recorte e o de ler o histórico (019, `SC-088`, `SC-090`).

**O modo de errar aqui é invisível com 40 pessoas e mata com 1.000.** Uma consulta por convocação
não aparece no cenário de teste comum — aparece no certame real, quando a tela que a comissão abre
dez vezes por dia passa a custar segundos. A medição é da **contagem de consultas**, e não só do
relógio: o relógio depende da máquina, e a contagem depende do desenho.

**O precedente está medido.** A tela do corte com 10.000 participantes custou 0,277 s contra teto de
3 s, e a contagem de consultas ficou intacta de 5 a 20.000 (`R-010`). O que se prende aqui é a mesma
propriedade: o custo é do **conjunto**, e não cresce com o número de chamadas praticadas.
"""

import time

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from processo_seletivo.convocacao.application import selectors
from processo_seletivo.convocacao.models import Convocacao
from processo_seletivo.ocupacao.application.selectors import apuracao_vigente
from tests.fixtures.convocacao import montar_cenario_da_convocacao
from tests.fixtures.corte import MARCO
from tests.fixtures.edital import PROFILE_ID

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

TETO_EM_SEGUNDOS = 3.0


@pytest.fixture
def cenario(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    return montar_cenario_da_convocacao(
        gestor, api_client, manager_headers, process_payload, prefixo="perf-019"
    )


def semear(edital, quantas, *, desde=0):
    """`quantas` convocações praticadas no recorte, gravadas direto.

    **Direto, e não pelo comando**: o que se mede é o custo da **leitura**, e fazer o comando
    percorrer autorização e idempotência mil vezes mediria outra coisa — e levaria minutos.
    """
    from processo_seletivo.inscricoes.models import Inscricao
    from processo_seletivo.publicacoes.application.selectors import effective_version

    apuracao = apuracao_vigente(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None)
    versao = effective_version(edital_id=edital.id)
    agora = timezone.now()
    inscricoes = [
        Inscricao.objects.create(
            created_at=agora,
            identity_subject=f"cpf:perf-{numero:05d}",
            edital=edital,
            profile_id=PROFILE_ID,
            nome=f"Candidata {numero}",
            email=f"perf{numero}@exemplo.test",
            protocolo=f"INS-2026-P{numero:04d}",
        )
        for numero in range(desde, desde + quantas)
    ]
    Convocacao.objects.bulk_create(
        Convocacao(
            edital=edital,
            perfil_id=PROFILE_ID,
            marco_id=MARCO,
            lista_id=None,
            inscricao=inscricao,
            especie="VAGA_INICIAL",
            fundamento="Semeada para medição.",
            apuracao=apuracao,
            ato_de_ordenacao_id=apuracao.ato_id,
            corte_id=apuracao.corte_id,
            versao=versao,
            criado_por="medicao",
            criado_em=agora,
        )
        for inscricao in inscricoes
    )
    return inscricoes


def ler_o_recorte(edital):
    return selectors.leitura_do_recorte(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )


def consultas_para(funcao):
    with CaptureQueriesContext(connection) as capturadas:
        funcao()
    return len(capturadas)


def test_a_contagem_de_consultas_nao_cresce_com_o_numero_de_convocacoes(cenario):
    """`SC-088` e `SC-090`: o custo é do conjunto.

    **É a propriedade, e não o número.** Comparar contra uma constante prenderia a implementação de
    hoje; comparar 5 com 200 prova o que importa — que a curva é plana. Uma consulta por convocação
    faria a segunda medição custar quarenta vezes a primeira.
    """
    edital, _, _ = cenario
    semear(edital, 5)
    poucas = consultas_para(lambda: ler_o_recorte(edital))

    semear(edital, 200, desde=5)
    muitas = consultas_para(lambda: ler_o_recorte(edital))

    assert muitas <= poucas + 2, (
        f"a leitura do recorte passou de {poucas} para {muitas} consultas ao ir de 5 para 205 "
        "convocações: há uma consulta por chamada em algum ponto"
    )


def test_o_historico_responde_por_conjunto(cenario):
    """`SC-088`, `T088b`: o histórico carrega desfechos e comunicações de uma vez."""
    edital, _, _ = cenario
    semear(edital, 5)
    poucas = consultas_para(
        lambda: selectors.convocacoes_do_recorte(
            edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
        )
    )

    semear(edital, 200, desde=5)
    muitas = consultas_para(
        lambda: selectors.convocacoes_do_recorte(
            edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
        )
    )

    assert muitas == poucas, (
        f"o histórico passou de {poucas} para {muitas} consultas: o `prefetch_related` deixou de "
        "cobrir alguma relação"
    )


def test_a_tela_do_recorte_abre_abaixo_do_teto_com_mil_participantes(cenario):
    """`SC-090`: 1.000 participantes, teto de 3 s.

    **O relógio é o piso da garantia, e a contagem de consultas é o teto.** Uma máquina lenta faria
    esta medição falhar sem que o desenho tivesse piorado — por isso ela vem acompanhada da
    asserção de curva plana acima, que é a que de fato prende o defeito.
    """
    edital, _, _ = cenario
    semear(edital, 1000)

    inicio = time.perf_counter()
    leitura = ler_o_recorte(edital)
    decorrido = time.perf_counter() - inicio

    assert leitura["convocadas"] >= 1000
    assert decorrido < TETO_EM_SEGUNDOS, (
        f"a tela do recorte levou {decorrido:.3f}s com 1.000 convocações, contra teto de "
        f"{TETO_EM_SEGUNDOS}s"
    )
