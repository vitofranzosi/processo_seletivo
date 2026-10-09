"""O reconhecimento do número que quem elabora digita, e das remissões do texto (065).

Funções puras, sem banco: o número de subitem no começo de um parágrafo (FR-1199), o título de seção
colado do original (FR-1201) e as remissões internas (FR-1204). A forma é estreita de propósito — o
conflito que ela alimenta impede a submissão (D-001) —, e o conjunto de prova abaixo é o que segura
os falsos positivos (SC-464). Os casos são sintéticos, escritos nas formas dos nove Editais da
amostra; nenhum texto real.
"""

import pytest

from processo_seletivo.editais.domain.numeracao_digitada import (
    numero_de_subitem,
    remissoes,
    titulo_transcrito,
)

# --- o número de subitem (FR-1199) ------------------------------------------------------------


@pytest.mark.parametrize(
    ("paragrafo", "texto", "primeiro"),
    [
        ("4.1 A inscrição será feita pela internet.", "4.1", 4),
        ("4.1. A inscrição será feita pela internet.", "4.1", 4),
        ("4.1) A inscrição será feita pela internet.", "4.1", 4),
        ("4.1 – A inscrição será feita pela internet.", "4.1", 4),
        ("4.1 - A inscrição será feita pela internet.", "4.1", 4),
        ("4.1 — A inscrição será feita pela internet.", "4.1", 4),
        ("4.1", "4.1", 4),
        ("4.1.", "4.1", 4),
        ("4.2.1 Os documentos serão enviados em PDF.", "4.2.1", 4),
        ("4.2.1.3 O arquivo terá até 10 MB.", "4.2.1.3", 4),
        ("• 4.1 A inscrição será feita pela internet.", "4.1", 4),
        ("   4.1 A inscrição será feita pela internet.", "4.1", 4),
        ("04.1 A inscrição será feita pela internet.", "04.1", 4),
        ("12.10 Os casos omissos serão resolvidos pela Comissão.", "12.10", 12),
    ],
)
def test_reconhece_o_numero_de_subitem(paragrafo, texto, primeiro):
    numero = numero_de_subitem(paragrafo)
    assert numero is not None, paragrafo
    assert numero.texto == texto
    assert numero.primeiro == primeiro


def test_o_resto_e_o_texto_depois_do_numero():
    assert numero_de_subitem("4.1. A inscrição.").resto == "A inscrição."
    assert numero_de_subitem("4.1").resto == ""


# --- o conjunto de prova: números legítimos que não são subitem (SC-464) ------------------------

LEGITIMOS = [
    # datas
    "20/10/2026, às 9h, será divulgado o resultado.",
    "24.08.2026 — data da retificação deste Edital.",
    "31/12/2026 é o último dia de validade.",
    # números de lei, decreto e portaria, inclusive quebrados no começo da linha
    "13.146/2015, que considera pessoa com deficiência aquela que tem impedimento.",
    "8.112/1990, no que couber.",
    "12.711/2012 e suas alterações.",
    "9.508/2018, que reserva vagas.",
    # valores
    "1.000,00 (mil reais) é o valor da bolsa.",
    "R$ 1.500,00 por mês.",
    "2.500,50 é o teto.",
    # horas e carga horária
    "30h semanais de dedicação.",
    "1.000 horas de carga horária total.",
    "14h30 é o horário de início.",
    "08:00 é o horário de abertura.",
    "8h às 17h, de segunda a sexta-feira.",
    # percentual
    "25% das vagas são reservadas.",
    "5.5% do total.",
    # ordinais
    "1º lugar na classificação.",
    "2ª chamada de suplentes.",
    "3º Os candidatos serão convocados.",
    # decimal com unidade
    "7.5 pontos para o título de mestre.",
    "6.0 (seis) pontos para a especialização.",
    "10.5 horas de atividades complementares.",
    "2.5 anos de experiência mínima.",
    "1.5 meses de duração.",
    # número de processo, CEP e telefone
    "23185.000123/2026-11 é o número do processo.",
    "29.000-000 é o CEP do Campus.",
    "(27) 3198-0925 é o telefone da Comissão.",
    "3198-0925, de segunda a sexta-feira.",
    # ano solto
    "2026. Fica estabelecido o calendário.",
    "2027 é o ano de início das aulas.",
    # listas de um nível
    "1. Ler atentamente o Edital.",
    "2. Possuir diploma de graduação.",
    "1) Documento de identificação.",
    "I – Documento de identificação.",
    "IV – Comprovante de residência.",
    "a) Documento de identificação.",
    "b) Diploma de graduação.",
    # texto que começa por palavra
    "A inscrição será feita pela internet.",
    "Os candidatos aprovados serão convocados.",
    # número no meio do parágrafo não é começo de parágrafo
    "Conforme o 4.1, a inscrição é gratuita.",
    # os cinco falsos positivos da revisão do PR (09/10/2026): intervalos de hora e de data,
    # reconhecidos pela expressão inteira, e decimais com multiplicador ou grandeza
    "8.30 às 12.00 – atendimento presencial.",
    "10.10 a 20.10 – período de recurso.",
    "1.5 salário mínimo é o valor da bolsa.",
    "1.2 mil candidatos inscritos na edição anterior.",
    "3.5 vezes o valor da taxa.",
    # variações das mesmas expressões
    "13.00 às 17.30h, de segunda a sexta-feira.",
    "25.10 a 05.11.2026 — período de inscrição.",
    "10.10 até 20.10, inclusive.",
]


@pytest.mark.parametrize("paragrafo", LEGITIMOS)
def test_numero_legitimo_nao_e_subitem(paragrafo):
    assert numero_de_subitem(paragrafo) is None, paragrafo


def test_o_conjunto_de_prova_tem_o_tamanho_que_a_spec_pede():
    assert len(LEGITIMOS) >= 40


@pytest.mark.parametrize(
    ("paragrafo", "texto"),
    [
        # intervalo de subitens: "a" não é o conectivo de hora, e o primeiro grupo se repete
        ("1.1 a 1.3 aplicam-se aos candidatos com deficiência.", "1.1"),
        ("8.10 a 8.12 tratam do recurso.", "8.10"),
        # ambíguo — de 10/10 a 10/12, ou dos itens 10.10 a 10.12 —, e fica com o subitem
        ("10.10 a 10.12 tratam do recurso.", "10.10"),
        # "às" sem a outra ponta não é intervalo de hora
        ("4.1 às pessoas com deficiência é assegurado atendimento.", "4.1"),
        # pontas que não são hora nem data
        ("9.30 às 25.00 é o horário estendido.", "9.30"),
        ("10.13 a 20.13 tratam do recurso.", "10.13"),
    ],
)
def test_o_intervalo_so_e_excluido_pela_expressao_inteira(paragrafo, texto):
    """A exclusão é da expressão de hora ou de data, e não do número seguido de "a" ou "às"."""
    numero = numero_de_subitem(paragrafo)
    assert numero is not None, paragrafo
    assert numero.texto == texto


# --- o título transcrito (FR-1201) ------------------------------------------------------------


@pytest.mark.parametrize(
    ("paragrafo", "numero"),
    [
        ("11. DA CONVOCAÇÃO", 11),
        ("6 - DA VERIFICAÇÃO DA AUTODECLARAÇÃO", 6),
        ("6 – DA VERIFICAÇÃO DA AUTODECLARAÇÃO", 6),
        ("4. VAGAS", 4),
    ],
)
def test_reconhece_o_titulo_transcrito(paragrafo, numero):
    assert titulo_transcrito(paragrafo) == numero


@pytest.mark.parametrize(
    "paragrafo",
    [
        "11. Da convocação",
        "1. Ler o Edital",
        "4.1 DA INSCRIÇÃO",
        "11. RG",
        "DA CONVOCAÇÃO",
        "2026. FICA ESTABELECIDO",
    ],
)
def test_nao_e_titulo_transcrito(paragrafo):
    assert titulo_transcrito(paragrafo) is None


# --- as remissões (FR-1204) -------------------------------------------------------------------


def _uma(texto):
    achadas = remissoes(texto)
    assert len(achadas) == 1, achadas
    return achadas[0]


@pytest.mark.parametrize(
    ("texto", "literal", "numeros", "especie"),
    [
        ("forma distinta da prevista no item 8.1.", "item 8.1", ("8.1",), "subitem"),
        ("Item 8.1 deste Edital.", "Item 8.1", ("8.1",), "subitem"),
        ("conforme o subitem 4.2, o candidato", "subitem 4.2", ("4.2",), "subitem"),
        ("nos itens 4.1, 4.2 e 4.3", "itens 4.1, 4.2 e 4.3", ("4.1", "4.2", "4.3"), "subitem"),
        ("nos itens 4.1 a 4.5", "itens 4.1 a 4.5", ("4.1", "4.5"), "subitem"),
        ("nos itens 4.1 ou 4.2", "itens 4.1 ou 4.2", ("4.1", "4.2"), "subitem"),
        (
            "conforme o subitens 4.2.1 e 4.2.2",
            "subitens 4.2.1 e 4.2.2",
            ("4.2.1", "4.2.2"),
            "subitem",
        ),
        ("conforme o item 5, a inscrição", "item 5", ("5",), "secao"),
        ("conforme a Tabela 3, as vagas", "Tabela 3", ("3",), "tabela"),
        ("conforme o Quadro 2, as vagas", "Quadro 2", ("2",), "quadro"),
        ("o item 5.4 deste Edital", "item 5.4", ("5.4",), "subitem"),
        ("conforme o item 5.4 do edital", "item 5.4", ("5.4",), "subitem"),
    ],
)
def test_reconhece_a_remissao_interna(texto, literal, numeros, especie):
    remissao = _uma(texto)
    assert remissao.literal == literal
    assert remissao.numeros == numeros
    assert remissao.especie == especie


@pytest.mark.parametrize(
    "texto",
    [
        "conforme o item 4.1 do Edital nº 28/2026, os candidatos",
        "conforme o item 4.1 da Resolução CS nº 10/2017 do Ifes",
        "nos termos do inciso II do art. 3º da Lei",
        "conforme o item 2.3 do Anexo II",
        "conforme o Quadro 2 do Anexo III",
        "conforme o item 7 da Portaria nº 309/2024",
        "conforme o item 4 do Decreto nº 9.508/2018",
        "conforme o item 1.2 da Instrução Normativa nº 5",
        "conforme o item 3.1 da Nota Técnica nº 11/2010",
        "conforme o item 5.1 do art. 2º",
    ],
)
def test_remissao_a_outro_ato_ou_a_anexo_nao_e_deste_documento(texto):
    assert remissoes(texto) == []


def test_a_exclusao_nao_atravessa_o_ponto_final():
    """ "…item 4.1. A Lei…": a Lei abre outra frase, e a remissão continua sendo deste Edital."""
    remissao = _uma("O prazo é o do item 4.1. A Lei nº 8.112/1990 rege o restante.")
    assert remissao.numeros == ("4.1",)


def test_a_exclusao_alcanca_ate_oito_palavras():
    assert remissoes("o item 4.1 e seus parágrafos, todos da Resolução CS nº 10/2017") == []
    # A designação do outro ato a nove palavras do número já não governa a remissão.
    distante = (
        "o item 4.1, que trata de um assunto muito longo e diferente, nada tendo da Resolução"
    )
    assert len(remissoes(distante)) == 1


def test_varias_remissoes_no_mesmo_texto():
    achadas = remissoes("Conforme o item 4.1 e a Tabela 2, observado o subitem 5.3.")
    assert [remissao.literal for remissao in achadas] == ["item 4.1", "Tabela 2", "subitem 5.3"]


@pytest.mark.parametrize(
    "texto",
    ["conforme o item 10.1.1.1.1, o candidato", "conforme o item 4.123, o candidato"],
)
def test_numero_maior_que_o_de_subitem_e_ignorado_inteiro(texto):
    """Sem virar remissão a "10.1.1.1" nem a "4" — itens que o texto não citou."""
    assert remissoes(texto) == []


def test_na_lista_so_o_numero_maior_e_ignorado():
    assert _uma("nos itens 4.1 e 10.1.1.1.1").numeros == ("4.1",)


def test_palavra_sem_numero_nao_e_remissao():
    assert remissoes("Cada item da lista será conferido; a tabela segue.") == []
