"""As regras puras da `141`: a sucessora espera as Etapas por fazer, e o corte espera o reingresso.

A cadeia inteira, com banco e pelos comandos, está em
`tests/integration/treinamento/test_sucessora_espera_o_reabilitado.py`. Aqui ficam as células, uma a
uma, inclusive os casos que o C08 não forma: duas Etapas por fazer, a lista em que ninguém concorre
e a preliminar já publicada com a ordem à espera.
"""

from datetime import UTC, datetime

from processo_seletivo.interface import andamento as a

FECHA = datetime(2026, 11, 15, 23, 59, tzinfo=UTC)


def celula(situacao, **campos):
    return a.Celula(situacao, **campos)


def _a_espera():
    return a.situacao_da_ordem({"celula": {"estado": "obsoleto"}, "faltam": ["Análise de títulos"]})


# --- a ordem sucessora (FR-4830 a FR-4832) ------------------------------------------------------


def test_a_sucessora_com_etapa_por_fazer_e_depois_e_diz_por_que():
    ordem = _a_espera()

    assert (ordem.situacao, ordem.ato, ordem.responsavel) == (a.DEPOIS, "", "")
    assert ordem.razao == (
        "a ordem sucessora lê Análise de títulos, que ainda não está feita; a vigente continua "
        "produzindo efeito"
    )
    assert ordem.vigente_para_tras
    assert not ordem.em_aberto, "Depois não entra no nível 1"


def test_duas_etapas_por_fazer_vao_ao_plural():
    ordem = a.situacao_da_ordem(
        {"celula": {"estado": "obsoleto"}, "faltam": ["Prova objetiva", "Análise de títulos"]}
    )

    assert "que ainda não estão feitas" in ordem.razao
    assert "Prova objetiva" in ordem.razao and "Análise de títulos" in ordem.razao


def test_sem_etapa_por_fazer_a_sucessora_e_providencia_como_antes():
    ordem = a.situacao_da_ordem({"celula": {"estado": "obsoleto", "url": "/o"}, "faltam": []})

    assert (ordem.situacao, ordem.ato, ordem.responsavel) == (
        a.OBSOLETO,
        "Emitir a ordem sucessora",
        a.CONDUZ,
    )
    assert not ordem.vigente_para_tras


def test_a_lista_vazia_sem_etapa_por_fazer_continua_com_a_frase_da_135():
    ordem = a.situacao_da_ordem({"celula": {"estado": "obsoleto"}, "vazia": True})

    assert ordem.ato == a.ATO_DA_SUCESSORA_VAZIA
    assert ordem.lista_vazia


def test_a_lista_vazia_com_etapa_por_fazer_espera_como_a_primeira_ordem():
    """A lista vazia muda o texto, e não a espera (a FR-4676 da `135`)."""
    ordem = a.situacao_da_ordem(
        {"celula": {"estado": "obsoleto"}, "faltam": ["Análise de títulos"], "vazia": True}
    )

    assert ordem.situacao == a.DEPOIS


def test_a_primeira_ordem_continua_como_antes():
    primeira = a.situacao_da_ordem(
        {"celula": {"estado": "falta"}, "faltam": ["Análise de títulos"]}
    )

    assert primeira.situacao == a.DEPOIS
    assert not primeira.vigente_para_tras, "sem ordem vigente, não há o que esteja para trás"
    assert primeira.razao == "a ordem lê Análise de títulos, que ainda não está feita"


# --- quem lê a ordem (FR-4833, FR-4834) ---------------------------------------------------------


def test_o_resultado_le_a_sucessora_a_espera_como_lia_a_obsoleta():
    for celula_do_resultado in (
        {"estado": "falta"},
        {"estado": "feito", "nota": "resultado preliminar", "natureza": "PRELIMINAR"},
        {"estado": "obsoleto", "natureza": "PRELIMINAR"},
    ):
        antes = a.situacao_do_resultado(
            {"celula": celula_do_resultado, "ordem": celula(a.OBSOLETO)}
        )
        agora = a.situacao_do_resultado({"celula": celula_do_resultado, "ordem": _a_espera()})
        assert (agora.situacao, agora.razao, agora.divulgado) == (
            antes.situacao,
            antes.razao,
            antes.divulgado,
        ), celula_do_resultado


def test_o_corte_e_a_apuracao_leem_a_sucessora_a_espera_como_a_obsoleta():
    for funcao in (a.situacao_do_corte, a.situacao_da_apuracao):
        antes = funcao({"celula": {"estado": "falta"}, "ordem": celula(a.OBSOLETO)})
        agora = funcao({"celula": {"estado": "falta"}, "ordem": _a_espera()})
        assert (agora.situacao, agora.razao) == (antes.situacao, antes.razao)
        assert agora.situacao == a.DEPOIS


def test_ordem_para_tras():
    assert a.ordem_para_tras(celula(a.OBSOLETO))
    assert a.ordem_para_tras(_a_espera())
    assert not a.ordem_para_tras(celula(a.FEITO))
    assert not a.ordem_para_tras(celula(a.DEPOIS))
    assert not a.ordem_para_tras(None)


# --- o corte (FR-4835 a FR-4837) ----------------------------------------------------------------


def test_com_reingresso_o_corte_a_emitir_espera():
    corte = a.situacao_do_corte(
        {"celula": {"estado": "falta"}, "ordem": celula(a.FEITO), "reingresso": True}
    )

    assert (corte.situacao, corte.ato, corte.responsavel) == (a.DEPOIS, "", "")
    assert corte.razao == a.REINGRESSO_NO_CORTE


def test_com_reingresso_a_geracao_sucessora_tambem_espera():
    corte = a.situacao_do_corte({"celula": {"estado": "obsoleto"}, "reingresso": True})

    assert corte.situacao == a.DEPOIS
    assert corte.razao.startswith("o corte vigente está para trás, e há inscrição reabilitada")


def test_o_reingresso_vem_antes_da_espera_do_prazo():
    """Com o reabilitado sem resultado, esperar o prazo não basta: a razão é o reingresso."""
    espera = {"ate": FECHA, "razao": "Aguarde o fim do prazo de recurso"}
    corte = a.situacao_do_corte(
        {
            "celula": {"estado": "falta"},
            "ordem": celula(a.FEITO),
            "espera": espera,
            "reingresso": True,
        }
    )

    assert corte.situacao == a.DEPOIS and not corte.recomendacao


def test_sem_reingresso_o_corte_e_o_de_antes():
    assert (
        a.situacao_do_corte({"celula": {"estado": "falta"}, "ordem": celula(a.FEITO)}).situacao
        == a.PENDENTE
    )
    assert a.situacao_do_corte({"celula": {"estado": "obsoleto"}}).ato == (
        "Emitir a geração sucessora do corte"
    )


def test_o_corte_feito_continua_feito_com_reingresso():
    """Ato vigente é fato: a leitura não o desmente (D-004)."""
    assert (
        a.situacao_do_corte({"celula": {"estado": "feito"}, "reingresso": True}).situacao == a.FEITO
    )


# --- o Centro de Controle (FR-4845) -------------------------------------------------------------


def test_no_centro_a_fase_com_a_sucessora_a_espera_esta_em_curso():
    """No C08, a Classificação dizia "ainda não começou" com a ordem emitida e divulgada."""
    from processo_seletivo.interface import centro as cc
    from processo_seletivo.interface import conceitos

    assert cc.agregar([_a_espera()]) == conceitos.EM_CURSO
    assert cc.agregar([_a_espera(), celula(a.DEPOIS)]) == conceitos.EM_CURSO
    primeira = a.situacao_da_ordem(
        {"celula": {"estado": "falta"}, "faltam": ["Análise de títulos"]}
    )
    assert cc.agregar([primeira]) == conceitos.NAO_INICIADA, "sem ordem vigente, não começou"
