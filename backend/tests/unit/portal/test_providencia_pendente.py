"""A providência pendente do candidato e o que depende dela (154).

Requisitos: FR-6200 a FR-6203, FR-6205 e FR-6209.

O achado 20 do estudo da jornada final: com tudo enviado, a convocação continuava dizendo *"Você foi
convocado!"* e advertindo do não atendimento a quem já tinha cumprido. A projeção da `118` passa a
dizer se há providência pendente — ter tarefa da FR-3726 —, e o título e a advertência a seguem.

**Arquivo próprio, e não `test_obrigacoes_da_convocacao.py`**: a `150` (#496), aberta em paralelo,
acrescenta casos ao fim daquele arquivo, e dois incrementos escrevendo no mesmo fim conflitariam a
cada merge. Os construtores (`lido`, `disp`, `projetar`) são os de lá, importados, para que as duas
suítes montem os itens do mesmo jeito.
"""

import pytest

from processo_seletivo.convocacao.domain import nomes
from processo_seletivo.portal import obrigacoes as o
from processo_seletivo.requerimentos.domain import nomes as req_nomes
from tests.unit.portal.test_obrigacoes_da_convocacao import disp, lido, projetar

ACOMPANHE = "Acompanhe sua convocação"
CONVOCADO = "Você foi convocado!"


def _cenarios():
    """Os cenários da tabela de decisão de `data-model.md`, com a chamada aberta.

    Cada um: `(itens, requerimento)`. Os itens são montados de novo a cada chamada, porque o `id`
    de cada um vem de um contador e a projeção os indexa.
    """
    return {
        # Com providência pendente.
        "C1": (lambda: [lido(nomes.ITEM_A_APRESENTAR), lido(nomes.ITEM_A_APRESENTAR)], None),
        "a_corrigir": (lambda: [lido(nomes.ITEM_PENDENTE), lido(nomes.ITEM_RECEBIDO)], None),
        "F": (lambda: [lido(nomes.ITEM_RECEBIDO), lido(nomes.ITEM_RECEBIDO)], disp()),
        "pendencia_nova_depois_de_T": (
            lambda: [lido(nomes.ITEM_RECEBIDO), lido(nomes.ITEM_PENDENTE)],
            disp(status=req_nomes.ENVIADO),
        ),
        # Sem providência pendente.
        "T": (
            lambda: [lido(nomes.ITEM_RECEBIDO), lido(nomes.ITEM_RECEBIDO)],
            disp(status=req_nomes.ENVIADO),
        ),
        "T_com_opcional_nao_enviado": (
            lambda: [lido(nomes.ITEM_RECEBIDO), lido(nomes.ITEM_A_APRESENTAR, obrigatorio=False)],
            None,
        ),
        "T_com_reenviado": (
            lambda: [lido(nomes.ITEM_RECEBIDO), lido(nomes.ITEM_COMPLEMENTADO)],
            None,
        ),
        "T_com_aproveitado": (
            lambda: [lido(nomes.ITEM_RECEBIDO, origem="inscricao"), lido(nomes.ITEM_RECEBIDO)],
            None,
        ),
        "meio_conferido": (
            lambda: [lido(nomes.ITEM_CONFORME), lido(nomes.ITEM_RECEBIDO)],
            None,
        ),
        "Tc": (
            lambda: [lido(nomes.ITEM_CONFORME), lido(nomes.ITEM_NAO_SE_APLICA)],
            disp(status=req_nomes.ENVIADO),
        ),
        "Tc_com_opcional_recebido": (
            lambda: [lido(nomes.ITEM_CONFORME), lido(nomes.ITEM_RECEBIDO, obrigatorio=False)],
            None,
        ),
        "so_facultativo": (
            lambda: [lido(nomes.ITEM_A_APRESENTAR, obrigatorio=False)],
            None,
        ),
        "facultativo_pendente": (
            lambda: [lido(nomes.ITEM_RECEBIDO), lido(nomes.ITEM_PENDENTE, obrigatorio=False)],
            None,
        ),
    }


COM_PROVIDENCIA = {"C1", "a_corrigir", "F", "pendencia_nova_depois_de_T"}
SEM_PROVIDENCIA = set(_cenarios()) - COM_PROVIDENCIA
CONFERENCIA_TERMINADA = {"Tc", "Tc_com_opcional_recebido"}


def _projetar(nome, **opcoes):
    itens, requerimento = _cenarios()[nome]
    return projetar(itens(), requerimento=requerimento, **opcoes)


# --- FR-6200: a providência pendente ------------------------------------------------------------


@pytest.mark.parametrize("nome", sorted(_cenarios()))
def test_a_providencia_pendente_e_ter_tarefa_obrigatoria(nome):
    """FR-6200, D-001: obrigatório a corrigir ou a enviar, ou o Requerimento a preencher.

    O opcional, o facultativo pendente, o que está com a comissão e o conferido não contam."""
    projecao = _projetar(nome)

    assert projecao.providencia_pendente is (nome in COM_PROVIDENCIA)
    # **A página nunca diz "Acompanhe" e, logo abaixo, uma tarefa** (D-001): a providência é a
    # existência das mesmas tarefas que montam o resumo e a ação.
    assert projecao.providencia_pendente is bool(projecao.tarefas)


@pytest.mark.parametrize("momento", [o.ENCERRADA_PELO_PRAZO, o.ENCERRADA_PELO_PROCESSO, o.DECIDIDA])
def test_fechada_a_chamada_nao_ha_providencia(momento):
    """Fora da chamada aberta não há tarefa, e a providência não se pergunta."""
    projecao = projetar([lido(nomes.ITEM_A_APRESENTAR)], momento)

    assert projecao.providencia_pendente is False


# --- FR-6205: a conferência terminada (derivação; a frase é da US2) -----------------------------


@pytest.mark.parametrize("nome", sorted(_cenarios()))
def test_a_conferencia_terminada_so_com_todo_obrigatorio_conferido(nome):
    """FR-6205, D-002: ao menos um obrigatório, todos conformes ou *não se aplica*, sem tarefa. O
    opcional não entra na conta; a chamada só com facultativo não tem obrigatório a conferir."""
    assert _projetar(nome).conferencia_terminada is (nome in CONFERENCIA_TERMINADA)


def test_a_conferencia_terminada_nao_vale_com_o_requerimento_a_preencher():
    projecao = projetar([lido(nomes.ITEM_CONFORME)], requerimento=disp())

    assert projecao.providencia_pendente is True
    assert projecao.conferencia_terminada is False


def test_a_conferencia_terminada_nao_vale_com_a_chamada_fechada():
    projecao = projetar([lido(nomes.ITEM_CONFORME)], o.ENCERRADA_PELO_PRAZO)

    assert projecao.conferencia_terminada is False


# --- FR-6202 e FR-6203: o título ----------------------------------------------------------------


@pytest.mark.parametrize("nome", sorted(_cenarios()))
def test_o_titulo_segue_a_providencia(nome):
    """FR-6202: a linha da chamada aberta da FR-3858 da `121` dividida em duas."""
    esperado = CONVOCADO if nome in COM_PROVIDENCIA else ACOMPANHE

    assert _projetar(nome).titulo == esperado


def test_o_titulo_novo_nao_promete_nada():
    """FR-6202, FR-3751 da `118`: nem matrícula, nem contratação, nem bolsa, nem vaga, nem
    aprovação."""
    titulo = o.TITULO_SEM_PROVIDENCIA.lower()

    assert titulo == ACOMPANHE.lower()
    for termo in ("matr", "contrat", "bolsa", "vaga", "aprov", "garant", "conclu"):
        assert termo not in titulo


@pytest.mark.parametrize(
    ("estado", "vencimento"),
    [
        (nomes.CONVOCADO_PRAZO_NAO_INICIADO, None),
        (nomes.CONVOCADO_PRAZO_EM_CURSO, None),
    ],
    ids=["prazo_nao_iniciado", "sem_vencimento"],
)
def test_o_titulo_segue_a_providencia_sem_prazo_correndo(estado, vencimento):
    """Casos-limite *prazo não iniciado* e *sem vencimento*, com tudo enviado e sem nada enviado."""
    tudo = projetar(
        [lido(nomes.ITEM_RECEBIDO)], estado=estado, vencimento=vencimento, requerimento=None
    )
    nada = projetar([lido(nomes.ITEM_A_APRESENTAR)], estado=estado, vencimento=vencimento)

    assert tudo.titulo == ACOMPANHE
    assert nada.titulo == CONVOCADO


def test_o_titulo_volta_com_a_pendencia_nova():
    """FR-6203, nos dois sentidos: o título é lido a cada projeção, e nada o guarda."""
    antes = projetar([lido(nomes.ITEM_RECEBIDO)])
    depois = projetar([lido(nomes.ITEM_PENDENTE)])

    assert (antes.titulo, depois.titulo) == (ACOMPANHE, CONVOCADO)


@pytest.mark.parametrize(
    ("momento", "titulo"),
    [
        (o.ENCERRADA_PELO_PRAZO, o.TITULO_ENCERRADA_PELO_PRAZO),
        (o.ENCERRADA_PELO_PROCESSO, o.TITULO_ENCERRADA_PELO_PROCESSO),
        (o.DECIDIDA, o.TITULO_DECIDIDA),
    ],
)
def test_os_demais_titulos_nao_mudam(momento, titulo):
    """FR-6202: "as demais linhas não mudam", com e sem providência."""
    for itens in ([lido(nomes.ITEM_RECEBIDO)], [lido(nomes.ITEM_A_APRESENTAR)]):
        assert projetar(itens, momento).titulo == titulo


# --- FR-6208 e FR-6209: a advertência separada do prazo -----------------------------------------


@pytest.mark.parametrize("nome", sorted(_cenarios()))
def test_a_consequencia_so_com_providencia_e_o_prazo_continua(nome):
    """FR-6209: a advertência só com providência; FR-6208: o cartão do prazo com e sem ela."""
    projecao = _projetar(nome)

    assert projecao.cabe_a_consequencia is (nome in COM_PROVIDENCIA)
    assert projecao.cartao is not None and projecao.cartao.data


@pytest.mark.parametrize(
    ("estado", "vencimento"),
    [
        (nomes.CONVOCADO_PRAZO_NAO_INICIADO, None),
        (nomes.CONVOCADO_PRAZO_EM_CURSO, None),
    ],
    ids=["prazo_nao_iniciado", "sem_vencimento"],
)
def test_sem_prazo_correndo_nao_ha_consequencia_nem_com_providencia(estado, vencimento):
    """As outras condições da FR-1177 da `063` continuam: comunicação enviada e vencimento."""
    projecao = projetar([lido(nomes.ITEM_A_APRESENTAR)], estado=estado, vencimento=vencimento)

    assert projecao.providencia_pendente is True
    assert projecao.cabe_a_consequencia is False


def test_a_ressalva_continua_com_e_sem_providencia():
    """FR-6210: a ressalva não é frase de consequência."""
    for itens in ([lido(nomes.ITEM_RECEBIDO)], [lido(nomes.ITEM_A_APRESENTAR)]):
        assert projetar(itens).ressalva == o.RESSALVA_DO_RESULTADO


# --- FR-6201: a chamada que não pede documento (D-006) ------------------------------------------


@pytest.mark.parametrize(
    ("disponibilidade", "pendente"),
    [
        (disp(), True),
        (disp(status=req_nomes.RASCUNHO), True),
        (disp(status=req_nomes.ENVIADO), False),
        # Pedido **na inscrição** e enviado: a chamada não pede nada pelo portal (R-005).
        (disp(req_nomes.NA_INSCRICAO, status=req_nomes.ENVIADO), True),
        (disp(None), True),
        (None, True),
    ],
    ids=[
        "so_requerimento_a_preencher",
        "so_requerimento_em_rascunho",
        "so_requerimento_enviado",
        "requerimento_da_inscricao_enviado",
        "nada_pedido",
        "sem_politica",
    ],
)
def test_sem_documento_so_o_requerimento_da_chamada_enviado_desfaz_a_providencia(
    disponibilidade, pendente
):
    assert o.providencia_pendente_sem_documento(disponibilidade) is pendente
