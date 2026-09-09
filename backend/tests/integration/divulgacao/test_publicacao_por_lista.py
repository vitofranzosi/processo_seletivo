"""A divulgação ganha a dimensão da lista, e a metade sem lista não muda (021, D-015, FR-068).

**O bloqueio que este arquivo remove.** A `021` fez o ato admitir três raízes por marco — ampla
concorrência, PPI e PcD —, e parou aí. `PublicacaoResultado` continuava única por
`(Edital, Perfil, marco)`: o certame com cotas sorteava as três listas e não conseguia divulgar a
segunda. A tarefa de publicar cada lista existia sobre um agregado que a recusava — cobertura de
requisito sobre impossibilidade de modelo.

**E a trigger de coerência passou a conhecer a lista.** Ela existe para dizer que o ato citado é a
autoridade sobre os eixos; sem o quarto eixo, uma publicação da PPI podia citar o ato da PcD e o
banco aceitava.
"""

import uuid

import pytest
from django.db import IntegrityError, ProgrammingError, transaction
from django.utils import timezone

from processo_seletivo.classificacao.models import AtoDeOrdenacao, OrigemDaOrdem
from processo_seletivo.divulgacao.models import Natureza, PublicacaoResultado
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.comissao import rascunho_com_etapas
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.publicacao import publish_original
from tests.fixtures.sorteio import LISTA_PCD, LISTA_PPI, MARCO, marco_com_metodo

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


@pytest.fixture
def cenario(api_client, manager_headers, process_payload):
    rascunho = rascunho_com_etapas()
    marco_com_metodo(rascunho, perfil_id=PROFILE_ID, etapa_id=rascunho["stages"][1]["id"])
    edital = publish_original(api_client, manager_headers, process_payload, draft=rascunho)
    return edital, VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")


def _ato(edital, versao, *, lista_id=None, anterior=None):
    return AtoDeOrdenacao.objects.create(
        edital=edital,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        lista_id=lista_id,
        ato_anterior=anterior,
        motivo_da_sucessao="Sorteio anulado." if anterior is not None else "",
        origem=OrigemDaOrdem.SORTEIO,
        versao=versao,
        universo={
            "editalId": str(edital.id),
            "profileId": PROFILE_ID,
            "milestoneId": MARCO,
            "versionId": str(versao.id),
            "stageResults": [],
            "origem": "SORTEIO",
        },
        emitido_por="cpf:presidente",
        emitido_em=timezone.now(),
    )


def _publicar(edital, ato, *, lista_id=None, natureza=Natureza.PRELIMINAR, anterior=None):
    return PublicacaoResultado.objects.create(
        edital=edital,
        ato=ato,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        lista_id=lista_id,
        natureza=natureza,
        publicacao_anterior=anterior,
        conteudo_publico=b'{"ordem":[]}',
        conteudo_publico_hash="0" * 64,
        publicado_por="cpf:publicadora",
        publicado_em=timezone.now(),
        signatario_id=uuid.uuid4(),
        signatario_nome="Diretora-Geral",
        signatario_cargo="Diretoria",
    )


def test_duas_publicacoes_raiz_sem_lista_continuam_sendo_recusadas(cenario):
    """A metade que **não** pode ter mudado: é a garantia de toda divulgação já publicada.

    O segundo ato é **sucessor** do primeiro, e não uma segunda raiz: duas raízes sem lista no mesmo
    marco já são recusadas pelo próprio `AtoDeOrdenacao`, e o que se quer exercitar aqui é a
    constraint da publicação — duas publicações **raiz** para o mesmo marco sem lista.
    """
    edital, versao = cenario
    raiz = _ato(edital, versao)
    _publicar(edital, raiz)

    with pytest.raises(IntegrityError, match="uq_publicacao_raiz_por_marco"):
        with transaction.atomic():
            _publicar(edital, _ato(edital, versao, anterior=raiz))


def test_tres_listas_do_mesmo_marco_produzem_tres_publicacoes(cenario):
    edital, versao = cenario

    publicadas = [
        _publicar(edital, _ato(edital, versao, lista_id=lista), lista_id=lista)
        for lista in (None, LISTA_PPI, LISTA_PCD)
    ]

    assert len({p.id for p in publicadas}) == 3
    assert PublicacaoResultado.objects.filter(edital=edital, marco_id=MARCO).count() == 3


def test_duas_publicacoes_raiz_da_mesma_lista_sao_recusadas(cenario):
    edital, versao = cenario
    raiz = _ato(edital, versao, lista_id=LISTA_PPI)
    _publicar(edital, raiz, lista_id=LISTA_PPI)

    with pytest.raises(IntegrityError, match="uq_publicacao_raiz_por_marco_e_lista"):
        with transaction.atomic():
            _publicar(
                edital,
                _ato(edital, versao, lista_id=LISTA_PPI, anterior=raiz),
                lista_id=LISTA_PPI,
            )


def test_a_publicacao_de_uma_lista_nao_pode_citar_o_ato_de_outra(cenario):
    """A trigger de coerência, agora com o quarto eixo: o ato é a autoridade sobre a lista."""
    edital, versao = cenario

    with pytest.raises(ProgrammingError, match="does not match the ordering act it cites"):
        with transaction.atomic():
            _publicar(edital, _ato(edital, versao, lista_id=LISTA_PCD), lista_id=LISTA_PPI)


def test_suceder_a_publicacao_de_uma_lista_nao_arrasta_as_outras(cenario):
    edital, versao = cenario
    publicadas = {
        lista: _publicar(edital, _ato(edital, versao, lista_id=lista), lista_id=lista)
        for lista in (None, LISTA_PPI, LISTA_PCD)
    }

    # O mesmo ato, publicado uma vez por natureza: é o que a `017` já admite (D-007, FR-039).
    sucessora = _publicar(
        edital,
        publicadas[LISTA_PPI].ato,
        lista_id=LISTA_PPI,
        natureza=Natureza.DEFINITIVA,
        anterior=publicadas[LISTA_PPI],
    )

    assert sucessora.publicacao_anterior_id == publicadas[LISTA_PPI].id
    for lista in (None, LISTA_PCD):
        assert not PublicacaoResultado.objects.filter(
            publicacao_anterior=publicadas[lista]
        ).exists()
