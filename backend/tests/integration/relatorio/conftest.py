"""O que os testes do relatório do Edital (099) compartilham: endereços e a leitura do texto."""

import pytest

from processo_seletivo.interface import relatorio_do_edital, relatorio_pdf
from tests.fixtures.relatorio import REFERENCIA, montar_cenario

SELECAO = "https://gps.exemplo/selecoes/61/"


class Enderecos:
    """Endereços públicos fixos: a derivação não conhece a requisição (R-005)."""

    def selecao(self):
        return SELECAO

    def resultado(self, publicacao_id):
        return f"https://gps.exemplo/selecoes/resultados/{publicacao_id}/"


def ler(cenario, agora=REFERENCIA):
    return relatorio_do_edital.ler(cenario.edital, agora=agora, enderecos=Enderecos())


def texto_do_documento(relatorio, emissao=1):
    """O texto realmente desenhado no PDF, com os espaços normalizados entre linhas e trechos."""
    from tests.interface.test_fluxo import texto_de_pdf_bytes

    texto = texto_de_pdf_bytes(relatorio_pdf.compor(relatorio, emissao=emissao))
    return " ".join(texto.split())


def executiva_e_anexo(texto):
    executiva, _, anexo = texto.partition("Anexo técnico")
    return executiva, anexo


@pytest.fixture
def pendente(db):
    """O cenário da maquete v2: encerrado com a convocação reservada no prazo."""
    return montar_cenario(final="pendente")
