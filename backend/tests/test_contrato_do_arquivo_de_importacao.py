"""O contrato do arquivo e o código dizem a mesma coisa — coluna a coluna (`031`, `FR-445`).

**Irmão de `test_contrato_de_saida_do_requerimento.py`**, e com uma pergunta a mais. Aquele prende
*"de onde sairia cada coluna"*; este prende *"quem produz o valor"* — e prende contra a
implementação, não contra si mesmo.

**Por que um contrato precisa de teste.** Um documento de correspondência é a coisa mais fácil de
deixar para trás: renomeia-se um serializador, e a linha do contrato continua parecendo certa. Ele
não tem como acusar o que não sabe que mudou. O que o prende é a comparação com o módulo real.

**E é este teste que guarda a `FR-445` de verdade.** A regra é *"cada uma das 34 colunas tem
serializador próprio"*, e a forma de violá-la sem perceber é nomear um `texto` genérico em dezesseis
linhas — que é o mesmo `legivel()` com outro nome. Aqui, duas colunas que compartilhem função são
acusadas, com a exceção nomeada das três que **são** a mesma decisão (`D-001`).
"""

import re
from pathlib import Path

import pytest

from processo_seletivo.matriculas.domain import colunas

CONTRATO = (
    Path(__file__).resolve().parents[2]
    / "specs/031-exportacao-de-matriculas/contracts/arquivo-de-importacao.md"
)

TOTAL_DE_COLUNAS = 34
# As três da `D-001` compartilham `vazio_externo` **de propósito**: elas não são três decisões
# parecidas, são a mesma decisão — o valor é vocabulário de outro sistema — aplicada a três colunas.
# Dar função própria a cada uma sugeriria que uma delas pode passar a ter fonte sem que as outras
# mudem, e a decisão diz o contrário.
COMPARTILHADO = {"COD_CURSO", "COD_TURNO", "COD_POLO"}


def linhas_do_contrato():
    encontradas = []
    for linha in CONTRATO.read_text(encoding="utf-8").splitlines():
        if not linha.startswith("|"):
            continue
        celulas = [celula.strip() for celula in linha.strip("|").split("|")]
        if len(celulas) == 5 and celulas[0].isdigit():
            encontradas.append(
                {
                    "ordem": int(celulas[0]),
                    "coluna": celulas[1].strip("`"),
                    "serializador": celulas[2].strip("`"),
                }
            )
    return encontradas


def test_o_contrato_existe_e_e_legivel():
    """Renomear o arquivo não pode transformar a garantia em silêncio aprovado."""
    assert CONTRATO.exists(), f"o contrato desta feature não está em {CONTRATO}"
    assert len(linhas_do_contrato()) == TOTAL_DE_COLUNAS


def test_o_contrato_e_o_codigo_descrevem_as_mesmas_colunas_na_mesma_ordem():
    """`FR-436`: a ordem é a do destino, e uma coluna fora de lugar é um arquivo recusado."""
    do_contrato = [linha["coluna"] for linha in linhas_do_contrato()]
    assert do_contrato == list(colunas.CABECALHOS)


@pytest.mark.parametrize("linha", linhas_do_contrato(), ids=lambda linha: linha["coluna"])
def test_cada_serializador_nomeado_no_contrato_existe_no_codigo(linha):
    """O nome escrito no contrato é o nome da função que produz o valor daquela coluna."""
    funcao = getattr(colunas, linha["serializador"], None)
    assert funcao is not None, (
        f"o contrato nomeia `{linha['serializador']}` para `{linha['coluna']}`, e a função não "
        "existe em `matriculas/domain/colunas.py`"
    )
    posicao = colunas.CABECALHOS.index(linha["coluna"])
    assert colunas.COLUNAS[posicao].serializador is funcao


def test_nenhuma_coluna_reaproveita_a_funcao_de_outra():
    """`FR-445`: um `texto` genérico em dezesseis colunas é `legivel()` com outro nome.

    A exceção é a `D-001`, e ela está nomeada em `COMPARTILHADO` — três colunas, uma decisão só.
    """
    por_funcao = {}
    for coluna in colunas.COLUNAS:
        por_funcao.setdefault(coluna.serializador.__name__, []).append(coluna.cabecalho)
    repetidas = {
        nome: cabecalhos
        for nome, cabecalhos in por_funcao.items()
        if len(cabecalhos) > 1 and set(cabecalhos) != COMPARTILHADO
    }
    assert repetidas == {}, (
        f"colunas diferentes compartilham serializador sem decisão que o justifique: {repetidas}"
    )


def test_o_contrato_nao_promete_conversao_que_o_codigo_recusa():
    """As quatro tentações estão escritas no contrato, e o código as recusa uma a uma."""
    texto = CONTRATO.read_text(encoding="utf-8")
    for tentacao in ("per capita", "PPI", "PT", "sequencial"):
        assert re.search(rf"\b{re.escape(tentacao)}\b", texto), (
            f"o contrato deixou de registrar a tentação «{tentacao}» — e ela é o que o próximo "
            "leitor vai querer 'consertar'"
        )
    assert "PPI" in colunas.CODIGOS_DO_DESTINO
    assert colunas.CORES_DO_DESTINO.get("INDIGENA") is None
