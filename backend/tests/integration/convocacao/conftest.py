"""O cenário da convocação. As funções moram em `tests/fixtures/convocacao.py`."""

import pytest

from processo_seletivo.publicacoes.domain.vocabulario_da_regra import FORMA_POR_PUBLICACAO
from tests.fixtures.convocacao import montar_cenario_da_convocacao
from tests.fixtures.corte import regra


@pytest.fixture
def cenario(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    """Três habilitadas, faixa de dois, quadro de três — e apuração emitida.

    Sobra **uma** vaga a ocupar: os dois que a faixa alcançou ocupam duas das três publicadas. É o
    recorte em que a primeira convocação do certame acontece, e em que `faltando` é 1.
    """
    return montar_cenario_da_convocacao(
        gestor, api_client, manager_headers, process_payload, prefixo="convocacao-019"
    )


@pytest.fixture
def cenario_com_suplente(
    db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos
):
    """Quadro de **uma** vaga e faixa de dois: um titular e um suplente, sem vaga faltante.

    É o recorte que a `sem_deficit` existe para proteger — chamar o suplente aqui seria prometer
    uma vaga que a apuração não registra como faltante.
    """
    return montar_cenario_da_convocacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="convocacao-019-suplente",
        geral=1,
    )


@pytest.fixture
def cenario_do_77(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    """Duas vagas, faixa de três: dois titulares e **um suplente** — o recorte do 77/2026.

    É o cenário em que a desistência de um titular abre vaga de verdade e a suplente é chamada para
    ela. Sem o excedente na regra de corte, a faixa pararia no alvo e não haveria suplente nenhum —
    e o ciclo que a `SC-085` mede não existiria.
    """
    return montar_cenario_da_convocacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="convocacao-019-77",
        geral=2,
        cut=regra(surplusCount=1),
    )


@pytest.fixture
def cenario_sem_forma(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    """O Edital que **não declarou** como comunica — e a `019` recusa emitir nele.

    É o estado de todo Edital publicado antes do degrau 15, e a ausência não vira padrão: as duas
    formas da amostra são normais, e escolher uma decidiria norma no lugar do Edital.
    """
    return montar_cenario_da_convocacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="convocacao-019-sem-forma",
        forma=None,
    )


@pytest.fixture
def cenario_por_publicacao(
    db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos
):
    """O Edital que convoca **por publicação** — a forma do 69/2026 (7.2).

    Não há destinatário individual, e a emissão não passa por caixa de entrada nenhuma.
    """
    return montar_cenario_da_convocacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="convocacao-019-publicacao",
        forma=FORMA_POR_PUBLICACAO,
    )
