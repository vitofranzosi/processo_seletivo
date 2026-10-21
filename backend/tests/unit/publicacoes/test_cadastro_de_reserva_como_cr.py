"""O Perfil de cadastro de reserva sem vaga imediata sai como `CR` no documento (096).

Nenhuma decisão anterior tinha escolhido o `0` contra o `CR`: ele era o resíduo da `027` ("`0` diz
zero", que é sobre o dado), da linha "Total 0" tirada em 30/09 e da `067`, que deixou a tabela de
Perfis com "Vagas imediatas: 0". A equipe escreve `CR` à mão (o 76/2026), e nenhum Edital de
cadastro de reserva da amostra imprime `0`. O dado continua `0` (D-001); a composição imprime a
sigla, com a nota "CR: cadastro de reserva." abaixo de toda tabela que a usa (D-002).
"""

import copy
import re

import pytest

from processo_seletivo.publicacoes.infrastructure import pdf
from tests.unit.publicacoes.cenarios_da_auditoria import levado_ao_catalogo_novo, por_perguntas
from tests.unit.publicacoes.test_pdf import documento, snapshot, texto_de

NOTA = "CR: cadastro de reserva."


def _perfil(total=0, reserva="LIMITED", linhas=None):
    perfil = {"immediateVacancies": total, "reserveType": reserva}
    if linhas is not None:
        perfil["vacancyTable"] = [{"modalityId": None, "immediateVacancies": v} for v in linhas]
    return perfil


# ---------------------------------------------------------------------------
# As peças (T004)
# ---------------------------------------------------------------------------


def test_a_sigla_e_a_nota_sao_as_da_equipe():
    assert pdf.SIGLA_DO_CADASTRO == "CR"
    assert pdf.NOTA_DO_CADASTRO == NOTA


@pytest.mark.parametrize(
    ("perfil", "celula"),
    [
        pytest.param(_perfil(reserva="LIMITED"), "CR", id="limitado"),
        pytest.param(_perfil(reserva="UNLIMITED"), "CR", id="ilimitado"),
        pytest.param(_perfil(reserva="NONE"), "0", id="sem cadastro"),
        pytest.param(_perfil(linhas=[2]), "0", id="incoerente"),
        pytest.param(_perfil(total=7), "7", id="com vaga e cadastro"),
        pytest.param(_perfil(total=7, reserva="NONE"), "7", id="com vaga sem cadastro"),
    ],
)
def test_a_celula_de_vagas(perfil, celula):
    """FR-2403, FR-2408."""
    assert pdf.vagas_impressas(perfil) == celula


def test_a_celula_do_total_ausente_e_a_de_sempre():
    """O `get("immediateVacancies", 0)` de antes: o que não é CR imprime o que imprimia."""
    assert pdf.vagas_impressas({"reserveType": "NONE"}) == "0"


def test_a_nota_sai_quando_algum_e_cr():
    assert pdf.nota_da_sigla([_perfil(total=6), _perfil()]) == NOTA


@pytest.mark.parametrize(
    "perfis",
    [
        pytest.param([], id="nenhum"),
        pytest.param([_perfil(total=6)], id="com vaga"),
        pytest.param([_perfil(reserva="NONE")], id="sem cadastro"),
    ],
)
def test_a_nota_nao_sai_sem_cr(perfis):
    assert pdf.nota_da_sigla(perfis) is None


# ---------------------------------------------------------------------------
# A nota na tabela (T005)
# ---------------------------------------------------------------------------


def _itens_da_tabela(**kwargs):
    composicao = pdf.Composicao()
    pdf._tabela(composicao, ["Perfil", "Vagas"], [["TP-01", "CR"], ["TD-ADM", "6"]], **kwargs)
    return composicao.itens


def test_a_nota_sai_depois_da_grade_em_corpo_de_tabela():
    itens = _itens_da_tabela(nota=NOTA)
    fim_da_tabela = max(i for i, item in enumerate(itens) if item[:2] == ("fecha", "tabela"))
    textos = [(i, item) for i, item in enumerate(itens) if item[0] == "texto" and item[1] == NOTA]

    assert len(textos) == 1
    indice, nota = textos[0]
    assert indice > fim_da_tabela, "a nota explica a tabela, e vem depois dela"
    assert indice == len(itens) - 1
    # ("texto", parte, fonte, tamanho, recuo, antes, alinhamento, junto, repetir, justificar)
    assert nota[2] == pdf.REGULAR
    assert nota[3] == pdf.CORPO_TABELA, "CORPO_NOTA é o do rodapé técnico"
    assert nota[5] == pdf.ANTES_DE_LINHA


def test_a_nota_nao_vai_junto():
    """D-007, corrigido na implementação: `junto` prende à linha **seguinte**, e não à anterior.

    O paginador não leva a grade com a linha que a segue (`prender_a_ultima_linha`, de propósito):
    a nota segue a tabela como a frase de reversão segue o quadro.
    """
    nota = _itens_da_tabela(nota=NOTA)[-1]

    assert nota[7] is False


def test_sem_nota_a_tabela_e_a_de_antes():
    assert _itens_da_tabela(nota=None) == _itens_da_tabela()


# ---------------------------------------------------------------------------
# US1 — a tabela de Perfis da apresentação plana (T010, T011)
# ---------------------------------------------------------------------------

LEGENDA = re.compile(r"^Tabela (\d+) — (.+)$")
COLUNAS_DA_TABELA_DE_PERFIS = 5


def _perfil_do_snapshot(codigo, total, reserva="LIMITED", *, linhas=None, limite=15):
    base = copy.deepcopy(snapshot()["profiles"][0])
    base.update(
        id=f"{codigo}-id",
        code=codigo,
        name=f"Perfil {codigo}",
        immediateVacancies=total,
        reserveType=reserva,
        reserveLimit=limite if reserva == "LIMITED" else None,
    )
    if linhas is not None:
        base["vacancyTable"] = [
            {"id": f"{codigo}-l{i}", "modalityId": None, "immediateVacancies": valor}
            for i, valor in enumerate(linhas)
        ]
    return base


def _linhas(pdf_):
    return [linha.strip() for linha in texto_de(pdf_).splitlines() if linha.strip()]


def _tabela_de_perfis(pdf_):
    """`({código: célula de vagas}, total ou None, linha depois da tabela)` da tabela de Perfis."""
    linhas = _linhas(pdf_)
    inicio = linhas.index("Tabela 1 — Perfis de vaga") + 1 + COLUNAS_DA_TABELA_DE_PERFIS
    celulas, indice = {}, inicio
    while " — Perfil " in linhas[indice]:
        celulas[linhas[indice].split(" — ")[0]] = linhas[indice + 2]
        indice += COLUNAS_DA_TABELA_DE_PERFIS
    total = None
    if linhas[indice] == "Total":
        total, indice = linhas[indice + 1], indice + 2
    return celulas, total, linhas[indice]


def _documento(*perfis):
    return documento(snapshot(profiles=list(perfis)))


@pytest.mark.parametrize("reserva", ["LIMITED", "UNLIMITED"])
def test_na_tabela_de_perfis_o_cadastro_sem_vaga_sai_cr(reserva):
    """FR-2403: os dois tipos de cadastro, e a nota logo depois da tabela (FR-2406)."""
    celulas, _, depois = _tabela_de_perfis(
        _documento(_perfil_do_snapshot("TP-01", 0, reserva), _perfil_do_snapshot("TD-ADM", 6))
    )

    assert celulas == {"TP-01": "CR", "TD-ADM": "6"}
    assert depois == NOTA


def test_o_total_soma_so_as_vagas_e_sai():
    """FR-2407: o `CR` vale zero na soma, e a linha sai porque a soma é positiva."""
    _, total, depois = _tabela_de_perfis(
        _documento(
            _perfil_do_snapshot("TP-01", 0),
            _perfil_do_snapshot("TD-ADM", 6),
            _perfil_do_snapshot("TD-INFO", 4),
        )
    )

    assert total == "10"
    assert depois == NOTA, "a nota vem depois da linha de total, que é da grade"


def test_todos_cr_sem_linha_de_total():
    celulas, total, depois = _tabela_de_perfis(
        _documento(_perfil_do_snapshot("TP-01", 0), _perfil_do_snapshot("TP-02", 0, "UNLIMITED"))
    )

    assert celulas == {"TP-01": "CR", "TP-02": "CR"}
    assert total is None, "sem vaga imediata, não há linha de total (054, FR-997)"
    assert depois == NOTA


def test_sem_nenhum_cr_a_tabela_sai_sem_nota():
    """FR-2409: o Edital sem Perfil CR não ganha nada."""
    gerado = _documento(_perfil_do_snapshot("TD-ADM", 6), _perfil_do_snapshot("TP-01", 0, "NONE"))
    celulas, _, depois = _tabela_de_perfis(gerado)

    assert celulas == {"TD-ADM": "6", "TP-01": "0"}
    assert depois != NOTA
    assert NOTA not in _linhas(gerado)


def test_sem_cadastro_continua_zero_ao_lado_de_cr():
    """FR-2408: o zero sem cadastro não oferece nada, e `CR` afirmaria um cadastro que não há."""
    celulas, _, depois = _tabela_de_perfis(
        _documento(_perfil_do_snapshot("TP-01", 0), _perfil_do_snapshot("TP-02", 0, "NONE"))
    )

    assert celulas == {"TP-01": "CR", "TP-02": "0"}
    assert depois == NOTA


def test_o_incoerente_continua_zero():
    """Caso-limite: total zero com uma linha positiva — o erro precisa ser visto na prévia."""
    celulas, _, _ = _tabela_de_perfis(
        _documento(_perfil_do_snapshot("X", 0, linhas=[2]), _perfil_do_snapshot("TD-ADM", 6))
    )

    assert celulas["X"] == "0"


def test_o_cadastro_limitado_a_zero_sai_cr():
    """Caso-limite: o tipo declarado é de cadastro, e a incoerência do limite 0 fica registrada."""
    celulas, _, _ = _tabela_de_perfis(
        _documento(_perfil_do_snapshot("TP-01", 0, limite=0), _perfil_do_snapshot("TD-ADM", 6))
    )

    assert celulas["TP-01"] == "CR"


def test_a_nota_nao_e_tabela_nem_desloca_a_numeracao():
    """FR-2410, D-008: as legendas seguem sem lacuna, e a contagem da `065` é a do documento."""
    conteudo = snapshot(
        profiles=[_perfil_do_snapshot("TP-01", 0), _perfil_do_snapshot("TD-ADM", 6)]
    )
    legendas = [
        int(casada.group(1))
        for linha in _linhas(documento(conteudo))
        if (casada := LEGENDA.match(linha))
    ]

    assert legendas == list(range(1, len(legendas) + 1))
    assert pdf.tabelas_do_documento(conteudo) == len(legendas)


@pytest.mark.parametrize("redacao", [pdf.REDACAO_1, pdf.REDACAO_2])
def test_a_celula_e_a_mesma_nas_duas_redacoes(redacao):
    """FR-2402: a regra não depende do vocabulário; muda o rótulo da coluna, e não a célula."""
    composicao = pdf.Composicao(redacao=redacao)
    pdf._quadro_de_perfis(
        composicao,
        [_perfil_do_snapshot("TP-01", 0), _perfil_do_snapshot("TD-ADM", 6)],
        pdf._Numerador(),
    )
    textos = [item[1] for item in composicao.itens if item[0] == "texto" and item[1]]

    assert "CR" in textos
    assert textos[-1] == NOTA


# ---------------------------------------------------------------------------
# US2 — a ficha do Edital de um Perfil só (T014)
# ---------------------------------------------------------------------------


def _ficha(perfil):
    """`(valor de "Vagas imediatas:", a linha depois do par do cadastro)` da ficha do Perfil."""
    linhas = _linhas(_documento(perfil))
    vagas = linhas.index("Vagas imediatas:")
    cadastro = next(i for i in range(vagas, len(linhas)) if linhas[i].startswith("Cadastro"))
    return linhas[vagas + 1], linhas[cadastro + 2]


def test_no_perfil_unico_o_par_diz_cr_e_a_nota_sai_depois_dos_pares():
    """FR-2404, FR-2406."""
    vagas, depois = _ficha(_perfil_do_snapshot("DE-01", 0, "UNLIMITED"))

    assert vagas == "CR"
    assert depois == NOTA


@pytest.mark.parametrize(
    ("total", "reserva", "esperado"),
    [
        pytest.param(3, "LIMITED", "3", id="com vaga"),
        pytest.param(0, "NONE", "0", id="sem cadastro"),
    ],
)
def test_no_perfil_unico_sem_cr_o_par_e_o_numero_e_nao_ha_nota(total, reserva, esperado):
    gerado = _documento(_perfil_do_snapshot("DE-01", total, reserva))
    vagas, _ = _ficha(_perfil_do_snapshot("DE-01", total, reserva))

    assert vagas == esperado
    assert NOTA not in _linhas(gerado)


# ---------------------------------------------------------------------------
# US3 — a apresentação por perguntas (T017, T018)
# ---------------------------------------------------------------------------


def _trechos_por_tabela(linhas):
    """`{legenda: linhas até a próxima legenda}`: cada tabela e o que vem logo depois dela."""
    trechos, atual = {}, None
    for linha in linhas:
        if casada := LEGENDA.match(linha):
            atual = casada.group(2)
            trechos[atual] = []
        elif atual is not None:
            trechos[atual].append(linha)
    return trechos


def test_em_b_por_perguntas_os_tutores_presenciais_saem_cr_com_a_nota():
    """FR-2405, FR-2406: dezesseis `CR` na tabela do grupo, e a nota só depois dela."""
    trechos = _trechos_por_tabela(_linhas(por_perguntas("B")))
    grupo = trechos["Tutor presencial — Perfis TP-01 a TP-16"]
    avulsos = trechos["Perfis"]

    assert grupo.count("CR") == 16
    assert "0" not in grupo
    assert grupo.count(NOTA) == 1
    assert grupo.index(NOTA) > max(i for i, linha in enumerate(grupo) if linha == "CR")
    assert NOTA not in avulsos, "TD-ADM e TD-INFO-EDU têm vaga, e a tabela deles não usa a sigla"
    assert "6" in avulsos and "4" in avulsos


def test_em_b_por_perguntas_a_tabela_por_lista_e_o_resumo_nao_mudam():
    """Os dois Perfis com vaga na tabela por lista, como desde a `067`; o resumo, como hoje."""
    linhas = _linhas(por_perguntas("B"))
    trechos = _trechos_por_tabela(linhas)
    por_lista = trechos["Vagas imediatas por lista de concorrência"]

    assert "TD-ADM" in por_lista and "TD-INFO-EDU" in por_lista
    assert not [linha for linha in por_lista if linha.startswith("TP-")]
    assert "São 10 vagas imediatas, nos Perfis TD-ADM e TD-INFO-EDU." in linhas
    assert NOTA not in por_lista


def test_por_perguntas_um_perfil_so_cr():
    """T018: "Não há vagas imediatas.", a tabela "Perfis" com `CR`, e a nota."""
    conteudo = levado_ao_catalogo_novo(snapshot(profiles=[_perfil_do_snapshot("DE-01", 0)]))
    linhas = _linhas(documento(conteudo))
    perfis = _trechos_por_tabela(linhas)["Perfis"]

    assert pdf.por_perguntas(conteudo)
    assert "Não há vagas imediatas." in linhas
    assert "CR" in perfis
    assert NOTA in perfis
