"""A chamada nova da mesma inscrição aproveita o que a anterior recebeu (115, US8, D-013).

O percurso é o do 69/2026, pelo caminho real: a titular é reclassificada, a lista se esgota, e ela é
chamada de novo. A chamada nova grava a sua lista, e cada item que a anterior recebeu e não estava
*pendente* nasce aproveitado por referência — sem arquivo novo e **sem a conferência de lá**
(FR-3619 a FR-3621, SC-1092).
"""

import pytest

from processo_seletivo.convocacao.application import selectors
from processo_seletivo.convocacao.domain import nomes
from processo_seletivo.convocacao.models import Convocacao
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures import documentos_da_convocacao as cenarios
from tests.fixtures.convocacao import apurar, convocar
from tests.fixtures.corte import MARCO, regra
from tests.fixtures.documentos_da_convocacao import (
    CERTIDAO,
    HISTORICO,
    RESIDENCIA,
    apresentar,
    arquivos_no_armazenamento,
    conferir,
    desfechar,
    lido,
)
from tests.fixtures.edital import PROFILE_ID

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


@pytest.fixture
def aluno_do_69(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    """Duas vagas e faixa de três: dois titulares e uma suplente, com os documentos do aluno."""
    return cenarios.montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        documentos=cenarios.documentos_do_aluno(),
        prefixo="aluno-69-115",
        geral=2,
        cut=regra(surplusCount=1),
    )


def _fila(edital):
    return selectors.contexto_do_recorte(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )["fila"]


def _chamada_nova_da_reclassificada(cenario, gestor, depois_da_primeira):
    """Chama, reclassifica, esgota a lista e chama de novo a mesma inscrição."""
    edital, _, inscricoes = cenario
    inicio = _fila(edital)
    reclassificada, titular, suplente = inicio[0], inicio[1], inicio[2]
    pessoa = next(i for i in inscricoes if i.id == reclassificada)
    primeira = Convocacao.objects.get(
        id=convocar(edital, gestor, reclassificada, idempotency_key="ec-1")["id"]
    )
    depois_da_primeira(pessoa, primeira)
    desfechar(edital, gestor, primeira, nomes.RECLASSIFICACAO, "ec-1-desfecho", "Não compareceu.")
    apurar(edital, gestor, chave="ec-apura-1", motivo="Reclassificação registrada")
    convocar(edital, gestor, titular, idempotency_key="ec-titular")
    chamada = convocar(
        edital, gestor, suplente, especie=nomes.SUPLENCIA, idempotency_key="ec-suplente"
    )
    desfechar(
        edital,
        gestor,
        Convocacao.objects.get(id=chamada["id"]),
        nomes.DESISTENCIA_EXPRESSA,
        "ec-suplente-desiste",
        "Desistiu por escrito.",
    )
    apurar(edital, gestor, chave="ec-apura-2", motivo="Desistência da suplente")
    segunda = Convocacao.objects.get(
        id=convocar(edital, gestor, reclassificada, idempotency_key="ec-2")["id"]
    )
    return pessoa, primeira, segunda


def test_a_chamada_nova_aproveita_o_que_nao_estava_pendente_sem_copia(
    aluno_do_69, gestor, raiz_de_arquivos
):
    def na_primeira(pessoa, primeira):
        apresentar(pessoa, primeira, CERTIDAO, corpo=b"certidao")
        conferir(gestor, primeira, CERTIDAO, "CONFORME", chave="ec-c1")
        apresentar(pessoa, primeira, HISTORICO, corpo=b"historico incompleto")
        conferir(gestor, primeira, HISTORICO, "PENDENTE", chave="ec-c2", motivo="Falta página.")
        apresentar(pessoa, primeira, RESIDENCIA, corpo=b"residencia")

    arquivos = {}

    def contar(pessoa, primeira):
        na_primeira(pessoa, primeira)
        arquivos["antes"] = arquivos_no_armazenamento(raiz_de_arquivos)

    pessoa, primeira, segunda = _chamada_nova_da_reclassificada(aluno_do_69, gestor, contar)

    assert segunda.convocacao_anterior_id is None
    assert segunda.itens_da_lista.count() == 4, "a chamada nova tem a sua própria lista"
    certidao = lido(segunda, CERTIDAO)
    origem = lido(primeira, CERTIDAO).vigente
    assert certidao.vigente.apresentacao_de_origem_id == origem.id
    assert certidao.vigente.content_hash == origem.content_hash
    assert not certidao.vigente.arquivo
    assert certidao.estado == nomes.ITEM_RECEBIDO, "a conferência de lá não vem junto"
    assert certidao.aproveitada["de"] == "chamada"
    assert lido(segunda, RESIDENCIA).estado == nomes.ITEM_RECEBIDO, "recebido e não conferido"
    assert lido(segunda, HISTORICO).estado == nomes.ITEM_A_APRESENTAR, "pendente não se aproveita"
    assert arquivos_no_armazenamento(raiz_de_arquivos) == arquivos["antes"], "SC-1092"


def test_a_abertura_na_chamada_anterior_nao_autoriza_o_conforme_da_nova(aluno_do_69, gestor):
    """FR-3611 e D-012, aprovada: a referência da chamada nova é outra apresentação."""

    def na_primeira(pessoa, primeira):
        apresentar(pessoa, primeira, CERTIDAO, corpo=b"certidao")
        conferir(gestor, primeira, CERTIDAO, "CONFORME", chave="ab-c1")

    _, _, segunda = _chamada_nova_da_reclassificada(aluno_do_69, gestor, na_primeira)

    with pytest.raises(DomainError) as recusa:
        conferir(gestor, segunda, CERTIDAO, "CONFORME", chave="ab-c2", abrir_antes=False)
    assert recusa.value.code == nomes.CONFORME_SEM_ABERTURA

    conferencia = conferir(gestor, segunda, CERTIDAO, "CONFORME", chave="ab-c3")
    assert conferencia.item.chamada_id == segunda.id


def test_a_referencia_aponta_a_origem_e_nunca_outra_referencia(aluno_do_69, gestor):
    """Se o que a chamada anterior tinha era ela mesma uma referência, a nova aponta o arquivo."""
    from processo_seletivo.convocacao.application.documentos import _origem_aproveitavel

    def na_primeira(pessoa, primeira):
        apresentar(pessoa, primeira, CERTIDAO, corpo=b"certidao")

    _, primeira, segunda = _chamada_nova_da_reclassificada(aluno_do_69, gestor, na_primeira)

    referencia = lido(segunda, CERTIDAO).vigente
    item_da_segunda = segunda.itens_da_lista.get(requisito_id=CERTIDAO)
    assert _origem_aproveitavel(item_da_segunda) == referencia.apresentacao_de_origem
    assert referencia.apresentacao_de_origem.arquivo, "a origem guarda o arquivo"
