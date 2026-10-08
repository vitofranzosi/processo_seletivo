"""A convocação que o portal mostra, lida por conjunto: uma regra só, três telas (059, `D-001`).

**A lista, o acompanhamento e a tela da convocação mostram a mesma convocação** (`FR-1100`). Antes
desta feature só a tela da convocação a lia, com uma consulta escrita dentro da view; agora as três
leem do mesmo seletor, e é aqui que a regra fica presa.

**Vigente mais recente, e não "em aberto".** `chamada_em_aberto` responde outra pergunta — a do
requerimento — e some com a convocação concluída. O portal precisa mostrá-la também: quem atendeu
continua vendo que foi chamado e o que se registrou.

**E o custo não cresce com as inscrições pedidas.** A lista é o lugar onde uma consulta por item é
invisível com três inscrições e fatal com trezentas.
"""

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from processo_seletivo.convocacao.application import selectors
from tests.fixtures.convocacao import convocar
from tests.fixtures.corte import MARCO
from tests.fixtures.edital import PROFILE_ID

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


def primeira_da_fila(edital):
    """Quem a fila chama primeiro — a fila guarda identificadores, e não linhas."""
    return selectors.contexto_do_recorte(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )["fila"][0]


def consultas(ids):
    with CaptureQueriesContext(connection) as capturadas:
        resultado = selectors.vigentes_por_inscricao(ids)
        # Tocar o que as telas tocam: o desfecho e o envio. Prefetch que faltasse viraria consulta
        # aqui, e não no seletor — que é onde uma medição só do seletor deixaria de ver.
        for chamada in resultado.values():
            selectors.desfecho_de(chamada)
            selectors.envio_de(chamada)
    return len(capturadas), resultado


def test_devolve_a_vigente_da_inscricao_e_nada_para_quem_nao_foi_chamado(cenario, gestor):
    edital, _, inscricoes = cenario
    pessoa = primeira_da_fila(edital)
    declarado = convocar(edital, gestor, pessoa, idempotency_key="vpi-1")
    outra = next(i for i in inscricoes if i.id != pessoa)

    vigentes = selectors.vigentes_por_inscricao([pessoa, outra.id])

    assert set(vigentes) == {pessoa}
    assert str(vigentes[pessoa].id) == declarado["id"]


def test_a_sucessora_ocupa_o_lugar_da_sucedida(cenario, gestor):
    """Correção é sucessão: mostrar a anterior diria à pessoa um prazo que já não vale."""
    edital, _, _ = cenario
    pessoa = primeira_da_fila(edital)
    convocar(edital, gestor, pessoa, idempotency_key="vpi-raiz")
    sucessora = convocar(
        edital,
        gestor,
        pessoa,
        motivo="Vencimento informado com o ano errado.",
        idempotency_key="vpi-sucessora",
    )

    vigentes = selectors.vigentes_por_inscricao([pessoa])

    assert str(vigentes[pessoa].id) == sucessora["id"]


def test_sem_inscricao_pedida_nao_consulta_nada(db):
    """A lista de quem só tem rascunho não paga leitura de convocação nenhuma."""
    total, resultado = consultas([])

    assert (total, resultado) == (0, {})


def test_o_custo_nao_cresce_com_as_inscricoes_pedidas(cenario, gestor):
    edital, _, inscricoes = cenario
    pessoa = primeira_da_fila(edital)
    convocar(edital, gestor, pessoa, idempotency_key="vpi-custo")
    convocar(
        edital, gestor, pessoa, motivo="Correção do fundamento.", idempotency_key="vpi-custo-2"
    )

    com_uma, _ = consultas([pessoa])
    com_todas, resultado = consultas([i.id for i in inscricoes])

    assert com_todas == com_uma, f"{com_uma} -> {com_todas}"
    assert set(resultado) == {pessoa}


@pytest.fixture
def dois_titulares(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    """Duas vagas e faixa de três: dois titulares, que se convocam sem disputar vaga."""
    from tests.fixtures.convocacao import montar_cenario_da_convocacao
    from tests.fixtures.corte import regra

    return montar_cenario_da_convocacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="convocacao-059-dois",
        geral=2,
        cut=regra(surplusCount=1),
    )


def test_o_custo_nao_cresce_com_as_convocacoes(dois_titulares, gestor):
    """`SC-426`: com uma convocada e com duas, o mesmo número de consultas."""
    edital, _, inscricoes = dois_titulares
    fila = selectors.contexto_do_recorte(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )["fila"]
    todas = [i.id for i in inscricoes]

    convocar(edital, gestor, fila[0], idempotency_key="vpi-dois-1")
    com_uma, _ = consultas(todas)
    convocar(edital, gestor, fila[1], idempotency_key="vpi-dois-2")
    com_duas, resultado = consultas(todas)

    assert len(resultado) == 2
    assert com_duas == com_uma, f"{com_uma} -> {com_duas}"
