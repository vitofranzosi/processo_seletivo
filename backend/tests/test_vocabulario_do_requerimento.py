"""Nenhuma superfície da `029` afirma um desfecho que ela não decide (`UX-058`, `SC-132`).

**A fronteira que esta varredura guarda.** O Requerimento de Matrícula é **declaração da pessoa**.
Quem decide a vaga é a convocação; quem efetiva a matrícula é o Registro Acadêmico. Dizer
*"deferido"* numa tela desta feature prometeria ao candidato um desfecho que ela não tem como
produzir — e quem lê a tela lê a palavra, não a spec.

**As quatro palavras não são sinônimas, e cada uma mente de um jeito.** *Deferido* e *indeferido*
afirmam um juízo sobre o que foi declarado, e nenhum ato desta feature o pratica. *Homologado*
afirma um ato de autoridade que pertence à publicação. *Matrícula efetivada* afirma o fato final do
arco inteiro — e é o mais perigoso, porque é exatamente o que a pessoa quer ler.

**Comentário não é afirmação.** Explicar por que uma palavra está proibida exige escrevê-la, e por
isso a varredura lê o texto **sem** comentário e sem docstring. Quem esquecer isso escreve um teste
que reprova pelo próprio comentário que o explica — e foi o que aconteceu neste repositório com a
varredura de armazenamento no navegador, num arquivo desta mesma feature.

**A lista de arquivos é literal, e não um glob.** Um glob sobre `requerimentos/` deixaria de fora as
telas — que moram em `portal/` e em `interface/` — e é justamente nelas que a palavra escorrega. A
lista é o que torna a omissão visível a quem acrescentar superfície nova.
"""

import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1] / "processo_seletivo"
PORTAL = RAIZ / "portal/templates/portal"
GESTAO = RAIZ / "interface/templates/interface"

# As superfícies desta feature: as telas dos dois canais, o que produz o texto delas, e o
# vocabulário que as duas leem.
DA_029 = [
    PORTAL / "requerimento.html",
    PORTAL / "requerimento_anterior.html",
    PORTAL / "_cartao_do_requerimento.html",
    GESTAO / "compor_inscricao.html",
    RAIZ / "portal/requerimento.py",
    RAIZ / "requerimentos/domain/rotulos.py",
    RAIZ / "requerimentos/domain/nomes.py",
    RAIZ / "requerimentos/domain/disponibilidade.py",
    RAIZ / "requerimentos/application/selectors.py",
    RAIZ / "requerimentos/application/preencher.py",
    RAIZ / "requerimentos/application/exigencia.py",
    RAIZ / "editais/application/requerimento.py",
]

# Cada termo com o que ele afirmaria indevidamente. A frase entra na falha, para que quem a receba
# entenda a fronteira em vez de só apagar a palavra.
PROIBIDOS = {
    r"deferid": "afirma um juízo sobre o que foi declarado; nenhum ato desta feature o pratica — "
    "e o particípio alcança *deferido* e *indeferido* de uma vez",
    r"homologa": "homologação é ato de autoridade da publicação, e não do requerimento",
    r"matr[íi]cula efetivad": "é o fato final do arco inteiro, e o mais perigoso de escrever — "
    "é exatamente o que a pessoa quer ler",
    # **Além das quatro que a `UX-058` nomeia**, e a razão é a mesma: é promessa de desfecho. A
    # tela da convocação já a proíbe por conta própria, e ter as duas listas concordando é o que
    # impede a frase de migrar de uma feature para a outra.
    r"vaga garantid": "quem decide a vaga é a convocação; declarar não garante nada",
}

# **`aprovado` esteve nesta lista e saiu.** Ele não é da `UX-058`, e a primeira redação o incluiu
# por simetria com a varredura da `016`. A frase que ele reprovou — *"todo mundo preenche, inclusive
# quem não for aprovado"*, dita a quem elabora — é verdadeira e não afirma nada sobre o
# requerimento: ela descreve o resultado da **seleção**, que é o fato que torna a coleta antecipada
# uma decisão a pesar. Proibir a palavra obrigaria a reescrever prosa clara para satisfazer o teste,
# que é o modo de uma varredura passar a governar o produto em vez de guardá-lo.

SEM_COMENTARIO = re.compile(
    r"\{%\s*comment\s*%\}.*?\{%\s*endcomment\s*%\}|^\s*#.*$|\"\"\".*?\"\"\"",
    re.S | re.M,
)


def visivel(caminho):
    """O arquivo sem comentário e sem docstring: o que ele de fato afirma a quem o lê."""
    return SEM_COMENTARIO.sub(" ", caminho.read_text())


def test_a_lista_de_superficies_existe_inteira():
    """Renomear um arquivo não pode transformar a garantia em silêncio aprovado."""
    ausentes = [caminho.name for caminho in DA_029 if not caminho.exists()]

    assert ausentes == [], f"a varredura aponta para arquivos que não existem: {ausentes}"


@pytest.mark.parametrize("caminho", DA_029, ids=lambda item: item.name)
def test_nenhuma_superficie_da_029_afirma_desfecho_que_ela_nao_decide(caminho):
    corpo = visivel(caminho).lower()
    achados = [
        f"{termo!r} — {porque}" for termo, porque in PROIBIDOS.items() if re.search(termo, corpo)
    ]

    assert achados == [], f"{caminho.name}: " + "; ".join(achados)


def test_a_varredura_enxerga_um_termo_proibido():
    """Uma expressão que deixa de casar não falha: ela aprova tudo, calada."""
    corpo = "a tela dizia que o requerimento foi deferido".lower()

    assert [termo for termo in PROIBIDOS if re.search(termo, corpo)] == [r"deferid"]


def test_a_varredura_descarta_comentario_e_docstring(tmp_path):
    """Sem isto, a prosa que explica a fronteira reprovaria a si própria.

    Não é hipótese: nesta mesma feature, a varredura de armazenamento no navegador reprovou um
    comentário que **prometia** não usar as APIs que ele citava para explicar a proibição.
    """
    arquivo = tmp_path / "sintetico.py"
    arquivo.write_text(
        '"""Nada aqui é deferido nem indeferido."""\n'
        "# e homologação também não\n"
        "def declarar():\n"
        "    return 'enviado'\n",
        encoding="utf-8",
    )

    corpo = visivel(arquivo).lower()

    assert [termo for termo in PROIBIDOS if re.search(termo, corpo)] == []


def test_o_comentario_de_template_tambem_e_descartado(tmp_path):
    """Os templates desta feature explicam a proibição dentro de `{% comment %}`."""
    arquivo = tmp_path / "sintetico.html"
    arquivo.write_text(
        "{% comment %}nao dizer deferido nem matricula efetivada{% endcomment %}\n"
        "<p>Requerimento enviado.</p>\n",
        encoding="utf-8",
    )

    corpo = visivel(arquivo).lower()

    assert [termo for termo in PROIBIDOS if re.search(termo, corpo)] == []
