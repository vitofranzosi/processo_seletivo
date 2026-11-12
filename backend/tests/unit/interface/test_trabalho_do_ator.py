"""As partes puras da derivação do trabalho: ordem, faixa e rótulos (104, R-001, R-008).

O que depende do banco — quem vê o quê — está nas jornadas de `test_acoes_disponiveis.py`. Aqui fica
o que se lê sem requisição: a regra de ordem que não sugere urgência, o corte em cinco, e os rótulos
que distinguem a devolvida do rascunho que nunca saiu.
"""

from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

import pytest

from processo_seletivo.interface import atos_retificacao, trabalho


def edital(numero, ano=2026):
    return SimpleNamespace(id=uuid4(), number=numero, year=ano)


def objeto(numero, desde=None, natureza="retificacao", ano=2026):
    e = edital(numero, ano)
    return trabalho.ObjetoDeTrabalho(natureza, (natureza, e.id), "t", "a", "s", "", "/u", e, desde)


def test_quem_espera_ha_mais_tempo_vem_primeiro_e_o_resto_pelo_edital():
    antiga = objeto("26", datetime(2026, 10, 1, tzinfo=UTC))
    recente = objeto("01", datetime(2026, 10, 29, tzinfo=UTC))
    sem_instante_10 = objeto("10")
    sem_instante_2 = objeto("2")

    ordenados = sorted([sem_instante_10, recente, sem_instante_2, antiga], key=trabalho._ordem)

    assert ordenados == [antiga, recente, sem_instante_2, sem_instante_10]


def test_o_numero_do_edital_ordena_como_numero_e_nao_como_texto():
    assert sorted([objeto("11"), objeto("2")], key=trabalho._ordem)[0].edital.number == "2"


def test_a_faixa_mostra_cinco_e_guarda_o_resto():
    faixa = trabalho.Faixa([objeto(str(n)) for n in range(7)])

    assert (faixa.total, len(faixa.mostrados), len(faixa.demais)) == (7, 5, 2)
    assert bool(faixa)
    assert not trabalho.Faixa([])


def test_a_faixa_diz_o_que_nao_cobre():
    assert "Classificação" in trabalho.Faixa([]).cobertura
    assert "detalhe de cada Edital" in trabalho.Faixa([]).cobertura


def retificacao(status, return_reason=""):
    return SimpleNamespace(
        status=status,
        return_reason=return_reason,
        submitted_at=datetime(2026, 10, 30, tzinfo=UTC),
        homologated_at=datetime(2026, 10, 31, tzinfo=UTC),
    )


@pytest.mark.parametrize(
    ("status", "motivo", "rotulo", "ato"),
    [
        ("EM_ELABORACAO", "", "em elaboração", "Concluir e submeter a Retificação"),
        ("EM_ELABORACAO", "Falta a linha", "devolvida", "Corrigir a Retificação devolvida"),
        ("EM_REVISAO", "", "em revisão", "Analisar a Retificação"),
        ("EM_REVISAO", "Falta a linha", "reenviada, em revisão", "Analisar a Retificação"),
        ("HOMOLOGADA", "", "homologada", "Publicar a Retificação"),
    ],
)
def test_os_rotulos_distinguem_a_devolvida_e_a_reenviada(status, motivo, rotulo, ato):
    item = retificacao(status, motivo)
    resumo = {"retificacao": item, "devolvida": atos_retificacao.foi_devolvida(item)}

    assert atos_retificacao.rotulo_da_situacao(item) == rotulo
    assert atos_retificacao.ato_na_lista(resumo) == ato


@pytest.mark.parametrize(
    ("status", "desde"),
    [
        ("EM_ELABORACAO", None),
        ("EM_REVISAO", datetime(2026, 10, 30, tzinfo=UTC)),
        ("HOMOLOGADA", datetime(2026, 10, 31, tzinfo=UTC)),
    ],
)
def test_a_espera_so_e_dita_quando_o_modelo_grava_o_instante(status, desde):
    assert atos_retificacao.desde(retificacao(status, "devolvida antes")) == desde
