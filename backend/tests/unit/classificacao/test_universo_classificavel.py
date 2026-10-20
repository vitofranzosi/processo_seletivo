"""A montagem do universo classificável, sem banco (094, D-004).

O comportamento é o que `calcular_ordem` tinha antes da extração; quem prova que nada mudou no
caminho oficial é `tests/integration/classificacao/test_previa_equivale_ao_oficial.py`. Aqui ficam
as regras uma a uma, na forma em que a prévia vai exercê-las.
"""

from decimal import Decimal

import pytest

from processo_seletivo.classificacao.domain.combinacao import RegraIncompleta
from processo_seletivo.classificacao.domain.universo_classificavel import (
    ELIMINADA,
    HABILITADA,
    preparar,
)
from processo_seletivo.resultados.models import ResultadoEtapa

ESCRITA = "00000000-0000-0000-0000-0000000009e1"
TITULOS = "00000000-0000-0000-0000-0000000009e2"
DOCUMENTOS = "00000000-0000-0000-0000-0000000009e3"
COTA = "00000000-0000-0000-0000-0000000009c1"

ETAPAS = {
    DOCUMENTOS: {"id": DOCUMENTOS, "name": "Análise documental", "order": 1, "forma": "DECISORIA"},
    ESCRITA: {"id": ESCRITA, "name": "Prova escrita", "order": 2, "weight": "2.0000"},
    TITULOS: {"id": TITULOS, "name": "Prova de títulos", "order": 3, "weight": "1.0000"},
}
MARCO = {
    "stages": [ESCRITA, TITULOS],
    "operation": "SOMA_PONDERADA",
    "normalization": "NENHUMA",
    "rounding": {"scale": 2, "mode": "MEIO_PARA_CIMA"},
    "tiebreakers": [],
}


def resultado(etapa, pontuacao=None, *, consequencia=HABILITADA, motivo="Consolidado.", ident=None):
    return {
        "id": ident or f"r-{etapa[-3:]}-{pontuacao}",
        "etapa_id": etapa,
        "pontuacao": None if pontuacao is None else Decimal(pontuacao),
        "consequencia": consequencia,
        "motivo": motivo,
    }


def inscrito(nome, *resultados, modalidade=None, fatos=None):
    return {
        "inscricao_id": f"id-{nome}",
        "protocolo": f"INS-2026-{nome}",
        "nome": nome,
        "identity_subject": f"cpf:{nome}",
        "modalidade_id": modalidade,
        "fatos": fatos or {},
        "resultados": list(resultados),
    }


def nomes(linhas):
    return [item["nome"] for item in linhas]


def test_o_vocabulario_e_o_da_consequencia_gravada():
    """O módulo não importa modelo, e por isso o texto precisa ser preso aqui."""
    assert ELIMINADA == ResultadoEtapa.Consequencia.ELIMINADA
    assert HABILITADA == ResultadoEtapa.Consequencia.HABILITADA


def test_quem_tem_todas_as_notas_e_classificavel_com_a_pontuacao_combinada():
    (classificavel,), sem_posicao = preparar(
        MARCO, ETAPAS, [inscrito("ana", resultado(ESCRITA, "8"), resultado(TITULOS, "5"))]
    )

    assert sem_posicao == []
    assert classificavel["pontuacao"] == Decimal("21.00")
    assert classificavel["consequencia"] == HABILITADA
    assert classificavel["motivo"] == ""
    assert classificavel["pontuacoes"] == {ESCRITA: Decimal("8"), TITULOS: Decimal("5")}
    assert classificavel["resultados"] == ["r-9e1-8", "r-9e2-5"]
    assert "posicao" not in classificavel, "a posição é de `ordenar`, e não daqui"


def test_a_eliminacao_mais_recente_e_a_da_etapa_de_maior_ordem():
    """A ordem da Etapa decide, e não a ordem em que os Resultados chegaram."""
    titulos = resultado(
        TITULOS, "1", consequencia=ELIMINADA, motivo="Abaixo da mínima nos títulos."
    )
    escrita = resultado(ESCRITA, "1", consequencia=ELIMINADA, motivo="Abaixo da mínima na escrita.")

    classificaveis, (eliminado,) = preparar(MARCO, ETAPAS, [inscrito("bia", titulos, escrita)])

    assert classificaveis == []
    assert eliminado["consequencia"] == ELIMINADA
    assert eliminado["motivo"] == "Abaixo da mínima nos títulos."
    assert eliminado["posicao"] is None
    assert eliminado["pontuacao"] is None
    assert eliminado["empate_residual"] is False
    assert eliminado["separado_por"] is None


def test_a_eliminacao_vence_a_pontuacao_completa():
    """Quem foi eliminado não é classificável, ainda que tenha nota em tudo."""
    _, (eliminado,) = preparar(
        MARCO,
        ETAPAS,
        [
            inscrito(
                "caio",
                resultado(ESCRITA, "9"),
                resultado(TITULOS, "9", consequencia=ELIMINADA, motivo="Não compareceu."),
            )
        ],
    )

    assert eliminado["motivo"] == "Não compareceu."


def test_sem_pontuacao_nomeia_as_etapas_que_faltam():
    classificaveis, (sem_nota,) = preparar(
        MARCO, ETAPAS, [inscrito("davi", resultado(ESCRITA, "7"))]
    )

    assert classificaveis == []
    assert sem_nota["consequencia"] == ""
    assert sem_nota["motivo"] == "Sem pontuação nas Etapas enumeradas: Prova de títulos."


def test_etapa_enumerada_que_nao_esta_no_conteudo_e_nomeada_pelo_identificador():
    marco = {**MARCO, "stages": [ESCRITA, "etapa-perdida"]}

    _, (sem_nota,) = preparar(marco, ETAPAS, [inscrito("eva", resultado(ESCRITA, "7"))])

    assert sem_nota["motivo"] == "Sem pontuação nas Etapas enumeradas: etapa-perdida."


def test_a_porta_decisoria_sem_nota_entra_no_motivo_como_sempre_entrou():
    """O texto é o que os atos já gravaram; a porta nunca tem pontuação, e é listada."""
    marco = {**MARCO, "stages": [DOCUMENTOS, ESCRITA, TITULOS]}

    _, (sem_nota,) = preparar(
        marco, ETAPAS, [inscrito("fabio", resultado(DOCUMENTOS), resultado(ESCRITA, "7"))]
    )

    assert sem_nota["motivo"] == (
        "Sem pontuação nas Etapas enumeradas: Análise documental, Prova de títulos."
    )


def test_marco_so_de_portas_classifica_com_pontuacao_nula():
    """Sem parcela numérica, todos entram no mesmo grupo — e quem ordena são os critérios."""
    marco = {**MARCO, "stages": [DOCUMENTOS]}

    (classificavel,), sem_posicao = preparar(
        marco, ETAPAS, [inscrito("gil", resultado(DOCUMENTOS))]
    )

    assert sem_posicao == []
    assert classificavel["pontuacao"] is None
    assert classificavel["consequencia"] == HABILITADA


def test_regra_incompleta_sobe_sem_captura():
    etapas = {**ETAPAS, TITULOS: {**ETAPAS[TITULOS], "weight": None}}

    with pytest.raises(RegraIncompleta):
        preparar(
            MARCO,
            etapas,
            [inscrito("hugo", resultado(ESCRITA, "8"), resultado(TITULOS, "5"))],
        )


def test_dois_resultados_da_mesma_etapa_colapsam_no_ultimo():
    """O chamador entrega os Resultados em ordem de consolidação, e o sucessor vem por último."""
    (classificavel,), _ = preparar(
        MARCO,
        ETAPAS,
        [
            inscrito(
                "iara",
                resultado(ESCRITA, "4", ident="superado"),
                resultado(ESCRITA, "8", ident="sucessor"),
                resultado(TITULOS, "5"),
            )
        ],
    )

    assert classificavel["pontuacoes"][ESCRITA] == Decimal("8")
    assert classificavel["resultados"] == ["superado", "sucessor", "r-9e2-5"]


def test_a_ordem_de_entrada_e_preservada_nas_duas_saidas():
    entrada = [
        inscrito("zeca", resultado(ESCRITA, "1"), resultado(TITULOS, "1")),
        inscrito("yara", resultado(ESCRITA, "1")),
        inscrito("xavier", resultado(ESCRITA, "9"), resultado(TITULOS, "9")),
        inscrito("wanda"),
    ]

    classificaveis, sem_posicao = preparar(MARCO, ETAPAS, entrada)

    assert nomes(classificaveis) == ["zeca", "xavier"]
    assert nomes(sem_posicao) == ["yara", "wanda"]


def test_os_dados_do_inscrito_atravessam_sem_mudanca():
    entrada = inscrito(
        "lia",
        resultado(ESCRITA, "8"),
        resultado(TITULOS, "5"),
        modalidade=COTA,
        fatos={"fato": 3},
    )

    (classificavel,), _ = preparar(MARCO, ETAPAS, [entrada])

    for chave in ("inscricao_id", "protocolo", "nome", "identity_subject", "modalidade_id"):
        assert classificavel[chave] == entrada[chave]
    assert classificavel["fatos"] == {"fato": 3}


# --- o recorte ----------------------------------------------------------------------------------

ENTRADA_MISTA = [
    inscrito("ana", resultado(ESCRITA, "8"), resultado(TITULOS, "5"), modalidade=COTA),
    inscrito("bia", resultado(ESCRITA, "9"), resultado(TITULOS, "5")),
    inscrito("caio", resultado(ESCRITA, "7"), modalidade=COTA),
    inscrito("davi", resultado(ESCRITA, "6"), resultado(TITULOS, "6"), modalidade="outra"),
]


def test_sem_recorte_o_universo_e_o_perfil_inteiro():
    """A ampla é o universo inteiro: quem se autodeclarou numa reservada permanece (034, D-001)."""
    classificaveis, sem_posicao = preparar(MARCO, ETAPAS, ENTRADA_MISTA)

    assert nomes(classificaveis) == ["ana", "bia", "davi"]
    assert nomes(sem_posicao) == ["caio"]


def test_o_recorte_filtra_pela_modalidade_declarada():
    classificaveis, sem_posicao = preparar(MARCO, ETAPAS, ENTRADA_MISTA, recorte=COTA)

    assert nomes(classificaveis) == ["ana"]
    assert nomes(sem_posicao) == ["caio"]


def test_o_recorte_e_idempotente_sobre_a_entrada_ja_filtrada():
    """É o caso do caminho oficial: a consulta já filtrou, e reaplicar não muda nada."""
    filtrada = [item for item in ENTRADA_MISTA if item["modalidade_id"] == COTA]

    assert preparar(MARCO, ETAPAS, filtrada, recorte=COTA) == preparar(MARCO, ETAPAS, filtrada)


def test_o_recorte_compara_pelo_texto_do_identificador():
    """O recorte pode chegar como UUID; a modalidade do inscrito chega como texto."""
    from uuid import UUID

    cota = "00000000-0000-0000-0000-0000000009c1"
    entrada = [inscrito("ana", resultado(ESCRITA, "8"), resultado(TITULOS, "5"), modalidade=cota)]

    classificaveis, _ = preparar(MARCO, ETAPAS, entrada, recorte=UUID(cota))

    assert nomes(classificaveis) == ["ana"]
