"""Caractere sem grafia — a lista fechada do que o documento normaliza, e o que ele recusa.

A lista é decisão do responsável pelo produto (08/10/2026), e cada linha aqui a fixa: acrescentar
um caractere à normalização é decisão nova, e não ajuste de teste. Os recusados estão nomeados pela
mesma razão — o `◦` em particular, que foi tirado da lista proposta porque trocá-lo por `•` apaga a
diferença de nível entre listas.
"""

import unicodedata

import pytest

from processo_seletivo.publicacoes.domain import grafia


@pytest.mark.parametrize(
    "original",
    [
        "●",  # ●
        "\uf0b7",  # marcador da Symbol, colado do Word
        "\uf0a7",  # quadrado da Wingdings, colado do Word
        "▪",  # ▪
        "■",  # ■
        "‣",  # ‣
        "⁃",  # ⁃
        "∙",  # ∙
    ],
)
def test_marcador_cheio_vira_o_marcador_do_winansi(original):
    assert grafia.normalizar(f"{original} Conhecer a norma") == "• Conhecer a norma"


@pytest.mark.parametrize("invisivel", ["\u200b", "\u200c", "\u200d", "\u2060", "\ufeff", "\u00ad"])
def test_invisivel_some(invisivel):
    assert grafia.normalizar(f"pla{invisivel}nejar") == "planejar"


def test_hifen_condicional_some_embora_esteja_no_cp1252():
    """Ele nunca virou `?` — mas o WinAnsi o desenha como `-` visível no meio da palavra."""
    assert "\u00ad".encode("cp1252") == b"\xad"
    assert grafia.normalizar("coor\u00addenação") == "coordenação"


@pytest.mark.parametrize(
    "espaco",
    [chr(codigo) for codigo in range(0x2000, 0x200B)] + ["\u202f", "\u205f", "\u3000"],
)
def test_espaco_tipografico_vira_espaco(espaco):
    assert grafia.normalizar(f"20{espaco}horas") == "20 horas"


@pytest.mark.parametrize("traco", ["\u2010", "\u2011", "\u2212"])
def test_hifen_e_sinal_de_menos_viram_hifen(traco):
    assert grafia.normalizar(f"pré{traco}requisito") == "pré-requisito"


@pytest.mark.parametrize("separador", ["\u2028", "\u2029"])
def test_separador_de_linha_vira_quebra(separador):
    assert grafia.normalizar(f"Primeiro.{separador}Segundo.") == "Primeiro.\nSegundo."


def test_texto_decomposto_e_composto():
    """O texto colado do macOS chega em NFD, e a cedilha solta não está no cp1252."""
    decomposto = unicodedata.normalize("NFD", "Seleção pública")
    assert decomposto != "Seleção pública"
    assert grafia.normalizar(decomposto) == "Seleção pública"
    assert grafia.sem_grafia(decomposto) == []


@pytest.mark.parametrize(
    "recusado",
    [
        "◦",  # ◦ — o vazado: normalizá-lo apagaria o nível da lista
        "○",  # ○
        "≥",  # ≥
        "≤",  # ≤
        "≠",  # ≠
        "→",  # →
        "➢",  # ➢
        "✓",  # ✓
        "№",  # №
        "′",  # ′
        "\U0001f600",  # emoji
        "Ω",  # Ω
        "\x07",  # controle sem glifo
    ],
)
def test_o_que_a_lista_nao_resolve_e_recusado(recusado):
    assert grafia.sem_grafia(f"Texto {recusado} aqui") == [recusado]


def test_letra_sem_forma_composta_continua_recusada():
    """NFC compõe o que tem forma composta; `q` com acento agudo não tem, e o acento sobra."""
    assert grafia.sem_grafia("q́") == ["́"]


@pytest.mark.parametrize("consumido", ["\t", "\n", "\r"])
def test_tabulacao_e_quebra_nao_sao_recusadas(consumido):
    """O refluxo as consome como espaço em branco antes de o texto chegar ao papel."""
    assert grafia.sem_grafia(f"a{consumido}b") == []


def test_o_portugues_inteiro_e_os_sinais_do_documento_passam():
    texto = "Ação, pública: “Edital” — 1º/2ª • § 3° · R$ 4.200,00 – 50% … € ½"
    assert grafia.normalizar(texto) == texto
    assert grafia.sem_grafia(texto) == []


def test_sem_grafia_diz_cada_caractere_uma_vez_na_ordem():
    assert grafia.sem_grafia("≥ 18 anos → ≥ 2 anos ✓") == ["≥", "→", "✓"]


def test_a_descricao_nomeia_o_caractere_e_o_codigo():
    assert grafia.descrever("≥") == "«≥» (U+2265)"


def test_o_invisivel_e_descrito_pelo_codigo_e_pelo_nome():
    """Entre aspas ele seria `«»`, que não diz nada a quem procura o que colou."""
    assert grafia.descrever("\x07") == "(U+0007)"
    assert grafia.descrever("\u2061") == "(U+2061, FUNCTION APPLICATION)"
