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
