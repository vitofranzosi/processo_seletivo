"""O que os testes do relatório consolidado (100) compartilham: o conjunto, a leitura e o texto.

Os Editais saem do cenário coerente da `099`, cada um com o seu número e a sua data de publicação:
o ciclo inteiro, pelos comandos da aplicação, e as mesmas pessoas inscritas em todos.
"""

import pytest
from django.http import QueryDict

from processo_seletivo.interface import relatorio_consolidado as rc
from processo_seletivo.interface import relatorio_consolidado_pdf
from processo_seletivo.unidades.models import Unidade
from tests.conftest import ator_institucional
from tests.fixtures.relatorio import REFERENCIA, dia, montar_cenario

GESTOR = ator_institucional("gustavo.gestor", "visao:consultar", "comissao:gerir")


def consulta(texto=""):
    return QueryDict(texto, mutable=True)


def conjunto(texto="", ator=GESTOR):
    return rc.conjunto_de(ator, consulta(texto), hoje=REFERENCIA.date())


def ler(conjunto_, agora=REFERENCIA):
    return rc.ler(conjunto_, agora=agora, unidade=Unidade.objects.get(codigo="cefor"))


def texto_do_documento(consolidado, emissao=1):
    """O texto realmente desenhado no PDF, com os espaços normalizados entre linhas e trechos."""
    from tests.interface.test_fluxo import texto_de_pdf_bytes

    texto = texto_de_pdf_bytes(relatorio_consolidado_pdf.compor(consolidado, emissao=emissao))
    return " ".join(texto.split())


@pytest.fixture
def tres_editais(db):
    """Dois encerrados — um com convocação no prazo, outro sem pendência — e um cancelado.

    O 62 foi publicado em fevereiro, os outros em agosto: o 1º semestre alcança só o 62.
    """
    return {
        "61": montar_cenario(final="pendente"),
        "62": montar_cenario(final="sem-pendencia", numero="62", publicado_em=dia(10, 2, 9)),
        "63": montar_cenario(final="cancelado", numero="63", maximo=4),
    }


@pytest.fixture
def em_elaboracao(api_client, manager_headers, process_payload):
    """Um Edital de 2026 ainda em elaboração, no mesmo escopo dos do cenário."""
    from processo_seletivo.processos.models import Edital

    dados = {**process_payload, "institutionalCode": "PS-ELABORACAO-100"}
    criado = api_client.post("/api/v1/admin/processos", dados, format="json", **manager_headers)
    assert criado.status_code == 201, criado.content
    return Edital.objects.get(processo_id=criado.json()["id"])
