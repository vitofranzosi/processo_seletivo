"""Só os atos próprios gravam a destinação da vaga (155, SC-2103, FR-6308, FR-6323).

**Por que existe.** A `155` nasceu de uma reversão que acontecia como efeito de outro ato: a emissão
da apuração gravava o movimento de vaga na mesma transação, sem que quem a emitia confirmasse a
cessão. Um caminho novo que voltasse a gravar movimento — ou declaração de vaga não preenchida —
fora dos comandos com conferência repetiria o defeito sem que teste de comportamento algum o
notasse, porque a quantidade sairia certa.

**O que se permite, e por quê.**

- `ocupacao/application/destinacao.py`: os comandos da destinação, da declaração e dos
  desfazimentos, todos com prévia assinada e conferência.
- `ocupacao/application/movimento.py::gravar_reversao`: a gravação da reversão por saldo, que a
  emissão ainda faz até a decisão do usuário sobre a condição do saldo (incremento F, R-010 da
  pesquisa). Quem a chama também é contado: só a emissão e o auxiliar de teste `reverter_cota`.

A varredura lê o texto do código, e não executa nada.
"""

import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1] / "processo_seletivo"

GRAVACAO = re.compile(r"\b(MovimentoDeVaga|VagaNaoPreenchida)(\.objects\.(create|bulk_create)|\()")
CHAMADA_DA_REVERSAO = re.compile(r"\bgravar_reversao\(")

QUEM_GRAVA = {
    "ocupacao/application/destinacao.py",
    "ocupacao/application/movimento.py",
}
QUEM_CHAMA_A_REVERSAO = {
    "ocupacao/application/emissao.py",
    "ocupacao/application/movimento.py",
}


def _fontes():
    for arquivo in sorted(RAIZ.rglob("*.py")):
        if "migrations" in arquivo.parts or arquivo.name == "models.py":
            continue
        yield arquivo.relative_to(RAIZ).as_posix(), arquivo.read_text(encoding="utf-8")


def test_so_os_atos_proprios_gravam_movimento_ou_vaga_nao_preenchida():
    fora = sorted(
        caminho
        for caminho, texto in _fontes()
        if GRAVACAO.search(texto) and caminho not in QUEM_GRAVA
    )
    assert not fora, f"gravação de destinação fora dos atos próprios: {fora}"


def test_a_reversao_por_saldo_so_e_gravada_pela_emissao():
    fora = sorted(
        caminho
        for caminho, texto in _fontes()
        if CHAMADA_DA_REVERSAO.search(texto.replace("def gravar_reversao(", ""))
        and caminho not in QUEM_CHAMA_A_REVERSAO
    )
    assert not fora, f"gravar_reversao chamada fora da emissão: {fora}"


def test_a_varredura_reconhece_uma_gravacao():
    """Sem este caso, um padrão quebrado deixaria os dois de cima verdes para sempre."""
    assert GRAVACAO.search("MovimentoDeVaga.objects.create(")
    assert GRAVACAO.search("VagaNaoPreenchida(especie=...)")
    assert not GRAVACAO.search("MovimentoDeVaga.objects.filter(")
