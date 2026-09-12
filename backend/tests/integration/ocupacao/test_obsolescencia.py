"""As quatro causas de obsolescência, uma por vez e com a causa nomeada (016, `FR-263`).

**Obsoleta não é sucedida.** A primeira é leitura do mundo em volta; a segunda é ato novo. Uma
apuração pode estar vigente e obsoleta ao mesmo tempo — e nesse estado não causa faixa seguinte.

**Nenhuma delas é coluna.** São calculadas a cada leitura, como a `014` já faz com o corte, e por
isso este arquivo ataca o mundo em volta em vez de escrever flag nenhuma.
"""

import pytest

from processo_seletivo.ocupacao.application import selectors
from processo_seletivo.ocupacao.domain import nomes
from tests.fixtures.corte import MARCO
from tests.fixtures.edital import PROFILE_ID
from tests.integration.ocupacao.test_emissao import apurar

pytestmark = pytest.mark.django_db(transaction=True)


def causas(edital):
    vigente = selectors.apuracao_vigente(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )
    return [item["causa"] for item in selectors.causas_de_obsolescencia(vigente)]


def test_apuracao_recem_emitida_nao_tem_causa(cenario, gestor):
    edital, _, _ = cenario
    apurar(edital, gestor)

    assert causas(edital) == []


def test_a_ordem_sucedida_obsoleta_a_apuracao(cenario, gestor):
    """Primeira causa: a apuração contou sobre uma ordem que já não é a vigente."""
    edital, _, _ = cenario
    apurar(edital, gestor)

    _suceder_a_ordem(edital, gestor)

    assert nomes.CAUSA_ORDEM_SUCEDIDA in causas(edital)


def test_o_movimento_posterior_obsoleta_o_recorte(cenario, gestor):
    """**Quarta causa, e é a que dispensa orquestração** (`SC-084`).

    Recebida a reversão, o recorte de destino aparece obsoleto **sem que ninguém emita nada** — e
    passa a vigente na primeira emissão seguinte. Obrigar a reversão a disparar, em cascata, a
    emissão do destino custaria uma orquestração entre dois recortes; reusar a obsolescência que já
    existe custa esta causa.
    """
    from django.utils import timezone

    from processo_seletivo.ocupacao.models import ApuracaoDeOcupacao, MovimentoDeVaga

    edital, _, _ = cenario
    apurar(edital, gestor)
    vigente = ApuracaoDeOcupacao.objects.get()
    assert causas(edital) == []

    MovimentoDeVaga.objects.create(
        apuracao=vigente,
        especie=nomes.MOVIMENTO_REVERSAO,
        origem_lista_id="00000000-0000-4000-8000-000000000473",
        destino_lista_id=None,
        quantidade=2,
        causa="Cota esgotada com saldo",
        registrado_por="teste",
        registrado_em=timezone.now(),
    )

    assert nomes.CAUSA_MOVIMENTO_POSTERIOR in causas(edital)

    # E a emissão seguinte o lê: volta a vigente, com o número novo.
    declarado = apurar(edital, gestor, chave="ocupacao-016-apurar-2", motivo="Reversão recebida")
    assert declarado["efetivas"] == declarado["publicadas"] + 2
    assert causas(edital) == []


def _suceder_a_ordem(edital, gestor):
    """Emite uma ordem sucessora no mesmo recorte, que é o que torna a anterior não vigente."""
    from processo_seletivo.classificacao.application.calculo import calcular_ordem
    from processo_seletivo.classificacao.application.emissao import (
        assinatura_da_proposta,
        emitir_ordem,
    )
    from processo_seletivo.classificacao.application.selectors import ato_vigente

    # **A assinatura precisa citar o ato vigente visto na leitura.** Sem isso a emissão recusa com
    # `ordering_act_already_exists`, e com razão: confirmar um cálculo sem dizer sobre qual estado
    # ele foi feito é exatamente o que a conferência existe para impedir.
    vigente = ato_vigente(edital=edital, marco_id=MARCO, lista_id=None)
    emitir_ordem(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        idempotency_key="ocupacao-016-ordem-2",
        correlation_id="teste-ocupacao-016",
        confirmacao_do_calculo=assinatura_da_proposta(
            calcular_ordem(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO),
            ato_vigente=vigente,
        ),
        motivo="Sucessão para o teste de obsolescência",
    )
