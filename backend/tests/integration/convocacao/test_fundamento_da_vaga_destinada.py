"""A chamada na ampla que conta com a vaga destinada cita a destinação no fundamento (155, T046).

FR-6340. O cenário é a V-1 de `tests/integration/ocupacao/test_destinacao.py`: a reserva PPI fica
sem quem a ocupe, a presidência destina a vaga à ampla, e a apuração seguinte da ampla lê o
movimento. Quem é chamado na ampla a partir dali tem o fundamento dizendo de onde a vaga veio.
"""

import pytest

from processo_seletivo.convocacao.application import selectors
from processo_seletivo.convocacao.domain import fundamento
from processo_seletivo.convocacao.models import Convocacao
from processo_seletivo.ocupacao.domain import nomes
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.sorteio import MARCO
from tests.integration.convocacao.test_suplencia import chamar
from tests.integration.ocupacao.test_concomitancia import apurar, habilitar
from tests.integration.ocupacao.test_destinacao import destinar, esgotado

pytestmark = pytest.mark.django_db(transaction=True)

FUNDAMENTO_DIGITADO = "No interesse da Administração, item 8.2 do Edital 77/2026."


@pytest.fixture
def destinada(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    certame = esgotado(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        "fund-155",
        reversao=nomes.REVERSAO_POR_ESGOTAMENTO,
    )
    destinar(certame, gestor, chave="fund-155-destinar")
    # **Habilitados na ampla depois da destinação**: sem isso a faixa da ampla não tem ninguém a
    # chamar, e a condição da reserva não depende deles.
    habilitar(certame, [i for i in certame["inscricoes"] if i.id != certame["cotista_ppi"].id])
    apurar(certame, gestor, chave="fund-155-ampla-3", motivo="Vaga destinada à ampla")
    return certame


def primeira_da_fila(certame):
    return selectors.contexto_do_recorte(
        edital=certame["edital"], perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )["fila"][0]


def test_a_chamada_na_ampla_cita_a_destinacao(destinada, gestor):
    declarado = chamar(
        destinada, gestor, primeira_da_fila(destinada), lista_id=None, chave="fund-155-chamar"
    )

    texto = Convocacao.objects.get(id=declarado["id"]).fundamento
    assert texto.startswith(FUNDAMENTO_DIGITADO), "o fundamento de quem chama continua primeiro"
    assert "incluem a destinação de 1 vaga da lista «" in texto
    assert "(PPI)» destinada à ampla concorrência em" in texto


def test_a_citacao_nao_se_repete_quando_o_fundamento_ja_a_traz():
    citacao = fundamento.da_destinacao([(1, "Pretos, pardos e indígenas (PPI)", "11/11/2026")])
    texto = fundamento.com_destinacao("Fundamento.", citacao)

    assert texto == f"Fundamento. {citacao}"
    assert fundamento.com_destinacao(texto, citacao) == texto
    assert fundamento.com_destinacao("Fundamento.", "") == "Fundamento."
    assert fundamento.da_destinacao([]) == ""
