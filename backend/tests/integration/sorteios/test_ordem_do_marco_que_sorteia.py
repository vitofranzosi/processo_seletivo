"""A ordem de um marco de sorteio não nasce do cálculo por Etapas (021, D-001, FR-034).

**O caminho do defeito, inteiro.** O detalhe do Edital manda todo marco classificatório para a
tela de ordenação. Sem ato, o estado do marco dizia `recomputavel=True`, a tela oferecia "Emitir
ordem", e `emitir_ordem` não sabia nada sobre `drawMethod`: emitido, o ato computado ocupava o
**ato raiz do recorte**.

Dali em diante o certame não sortejava mais. `constituir_sorteio` recusava — corretamente, com
`ordering_act_already_exists` —, e o único caminho que a recusa nomeia é o do sucessor, que exige um
`sorteio_anterior` que nunca existiu. Um clique bastava, e a saída não estava em tela alguma.

São duas camadas, como sempre: a tela deixou de oferecer (`test_console_do_sorteio.py`), e o comando
recusa — que é a que vale para quem chegar por qualquer outra porta.
"""

import pytest

from processo_seletivo.classificacao.application.emissao import emitir_ordem
from processo_seletivo.classificacao.models import AtoDeOrdenacao
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.sorteio import certame_de_sorteio, presidente

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


@pytest.fixture
def certame(gestor, api_client, manager_headers, process_payload):
    return certame_de_sorteio(gestor, api_client, manager_headers, process_payload)


def test_emitir_ordem_recusa_o_marco_que_declara_sorteio(certame):
    with pytest.raises(DomainError) as recusa:
        emitir_ordem(
            actor=presidente(),
            processo_id=certame["processo"].id,
            edital_id=certame["edital"].id,
            perfil_id=certame["perfil"],
            marco_id=certame["marco"],
            idempotency_key="computar-marco-de-sorteio",
            correlation_id="teste-021",
            confirmacao_do_calculo="qualquer",
        )

    assert recusa.value.code == "milestone_ordered_by_draw"
    assert recusa.value.status == 409
    assert not AtoDeOrdenacao.objects.exists(), (
        "o ato raiz do recorte não pode ser ocupado por um cálculo que a norma não prevê"
    )


def test_a_recusa_vem_antes_da_confirmacao_do_calculo(certame):
    """A ordem das recusas importa: a assinatura da proposta não é o assunto aqui.

    Recusar primeiro por confirmação faltante mandaria quem lê conferir e reenviar um cálculo que
    **nunca** deveria ser emitido — e a segunda tentativa, já com a assinatura certa, passaria.
    """
    with pytest.raises(DomainError) as recusa:
        emitir_ordem(
            actor=presidente(),
            processo_id=certame["processo"].id,
            edital_id=certame["edital"].id,
            perfil_id=certame["perfil"],
            marco_id=certame["marco"],
            idempotency_key="computar-sem-confirmacao",
            correlation_id="teste-021",
            confirmacao_do_calculo="",
        )

    assert recusa.value.code == "milestone_ordered_by_draw"


def test_o_sorteio_continua_possivel_depois_da_recusa(certame):
    """A recusa protege o que vem depois: com o ato raiz livre, o sorteio nasce normalmente."""
    from processo_seletivo.sorteios.application.ocorrencia import observar_ocorrencia
    from processo_seletivo.sorteios.application.relacao import publicar_relacao
    from processo_seletivo.sorteios.application.sorteio import constituir_sorteio
    from tests.fixtures.sorteio import METODO

    with pytest.raises(DomainError):
        emitir_ordem(
            actor=presidente(),
            processo_id=certame["processo"].id,
            edital_id=certame["edital"].id,
            perfil_id=certame["perfil"],
            marco_id=certame["marco"],
            idempotency_key="computar-antes-de-sortear",
            correlation_id="teste-021",
            confirmacao_do_calculo="qualquer",
        )

    relacao = publicar_relacao(
        actor=presidente(),
        processo_id=certame["processo"].id,
        edital_id=certame["edital"].id,
        perfil_id=certame["perfil"],
        marco_id=certame["marco"],
        idempotency_key="relacao-depois-da-recusa",
        correlation_id="teste-021",
    )
    ocorrencia = observar_ocorrencia(
        actor=presidente(),
        processo_id=certame["processo"].id,
        fonte=METODO["source"],
        referencia=METODO["occurrence"],
        idempotency_key="ocorrencia-depois-da-recusa",
        correlation_id="teste-021",
    )
    declarado = constituir_sorteio(
        actor=presidente(),
        processo_id=certame["processo"].id,
        edital_id=certame["edital"].id,
        relacao_id=relacao["relacao"],
        ocorrencia_id=ocorrencia["ocorrencia"],
        idempotency_key="sorteio-depois-da-recusa",
        correlation_id="teste-021",
    )

    assert declarado["quantidade"] == len(certame["inscricoes"])
