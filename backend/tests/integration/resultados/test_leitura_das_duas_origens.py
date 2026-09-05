"""Os seletores leem as duas origens — e é isto que a 015 vai consumir (D-1).

O risco que estes testes cobrem não é a exceção: é o **silêncio**. Um seletor que percorresse
`avaliacao__versao` continuaria funcionando para os Resultados por Avaliação e simplesmente
deixaria os por Ocorrência de fora da ordem — sem erro, sem log, sem nada. Quem foi eliminado por
faltar reapareceria classificado, que é o pior modo possível de falhar.

Junto vai o custo: a norma passou a ser campo do Resultado, e `select_related("versao")` seria a
leitura óbvia — traria uma cópia do Edital inteiro em JSON por linha da página **sem mudar a
contagem de consultas**, de modo que nenhum teste de custo denunciaria. O que denuncia é contar
linhas de Versão Consolidada lidas, e é o que o último teste faz.
"""

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from processo_seletivo.resultados.application import selectors
from processo_seletivo.resultados.application.consolidacao import consolidar
from processo_seletivo.resultados.application.ocorrencia import registrar_ocorrencia
from processo_seletivo.resultados.application.prontidao import (
    participa_da_etapa,
    restringir_a_participantes,
)
from processo_seletivo.resultados.models import ResultadoEtapa
from tests.conftest import ator_institucional
from tests.fixtures.comissao import inscrever
from tests.fixtures.mesa import concluir_como, distribuir_para
from tests.fixtures.resultado import montar_etapa_de_leitura_unica

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

FALTOU = "não compareceu à Entrevista (item 6.3 do Edital)"


@pytest.fixture
def mistura(gestor, api_client, manager_headers):
    """Uma Etapa com as duas origens lado a lado — habilitada por avaliação, eliminada por falta."""
    cenario = montar_etapa_de_leitura_unica(
        gestor, api_client, manager_headers, seed=1800, codigo="1800"
    )
    avaliada, faltante = inscrever(cenario["edital"], 2, primeiro=1)
    presidente = ator_institucional("maria")

    distribuir_para(cenario, gestor, ["joao"], [avaliada], chave="lote-1800")
    concluir_como(cenario, "joao", avaliada, pontuacao="75")
    consolidar(
        actor=presidente,
        processo_id=cenario["processo"].id,
        edital_id=cenario["edital"].id,
        etapa_id=cenario["primeira"],
        inscricao_ids=[avaliada.id],
        idempotency_key="c-1800",
        correlation_id="teste",
    )
    registrar_ocorrencia(
        actor=presidente,
        processo_id=cenario["processo"].id,
        edital_id=cenario["edital"].id,
        etapa_id=cenario["primeira"],
        inscricao_ids=[faltante.id],
        motivo=FALTOU,
        idempotency_key="o-1800",
        correlation_id="teste",
    )
    cenario["avaliada"] = avaliada
    cenario["faltante"] = faltante
    return cenario


def test_a_listagem_traz_as_duas_e_a_norma_de_cada_uma(mistura):
    """A consulta que responde a recurso não pode perder metade dos desfechos."""
    pagina = selectors.resultados_da_etapa(edital=mistura["edital"], etapa_id=mistura["primeira"])
    linhas = {linha.inscricao_id: linha for linha in pagina}
    assert set(linhas) == {mistura["avaliada"].id, mistura["faltante"].id}

    por_ocorrencia = linhas[mistura["faltante"].id]
    assert por_ocorrencia.avaliacao is None, "a junção da fonte é `LEFT`, e não some com a linha"
    assert por_ocorrencia.versao_id is not None

    vigencias = selectors.vigencias_das_versoes({linha.versao_id for linha in linhas.values()})
    assert all(vigencias.get(linha.versao_id) is not None for linha in linhas.values())


def test_a_contestacao_superveniente_ignora_quem_nao_tem_fonte(mistura):
    """Sem Avaliação não há impedimento a cruzar — e a leitura não pode estourar por isso."""
    linhas = list(
        selectors.resultados_da_etapa(edital=mistura["edital"], etapa_id=mistura["primeira"])
    )
    assert selectors.contestacoes_supervenientes(linhas) == {}


def test_os_conjuntos_da_progressao_contam_as_duas_origens(mistura):
    """`ELIMINADA` é `ELIMINADA`, qualquer que seja a origem que a produziu (D-003)."""
    edital, primeira = mistura["edital"], mistura["primeira"]
    assert selectors.ha_resultado_em(edital=edital, etapa_id=primeira)
    assert selectors.inscricoes_com_resultado(edital=edital, etapa_id=primeira) == {
        mistura["avaliada"].id,
        mistura["faltante"].id,
    }
    assert selectors.habilitadas_em(edital=edital, etapa_id=primeira) == {mistura["avaliada"].id}
    assert selectors.eliminadas_ate(edital=edital, etapas_ids=[primeira]) == {
        mistura["faltante"].id
    }


def test_a_restricao_em_conjunto_e_a_individual_concordam_sobre_a_ocorrencia(mistura):
    """As duas formas da mesma regra: a de listagem e a da rota individual.

    Divergirem seria a pior combinação — a organização excluiria e a Mesa entregaria.
    """
    from processo_seletivo.inscricoes.models import Inscricao

    edital, segunda = mistura["edital"], mistura["segunda"]
    restantes = set(
        restringir_a_participantes(
            Inscricao.objects.filter(edital=edital), edital=edital, etapa_id=segunda, prefixo=""
        ).values_list("id", flat=True)
    )
    assert mistura["faltante"].id not in restantes
    assert mistura["avaliada"].id in restantes

    assert not participa_da_etapa(
        edital=edital, etapa_id=segunda, inscricao_id=mistura["faltante"].id
    )
    assert participa_da_etapa(edital=edital, etapa_id=segunda, inscricao_id=mistura["avaliada"].id)


def test_a_versao_nao_e_lida_uma_vez_por_linha(mistura):
    """O alerta que a materialização da norma criou, verificado onde ele se manifesta.

    `select_related("versao")` não mudaria a **contagem** de consultas — mudaria o que cada uma
    traz. Por isso a asserção é sobre a consulta que carrega o conteúdo do Edital: ela existe uma
    vez por versão distinta, e não uma por Resultado.
    """
    with CaptureQueriesContext(connection) as consultas:
        pagina = selectors.resultados_da_etapa(
            edital=mistura["edital"], etapa_id=mistura["primeira"]
        )
        linhas = list(pagina)
        selectors.vigencias_das_versoes({linha.versao_id for linha in linhas})

    assert len(linhas) == 2
    tocam_a_versao = [
        consulta["sql"]
        for consulta in consultas.captured_queries
        if "publicacoes_versaoconsolidada" in consulta["sql"]
    ]
    assert len(tocam_a_versao) == 1, tocam_a_versao
    # E o conteúdo do Edital não viaja junto da listagem: a única consulta que toca a Versão é a
    # da vigência, e ela pede duas colunas.
    assert "content" not in tocam_a_versao[0]


def test_a_etapa_seguinte_conserva_quem_a_ocorrencia_nao_alcancou(mistura):
    """A ocorrência exclui quem ela nomeia, e só ele: nada de esvaziar a Etapa seguinte."""
    from processo_seletivo.resultados.application.prontidao import participacao

    participantes, eliminadas, _ = participacao(
        edital=mistura["edital"], etapa_id=mistura["segunda"]
    )
    assert eliminadas == {mistura["faltante"].id}
    assert participantes == {mistura["avaliada"].id}
    assert ResultadoEtapa.objects.filter(edital=mistura["edital"]).count() == 2
