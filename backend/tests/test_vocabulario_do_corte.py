"""Nenhuma superfície da `014` afirma que vaga foi ocupada, preenchida, ou que há déficit.

**Por que existe.** A fronteira com a `016` é a frase mais fácil de atravessar sem perceber. O corte
diz **quem progride**; quantas vagas foram ocupadas e quantas faltam é conta que esta feature não
faz e não tem como fazer — ela não sabe de aceite, de matrícula nem de desistência. Uma legenda
escrita com pressa transforma "progrediu" em "está com a vaga", e o candidato lê a palavra, não a
spec.

É defeito silencioso por natureza: nada quebra, nenhum teste de comportamento falha, e a promessa
só se desfaz quando alguém a cobra. Por isso vira varredura de fonte, como a da `013` — e este
arquivo é irmão de `test_vocabulario_do_resultado.py`, com a mesma mecânica e pelo mesmo motivo.

**Comentário não é afirmação.** O template explica a si mesmo, e explicar por que uma palavra está
proibida exige escrevê-la. A varredura lê o template **sem** os blocos `{% comment %}`, que é o
mesmo critério do precedente — sem ele, a prosa que explica a fronteira reprovaria a si própria.

**A varredura alcança o código também**, e não só a tela: a mensagem de uma recusa é tão publicada
quanto uma legenda, e é ela que a operação lê no dia em que o corte não sai.
"""

import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1] / "processo_seletivo"
TEMPLATES = RAIZ / "interface/templates/interface"

# A tela da feature, e os módulos que produzem o que ela e a API dizem.
DA_014 = [
    TEMPLATES / "corte.html",
    RAIZ / "classificacao/application/corte.py",
    RAIZ / "classificacao/application/emissao_do_corte.py",
    RAIZ / "classificacao/domain/faixa.py",
]

# Cada termo com o que ele afirmaria indevidamente. A mensagem entra na falha, para que quem a
# receba entenda a fronteira em vez de só remover a palavra.
PROIBIDOS = {
    r"vaga ocupada": "ocupação de vaga é da 016, e depende de aceite e matrícula",
    r"vagas ocupadas": "idem — e o plural é o mais fácil de escrever sem perceber",
    r"vaga preenchida": "preenchimento é o desfecho da ocupação, e não da progressão",
    r"vagas preenchidas": "idem",
    r"d[ée]ficit": "apurar déficit é a conta da 016; esta feature não sabe de desistência",
    r"remanejamento": "remanejar entre modalidades é da 016",
    r"convoca[çc]": "convocar e comunicar é da 019",
}

SEM_COMENTARIO = re.compile(
    r"\{%\s*comment\s*%\}.*?\{%\s*endcomment\s*%\}|^\s*#.*$|\"\"\".*?\"\"\"",
    re.S | re.M,
)


def visivel(caminho):
    """O arquivo sem comentário e sem docstring: o que ele de fato afirma a quem o lê na tela."""
    return SEM_COMENTARIO.sub(" ", caminho.read_text())


@pytest.mark.parametrize("caminho", DA_014, ids=lambda item: item.name)
def test_nenhuma_superficie_da_014_afirma_o_que_ela_nao_decide(caminho):
    corpo = visivel(caminho).lower()
    achados = [
        f"{termo!r} — {porque}" for termo, porque in PROIBIDOS.items() if re.search(termo, corpo)
    ]
    assert achados == [], f"{caminho.name}: " + "; ".join(achados)


def test_a_varredura_enxerga_um_termo_proibido():
    """Uma expressão que deixa de casar não falha: ela aprova tudo, calada."""
    corpo = "a tela dizia que a vaga ocupada era dele".lower()

    assert [termo for termo in PROIBIDOS if re.search(termo, corpo)] == ["vaga ocupada"]


def test_a_varredura_descarta_comentario_e_docstring(tmp_path):
    """Sem isto, a prosa que explica a fronteira reprovaria a si própria.

    A prova é feita sobre um arquivo sintético de propósito: escrever o termo proibido dentro de um
    comentário do template real para provar o descarte seria pôr a palavra na árvore justamente
    onde a próxima varredura — a de outra feature, com outra lista — a encontraria.
    """
    template = tmp_path / "exemplo.html"
    template.write_text(
        "<p>Progride quem a faixa alcançou.</p>\n"
        "{% comment %}Não escrever vaga ocupada aqui.{% endcomment %}\n"
    )

    corpo = visivel(template).lower()

    assert "progride" in corpo
    assert "vaga ocupada" not in corpo


def test_a_varredura_alcanca_os_arquivos_que_promete():
    """Renomear um arquivo transformaria a garantia em silêncio aprovado."""
    assert all(caminho.exists() for caminho in DA_014)
    assert len(DA_014) >= 4
