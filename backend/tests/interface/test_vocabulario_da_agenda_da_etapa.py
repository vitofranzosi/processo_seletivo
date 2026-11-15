"""O que as telas da agenda da Etapa não dizem (167, T033, D-004, D-005, FR-7250 a FR-7252).

A agenda diz **quando** cada pessoa é atendida. Ela não registra presença, ausência nem nota — a
ausência continua sendo uma Ocorrência —; a banca é ponto de atendimento, e não grupo de
avaliadores; e a agenda não convoca para vaga. Uma frase basta para prometer o contrário, e por isso
a varredura lê o texto visível de cada tela.

**A lista é literal**, como nas varreduras irmãs: uma lista calculada deixaria de ver a tela que
sumisse dela. Cada entrega acrescenta os templates dela aqui; os do portal, que a B trouxe, estão na
varredura das telas públicas, sobre a página renderizada.
"""

import re
from pathlib import Path

import pytest

TEMPLATES = Path(__file__).resolve().parents[2] / "processo_seletivo/interface/templates/interface"

DA_167 = [
    "agenda_configurar.html",
    "_agenda_formulario.html",
    "_agenda_capacidade.html",
    "agenda_montar.html",
    "_agenda_grade.html",
    "_agenda_painel.html",
    # A entrega B: conferir e a agenda publicada.
    "agenda_conferir.html",
    "agenda_publicada.html",
]

PROIBIDAS = [
    (r"\bpresen[çc]a", "a agenda não registra presença (FR-7251)"),
    (r"\bausen[tc]", "a ausência é Ocorrência, e não da agenda (FR-7250)"),
    (r"\bnota\b", "a agenda não registra nota (FR-7250)"),
    (r"\bavaliador", "a banca não é grupo de avaliadores (D-004)"),
    (r"\bconvoca", "a agenda não convoca para vaga (D-005)"),
    (r"\bvaga\b", "a agenda não convoca para vaga (D-005)"),
]


def visivel(texto):
    sem_comentario = re.sub(r"\{%\s*comment\s*%\}.*?\{%\s*endcomment\s*%\}", " ", texto, flags=re.S)
    sem_marcacao = re.sub(r"\{%.*?%\}|\{\{.*?\}\}", " ", sem_comentario, flags=re.S)
    return re.sub(r"<[^>]+>", " ", sem_marcacao)


def test_a_lista_existe_no_disco():
    assert all((TEMPLATES / nome).exists() for nome in DA_167)


@pytest.mark.parametrize("nome", DA_167)
def test_nenhuma_tela_da_agenda_promete_o_que_ela_nao_faz(nome):
    texto = visivel((TEMPLATES / nome).read_text()).lower()

    achados = [motivo for padrao, motivo in PROIBIDAS if re.search(padrao, texto)]
    assert achados == [], f"{nome}: {achados}"


def test_a_varredura_ainda_enxerga():
    assert re.search(PROIBIDAS[3][0], visivel("<p>Cada avaliador da banca</p>").lower())
    assert not re.search(PROIBIDAS[5][0], visivel('<a class="vaga">Livre</a>').lower())
