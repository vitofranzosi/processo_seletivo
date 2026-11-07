"""O recorte da lista de Processos no seletor: o grupo, a busca e a contagem (129).

**O recorte é pelo Processo** (D-001): Edital encerrado ainda convoca, recebe documento e recurso, e
o critério de "concluído" é a situação do Processo. O Processo final com Edital não final — o acervo
anterior à regra de 28/09 — vai para "Em andamento", e o recorte fica estritamente mais seguro que o
critério puro.
"""

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from processo_seletivo.processos.application.selectors import (
    ANDAMENTO,
    CANCELADOS,
    ENCERRADOS,
    contar_por_situacao,
    listar_processos,
)
from processo_seletivo.processos.models import ProcessoSeletivo
from processo_seletivo.seguranca.domain import Actor
from tests.fixtures.lista_de_processos import processo

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

Status = ProcessoSeletivo.Status
ATOR = Actor("leitora", "cefor", frozenset())


def titulos(consulta):
    return [p.title for p in consulta]


def grupo_de(titulo):
    return listar_processos(actor=ATOR).get(title=titulo).grupo


def test_o_grupo_de_cada_combinacao_de_processo_e_editais():
    processo("elaboracao", status=Status.EM_ELABORACAO)
    processo("ativo com encerrados", editais=[("1", 2026, "ENCERRADO"), ("2", 2026, "CANCELADO")])
    processo("encerrado com publicado", status=Status.ENCERRADO, editais=[("3", 2026, "PUBLICADO")])
    processo(
        "cancelado em elaboracao", status=Status.CANCELADO, editais=[("4", 2026, "EM_ELABORACAO")]
    )
    processo("encerrado final", status=Status.ENCERRADO, editais=[("5", 2026, "ENCERRADO")])
    processo("encerrado sem edital", status=Status.ENCERRADO)
    processo("cancelado final", status=Status.CANCELADO, editais=[("6", 2026, "CANCELADO")])

    assert {p.title: p.grupo for p in listar_processos(actor=ATOR)} == {
        "elaboracao": ANDAMENTO,
        # Edital encerrado ainda convoca: o Processo ativo fica em andamento.
        "ativo com encerrados": ANDAMENTO,
        # O acervo anterior a 28/09: o Edital não final puxa o Processo para "Em andamento".
        "encerrado com publicado": ANDAMENTO,
        "cancelado em elaboracao": ANDAMENTO,
        "encerrado final": ENCERRADOS,
        "encerrado sem edital": ENCERRADOS,
        "cancelado final": CANCELADOS,
    }


def test_as_tres_abas_particionam_a_unidade_e_todos_e_a_soma():
    processo("a", editais=[("1", 2026, "PUBLICADO")])
    processo("b", status=Status.ENCERRADO, editais=[("2", 2026, "ENCERRADO")])
    processo("c", status=Status.CANCELADO)
    processo("d", status=Status.ENCERRADO, editais=[("3", 2026, "HOMOLOGADO")])

    por_aba = {g: set(titulos(listar_processos(actor=ATOR, grupo=g))) for g in (0, 1, 2)}

    assert por_aba == {ANDAMENTO: {"a", "d"}, ENCERRADOS: {"b"}, CANCELADOS: {"c"}}
    assert set(titulos(listar_processos(actor=ATOR))) == {"a", "b", "c", "d"}
    contagem = contar_por_situacao(actor=ATOR)
    assert contagem.por_grupo == {ANDAMENTO: 2, ENCERRADOS: 1, CANCELADOS: 1}
    assert contagem.todos == 4


def test_a_ordem_e_do_mais_recente_ao_mais_antigo():
    processo("antigo", ha_minutos=30)
    processo("novo", ha_minutos=1)
    processo("meio", ha_minutos=10)

    assert titulos(listar_processos(actor=ATOR, grupo=ANDAMENTO)) == ["novo", "meio", "antigo"]


def test_outra_unidade_nao_aparece_nem_na_busca_nem_na_contagem():
    processo("nosso", editais=[("90", 2026, "PUBLICADO")])
    processo("alheio", editais=[("90", 2026, "PUBLICADO")], escopo="outra-unidade")

    assert titulos(listar_processos(actor=ATOR, busca="90/2026")) == ["nosso"]
    assert contar_por_situacao(actor=ATOR, busca="90/2026").encontrados_no_total == 1


def _busca(termo):
    return set(titulos(listar_processos(actor=ATOR, busca=termo)))


def test_a_busca_por_numero_e_ano():
    processo("de 2025", status=Status.CANCELADO, editais=[("90", 2025, "CANCELADO")])
    processo("de 2026", status=Status.CANCELADO, editais=[("90", 2026, "CANCELADO")])
    processo("cento e noventa", editais=[("190", 2026, "PUBLICADO")])
    processo("com zero", editais=[("01", 2026, "PUBLICADO")])

    assert _busca("90/2026") == {"de 2026"}
    assert _busca(" 90 / 2026 ") == {"de 2026"}
    # "N" sozinho casa o número em qualquer ano: pelo número, "190" não é o Edital 90 (o texto
    # também conta, e aqui nenhum título nem código contém "90").
    assert _busca("90") == {"de 2025", "de 2026"}
    # "N/AAAA" é identificador: o título que contém a citação de outro Edital não conta.
    processo(
        "Professor de Libras", editais=[("290", 2026, "PUBLICADO", "Edital 290/2026 — Libras")]
    )
    assert _busca("90/2026") == {"de 2026"}
    # O zero à esquerda não separa "1/2026" de "01/2026".
    assert _busca("1/2026") == {"com zero"}
    assert _busca("001") == {"com zero"}


def test_a_busca_por_titulo_codigo_e_titulo_de_edital_ignora_caixa_e_espacos():
    processo("Professor Substituto — Matemática", codigo="PS-DEMO-2026")
    processo(
        "Seleção de tutores",
        editais=[("7", 2026, "PUBLICADO", "Tutoria em Física"), ("8", 2026, "PUBLICADO", "Outro")],
    )

    assert _busca("  matemática ") == {"Professor Substituto — Matemática"}
    assert _busca("ps-demo") == {"Professor Substituto — Matemática"}
    assert _busca("DEMO-20") == {"Professor Substituto — Matemática"}
    # O título de um Edital traz o Processo — com todos os Editais, que a busca não filtra.
    [achado] = listar_processos(actor=ATOR, busca="física")
    assert achado.title == "Seleção de tutores"
    assert achado.editais.count() == 2


def test_barra_incompleta_se_busca_como_texto():
    processo("Edital 90/ de teste", editais=[("90", 2026, "PUBLICADO", "x")])
    processo("Programa /2026", editais=[("3", 2025, "PUBLICADO", "y")])
    processo("Nada a ver", editais=[("90", 2025, "PUBLICADO", "z")])

    assert _busca("90/") == {"Edital 90/ de teste"}
    assert _busca("/2026") == {"Programa /2026"}
    # "90/26" não é "N/AAAA" (o ano tem quatro dígitos): texto, e nenhum título o contém.
    assert _busca("90/26") == set()


def test_a_busca_ordena_por_grupo_e_depois_pela_ordem_das_abas():
    processo(
        "cancelado novo", status=Status.CANCELADO, editais=[("5", 2026, "CANCELADO")], ha_minutos=1
    )
    processo("encerrado", status=Status.ENCERRADO, editais=[("5", 2025, "ENCERRADO")], ha_minutos=2)
    processo("andamento antigo", editais=[("5", 2024, "PUBLICADO")], ha_minutos=50)
    processo("andamento novo", editais=[("5", 2023, "PUBLICADO")], ha_minutos=3)

    assert titulos(listar_processos(actor=ATOR, busca="5")) == [
        "andamento novo",
        "andamento antigo",
        "encerrado",
        "cancelado novo",
    ]
    contagem = contar_por_situacao(actor=ATOR, busca="5")
    assert contagem.encontrados_no_total == 4
    assert contagem.encontrados_finais == 2


def test_busca_so_com_espacos_e_ausencia_de_busca():
    processo("a")
    processo("b", status=Status.ENCERRADO)

    assert titulos(listar_processos(actor=ATOR, grupo=ANDAMENTO, busca="   ")) == ["a"]


def test_a_contagem_com_e_sem_busca_custa_uma_consulta():
    processo("a", editais=[("1", 2026, "PUBLICADO")])
    processo("b", status=Status.CANCELADO)

    for termo in ("", "a", "1/2026", "1"):
        with CaptureQueriesContext(connection) as capturadas:
            contar_por_situacao(actor=ATOR, busca=termo)
        assert len(capturadas) == 1, termo
