"""A prévia sobre o motor oficial: a matriz do achado, as recusas e o que mudou (094).

A matriz é a da reprodução do achado de 19/10 (`doc/achado-empate-estrito-tem-tres-leituras.md`,
R-007): alvo 10, com e sem 5 suplentes, empate de dois na 10ª ou na 15ª, os dois desfechos, e 10
vagas. **Absoluta, e não comparativa**: se `faixa.calcular` ou a apuração mudarem, ela reprova dos
dois lados ao mesmo tempo — é a metade da sentinela que a equivalência com o caminho oficial não vê
(FR-2233).
"""

import time

import pytest

from processo_seletivo.classificacao.application import previa
from processo_seletivo.ocupacao.domain import apuracao

ETAPAS = [
    {"id": "e1", "name": "Prova Escrita", "order": 1, "forma": "PONTUADA", "weight": "2.0000"},
    {"id": "e2", "name": "Prova de Títulos", "order": 2, "forma": "PONTUADA", "weight": "1.0000"},
    {"id": "e3", "name": "Análise documental", "order": 3, "forma": "DECISORIA", "weight": None},
    {"id": "e4", "name": "Entrevista", "order": 4, "forma": "PONTUADA", "weight": "1.0000"},
]
FATOS = [
    {"id": "f1", "code": "NASC", "label": "Data de nascimento", "type": "DATA"},
    {"id": "f2", "code": "SERV", "label": "Tempo de serviço", "type": "INTEIRO"},
]
CRITERIOS = [
    {
        "order": 1,
        "type": "MAIOR_PONTUACAO_NA_ETAPA",
        "parameters": {"stageId": "e1"},
        "whenMissing": "ULTIMO_NO_CRITERIO",
    },
    {
        "order": 2,
        "type": "MENOR_VALOR_DE_FATO",
        "parameters": {"factId": "f1"},
        "whenMissing": "ULTIMO_NO_CRITERIO",
    },
    {
        "order": 3,
        "type": "MAIOR_VALOR_DE_FATO",
        "parameters": {"factId": "f2"},
        "whenMissing": "ULTIMO_NO_CRITERIO",
    },
]


def apurar_vagas(progrediram, vagas, empates):
    try:
        apuracao.titulares_iniciais(
            progrediram_em_ordem=progrediram, efetivas=vagas, empates_residuais=empates
        )
    except apuracao.EmpateNaFronteiraDoAlvo as erro:
        return erro.posicao, erro.quantas
    return None


def marco(*, alvo=10, suplentes=5, desfecho="ADMITS_SURPLUS", criterios=CRITERIOS, **regra):
    corte = {
        "targetKind": "FIXED",
        "targetCount": alvo,
        "surplusCount": suplentes,
        "tieOutcome": desfecho,
        "governedStage": "e4",
        "continuation": "ALLOWED",
        **regra,
    }
    return {
        "orderProduction": "POR_PONTUACAO",
        "stages": ["e1", "e2"],
        "operation": "SOMA_PONDERADA",
        "normalization": "NENHUMA",
        "rounding": {"scale": 2, "mode": "MEIO_PARA_CIMA"},
        "tiebreakers": criterios,
        "cutRule": corte,
    }


def simular(m, **opcoes):
    opcoes = {"vagas": 10, "apurar_vagas": apurar_vagas, **opcoes}
    return previa.simular(m, ETAPAS, FATOS, **opcoes)


# --- A matriz do achado (R-007) ---------------------------------------------------------------

MATRIZ = [
    # caso-limite, suplentes, desfecho → corte, além da faixa, apuração das vagas
    ("empate_nas_vagas", 5, "ADMITS_SURPLUS", 15, 0, 10),
    ("empate_nas_vagas", 5, "STRICT", 15, 0, 10),
    ("empate_na_faixa", 5, "ADMITS_SURPLUS", 16, 1, None),
    ("empate_na_faixa", 5, "STRICT", "recusado-15", None, None),
    ("empate_nas_vagas", 0, "ADMITS_SURPLUS", 11, 1, 10),
    ("empate_nas_vagas", 0, "STRICT", "recusado-10", None, None),
]


@pytest.mark.parametrize(("caso", "suplentes", "desfecho", "corte", "alem", "vagas"), MATRIZ)
def test_a_matriz_do_achado(caso, suplentes, desfecho, corte, alem, vagas):
    r = simular(marco(suplentes=suplentes, desfecho=desfecho), modo="caso", caso=caso)
    if isinstance(corte, str):
        assert r["corte"]["recusado"]
        assert r["corte"]["posicao"] == int(corte.split("-")[1])
        assert r["aviso_das_vagas"]["avaliado"] is False
        return
    assert len(r["corte"]["progrediram"]) == corte
    assert len(r["corte"]["excedentes"]) == alem
    if vagas is None:
        assert r["aviso_das_vagas"] == {"avaliado": True, "para": False}
    else:
        assert r["aviso_das_vagas"]["posicao"] == vagas


def test_o_empate_pelo_desfecho_marca_o_grupo_inteiro():
    """FR-2212: um excede a faixa, mas os dois avançam pelo desfecho — a marca é do grupo."""
    r = simular(marco(), modo="caso", caso="empate_na_faixa")
    empatados = [i["inscricao_id"] for i in r["ordem"] if i["posicao"] == 15]
    assert len(empatados) == 2
    assert {r["consequencias"][i] for i in empatados} == {previa.PELO_EMPATE}


def test_corte_recusado_ninguem_avanca():
    r = simular(marco(desfecho="STRICT"), modo="caso", caso="empate_na_faixa")
    assert {r["consequencias"][i["inscricao_id"]] for i in r["ordem"]} == {previa.AGUARDA}


def test_desfecho_nao_declarado_mostra_os_dois_sem_escolher():
    r = simular(marco(desfecho=""), modo="caso", caso="empate_na_faixa")
    assert r["corte"]["sem_desfecho"] and r["corte"]["atravessa"]
    assert r["corte"]["comparacao"]["estrito"]["recusado"]
    assert len(r["corte"]["comparacao"]["admite"]["progrediram"]) == 16
    assert previa.impedido(r["corte"])


def test_desfecho_nao_declarado_sem_empate_na_fronteira_nao_muda_nada():
    r = simular(marco(desfecho=""), modo="caso", caso="sem_empate")
    assert not r["corte"]["atravessa"]
    assert len(r["corte"]["progrediram"]) == 15


def test_o_outro_desfecho_so_quando_o_empate_atravessa():
    com_empate = simular(marco(), modo="caso", caso="empate_na_faixa")
    assert com_empate["corte"]["alternativo"]["recusado"]
    sem_empate = simular(marco(), modo="caso", caso="sem_empate")
    assert sem_empate["corte"]["alternativo"] is None


def test_sem_regra_de_corte_todos_seguem():
    m = marco()
    m["cutRule"] = None
    r = simular(m)
    assert not r["corte"]["declarado"]
    assert set(r["consequencias"].values()) <= {previa.SEGUE, previa.SEM_POSICAO}


# --- O que falta, sem presumir (FR-2227) ------------------------------------------------------


@pytest.mark.parametrize(
    ("alteracao", "trecho"),
    [
        ({"stages": []}, "ao menos uma Etapa"),
        ({"tiebreakers": [{"order": 1, "type": "", "parameters": {}}]}, "não diz qual é"),
        ({"tiebreakers": [{"order": 1, "type": "MAIOR_PONTUACAO_NA_ETAPA"}]}, "o que compara"),
        ({"rounding": {"scale": None, "mode": ""}}, "scale"),
    ],
)
def test_o_que_falta_e_nomeado(alteracao, trecho):
    with pytest.raises(previa.Incompleto) as erro:
        simular({**marco(), **alteracao})
    assert any(trecho in falta for falta in erro.value.faltas)


def test_alvo_vazio_e_quadro_sem_linha():
    with pytest.raises(previa.Incompleto, match="Declare o alvo"):
        simular(marco(alvo=None))
    m = marco(targetKind="FROM_VACANCY_TABLE")
    with pytest.raises(previa.Incompleto, match="não é apurável"):
        simular(m, vagas=None)


def test_valor_ausente_nao_declarado_nao_e_presumido():
    sem_declaracao = [{**CRITERIOS[1], "whenMissing": ""}]
    with pytest.raises(previa.Incompleto, match="não presume"):
        simular(marco(criterios=sem_declaracao), modo="caso", caso="valor_ausente")


def test_mais_de_quatro_etapas_com_nota():
    etapas = [
        {"id": f"x{n}", "name": f"E{n}", "order": n, "forma": "PONTUADA", "weight": "1"}
        for n in range(5)
    ]
    m = {**marco(criterios=[]), "stages": [e["id"] for e in etapas]}
    with pytest.raises(previa.Incompleto, match="até 4"):
        previa.simular(m, etapas, [], vagas=10)


def test_sorteio_fica_fora_da_fatia():
    with pytest.raises(previa.ForaDaFatia):
        simular({**marco(), "orderProduction": "POR_SORTEIO"})


def test_sem_apuracao_injetada_o_aviso_nao_e_avaliado():
    r = previa.simular(marco(), ETAPAS, FATOS, vagas=10)
    assert r["aviso_das_vagas"]["avaliado"] is False


# --- A população estável e o que mudou (FR-2243, FR-2244, SC-849, SC-850) ----------------------


def test_a_populacao_estavel_nao_muda_com_a_regra():
    antes = simular(marco())
    depois = simular(marco(suplentes=0, desfecho="STRICT"), populacao=antes["ancoras"])
    assert [i["inscricao_id"] for i in antes["ordem"]] == [
        i["inscricao_id"] for i in depois["ordem"]
    ]
    assert [i["pontuacao"] for i in antes["ordem"]] == [i["pontuacao"] for i in depois["ordem"]]


def test_o_que_mudou_com_o_desfecho_e_os_suplentes():
    um = simular(marco())
    dois = simular(marco(desfecho="STRICT"), populacao=um["ancoras"])
    mudanca = previa.comparar(previa.estado(um), previa.estado(dois))
    assert "Corte: emitível → impedido na 15ª." in mudanca["mudancas"]
    assert "Avançam: 16 → 0." in mudanca["mudancas"]
    tres = simular(marco(suplentes=0, desfecho="STRICT"), populacao=um["ancoras"])
    mudanca = previa.comparar(previa.estado(dois), previa.estado(tres))
    assert mudanca["mudancas"] == ["Corte: impedido na 15ª → impedido na 10ª."]
    assert mudanca["mudaram"] == set()


def test_alteracao_sem_efeito_nao_muda_nada():
    um = simular(marco())
    outro = simular(marco(continuation="NONE"), populacao=um["ancoras"])
    assert previa.comparar(previa.estado(um), previa.estado(outro)) == {
        "mudancas": [],
        "mudaram": set(),
    }


def test_populacoes_e_modos_diferentes_nao_se_comparam():
    estavel = simular(marco())
    caso = simular(marco(), modo="caso", caso="empate_na_faixa")
    assert previa.comparar(previa.estado(estavel), previa.estado(caso)) is None
    remontada = simular(marco(alvo=20))
    assert previa.comparar(previa.estado(estavel), previa.estado(remontada)) is None
    assert previa.comparar("", previa.estado(estavel)) is None
    assert previa.comparar("lixo", previa.estado(estavel)) is None


# --- O tempo (SC-841) --------------------------------------------------------------------------


@pytest.mark.parametrize("caso", ["", "sem_empate", "empate_na_faixa", "criterios_sucessivos"])
def test_uma_faixa_de_quinhentos_calcula_em_menos_de_um_segundo(caso):
    inicio = time.perf_counter()
    r = simular(marco(alvo=400, suplentes=100), modo="caso" if caso else "estavel", caso=caso)
    assert time.perf_counter() - inicio < 1.0
    assert r["total"] >= 500
