"""A consulta lê um número fixo de vezes, e nunca bytes de documento ou anexo (070, `R-019`, T011).

**Por que contar consultas, e não medir tempo.** Teste de tempo falha por motivo errado em CI
(`backend/scripts/carga_publica.py`). O que impede a regressão real é a leitura por listagem — uma
consulta por Perfil, por documento ou por Retificação —, e é isso que o número fixo prende: o
92/2026 tem dezoito Perfis, e o 01/2026, duas Retificações, uma delas de vigência futura.
"""

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from processo_seletivo.duvidas.application.consultar import consultar
from processo_seletivo.processos.application.finalizacao import cancel_edital
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from processo_seletivo.seguranca.domain import Actor
from tests.fixtures.corpus import publicar_do_corpus

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

#: Edital; versão vigente e proveniência (duas); futuras; publicações. Sempre.
FIXAS = 5
#: Só quando há o que ler: a proveniência das futuras, a versão anterior informada, o ato do
#: desfecho. O teto de `R-019` é a soma.
ORCAMENTO = FIXAS + 3

GESTORA = Actor("gestora.orcamento", "cefor", frozenset({"edital:cancelar"}))

#: Tabelas com bytes que a consulta nunca lê: documento publicado e artefato de anexo.
TABELAS_DE_BYTES = ("publicacoes_documentopublicado", "editais_artefatoanexo")


def _consultas(edital, pergunta, **parametros):
    with CaptureQueriesContext(connection) as capturadas:
        consultar(edital_id=edital.id, instante=timezone.now(), pergunta=pergunta, **parametros)
    return [consulta["sql"] for consulta in capturadas.captured_queries]


def test_o_numero_de_consultas_nao_cresce_com_perfis_nem_com_retificacoes(api_client):
    pequeno, _ = publicar_do_corpus(api_client, "01", chave="c01")
    grande, _ = publicar_do_corpus(api_client, "92", chave="c92")

    no_pequeno = _consultas(pequeno, "P-05", perfil="DOC-INFO", modalidade="nenhuma")
    no_grande = _consultas(grande, "P-05", perfil="TP-01", modalidade="nenhuma")

    # **Exatos, e não "até o teto"**: com folga, uma consulta a mais por Retificação ou duas por
    # Perfil passavam (revisão de 12/10). O 01/2026 tem uma versão futura e duas Retificações — a
    # proveniência das futuras é a única a mais —; o 92/2026, dezoito Perfis e nenhuma futura.
    assert len(no_pequeno) == FIXAS + 1, no_pequeno
    assert len(no_grande) == FIXAS, no_grande


def test_as_consultas_condicionais_sao_uma_cada(api_client):
    edital, _ = publicar_do_corpus(api_client, "92", chave="c92-condicionais")
    anterior = VersaoConsolidada.objects.filter(edital=edital).earliest("valid_from")
    atual = VersaoConsolidada.objects.filter(edital=edital).latest("valid_from")
    assert anterior.id != atual.id, "o 92/2026 precisa de duas versões"
    com_anterior = _consultas(edital, "P-02", versao_anterior=anterior.id)
    assert len(com_anterior) == FIXAS + 1, com_anterior

    edital.refresh_from_db()
    cancel_edital(
        actor=GESTORA,
        edital_id=edital.id,
        expected_revision=edital.revision,
        reason="Cancelamento para medir a consulta do desfecho.",
        idempotency_key=f"cancelar-orcamento-{edital.id}",
        correlation_id="070-orcamento",
    )
    com_tudo = _consultas(edital, "P-02", versao_anterior=anterior.id)
    assert len(com_tudo) == FIXAS + 2, com_tudo
    assert len(com_tudo) <= ORCAMENTO


def test_nenhuma_consulta_le_bytes_de_documento_ou_anexo(api_client):
    edital, _ = publicar_do_corpus(api_client, "91", chave="c91")
    sql = " ".join(
        _consultas(edital, "P-05", perfil="INF-BJN", modalidade="PcD") + _consultas(edital, "P-12")
    )
    assert not [tabela for tabela in TABELAS_DE_BYTES if tabela in sql]
