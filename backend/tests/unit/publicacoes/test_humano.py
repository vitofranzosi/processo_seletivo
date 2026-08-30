"""T004 — a formatação humana do decimal, e a fronteira que ela não pode atravessar.

A tabela B.1 do contrato `specs/007-edital-institucional/contracts/institucional.md`.
"""

import pytest

from processo_seletivo.publicacoes.infrastructure import humano


@pytest.mark.parametrize(
    ("canonico", "esperado"),
    [
        # A tabela B.1, na íntegra.
        ("20.0000", "20"),
        ("12.5000", "12,5"),
        ("7.2500", "7,25"),
        ("2.0000", "2"),
        ("0.5000", "0,5"),
        ("60.0000", "60"),
        # Fronteiras da faixa do percentual (FR-030 da `006`): maior que zero, até cem.
        ("100.0000", "100"),
        ("0.0001", "0,0001"),
        # Zero não é valor legítimo de percentual nem de peso, mas o formatador não é o lugar
        # de recusá-lo — o domínio já o faz. Aqui ele só não pode virar string vazia.
        ("0.0000", "0"),
    ],
)
def test_escreve_em_portugues_descartando_zeros_a_direita(canonico, esperado):
    assert humano.decimal(canonico) == esperado


def test_ausencia_devolve_string_vazia():
    """Quem decide se a linha é composta é o chamador, não o formatador."""
    assert humano.decimal(None) == ""
    assert humano.decimal("") == ""
    assert humano.decimal("   ") == ""


def test_nunca_devolve_ponto_como_separador_decimal():
    """O ponto é a forma canônica; a vírgula é a humana. Confundi-los é o defeito."""
    for canonico in ("20.0000", "12.5000", "0.0001", "99.9999"):
        assert "." not in humano.decimal(canonico)


def test_nao_produz_notacao_cientifica():
    """`Decimal("20.0000").normalize()` é `2E+1` — a armadilha que este módulo evita."""
    for canonico in ("20.0000", "100.0000", "1000.0000", "0.0001"):
        resultado = humano.decimal(canonico)
        assert "E" not in resultado.upper()


def test_valor_nao_decimal_sai_como_esta_em_vez_de_sumir():
    """Um campo inesperado deve aparecer no documento, não virar vazio inexplicável."""
    assert humano.decimal("indeterminado") == "indeterminado"


def test_nao_depende_de_locale(monkeypatch):
    """O mesmo conteúdo publicado produz o mesmo documento em qualquer máquina.

    Um documento normativo cuja forma dependa do ambiente que o gerou não é reproduzível, e a
    reprodutibilidade é o que a cadeia "dados estruturados → versão homologada → PDF" promete.
    """
    monkeypatch.setenv("LC_ALL", "C")
    monkeypatch.setenv("LANG", "C")
    assert humano.decimal("12.5000") == "12,5"
