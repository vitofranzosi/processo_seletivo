"""Nenhuma tela da `013` afirma colocação, aprovação final, vaga ou convocação.

**Por que existe.** A fronteira entre esta feature e a próxima é a frase mais fácil de atravessar
sem perceber: `HABILITADA` significa "segue para a Etapa seguinte", e uma legenda escrita com
pressa a transforma em "aprovado". O candidato lê a palavra, não a spec — e uma tela que diga
"classificado" cria expectativa de direito que o ato não produziu.

É defeito silencioso por natureza: nada quebra, nenhum teste de comportamento falha, e a promessa
só se desfaz quando alguém a cobra. Por isso vira varredura de fonte, como a de citações da `010`.

**Comentário não é afirmação.** O template explica a si mesmo, e explicar por que uma palavra está
proibida exige escrevê-la. A varredura lê o template **sem** os blocos `{% comment %}` — o mesmo
critério que a folha de estilo já usa para separar citar de definir.

**A negação também não salva.** Escrever "não é aprovação" põe a palavra na tela para negá-la, e
quem lê depressa lê a palavra. A fronteira se diz pela afirmação — é essa a razão de a lista abaixo
não ter exceção para frases negativas.
"""

import re
from pathlib import Path

import pytest

TEMPLATES = Path(__file__).resolve().parents[1] / "processo_seletivo/interface/templates/interface"
# As telas que a 013 escreve ou amplia. Não é a pasta inteira: a 006 fala de vagas o tempo todo, e
# deve — é o Edital declarando o que oferece, e não um Resultado afirmando quem as ocupa.
DA_013 = ["resultados.html", "distribuicao.html"]

# Cada termo com o que ele afirmaria indevidamente. A mensagem entra na falha, para que quem a
# receba entenda a fronteira em vez de só remover a palavra.
PROIBIDOS = {
    r"coloca[çc][ãa]o": "colocação é ordenação entre candidatos, e nada aqui compara ninguém",
    r"classificad[oa]": "classificar exige comparar candidatos e combinar Etapas",
    r"aprovad[oa]": "aprovação é do Processo, e não de uma Etapa",
    r"reprovad[oa]": "reprovação é do Processo; a Etapa elimina, e elimina dela",
    r"convoca[çc]": "convocação decorre da classificação e da existência de vaga",
    r"ocupa\w* a vaga": "ocupação de vaga é decisão posterior à classificação",
    r"resultado final": "o Resultado desta feature é da Etapa, e nunca do Processo",
    r"resultado preliminar": "preliminar e definitivo pertencem à publicação, que é outra feature",
}

SEM_COMENTARIO = re.compile(r"\{%\s*comment\s*%\}.*?\{%\s*endcomment\s*%\}", re.S)


def visivel(caminho):
    """O template sem os blocos de comentário: o que a página de fato diz."""
    return SEM_COMENTARIO.sub(" ", caminho.read_text())


@pytest.mark.parametrize("nome", DA_013)
def test_nenhuma_tela_da_013_afirma_o_que_ela_nao_decide(nome):
    corpo = visivel(TEMPLATES / nome).lower()
    achados = [
        f"{termo!r} — {porque}" for termo, porque in PROIBIDOS.items() if re.search(termo, corpo)
    ]
    assert achados == [], f"{nome}: " + "; ".join(achados)


def test_a_varredura_enxerga_um_termo_proibido():
    """Quem verifica que a varredura ainda enxerga.

    Sem isto, um erro na expressão regular tornaria o teste acima verde para sempre — e um teste
    que não falha nunca é indistinguível de um que não existe.
    """
    corpo = "<p>a candidata foi classificada em segundo lugar</p>"
    assert any(re.search(termo, corpo) for termo in PROIBIDOS)


def test_o_comentario_do_template_pode_nomear_o_que_a_tela_nao_diz():
    """Explicar a proibição exige escrever a palavra proibida."""
    corpo = "{% comment %}aprovado não se diz aqui{% endcomment %}<p>Habilitada</p>"
    assert not any(re.search(termo, SEM_COMENTARIO.sub(" ", corpo)) for termo in PROIBIDOS)
