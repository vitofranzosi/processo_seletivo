"""Quem pergunta se um Edital pode ser publicado — uma lista fechada (046, `FR-756`).

**Por que existe.** O `RC-32` da auditoria de consolidação não foi um erro de regra: foi a validação
de publicabilidade consultada fora do lugar dela. A tela de um Edital publicado perguntava se ele
podia ser publicado e respondia *"Impede — corrija antes de publicar"*. Nenhum teste funcional
acusava, porque a resposta era a certa para a pergunta errada.

A próxima superfície que chamar `validate_for_publication` para "mostrar os problemas do Edital"
reintroduz o defeito, e é por isso que a garantia é estrutural, no molde de
`tests/test_vigencia_do_resultado.py`. **Acrescentar um chamador exige mudar a lista abaixo e
escrever por quê** — que é exatamente a conversa que este teste existe para forçar.
"""

import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
APLICACAO = RAIZ / "backend" / "processo_seletivo"

CHAMADA = re.compile(r"\bvalidate_for_publication\(")

# Cada entrada é um lugar que pergunta, e a razão pela qual ele pode perguntar.
QUEM_PERGUNTA = {
    "editais/domain/validation.py": "a definição",
    "publicacoes/application/publish_edital.py": (
        "submeter e publicar recusam pelo ato de publicação"
    ),
    "publicacoes/application/retificacoes.py": (
        "a Retificação recusa pelo próprio ato, e a confirmação dela adverte com ele"
    ),
    "interface/views.py": (
        "`_pendencias` antecipa o ato antes da publicação; depois dela, só os fatos da lista "
        "`FATOS_DO_CONTEUDO_PUBLICADO`"
    ),
}


def chamadores(raiz=APLICACAO):
    return {
        str(arquivo.relative_to(raiz))
        for arquivo in raiz.rglob("*.py")
        if CHAMADA.search(arquivo.read_text(encoding="utf-8"))
    }


def test_a_validacao_de_publicabilidade_so_e_consultada_por_quem_a_lista_nomeia():
    novos = sorted(chamadores() - set(QUEM_PERGUNTA))

    assert not novos, (
        "validate_for_publication chamada fora da lista de quem pode perguntar se o Edital pode "
        f"ser publicado: {novos}. Se for um ato que confere conteúdo normativo, ou superfície que "
        "o antecipa antes da publicação, acrescente-o a QUEM_PERGUNTA com a razão (046, FR-756)."
    )


def test_a_lista_nao_guarda_quem_ja_deixou_de_perguntar():
    """Entrada morta afrouxa a lista em silêncio: o próximo chamador ali passaria sem conversa."""
    assert set(QUEM_PERGUNTA) <= chamadores()


def test_a_varredura_enxerga(tmp_path):
    """A prova de que o padrão ainda casa — uma expressão que deixa de casar aprova tudo, calada."""
    (tmp_path / "tela.py").write_text("achados = validate_for_publication(conteudo)\n")
    (tmp_path / "outra.py").write_text("# fala de validate_for_publication sem chamar\n")

    assert chamadores(tmp_path) == {"tela.py"}
