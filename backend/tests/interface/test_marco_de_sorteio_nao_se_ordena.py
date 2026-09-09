"""A tela da `015` não ordena marco que o Edital manda sortear (`021`, `D-006`, `FR-069`).

**O defeito era irreversível, e foi o que fez esta porta existir.** A rota da ordenação pende do
marco, e a tela do Edital oferecia todos os marcos classificatórios — inclusive os de sorteio.
Aberta num deles, a `015` calculava a ordem por Etapas e oferecia "Emitir ordem"; o ato saía com
`origem=COMPUTADO` e `lista_id` nulo, que é exatamente a raiz da ampla concorrência. Dali em
diante `constituir_sorteio` recusava com `ordering_act_already_exists`, e não havia desfazer: a
tabela é append-only, e a sucessão de uma ordem sorteada nasce da anulação de um sorteio que nesse
caminho nunca chegou a existir.

As três afirmações abaixo são as três camadas: a tela encaminha, a rota que grava recusa, e o
comando recusa sozinho — porque fechar só a tela deixaria as outras duas de pé.
"""

import pytest
from django.urls import reverse

from processo_seletivo.classificacao.application.calculo import calcular_ordem
from processo_seletivo.classificacao.application.emissao import (
    assinatura_da_proposta,
    emitir_ordem,
)
from processo_seletivo.classificacao.models import AtoDeOrdenacao
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.sorteios.application.ocorrencia import observar_ocorrencia
from processo_seletivo.sorteios.application.relacao import publicar_relacao
from processo_seletivo.sorteios.application.sorteio import constituir_sorteio
from processo_seletivo.sorteios.infrastructure.fontes.loteria_federal import FonteDeTeste
from tests.fixtures.sorteio import METODO, certame_com_cotas, presidente
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def certame(gestor, api_client, manager_headers, process_payload, seletor_ligado):
    return certame_com_cotas(gestor, api_client, manager_headers, process_payload)


def test_a_tela_da_ordenacao_encaminha_para_o_sorteio(certame, client):
    """Encaminha, e não recusa: o marco existe e a pessoa pode vê-lo — na tela que é dele."""
    identificar(client, "maria", [])

    resposta = client.get(
        reverse("interface:ordenacao", args=[certame["edital"].id, certame["marco"]])
    )

    assert resposta.status_code == 302
    assert resposta.headers["Location"] == reverse(
        "interface:sorteio", args=[certame["edital"].id, certame["marco"]]
    )


def test_a_rota_que_grava_nao_constitui_ato_computado(certame, client):
    identificar(client, "maria", [])

    resposta = client.post(
        reverse("interface:emitir-ordenacao", args=[certame["edital"].id, certame["marco"]]),
        {"chave_idempotencia": "tentativa", "confirmacao_do_calculo": "", "motivo": ""},
    )

    assert resposta.status_code == 302
    assert resposta.headers["Location"] == reverse(
        "interface:sorteio", args=[certame["edital"].id, certame["marco"]]
    )
    assert not AtoDeOrdenacao.objects.exists()


def test_o_comando_recusa_sozinho(certame):
    """Sem passar por tela nenhuma: é esta camada que protege a tabela append-only."""
    proposta = calcular_ordem(
        edital=certame["edital"], perfil_id=certame["perfil"], marco_id=certame["marco"]
    )

    with pytest.raises(DomainError) as recusa:
        emitir_ordem(
            actor=presidente(),
            processo_id=certame["processo"].id,
            edital_id=certame["edital"].id,
            perfil_id=certame["perfil"],
            marco_id=certame["marco"],
            idempotency_key="comando-direto",
            correlation_id="teste-021",
            confirmacao_do_calculo=assinatura_da_proposta(proposta, ato_vigente=None),
        )

    assert recusa.value.code == "ordering_milestone_is_drawn"
    assert not AtoDeOrdenacao.objects.exists()


def test_o_sorteio_da_ampla_concorrencia_continua_possivel(certame, client):
    """A afirmação que dá a medida do estrago: com a porta fechada, o certame ainda sorteia.

    A confirmação vai **correta** de propósito. Com ela vazia a rota recusaria por falta de
    confirmação, e o teste passaria mesmo com a porta aberta — que foi o que a primeira versão
    dele fez. É a tentativa que chega ao fim que grava o ato irreversível.
    """
    proposta = calcular_ordem(
        edital=certame["edital"], perfil_id=certame["perfil"], marco_id=certame["marco"]
    )
    identificar(client, "maria", [])
    client.post(
        reverse("interface:emitir-ordenacao", args=[certame["edital"].id, certame["marco"]]),
        {
            "chave_idempotencia": "tentativa",
            "confirmacao_do_calculo": assinatura_da_proposta(proposta, ato_vigente=None),
            "motivo": "",
        },
    )

    relacao = publicar_relacao(
        actor=presidente(),
        processo_id=certame["processo"].id,
        edital_id=certame["edital"].id,
        perfil_id=certame["perfil"],
        marco_id=certame["marco"],
        lista_id=None,
        idempotency_key="relacao-ampla",
        correlation_id="teste-021",
    )["relacao"]
    ocorrencia = observar_ocorrencia(
        actor=presidente(),
        processo_id=certame["processo"].id,
        fonte=METODO["source"],
        referencia=METODO["occurrence"],
        idempotency_key="ocorrencia",
        correlation_id="teste-021",
        fonte_externa=FonteDeTeste(),
    )["ocorrencia"]

    constituir_sorteio(
        actor=presidente(),
        processo_id=certame["processo"].id,
        edital_id=certame["edital"].id,
        relacao_id=relacao,
        ocorrencia_id=ocorrencia,
        idempotency_key="sorteio-ampla",
        correlation_id="teste-021",
    )

    ato = AtoDeOrdenacao.objects.get()
    assert ato.origem == "SORTEIO"
    assert ato.lista_id is None
