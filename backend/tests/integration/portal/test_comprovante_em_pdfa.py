"""O comprovante sai do escritor que a inscrição registrou no envio (178, FR-8163 a FR-8165).

A inscrição enviada antes da `178` recebe, para sempre, o comprovante de antes, byte a byte: a
página dela já mostrou ao candidato o SHA-256 do arquivo (D-002). A enviada depois recebe o PDF/A. E
nos dois casos a página e o download usam o mesmo escritor, ou o resumo publicado deixaria de
conferir.

**O "antes" é produzido pela própria migration**, e não por um `UPDATE` na enviada, que o gatilho da
`0007` recusa: a inscrição é enviada pelo caminho da aplicação, a `0008` é desfeita e refeita, e a
coluna renasce falsa na linha que já existia — exatamente o que acontece na implantação.
"""

from hashlib import sha256

import pytest
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.urls import reverse

from processo_seletivo.inscricoes.application.rascunho import anexar_documento, gravar_dados
from processo_seletivo.inscricoes.application.submissao import enviar_inscricao
from processo_seletivo.inscricoes.models import Inscricao
from tests.fixtures.candidato import MARIA, MODALIDADE_AC, identificar, pdf
from tests.fixtures.selecao import DOCUMENTO_DE_TODOS, DOCUMENTO_DO_PERFIL

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

MIGRATION = ("inscricoes", "0008_comprovante_em_pdfa")


def _enviar(inscricao, chave="envio-pdfa"):
    inscricao = gravar_dados(
        identidade=MARIA, inscricao=inscricao, dados={"modality_id": MODALIDADE_AC}
    )
    for requisito, nome in ((DOCUMENTO_DE_TODOS, "rg.pdf"), (DOCUMENTO_DO_PERFIL, "diploma.pdf")):
        anexar_documento(
            identidade=MARIA, inscricao=inscricao, requirement_id=requisito, arquivo=pdf(nome)
        )
    inscricao.refresh_from_db()
    return enviar_inscricao(
        identidade=MARIA,
        inscricao=inscricao,
        declaracoes={"veracidade": True, "ciencia": True},
        idempotency_key=chave,
    )


def _refazer_a_migration():
    """Desfaz e refaz a `0008`: as linhas que existiam renascem com o escritor antigo."""
    executor = MigrationExecutor(connection)
    executor.loader.build_graph()
    pais = executor.loader.graph.node_map[MIGRATION].parents
    (anterior,) = [pai.key for pai in pais if pai.key[0] == "inscricoes"]
    executor.migrate([anterior])
    executor.loader.build_graph()
    executor.migrate([no for no in executor.loader.graph.leaf_nodes() if no[0] == "inscricoes"])


def _baixado_e_publicado(client, inscricao):
    arquivo = client.get(reverse("portal:comprovante-pdf", args=[inscricao.id])).content
    pagina = client.get(reverse("portal:comprovante", args=[inscricao.id])).content.decode()
    return arquivo, pagina


def test_a_inscricao_enviada_depois_da_178_recebe_o_comprovante_em_pdfa(client, inscricao_de_maria):
    """FR-8163, FR-8165: PDF/A, e o resumo da página é o do arquivo baixado."""
    enviada = _enviar(inscricao_de_maria)
    assert enviada.comprovante_em_pdfa is True
    identificar(client, MARIA)

    arquivo, pagina = _baixado_e_publicado(client, enviada)

    assert b"<pdfaid:part>2</pdfaid:part>" in arquivo
    assert b"/FontFile2" in arquivo
    assert sha256(arquivo).hexdigest() in pagina


def test_o_rascunho_de_antes_enviado_depois_recebe_o_pdfa(inscricao_de_maria):
    """FR-8163: o rascunho que a migration encontrou nasce com o escritor antigo, e o envio o troca.

    Nenhum resumo do comprovante foi mostrado antes do envio — não há promessa a guardar.
    """
    _refazer_a_migration()
    inscricao_de_maria.refresh_from_db()
    assert inscricao_de_maria.comprovante_em_pdfa is False

    enviada = _enviar(inscricao_de_maria)

    assert Inscricao.objects.get(pk=enviada.pk).comprovante_em_pdfa is True


def test_a_inscricao_enviada_antes_da_178_continua_com_o_comprovante_de_sempre(
    client, inscricao_de_maria
):
    """FR-8164, SC-2823: o escritor antigo, e o resumo que a página mostra continua o mesmo."""
    enviada = _enviar(inscricao_de_maria)
    identificar(client, MARIA)
    _, pagina_de_hoje = _baixado_e_publicado(client, enviada)

    _refazer_a_migration()
    enviada.refresh_from_db()
    assert enviada.comprovante_em_pdfa is False
    arquivo, pagina = _baixado_e_publicado(client, enviada)

    assert b"/BaseFont /Helvetica " in arquivo
    assert b"pdfaid" not in arquivo
    assert sha256(arquivo).hexdigest() in pagina, "a página e o download, do mesmo escritor"
    assert sha256(arquivo).hexdigest() not in pagina_de_hoje


def test_a_migration_nao_toca_a_enviada_pelo_gatilho(inscricao_de_maria):
    """A coluna nasce por catálogo, e não por `UPDATE`: o gatilho da `0007` não dispara."""
    enviada = _enviar(inscricao_de_maria)

    _refazer_a_migration()

    enviada.refresh_from_db()
    assert enviada.status == Inscricao.Status.SUBMETIDA
    assert enviada.comprovante_em_pdfa is False
