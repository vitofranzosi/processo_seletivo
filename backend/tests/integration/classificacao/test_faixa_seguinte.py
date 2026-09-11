"""A faixa seguinte: ela acrescenta à geração, e não a substitui (014, US4).

É o ciclo do 77/2026 — analisada a faixa, parte dela é indeferida, e o Edital manda analisar o
próximo *até que se preencha*. A continuação só existe onde a regra publicada a admite, e não tem
teto numérico: o Edital não publica nenhum, e quantas vagas foram ocupadas é conta da `016`.
"""

import pytest

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.classificacao.application.calculo import calcular_ordem
from processo_seletivo.classificacao.application.corte import calcular_corte, geracao_vigente
from processo_seletivo.classificacao.application.emissao import assinatura_da_proposta, emitir_ordem
from processo_seletivo.classificacao.application.emissao_do_corte import (
    CONTINUAR,
    continuar_corte,
    emitir_corte,
)
from processo_seletivo.classificacao.application.emissao_do_corte import (
    assinatura_da_proposta as assinatura_do_corte,
)
from processo_seletivo.classificacao.models import Corte, ItemDoCorte
from processo_seletivo.comissoes.domain.funcoes import Funcao
from processo_seletivo.resultados.application.consolidacao import consolidar
from processo_seletivo.resultados.application.prontidao import participacao
from tests.fixtures.comissao import alocar_em, constituir, inscrever, rascunho_com_etapas
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.mesa import concluir_como, distribuir_para
from tests.fixtures.publicacao import publish_original

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

MARCO = "00000000-0000-4000-8000-000000000481"
ANALISE = "00000000-0000-4000-8000-000000000482"


@pytest.fixture
def cenario(gestor, api_client, manager_headers, process_payload):
    """Quatro pontuados, alvo 2 e continuação **admitida** — o formato do 77."""
    base = rascunho_com_etapas(avaliacoes=1, maxima="100.0000", minima="60.0000")
    pontuada = base["stages"][1]
    pontuada["weight"] = "1.0000"
    base["stages"].append(
        {
            "id": ANALISE,
            "name": "Análise documental dos classificados",
            "order": 3,
            "eliminatory": True,
            "classificatory": True,
            "minimumScore": "60.0000",
            "maximumScore": "100.0000",
            "evaluationsPerRegistration": 1,
            "weight": "1.0000",
            "scheduleEventId": None,
        }
    )
    base["profiles"][0]["classificationMilestones"] = [
        {
            "id": MARCO,
            "code": "FINAL",
            "name": "Classificação",
            "stages": [pontuada["id"]],
            "operation": "SOMA_PONDERADA",
            "normalization": "NENHUMA",
            "rounding": {"scale": 2, "mode": "MEIO_PARA_CIMA"},
            "tiebreakers": [],
            "cutRule": {
                "targetKind": "FIXED",
                "targetCount": 2,
                "surplusCount": 0,
                "tieOutcome": "STRICT",
                "governedStage": ANALISE,
                "continuation": "ALLOWED",
            },
        }
    ]
    edital = publish_original(api_client, manager_headers, process_payload, draft=base)
    membros = constituir(
        gestor,
        edital.processo,
        [("maria", Funcao.PRESIDENTE), ("joao", Funcao.MEMBRO)],
        prefixo="faixa-014",
    )
    alocar_em(gestor, edital.processo, membros["joao"], edital, pontuada["id"])
    contexto = {
        "edital": edital,
        "processo": edital.processo,
        "membros": membros,
        "etapa": pontuada["id"],
    }
    inscricoes = inscrever(edital, 4, primeiro=901)
    distribuir_para(contexto, gestor, ["joao"], inscricoes, chave="faixa-014-lote")
    for indice, pontuacao in enumerate(["90.0000", "80.0000", "70.0000", "65.0000"]):
        concluir_como(contexto, "joao", inscricoes[indice], pontuacao=pontuacao)
    consolidar(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        etapa_id=pontuada["id"],
        inscricao_ids=[item.id for item in inscricoes],
        idempotency_key="faixa-014-consolidar",
        correlation_id="teste-faixa-014",
    )
    emitir_ordem(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        idempotency_key="faixa-014-ordem",
        correlation_id="teste-faixa-014",
        confirmacao_do_calculo=assinatura_da_proposta(
            calcular_ordem(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)
        ),
    )
    emitir_corte(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        idempotency_key="faixa-014-corte",
        correlation_id="teste-faixa-014",
        confirmacao_do_calculo=assinatura_do_corte(
            calcular_corte(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)
        ),
    )
    return edital, inscricoes


def continuar(
    edital, gestor, *, quantidade=1, chave="faixa-014-continuar", motivo="dois indeferidos"
):
    return continuar_corte(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        idempotency_key=chave,
        correlation_id="teste-faixa-014",
        quantidade=quantidade,
        motivo=motivo,
    )


# --- T071 · a continuação começa onde a anterior parou, e as duas ficam vigentes -------------


def test_a_continuacao_comeca_depois_da_ultima_posicao_alcancada(cenario, gestor):
    edital, inscricoes = cenario

    continuar(edital, gestor)

    seguinte = Corte.objects.exclude(faixa_anterior__isnull=True).get()
    assert seguinte.primeira_posicao == 3
    alcancados = set(
        seguinte.itens.filter(consequencia=ItemDoCorte.Consequencia.PROGREDIU).values_list(
            "inscricao_id", flat=True
        )
    )
    assert alcancados == {inscricoes[2].id}


def test_as_duas_faixas_ficam_vigentes_na_mesma_geracao(cenario, gestor):
    edital, _ = cenario
    raiz = Corte.objects.get()

    continuar(edital, gestor)

    geracao = geracao_vigente(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)
    assert len(geracao) == 2
    assert geracao[0] == raiz
    assert geracao[1].raiz_id == raiz.id


def test_a_etapa_governada_passa_a_receber_as_duas_faixas(cenario, gestor):
    edital, inscricoes = cenario

    continuar(edital, gestor)

    participantes, _, _ = participacao(edital=edital, etapa_id=ANALISE)
    assert participantes == {inscricoes[0].id, inscricoes[1].id, inscricoes[2].id}


def test_ninguem_e_alcancado_duas_vezes_pela_mesma_geracao(cenario, gestor):
    edital, _ = cenario

    continuar(edital, gestor)

    geracao = geracao_vigente(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)
    alcancados = [
        item
        for corte in geracao
        for item in corte.itens.filter(consequencia=ItemDoCorte.Consequencia.PROGREDIU).values_list(
            "inscricao_id", flat=True
        )
    ]
    assert len(alcancados) == len(set(alcancados))


# --- T072 · continuação **não** é sucessão ---------------------------------------------------


def test_a_continuacao_nao_sucede_a_faixa_anterior(cenario, gestor):
    """Trocar uma pela outra produz um sistema que parece funcionar e deixa alguém de fora."""
    edital, _ = cenario
    raiz = Corte.objects.get()

    continuar(edital, gestor)

    seguinte = Corte.objects.exclude(pk=raiz.pk).get()
    assert seguinte.corte_anterior_id is None, "continuação não aponta sucessão"
    assert seguinte.faixa_anterior_id == raiz.id
    assert not raiz.sucessores.exists(), "a faixa anterior não ganhou sucessor"


def test_a_geracao_admite_uma_cadeia_de_continuacoes(cenario, gestor):
    """O ciclo do 77 cruza a fronteira mais de uma vez, e cada volta é uma faixa nova.

    A continuação sempre pende da **última** faixa da geração, e não da raiz: continuar duas vezes
    produz três faixas encadeadas, e não duas continuações disputando a mesma anterior — que é o
    que `uq_corte_continuacao_unica` recusa, e que só uma corrida produziria.
    """
    edital, inscricoes = cenario
    continuar(edital, gestor)

    continuar(edital, gestor, chave="faixa-014-continuar-2", motivo="mais um indeferido")

    geracao = geracao_vigente(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)
    assert len(geracao) == 3
    assert [item.primeira_posicao for item in geracao] == [1, 3, 4]
    assert geracao[2].faixa_anterior_id == geracao[1].id
    participantes, _, _ = participacao(edital=edital, etapa_id=ANALISE)
    assert participantes == {item.id for item in inscricoes}


# --- T073a · a quantidade é pedida, e a continuação não tem teto numérico ---------------------


def test_a_quantidade_declarada_limita_quem_a_faixa_alcanca(cenario, gestor):
    """O sistema não sabe quantas vagas foram ocupadas, e não decide sozinho quantos chamar."""
    edital, inscricoes = cenario

    continuar(edital, gestor, quantidade=2)

    seguinte = Corte.objects.exclude(faixa_anterior__isnull=True).get()
    assert seguinte.itens.filter(consequencia=ItemDoCorte.Consequencia.PROGREDIU).count() == 2


def test_a_continuacao_gera_auditoria_propria(cenario, gestor):
    edital, _ = cenario

    continuar(edital, gestor)

    assert RegistroAuditoria.objects.filter(operation=CONTINUAR).count() == 1
