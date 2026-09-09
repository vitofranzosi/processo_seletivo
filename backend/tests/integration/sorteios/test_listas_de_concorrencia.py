"""Três relações, três sorteios, três ordens — e o cotista em duas (021, D-006, FR-004, FR-036).

É o que o 57 e o 28 exigem, palavra por palavra: *"todos os candidatos (inclusive os cotistas)
participem do sorteio da ampla concorrência e em sequência haverá o sorteio das reservas de vaga"*.
São sorteios **distintos**, e não um sorteio filtrado depois — e é por isso que a lista é dimensão
do ato, com numeração e ordem próprias em cada relação.
"""

import pytest

from processo_seletivo.classificacao.models import AtoDeOrdenacao, PosicaoNaOrdem
from processo_seletivo.sorteios.application.ocorrencia import observar_ocorrencia
from processo_seletivo.sorteios.application.relacao import publicar_relacao
from processo_seletivo.sorteios.application.sorteio import constituir_sorteio
from processo_seletivo.sorteios.infrastructure.fontes.loteria_federal import FonteDeTeste
from processo_seletivo.sorteios.models import ParticipanteHabilitado, RelacaoDeHabilitados, Sorteio
from tests.fixtures.sorteio import (
    LISTA_PCD,
    LISTA_PPI,
    METODO,
    certame_com_cotas,
    presidente,
)

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


@pytest.fixture
def certame(gestor, api_client, manager_headers, process_payload):
    return certame_com_cotas(gestor, api_client, manager_headers, process_payload)


def _sortear_todas(certame):
    """**As três relações congelam primeiro, e só então a semente existe.**

    A ordem não é conveniência do teste: é a inversão que organiza a feature. Observar a ocorrência
    entre o congelamento de uma lista e o da outra deixaria a segunda ser fechada já sabendo a
    semente — e o comando recusa, com `occurrence_precedes_freeze`, exatamente isso.
    """
    relacoes = {}
    for indice, lista in enumerate((None, LISTA_PPI, LISTA_PCD)):
        relacoes[lista] = publicar_relacao(
            actor=presidente(),
            processo_id=certame["processo"].id,
            edital_id=certame["edital"].id,
            perfil_id=certame["perfil"],
            marco_id=certame["marco"],
            lista_id=lista,
            idempotency_key=f"cotas-relacao-{indice}",
            correlation_id="teste-021",
        )["relacao"]

    ocorrencia_id = observar_ocorrencia(
        actor=presidente(),
        processo_id=certame["processo"].id,
        fonte=METODO["source"],
        referencia=METODO["occurrence"],
        idempotency_key="cotas-ocorrencia",
        correlation_id="teste-021",
        fonte_externa=FonteDeTeste(),
    )["ocorrencia"]

    return {
        lista: constituir_sorteio(
            actor=presidente(),
            processo_id=certame["processo"].id,
            edital_id=certame["edital"].id,
            relacao_id=relacao_id,
            ocorrencia_id=ocorrencia_id,
            idempotency_key=f"cotas-sorteio-{indice}",
            correlation_id="teste-021",
        )
        for indice, (lista, relacao_id) in enumerate(relacoes.items())
    }


def test_tres_atos_raiz_distintos_no_mesmo_marco(certame):
    _sortear_todas(certame)

    atos = AtoDeOrdenacao.objects.filter(
        edital=certame["edital"], marco_id=certame["marco"], ato_anterior__isnull=True
    )
    assert atos.count() == 3
    assert {str(a.lista_id) if a.lista_id else None for a in atos} == {None, LISTA_PPI, LISTA_PCD}


def test_a_ampla_concorrencia_alcanca_todos_e_a_reserva_so_quem_declarou(certame):
    _sortear_todas(certame)

    por_lista = {
        (str(r.lista_id) if r.lista_id else None): r
        for r in RelacaoDeHabilitados.objects.filter(edital=certame["edital"])
    }
    assert por_lista[None].quantidade == len(certame["inscricoes"])
    assert por_lista[LISTA_PPI].quantidade == 1
    assert por_lista[LISTA_PCD].quantidade == 1


def test_o_cotista_figura_em_duas_listas_com_numeracao_propria(certame):
    """FR-004: cada relação é numerada de 1 a N, e os números não se comunicam."""
    _sortear_todas(certame)
    cotista = certame["cotista_ppi"]

    participacoes = ParticipanteHabilitado.objects.filter(inscricao=cotista).select_related(
        "relacao"
    )

    assert participacoes.count() == 2, "ampla concorrência e a reserva declarada"
    numeros = {
        (str(p.relacao.lista_id) if p.relacao.lista_id else None): p.numero_publico
        for p in participacoes
    }
    assert numeros[LISTA_PPI] == 1, "primeiro da própria lista"
    assert numeros[None] >= 1


def test_o_cotista_tem_posicoes_independentes_nas_duas_ordens(certame):
    """A mesma pessoa, duas ordens, dois lugares — e nenhum deles decide o outro."""
    _sortear_todas(certame)
    cotista = certame["cotista_ppi"]

    posicoes = {
        (str(p.ato.lista_id) if p.ato.lista_id else None): p.posicao
        for p in PosicaoNaOrdem.objects.filter(inscricao=cotista).select_related("ato")
    }

    assert set(posicoes) == {None, LISTA_PPI}
    assert posicoes[LISTA_PPI] == 1, "sozinho na reserva, é o primeiro dela"


def test_a_mesma_ocorrencia_serve_as_tres_listas_sem_repetir_a_permutacao(certame):
    """O `relationHash` separa os três sorteios — é o vetor `mesma-semente-recortes-distintos`."""
    declarados = _sortear_todas(certame)

    sementes = {d["semente"] for d in declarados.values()}
    sorteios = Sorteio.objects.filter(edital=certame["edital"])
    assert len(sementes) == 1, "uma extração semeia as três listas"
    assert sorteios.count() == 3
    assert len({s.relacao.resumo for s in sorteios}) == 3, (
        "resumos distintos, permutações distintas"
    )
    assert len({s.ocorrencia_id for s in sorteios}) == 1
