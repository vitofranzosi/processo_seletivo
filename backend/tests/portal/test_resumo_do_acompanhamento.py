"""O resumo de resultados e prazos de recurso no cartão da vitrine (072, D-004, FR-1629 a 1633).

Sem banco: a regra é uma função sobre a lista de vigentes que a página da seleção já monta, e é
aqui que se prova cada combinação — inclusive as que o seed não produz (várias listas, prazos
diferentes).
A regra foi confirmada pelo responsável pelo produto em 12/10: prazo dito uma vez só quando vale,
com o mesmo término, para todos os vigentes; senão, "aberto para N de M", com o primeiro término
entre os abertos.
"""

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

from processo_seletivo.portal.leitura import resumo_do_acompanhamento

PUBLICADO = datetime(2026, 10, 12, 15, 0, tzinfo=UTC)
FIM = datetime(2026, 10, 17, 23, 59, tzinfo=UTC)


def vigente(*, natureza="PRELIMINAR", minutos=0, recurso_ate=None):
    rotulos = {"PRELIMINAR": "Resultado preliminar", "DEFINITIVA": "Resultado definitivo"}
    return {
        "publicacao": SimpleNamespace(
            natureza=natureza, publicado_em=PUBLICADO + timedelta(minutes=minutos)
        ),
        "natureza_rotulo": rotulos[natureza],
        "recurso_ate": recurso_ate,
    }


def test_sem_vigente_nao_ha_resumo():
    assert resumo_do_acompanhamento([]) is None


def test_um_vigente_com_prazo_diz_a_natureza_a_data_e_o_prazo_uma_vez():
    resumo = resumo_do_acompanhamento([vigente(recurso_ate=FIM)])

    assert resumo["total"] == 1
    assert resumo["natureza"] == "Resultado preliminar"
    assert resumo["mais_recente"] == PUBLICADO
    assert resumo["prazo_unico"] == FIM
    assert resumo["primeiro_prazo"] is None
    assert resumo["abertos"] == 1


def test_um_vigente_com_prazo_encerrado_nao_tem_frase_de_prazo():
    resumo = resumo_do_acompanhamento([vigente()])

    assert resumo["abertos"] == 0
    assert resumo["prazo_unico"] is None
    assert resumo["primeiro_prazo"] is None


def test_todos_abertos_com_o_mesmo_termino_dizem_o_prazo_uma_vez():
    resumo = resumo_do_acompanhamento(
        [
            vigente(recurso_ate=FIM),
            vigente(minutos=5, recurso_ate=FIM),
            vigente(minutos=9, recurso_ate=FIM),
        ]
    )

    assert resumo["prazo_unico"] == FIM
    assert resumo["primeiro_prazo"] is None
    assert resumo["mais_recente"] == PUBLICADO + timedelta(minutes=9)


def test_so_parte_aberta_diz_n_de_m_e_o_termino_do_aberto():
    resumo = resumo_do_acompanhamento(
        [vigente(), vigente(minutos=5, recurso_ate=FIM), vigente(minutos=9)]
    )

    assert (resumo["abertos"], resumo["total"]) == (1, 3)
    assert resumo["prazo_unico"] is None
    assert resumo["primeiro_prazo"] == FIM


def test_terminos_diferentes_dizem_o_primeiro_entre_os_abertos():
    """Todos abertos, mas não juntos: nenhum prazo vale para todos, e o mais próximo é o útil."""
    cedo = FIM - timedelta(days=2)
    resumo = resumo_do_acompanhamento(
        [vigente(recurso_ate=FIM), vigente(minutos=5, recurso_ate=cedo)]
    )

    assert (resumo["abertos"], resumo["total"]) == (2, 2)
    assert resumo["prazo_unico"] is None
    assert resumo["primeiro_prazo"] == cedo


def test_a_natureza_so_e_dita_quando_e_a_de_todos():
    """062, FR-1155: a natureza é de cada lista, e o cartão não a atribui ao conjunto."""
    mista = resumo_do_acompanhamento([vigente(), vigente(natureza="DEFINITIVA", minutos=5)])
    comum = resumo_do_acompanhamento(
        [vigente(natureza="DEFINITIVA"), vigente(natureza="DEFINITIVA")]
    )

    assert mista["natureza"] == ""
    assert mista["natureza_no_plural"] == ""
    assert comum["natureza"] == "Resultado definitivo"
    assert comum["natureza_no_plural"] == "resultados definitivos"
