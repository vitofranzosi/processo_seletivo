"""Só os caminhos permitidos gravam movimento ou vaga não preenchida (155, SC-2103, FR-6323).

**Por que existe.** A `155` nasceu de uma reversão que acontecia como efeito de outro ato. Nesta
entrega a reversão continua aplicada pela apuração, como antes dela, e o que entra é a declaração de
vaga não preenchida, sempre por ato com conferência. Um caminho novo que gravasse declaração fora
desse ato, ou movimento fora da reversão de antes, mudaria a vaga sem que teste de comportamento
algum o notasse, porque a quantidade sairia certa.

**O que se permite, e por quê.**

- `ocupacao/application/destinacao.py`: a declaração de vaga não preenchida e o desfazimento dela,
  com prévia assinada e conferência. É o único lugar que grava `VagaNaoPreenchida`.
- `ocupacao/application/movimento.py::gravar_reversao`: a reversão que a emissão da apuração grava,
  pela regra de antes da `155`, nas duas espécies. É o único lugar que grava `MovimentoDeVaga`.
  Quem a chama também é contado: só a emissão e o auxiliar de teste `reverter_cota`.

A destinação por ato próprio, que seria um terceiro caminho, ficou para a próxima entrega
(`claude/155-destinacao-completa`). A varredura lê o texto do código, e não executa nada.
"""

import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1] / "processo_seletivo"


def _gravacao(modelo):
    return re.compile(rf"\b{modelo}(\.objects\.(create|bulk_create|get_or_create)|\()")


GRAVACAO_DE_MOVIMENTO = _gravacao("MovimentoDeVaga")
GRAVACAO_DE_NAO_PREENCHIDA = _gravacao("VagaNaoPreenchida")
CHAMADA_DA_REVERSAO = re.compile(r"\bgravar_reversao\(")

QUEM_GRAVA_MOVIMENTO = {"ocupacao/application/movimento.py"}
QUEM_GRAVA_NAO_PREENCHIDA = {"ocupacao/application/destinacao.py"}
QUEM_CHAMA_A_REVERSAO = {
    "ocupacao/application/emissao.py",
    "ocupacao/application/movimento.py",
}


def _fontes():
    for arquivo in sorted(RAIZ.rglob("*.py")):
        if "migrations" in arquivo.parts or arquivo.name == "models.py":
            continue
        yield arquivo.relative_to(RAIZ).as_posix(), arquivo.read_text(encoding="utf-8")


def _fora(padrao, permitidos):
    return sorted(
        caminho
        for caminho, texto in _fontes()
        if padrao.search(texto) and caminho not in permitidos
    )


def test_so_a_declaracao_grava_vaga_nao_preenchida():
    fora = _fora(GRAVACAO_DE_NAO_PREENCHIDA, QUEM_GRAVA_NAO_PREENCHIDA)
    assert not fora, f"gravação de vaga não preenchida fora do ato próprio: {fora}"


def test_so_a_reversao_da_apuracao_grava_movimento():
    fora = _fora(GRAVACAO_DE_MOVIMENTO, QUEM_GRAVA_MOVIMENTO)
    assert not fora, f"gravação de movimento de vaga fora da reversão: {fora}"


def test_a_reversao_so_e_gravada_pela_emissao():
    fora = sorted(
        caminho
        for caminho, texto in _fontes()
        if CHAMADA_DA_REVERSAO.search(texto.replace("def gravar_reversao(", ""))
        and caminho not in QUEM_CHAMA_A_REVERSAO
    )
    assert not fora, f"gravar_reversao chamada fora da emissão: {fora}"


def test_a_varredura_reconhece_uma_gravacao():
    """Sem este caso, um padrão quebrado deixaria os de cima verdes para sempre."""
    assert GRAVACAO_DE_MOVIMENTO.search("MovimentoDeVaga.objects.create(")
    assert GRAVACAO_DE_NAO_PREENCHIDA.search("VagaNaoPreenchida(especie=...)")
    assert not GRAVACAO_DE_MOVIMENTO.search("MovimentoDeVaga.objects.filter(")
