"""T004 — a formatação humana do decimal, e a fronteira que ela não pode atravessar.

A tabela B.1 do contrato `specs/007-edital-institucional/contracts/institucional.md`.
"""

from datetime import datetime, timedelta, timezone

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


@pytest.mark.parametrize(
    ("momento", "esperado", "por_que"),
    [
        (datetime(2026, 10, 5, 14, 0), "05/10/2026, às 14h", "a hora cheia não ganha 00 de minuto"),
        (datetime(2026, 9, 20, 23, 59), "20/09/2026, às 23h59", "o prazo que termina em 23h59"),
        (datetime(2026, 9, 1, 9, 0), "01/09/2026, às 09h", "hora de um dígito sai com dois"),
        (datetime(2026, 9, 1, 9, 39), "01/09/2026, às 09h39", "e com dois também quando há minuto"),
        (datetime(2026, 9, 1, 0, 6), "01/09/2026, às 00h06", "a madrugada é 00h, e não 0h"),
        (datetime(2026, 9, 1, 0, 0), "01/09/2026, às 00h", "meia-noite é hora, não ausência dela"),
    ],
)
def test_a_hora_tem_sempre_dois_digitos_e_a_meia_noite_e_uma_hora(momento, esperado, por_que):
    """As duas exceções silenciosas que a omissão de minutos havia adquirido.

    A página passa pelo filtro `date` do Django com `H`, que preenche a hora; o documento não
    preenchia. Entre 00h e 09h59 — **dez horas de todo dia** — as duas superfícies escreviam o
    mesmo instante de dois jeitos. E `00:00` caía num ramo que devolvia só a data, de modo que o
    documento omitia a hora enquanto a página mostrava `00h00`.

    A omissão dos minutos na hora cheia continua: ela é regra de linguagem de Edital, e não um
    efeito colateral. `14h` e `00h` são a mesma regra; `9h` e a data sozinha eram os defeitos.
    """
    assert humano.instante(momento) == esperado, por_que


def test_instante_ausente_devolve_string_vazia():
    """Como no decimal: compor ou omitir a linha é decisão do chamador."""
    assert humano.instante(None) == ""


def test_instante_nao_converte_fuso():
    """Escreve o que recebe. Quem lê do banco converte antes — `humano` não conhece fuso algum."""
    momento = datetime(2026, 10, 18, 12, 39, tzinfo=timezone(timedelta(hours=0)))

    assert humano.instante(momento) == "18/10/2026, às 12h39"
