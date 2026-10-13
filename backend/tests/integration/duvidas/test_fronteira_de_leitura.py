"""A consulta só lê o publicado: nem rascunho, nem candidato, nem Retificação pendente (070, T012).

No padrão de `tests/portal/test_fronteira_publica.py`: a fronteira não é afirmada pela leitura do
código, e sim pelas tabelas que as consultas realmente tocam. As tabelas de elaboração do Edital
(`editais_*`) guardam, depois da publicação, o estado do dia da publicação, e não o vigente: lê-las
daria uma resposta da versão original de um Edital retificado (`FR-1412`).
"""

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from processo_seletivo.duvidas.application.consultar import consultar, pontos_para_revisao
from processo_seletivo.duvidas.domain import catalogo
from tests.fixtures.corpus import publicar_do_corpus

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

PROIBIDAS = (
    "inscricoes_",
    "divulgacao_",
    "resultados_",
    "classificacao_",
    "sorteios_",
    "convocacao_",
    "recursos_",
    "requerimentos_",
    "identidade_",
    "editais_",
    "publicacoes_revisaoedital",
    "publicacoes_homologacao",
    # As alterações de qualquer Retificação, publicada ou não: a consulta lê o consolidado, e não
    # o ato. A Retificação publicada só é lida junto da publicação dela, pela base que o documento
    # contém (`R-005`).
    "publicacoes_alteracaonormativa",
)


def test_toda_pergunta_le_so_o_publicado(api_client):
    edital, _ = publicar_do_corpus(api_client, "91", chave="fronteira")
    with CaptureQueriesContext(connection) as capturadas:
        agora = timezone.now()
        pontos_para_revisao(edital_id=edital.id, instante=agora)
        for pergunta in catalogo.PERGUNTAS:
            consultar(
                edital_id=edital.id,
                instante=agora,
                pergunta=pergunta.codigo,
                perfil="INF-BJN" if pergunta.parametros else None,
                modalidade="PPI" if catalogo.MODALIDADE in pergunta.parametros else None,
            )
    sql = "\n".join(consulta["sql"] for consulta in capturadas.captured_queries)
    # Pelo nome entre aspas, que é como o Django escreve tabela: `max_inscricoes_por_candidato` é
    # coluna do Edital, e não tabela de inscrição.
    tocadas = [tabela for tabela in PROIBIDAS if f'"{tabela}' in sql]
    assert tocadas == []
