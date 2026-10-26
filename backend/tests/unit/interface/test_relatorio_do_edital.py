"""As peças puras do relatório do Edital (099): ausência, razão, vagas e semanas."""

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from processo_seletivo.interface import relatorio_do_edital as rel
from processo_seletivo.interface.visao_geral import Numero


def test_ausencia_nunca_vira_zero():
    """FR-2548: o motivo é o texto; zero só quando a fonte produziu zero."""
    assert rel.interpretar(Numero.nao_aplicavel("só cadastro de reserva")) == (
        "só cadastro de reserva"
    )
    assert rel.interpretar(Numero.de(0)) == "0"
    assert rel.interpretar(Numero.de(Decimal("13.0"))) == "13,0"


def test_o_indicador_diz_de_quanto_e_se_e_parcial():
    indicador = rel.Indicador("convocações aceitas", Numero.de(1), "base", de=2)
    assert rel.texto_do_indicador(indicador) == "1 de 2"
    parcial = rel.Indicador("inscrições enviadas", Numero.de(11, parcial=True), "base")
    assert rel.texto_do_indicador(parcial) == "11 (parcial)"
    ausente = rel.Indicador("x", Numero.nao_disponivel("ainda não apurada"), "base", de=2)
    assert rel.texto_do_indicador(ausente) == "ainda não apurada"


@dataclass
class _Perfil:
    vagas: Numero
    vagas_por_lista: tuple
    reserva: str = "sem limite"


def test_a_celula_de_vagas():
    assert rel.texto_das_vagas(
        _Perfil(Numero.de(2), (("Ampla concorrência", 1), ("Pessoas pretas", 1)))
    ) == ("2 (1 ampla, 1 reservada)")
    assert rel.texto_das_vagas(_Perfil(Numero.de(3), (("Ampla concorrência", 3),))) == "3"
    assert rel.texto_das_vagas(_Perfil(Numero.de(0), ())) == "cadastro de reserva, sem limite"


@dataclass
class _Ponto:
    dia: date
    quantidade: int


@dataclass
class _Relatorio:
    serie: tuple
    termino_original: datetime | None


def test_semanas_marcam_o_termino_original_e_o_periodo_acrescentado():
    """FR-2536: blocos de sete dias a contar do primeiro, com a prorrogação dita."""
    dias = [_Ponto(date(2026, 8, d), 1) for d in range(10, 32)] + [
        _Ponto(date(2026, 9, d), 2) for d in range(1, 5)
    ]
    termino = datetime(2026, 8, 30, 23, 59, tzinfo=ZoneInfo("America/Sao_Paulo"))
    semanas = rel.semanas(_Relatorio(tuple(dias), termino))
    assert [(s.inicio.day, s.fim.day, s.envios) for s in semanas] == [
        (10, 16, 7),
        (17, 23, 7),
        (24, 30, 7),
        (31, 4, 9),
    ]
    assert [s.termino_original for s in semanas] == [False, False, True, False]
    assert [s.acrescentada for s in semanas] == [False, False, False, True]
    assert all(not s.termino_original for s in rel.semanas(_Relatorio(tuple(dias), None)))


def test_pendencia_de_perfil_omitido_nao_nomeia_o_perfil():
    """D-006: o fato não público do Perfil com menos de cinco inscrições não volta pela capa."""
    perfis = [{"id": "a", "name": "Professor"}, {"id": "b", "name": "Técnico"}]
    redigidas = rel._redigir(
        [("a", "1 convocação aguardando resposta"), ("b", "apuração das vagas desatualizada")],
        perfis,
        omitidos={"b"},
    )
    assert redigidas == [
        "Professor: 1 convocação aguardando resposta",
        "1 providência pendente em perfil com menos de 5 inscrições (detalhe omitido)",
    ]
    assert not any("Técnico" in r for r in redigidas)


# --- 100: supressão complementar, redação por tipo ---------------------------------------------


def test_sem_grupo_pequeno_nada_e_omitido():
    assert rel.omitidos_por_complemento({"a": 26, "b": 12}, 5) == (frozenset(), frozenset(), False)


def test_o_grupo_pequeno_leva_o_menor_dos_demais():
    """FR-2587: com um Perfil de 3, o total menos o outro devolveria os 3 — o outro sai junto."""
    assert rel.omitidos_por_complemento({"a": 26, "b": 3, "c": 40}, 5) == (
        frozenset({"b"}),
        frozenset({"a"}),
        False,
    )


def test_pequenos_que_somam_o_limiar_nao_pedem_complemento():
    assert rel.omitidos_por_complemento({"a": 3, "b": 2, "c": 40}, 5) == (
        frozenset({"a", "b"}),
        frozenset(),
        False,
    )


def test_edital_inteiro_abaixo_do_limiar_omite_o_total():
    assert rel.omitidos_por_complemento({"a": 3, "b": 1}, 5) == (
        frozenset({"a", "b"}),
        frozenset(),
        True,
    )


def test_o_desempate_do_complemento_e_pelo_identificador():
    """A mesma entrada dá sempre a mesma saída: dois candidatos de mesma população."""
    pequenos, complemento, _ = rel.omitidos_por_complemento({"z": 9, "y": 9, "b": 2}, 5)
    assert complemento == frozenset({"y"})


def test_a_pendencia_omitida_pelo_complemento_nao_diz_menos_de_cinco():
    perfis = [{"id": "a", "name": "Professor"}, {"id": "b", "name": "Técnico"}]
    redigidas = rel._redigir(
        [("a", "1 convocação aguardando resposta"), ("b", "apuração das vagas desatualizada")],
        perfis,
        omitidos={"a", "b"},
        complementares={"a"},
    )
    assert redigidas == ["2 providências pendentes em perfis com detalhe omitido por privacidade"]


def test_cada_tipo_de_pendencia_tem_a_frase_da_099():
    def texto(*a, **k):
        return rel.texto_da_pendencia(rel.Pendencia(*a, **k))

    assert texto(rel.RESULTADO_NAO_DIVULGADO, "a", marco="Final") == (
        "resultado de “Final” ainda não divulgado"
    )
    assert texto(rel.CONVOCACAO_AGUARDANDO, "a", 2) == "2 convocações aguardando resposta"
    assert texto(rel.CONVOCACAO_VENCIDA, "a", 1) == (
        "1 convocação com prazo encerrado sem registro de resposta"
    )
    assert texto(rel.RECURSO_AGUARDANDO, None, 3) == "3 recursos aguardam decisão"
    assert rel.Pendencia(rel.DEFINITIVO_NAO_PUBLICADO, "a").publica
    assert not rel.Pendencia(rel.APURACAO_DESATUALIZADA, "a").publica


def test_etapa_sem_registro_nao_diz_zero():
    """Caso-limite da 099: sem resultado registrado, a etapa diz que não há registro."""
    etapas = [{"id": "e1", "name": "Prova", "eliminatory": True, "order": 1}]
    (linha,) = rel._linhas_das_etapas("p", etapas, {})
    assert not linha.registrada
