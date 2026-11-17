"""O comprovante sai do escritor que a inscrição registrou no envio (178, FR-8163 a FR-8165).

A inscrição enviada antes da `178` recebe, para sempre, o comprovante de antes, byte a byte: a
página dela já mostrou ao candidato o SHA-256 do arquivo (D-002). A enviada depois recebe o PDF/A. E
nos dois casos a página e o download usam o mesmo escritor, ou o resumo publicado deixaria de
conferir.

**O rascunho de antes é produzido pela própria migration**: desfeita e refeita, a `0008` recria a
coluna falsa na linha que já existia, como na implantação. **A enviada de antes, não**: o desfazer é
recusado quando há enviada no PDF/A, e o caso a produz pelo desvio que desliga o gatilho da `0007`.
"""

from hashlib import sha256

import pytest
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.urls import reverse

from processo_seletivo.inscricoes.application.rascunho import anexar_documento, gravar_dados
from processo_seletivo.inscricoes.application.submissao import enviar_inscricao
from processo_seletivo.inscricoes.infrastructure.comprovante_pdf import render_comprovante_pdf
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.portal.views import _dados_do_comprovante
from tests.fixtures.candidato import MARIA, MODALIDADE_AC, identificar, pdf
from tests.fixtures.comissao import sem_imutabilidade_da_enviada
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
    try:
        executor.migrate([anterior])
    finally:
        # **Reaplicar até as folhas mesmo quando o desfazer é recusado.** Voltar à `0007` desfaz
        # antes as migrations que dependem da `0008` — a `0009` da `180` foi a primeira —, e a
        # recusa da `0008` só acontece depois delas. Sem o `finally`, a coluna da `0009` ficava
        # faltando no banco do worker, e todo teste seguinte quebrava longe daqui.
        executor = MigrationExecutor(connection)
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


def _como_se_enviada_antes_da_178(enviada):
    """A enviada antes da `178`, como a migration a deixou: com o escritor antigo.

    **Desvio** (`sem_imutabilidade_da_enviada`): a enviada é imutável, e o produto não produz este
    estado depois da `0008` — ele só existe nas linhas que a migration encontrou. Desfazer e refazer
    a migration o produziria, mas o desfazer é recusado justamente quando há enviada no PDF/A.
    """
    with sem_imutabilidade_da_enviada():
        Inscricao.objects.filter(pk=enviada.pk).update(comprovante_em_pdfa=False)
    enviada.refresh_from_db()
    return enviada


def test_a_inscricao_enviada_antes_da_178_continua_com_o_comprovante_de_sempre(
    client, inscricao_de_maria
):
    """FR-8164, SC-2823: o escritor antigo, sobre os mesmos dados, e a página confere com ele."""
    enviada = _como_se_enviada_antes_da_178(_enviar(inscricao_de_maria))
    identificar(client, MARIA)

    resposta = client.get(reverse("portal:comprovante-pdf", args=[enviada.id]))
    pagina = client.get(reverse("portal:comprovante", args=[enviada.id])).content.decode()

    versao = enviada.versao_aceita
    dados = _dados_do_comprovante(resposta.wsgi_request, enviada, versao.content, versao)
    assert resposta.content == render_comprovante_pdf(dados, pdfa=False)
    assert b"/BaseFont /Helvetica " in resposta.content
    assert b"pdfaid" not in resposta.content
    assert sha256(resposta.content).hexdigest() in pagina, "a página e o download, mesmo escritor"


def test_desfazer_a_migration_e_recusado_com_enviada_no_pdfa(inscricao_de_maria):
    """Desfazer apagaria o registro, e refazer trocaria o comprovante de quem viu o resumo novo."""
    enviada = _enviar(inscricao_de_maria)
    assert enviada.comprovante_em_pdfa is True

    with pytest.raises(RuntimeError, match="1 inscrições enviadas já têm o comprovante em PDF/A"):
        _refazer_a_migration()

    enviada.refresh_from_db()
    assert enviada.comprovante_em_pdfa is True


def test_a_migration_nao_toca_a_enviada_pelo_gatilho(inscricao_de_maria):
    """A coluna nasce por catálogo, e não por `UPDATE`: o gatilho da `0007` não dispara."""
    enviada = _como_se_enviada_antes_da_178(_enviar(inscricao_de_maria))

    _refazer_a_migration()

    enviada.refresh_from_db()
    assert enviada.status == Inscricao.Status.SUBMETIDA
    assert enviada.comprovante_em_pdfa is False
