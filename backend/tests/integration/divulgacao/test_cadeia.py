"""A publicação nasce coerente com o ato que cita e com a linha que sucede (FR-038, FR-042).

**Por que a trigger não é redundância com as constraints.** Os três eixos são colunas da
publicação, e `uq_publicacao_raiz_por_marco` opera **sobre elas** — não sobre o ato. Uma linha que
declare um marco e cite o ato de outro passa pela constraint sem ser vista, porque o par que ela
ocupa é o do marco declarado. É esse caso que
`test_o_eixo_adulterado_nao_abre_uma_segunda_raiz_sobre_o_mesmo_ato` exercita: sem a trigger,
bastaria variar o eixo declarado para inserir quantas raízes se quisesse sobre o mesmo ato, e a
cadeia deixaria de significar o que afirma.
"""

import uuid

import pytest
from django.db import DatabaseError, IntegrityError, connection, transaction
from django.utils import timezone

from processo_seletivo.divulgacao.models import PublicacaoResultado
from tests.fixtures.divulgacao import montar_ato_publicavel

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

SOMENTE_POSTGRES = pytest.mark.skipif(
    connection.vendor != "postgresql",
    reason="A trigger de coerência é de PostgreSQL; em sqlite a garantia não existe.",
)


@pytest.fixture
def cenario(gestor, api_client, manager_headers, process_payload):
    return montar_ato_publicavel(
        gestor, api_client, manager_headers, process_payload, seed=31, codigo="0731"
    )


def _publicar(cenario, **campos):
    ato = campos.pop("ato", None) or cenario["ato"]
    padrao = {
        "edital": cenario["edital"],
        "ato": ato,
        "perfil_id": ato.perfil_id,
        "marco_id": ato.marco_id,
        "natureza": "PRELIMINAR",
        "conteudo_publico": b"{}",
        "conteudo_publico_hash": "0" * 64,
        "publicado_por": "paula.publicadora",
        "publicado_em": timezone.now(),
        "signatario_id": uuid.uuid4(),
        "signatario_nome": "Diretora do Cefor",
        "signatario_cargo": "Diretora-Geral",
    }
    return PublicacaoResultado.objects.create(**{**padrao, **campos})


@SOMENTE_POSTGRES
@pytest.mark.parametrize("eixo", ["perfil_id", "marco_id"])
def test_a_trigger_recusa_publicacao_cujo_eixo_diverge_do_ato(cenario, eixo):
    """O ato citado é a autoridade sobre os eixos; a publicação apenas os declara."""
    with (
        pytest.raises(DatabaseError, match="does not match the ordering act"),
        transaction.atomic(),
    ):
        _publicar(cenario, **{eixo: uuid.uuid4()})


@SOMENTE_POSTGRES
def test_a_trigger_recusa_publicacao_cujo_edital_diverge_do_ato(
    gestor, api_client, manager_headers, process_payload, cenario
):
    """O Edital declarado é outro que existe — e o ato citado continua sendo o do primeiro."""
    alheio = montar_ato_publicavel(
        gestor, api_client, manager_headers, process_payload, seed=32, codigo="0732", primeiro=801
    )

    with (
        pytest.raises(DatabaseError, match="does not match the ordering act"),
        transaction.atomic(),
    ):
        _publicar(cenario, edital=alheio["edital"])


@SOMENTE_POSTGRES
def test_o_eixo_adulterado_nao_abre_uma_segunda_raiz_sobre_o_mesmo_ato(cenario):
    """O caso que a constraint sozinha não pega — e a razão de a coluna redundante existir.

    A primeira publicação ocupa `(edital, perfil, marco)`. Uma segunda que declare outro marco
    ocupa outro par e **passa** por `uq_publicacao_raiz_por_marco`: só a trigger vê que o ato
    citado é o mesmo e que o marco declarado não é o dele.
    """
    _publicar(cenario)

    with (
        pytest.raises(DatabaseError, match="does not match the ordering act"),
        transaction.atomic(),
    ):
        _publicar(cenario, marco_id=uuid.uuid4())

    assert PublicacaoResultado.objects.filter(ato=cenario["ato"]).count() == 1


@SOMENTE_POSTGRES
def test_a_trigger_recusa_predecessor_de_outro_marco(
    gestor, api_client, manager_headers, process_payload, cenario
):
    """Uma cadeia que atravessasse marcos não descreveria sucessão nenhuma."""
    alheio = montar_ato_publicavel(
        gestor, api_client, manager_headers, process_payload, seed=33, codigo="0733", primeiro=901
    )
    de_outro_marco = _publicar(alheio)

    with pytest.raises(DatabaseError, match="another milestone"), transaction.atomic():
        _publicar(cenario, publicacao_anterior=de_outro_marco)


@SOMENTE_POSTGRES
def test_a_trigger_recusa_preliminar_sucedendo_definitiva(cenario, gestor):
    """A ordem entre naturezas tem sentido único (D-007)."""
    from tests.fixtures.divulgacao import emitir

    definitiva = _publicar(cenario, natureza="DEFINITIVA")
    sucessor = emitir(cenario, gestor, chave="emitir-017-sucessor", motivo="Resultado tardio.")

    with pytest.raises(DatabaseError, match="nature regresses"), transaction.atomic():
        _publicar(cenario, ato=sucessor, natureza="PRELIMINAR", publicacao_anterior=definitiva)


def test_duas_raizes_do_mesmo_marco_sao_recusadas(cenario, gestor):
    """A constraint continua sendo a rede embaixo: mesmo eixo, sem predecessor, duas vezes."""
    from tests.fixtures.divulgacao import emitir

    _publicar(cenario)
    sucessor = emitir(cenario, gestor, chave="emitir-017-raiz", motivo="Resultado tardio.")

    with pytest.raises(IntegrityError), transaction.atomic():
        _publicar(cenario, ato=sucessor)


def test_dois_sucessores_da_mesma_publicacao_sao_recusados(cenario, gestor):
    from tests.fixtures.divulgacao import emitir

    primeira = _publicar(cenario)
    segundo = emitir(cenario, gestor, chave="emitir-017-b", motivo="Resultado tardio.")
    _publicar(cenario, ato=segundo, publicacao_anterior=primeira)
    terceiro = emitir(cenario, gestor, chave="emitir-017-c", motivo="Outra correção.")

    with pytest.raises(IntegrityError), transaction.atomic():
        _publicar(cenario, ato=terceiro, publicacao_anterior=primeira)


def test_o_mesmo_ato_na_mesma_natureza_duas_vezes_e_recusado(cenario):
    """`uq_publicacao_por_ato_natureza` — a garantia de banco do cenário das duas abas (FR-039)."""
    primeira = _publicar(cenario)

    with pytest.raises(IntegrityError), transaction.atomic():
        _publicar(cenario, publicacao_anterior=primeira)
