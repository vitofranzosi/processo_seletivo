"""O custo da lista de Processos é constante para **todo** papel, em toda aba, busca e página (129).

**Por que existe.** O teste de escala da `104` (`test_trabalho_em_escala.py`) mede quatro papéis, e
nenhum exporta para matrícula. Era justamente esse o único papel cujo custo crescia com o acervo:
a coluna de ações perguntava, Edital a Edital, se ele declara Requerimento de Matrícula — duas
consultas por Edital, 451 com 249 Editais e 1 323 com 739 (revisão de 06/11/2026, seção 6). A coluna
saiu (D-007), e o custo com ela; este teste é o que impede a pergunta de voltar à lista por outra
porta.

Os Editais têm inscrição (publicados, alguns encerrados) e **metade declara o Requerimento**: sem
isso, o ramo do exportador nem seria exercitado. Ficam em Processos de várias situações, e há
Processos bastantes para duas páginas, para que a medida passe pelo recorte e pela paginação.
"""

import pytest
from django.db import connection
from django.test import Client
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from processo_seletivo.interface.identidade import PAPEIS
from processo_seletivo.processos.models import Edital, ProcessoSeletivo
from processo_seletivo.requerimentos.domain import nomes as nomes_do_requerimento
from tests.fixtures.lista_de_processos import muitos, processo
from tests.interface.conftest import identificar
from tests.performance.test_visao_institucional import conteudo, publicar_direto

pytestmark = [pytest.mark.django_db, pytest.mark.performance]

TAMANHOS = (3, 30, 300)
RECORTES = ("", "?pagina=2", "?situacao=encerrados", "?situacao=todos", "?busca=Processo")


def com_requerimento(seed):
    """Metade dos Editais declara o Requerimento de Matrícula — o ramo que custava por Edital."""
    corpo = conteudo(seed)
    if seed % 2 == 0:
        corpo["matriculationRequest"] = {"moment": nomes_do_requerimento.NA_INSCRICAO}
    return corpo


def _acrescentar(quantos, primeiro):
    """`quantos` Editais publicados num Processo novo; o de número par termina encerrado."""
    criado = publicar_direto(quantos, ano=2026, primeiro=primeiro, fabrica=com_requerimento)
    if (primeiro // 3) % 2:
        ProcessoSeletivo.objects.filter(pk=criado.pk).update(
            status=ProcessoSeletivo.Status.ENCERRADO
        )
        Edital.objects.filter(processo=criado).update(status=Edital.Status.ENCERRADO)


def consultas(cliente, recorte):
    with CaptureQueriesContext(connection) as capturadas:
        assert cliente.get(reverse("interface:lista") + recorte).status_code == 200
    return len(capturadas)


@pytest.mark.parametrize(
    "papeis",
    [[papel] for papel in sorted(PAPEIS)] + [sorted(PAPEIS)],
    ids=[*sorted(PAPEIS), "todos"],
)
def test_as_consultas_da_lista_nao_crescem_nem_mudam_com_o_recorte(settings, papeis):
    settings.INTERFACE_SELETOR_IDENTIDADE = True
    muitos(25)
    processo(
        "Processo cancelado",
        status=ProcessoSeletivo.Status.CANCELADO,
        editais=[("9", 2025, "CANCELADO")],
    )
    cliente = Client()
    identificar(cliente, "pessoa.da.escala", papeis)

    medidas, criados = {}, 0
    for tamanho in TAMANHOS:
        # Em três lotes por tamanho, para que os Editais caiam em Processos de situações diferentes.
        faltam = tamanho - criados
        for lote in (faltam // 3, faltam // 3, faltam - 2 * (faltam // 3)):
            if lote:
                _acrescentar(lote, criados)
                criados += lote
        medidas[tamanho] = {recorte: consultas(cliente, recorte) for recorte in RECORTES}

    assert Edital.objects.filter(status__in=("PUBLICADO", "ENCERRADO")).count() >= 300
    valores = {valor for por_recorte in medidas.values() for valor in por_recorte.values()}
    assert len(valores) == 1, medidas
