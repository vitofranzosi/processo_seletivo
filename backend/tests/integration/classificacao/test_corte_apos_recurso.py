"""O corte emitido **depois** do recurso, e não antes.

Registro em `doc/achado-corte-nasce-obsoleto-apos-recurso.md`.

Os testes de `test_corte_obsoleto.py` cobrem uma cronologia só: corte emitido, depois o recurso. A
ordem de um certame real é a outra — preliminar, recurso julgado, ordem sucessora, e só então o
corte —, e nela o ato que a faixa leu **já cita** o Resultado sucessor. Não há reingresso a acusar:
uma geração sucessora sairia idêntica à anterior, que é a cerimônia que a `FR-230` recusa.
"""

import pytest

from processo_seletivo.classificacao.application.calculo import calcular_ordem
from processo_seletivo.classificacao.application.corte import estado_do_corte
from processo_seletivo.classificacao.application.emissao import assinatura_da_proposta, emitir_ordem
from processo_seletivo.classificacao.application.selectors import ato_vigente
from processo_seletivo.classificacao.models import Corte
from processo_seletivo.resultados.application.prontidao import impedimento_do_corte
from tests.fixtures.corte import ENTREVISTA, MARCO, emitir
from tests.fixtures.edital import PROFILE_ID
from tests.integration.classificacao.test_corte_obsoleto import _superar_resultado

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def _ordem_sucessora(edital, gestor):
    emitir_ordem(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        idempotency_key="corte-apos-recurso-ordem-sucessora",
        correlation_id="teste-corte-apos-recurso",
        confirmacao_do_calculo=assinatura_da_proposta(
            calcular_ordem(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO),
            ato_vigente=ato_vigente(edital=edital, marco_id=MARCO),
        ),
        motivo="recurso deferido sobre a pontuação",
    )


def test_corte_emitido_sobre_a_ordem_sucessora_nao_nasce_obsoleto(cenario, gestor):
    edital, pontuada, inscricoes = cenario
    preliminar = ato_vigente(edital=edital, marco_id=MARCO)

    superado = _superar_resultado(edital, inscricoes[0].id, pontuada["id"])
    _ordem_sucessora(edital, gestor)
    sucessora = ato_vigente(edital=edital, marco_id=MARCO)
    # O corte só se emite sobre ordem em dia (FR-198): chegar ao `emitir` já prova que a ordem
    # sucessora cita o Resultado sucessor, e não o superado.
    emitir(edital, gestor)
    corte = Corte.objects.get()

    assert sucessora.id != preliminar.id
    assert corte.ato_id == sucessora.id
    citados = {item["id"] for item in sucessora.universo["stageResults"]}
    assert str(superado.id) in citados, "o ato que a faixa leu já considerou o recurso"

    estado = estado_do_corte(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)
    assert (estado["obsoleto"], [item["tipo"] for item in estado["causas"]]) == (False, [])


def test_corte_emitido_sobre_a_ordem_sucessora_nao_bloqueia_a_etapa_governada(cenario, gestor):
    edital, pontuada, inscricoes = cenario
    _superar_resultado(edital, inscricoes[0].id, pontuada["id"])
    _ordem_sucessora(edital, gestor)
    emitir(edital, gestor)

    assert impedimento_do_corte(edital, ENTREVISTA) is None


def test_a_geracao_sucessora_que_a_recusa_indica_nasce_em_dia(cenario, gestor):
    """O caminho que `impedimento_do_corte` oferece leva a algum lugar (FR-1144).

    Antes da `061` não levava: a sucessora lê o mesmo ato, e nascia obsoleta pela mesma razão.
    """
    edital, pontuada, inscricoes = cenario
    _superar_resultado(edital, inscricoes[0].id, pontuada["id"])
    _ordem_sucessora(edital, gestor)
    emitir(edital, gestor)
    anterior = Corte.objects.get()

    emitir(
        edital,
        gestor,
        chave="corte-apos-recurso-sucessora",
        motivo="a recusa pediu a geração sucessora",
        geracao=[anterior],
    )

    estado = estado_do_corte(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)
    assert estado["geracao"][0].id != anterior.id
    assert (estado["obsoleto"], [item["tipo"] for item in estado["causas"]]) == (False, [])


# --- a publicação que depende da faixa (FR-219), nas duas cronologias --------------------------


def test_a_publicacao_da_ordem_sucessora_nao_e_impedida_pelo_corte_emitido_depois(cenario, gestor):
    from processo_seletivo.divulgacao.domain.publicabilidade import CORTE_OBSOLETO, aferir

    edital, pontuada, inscricoes = cenario
    _superar_resultado(edital, inscricoes[0].id, pontuada["id"])
    _ordem_sucessora(edital, gestor)
    emitir(edital, gestor)

    afericao = aferir(
        edital=edital,
        marco_id=MARCO,
        ato=ato_vigente(edital=edital, marco_id=MARCO),
        natureza="PRELIMINAR",
    )

    assert afericao.codigo != CORTE_OBSOLETO, afericao.divergencias


def test_o_recurso_deferido_depois_do_corte_continua_impedindo_a_publicacao(cenario, gestor):
    """A cronologia que a `FR-218` protege: aqui o ato que a faixa leu cita o Resultado superado."""
    from processo_seletivo.divulgacao.domain.publicabilidade import CORTE_OBSOLETO, aferir

    edital, pontuada, inscricoes = cenario
    emitir(edital, gestor)
    _superar_resultado(edital, inscricoes[0].id, pontuada["id"])

    afericao = aferir(
        edital=edital,
        marco_id=MARCO,
        ato=ato_vigente(edital=edital, marco_id=MARCO),
        natureza="PRELIMINAR",
    )

    assert afericao.codigo == CORTE_OBSOLETO
    assert [item["tipo"] for item in afericao.divergencias] == ["participante_reingressou"]


# --- o custo: a mesma pergunta, numa consulta só ------------------------------------------------


def test_a_comparacao_por_identidade_nao_acrescenta_consulta(cenario, gestor):
    """Os ids citados vêm do universo que o ato já trouxe; a exclusão entra na mesma consulta.

    `impedimento_do_corte` roda na prontidão de cada Etapa governada, sob orçamento: uma consulta a
    mais por leitura seria paga em toda tela que a mostra.
    """
    from django.db import connection
    from django.test.utils import CaptureQueriesContext

    from processo_seletivo.classificacao.application.corte import _reingressou, geracao_vigente

    edital, pontuada, inscricoes = cenario
    _superar_resultado(edital, inscricoes[0].id, pontuada["id"])
    _ordem_sucessora(edital, gestor)
    emitir(edital, gestor)
    geracao = geracao_vigente(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)
    geracao[0].ato  # noqa: B018 — o ato já vem carregado para quem chama, como em `estado_do_corte`

    with CaptureQueriesContext(connection) as consultas:
        _reingressou(edital, geracao)

    assert len(consultas) == 1, [item["sql"] for item in consultas]
