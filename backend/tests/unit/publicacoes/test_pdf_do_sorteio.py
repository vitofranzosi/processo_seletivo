"""O documento publicado exibe a proveniência do sorteio — e o do ato computado, não (FR-046).

**As duas metades importam igualmente.** A primeira é o requisito: identidade, algoritmo, semente e
os dois resumos aparecem no papel, para que quem o recebe possa conferir sem pedir nada à
instituição. A segunda é a regressão: o documento de um resultado **computado** sai exatamente como
saía, sem bloco vazio e sem afirmar, por omissão de conteúdo, que aquele resultado não foi sorteado.
"""

import pytest
from django.utils import timezone

from processo_seletivo.divulgacao.domain.conteudo import compor, conteudo_divulgado
from processo_seletivo.divulgacao.infrastructure.documento import render_resultado_pdf
from processo_seletivo.sorteios.models import Sorteio
from tests.unit.sorteios.test_manifesto import sorteado  # noqa: F401 — fixture compartilhada

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

CINCO_DADOS = ("Sorteio", "Algoritmo", "Semente", "Resumo da rela", "Resumo do manifesto")


def _divulgado(ato):
    """O documento é renderizado sobre o conteúdo **divulgado**, e não sobre a composição crua."""
    from processo_seletivo.publicacoes.domain.autoridades import escolher

    return conteudo_divulgado(
        compor(ato),
        natureza="PRELIMINAR",
        publicado_em=timezone.now(),
        signatario=escolher("diretoria-cefor"),
    )


def test_o_conteudo_divulgado_carrega_a_proveniencia_do_sorteio(sorteado):  # noqa: F811
    _certame, sorteio = sorteado

    composicao = compor(sorteio.ato)

    proveniencia = composicao["cabecalho"]["sorteio"]
    assert proveniencia["id"] == str(sorteio.id)
    assert proveniencia["algoritmo"] == "IFES-SORTEIO-SHA256-v1"
    assert proveniencia["semente"] == sorteio.semente_normalizada
    assert proveniencia["relacao_resumo"] == sorteio.relacao.resumo
    assert proveniencia["metodo_resumo"] == sorteio.metodo_hash
    assert proveniencia["manifesto_resumo"] == sorteio.manifesto_hash


def test_o_documento_publicado_exibe_os_cinco_dados(sorteado):  # noqa: F811
    _certame, sorteio = sorteado

    bytes_do_pdf = render_resultado_pdf(_divulgado(sorteio.ato))

    assert bytes_do_pdf.startswith(b"%PDF")
    corpo = bytes_do_pdf.decode("latin-1")
    for rotulo in CINCO_DADOS:
        assert rotulo in corpo or rotulo.encode("latin-1", "ignore").decode("latin-1") in corpo
    assert "Ordem constitu" in corpo, "o documento nomeia a origem da ordem"


def test_o_documento_de_um_ato_computado_segue_sem_a_secao(
    gestor, api_client, manager_headers, process_payload
):
    """A regressão: nada muda para os milhares de atos que nunca tiveram a pergunta colocada."""
    from tests.fixtures.divulgacao import montar_ato_publicavel

    cenario = montar_ato_publicavel(gestor, api_client, manager_headers, process_payload)

    composicao = _divulgado(cenario["ato"])
    corpo = render_resultado_pdf(composicao).decode("latin-1")

    assert "sorteio" not in composicao["cabecalho"], "chave ausente, e não chave vazia"
    assert "Ordem constitu" not in corpo
    assert not Sorteio.objects.filter(ato=cenario["ato"]).exists()
