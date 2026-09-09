"""A constraint que muda, e as duas metades dela (021, D-006, R-001, FR-036).

**A garantia de hoje continua palavra por palavra.** `uq_ato_raiz_por_marco` seguia sendo única por
`(edital, perfil, marco)` entre atos raiz, e três listas de concorrência sobre o mesmo marco
colidiam. A correção parte a constraint em duas parciais em vez de afrouxar a existente: onde não
há lista, o certame de hoje continua sob exatamente a regra que já o governava; onde há, a dimensão
nova é a que separa.

**Por que lista e não marco.** Um marco por lista triplicaria a janela recursal, que é do marco e
que os Editais publicam **uma vez** para as três listas. A lista é dimensão do ato.
"""

import uuid

import pytest
from django.db import IntegrityError, transaction
from django.utils import timezone

from processo_seletivo.classificacao.models import AtoDeOrdenacao, OrigemDaOrdem
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.comissao import rascunho_com_etapas
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.publicacao import publish_original
from tests.fixtures.sorteio import LISTA_PCD, LISTA_PPI, MARCO, marco_com_metodo

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


@pytest.fixture
def cenario(api_client, manager_headers, process_payload):
    """Um Edital cujo marco existe na versão publicada — a trigger de proveniência o exige."""
    rascunho = rascunho_com_etapas()
    marco_com_metodo(rascunho, perfil_id=PROFILE_ID, etapa_id=rascunho["stages"][1]["id"])
    edital = publish_original(api_client, manager_headers, process_payload, draft=rascunho)
    return edital, VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")


def _ato(
    edital, versao, *, lista_id=None, origem=OrigemDaOrdem.COMPUTADO, anterior=None, motivo=""
):
    return AtoDeOrdenacao.objects.create(
        edital=edital,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        lista_id=lista_id,
        origem=origem,
        versao=versao,
        ato_anterior=anterior,
        motivo_da_sucessao=motivo,
        # As quatro identidades e `stageResults` são exigência da trigger de proveniência, e não
        # adorno do teste: sem elas a gravação é recusada antes de qualquer constraint.
        universo={
            "editalId": str(edital.id),
            "profileId": PROFILE_ID,
            "milestoneId": MARCO,
            "versionId": str(versao.id),
            "stageResults": [],
        },
        emitido_por="cpf:presidente",
        emitido_em=timezone.now(),
    )


def test_dois_atos_raiz_de_ampla_concorrencia_continuam_sendo_recusados(cenario):
    """A metade que **não** pode ter mudado: é a garantia de todo certame já publicado."""
    edital, versao = cenario
    _ato(edital, versao)

    with pytest.raises(IntegrityError, match="uq_ato_raiz_por_marco"):
        with transaction.atomic():
            _ato(edital, versao)


def test_tres_atos_de_listas_distintas_sao_aceitos(cenario):
    edital, versao = cenario

    criados = [_ato(edital, versao, lista_id=lista) for lista in (None, LISTA_PPI, LISTA_PCD)]

    assert len({ato.id for ato in criados}) == 3
    assert AtoDeOrdenacao.objects.filter(edital=edital, marco_id=MARCO).count() == 3


def test_dois_atos_raiz_da_mesma_lista_sao_recusados(cenario):
    edital, versao = cenario
    _ato(edital, versao, lista_id=LISTA_PPI)

    with pytest.raises(IntegrityError, match="uq_ato_raiz_por_marco_e_lista"):
        with transaction.atomic():
            _ato(edital, versao, lista_id=LISTA_PPI)


def test_a_sucessao_continua_valendo_dentro_de_cada_lista(cenario):
    edital, versao = cenario
    raiz = _ato(edital, versao, lista_id=LISTA_PPI)

    sucessor = _ato(edital, versao, lista_id=LISTA_PPI, anterior=raiz, motivo="Sorteio anulado.")

    assert sucessor.ato_anterior_id == raiz.id
    assert not AtoDeOrdenacao.objects.filter(ato_anterior=sucessor).exists()


def test_origem_nasce_computado_e_todo_ato_existente_e_computado(cenario):
    """`NULL` e `"COMPUTADO"` descreveriam o mesmo ato com bytes diferentes (FR-034)."""
    edital, versao = cenario

    ato = _ato(edital, versao)

    assert ato.origem == OrigemDaOrdem.COMPUTADO
    assert AtoDeOrdenacao.objects.filter(origem=OrigemDaOrdem.COMPUTADO).count() >= 1
    assert not AtoDeOrdenacao.objects.filter(origem__isnull=True).exists()


def test_a_lista_e_identidade_publicada_e_nao_chave_estrangeira(cenario):
    """Como `perfil_id` e `marco_id`: a Retificação remove a Modalidade sem apagar o ato."""
    edital, versao = cenario

    ato = _ato(edital, versao, lista_id=str(uuid.uuid4()))
    ato.refresh_from_db()

    assert ato.lista_id is not None
