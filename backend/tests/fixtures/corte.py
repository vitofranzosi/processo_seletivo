"""O cenário do corte e os atalhos que três arquivos de teste usam (014).

**Funções ficam aqui, e a fixture fica no `conftest.py`.** Importar uma fixture de outro módulo de
teste a redefine no importador, que é o que o `F811` acusa; importar uma função comum não tem esse
problema, e é o que este módulo existe para permitir.

O cenário é o do 14/2026 reduzido ao que a feature precisa provar: uma Etapa pontuada que produz a
ordem, uma Entrevista que o corte alimenta, e um alvo que não alcança todo mundo.
"""

from processo_seletivo.classificacao.application.calculo import calcular_ordem
from processo_seletivo.classificacao.application.corte import calcular_corte
from processo_seletivo.classificacao.application.emissao import assinatura_da_proposta, emitir_ordem
from processo_seletivo.classificacao.application.emissao_do_corte import (
    assinatura_da_proposta as assinatura_do_corte,
)
from processo_seletivo.classificacao.application.emissao_do_corte import emitir_corte
from processo_seletivo.comissoes.domain.funcoes import Funcao
from processo_seletivo.resultados.application.consolidacao import consolidar
from tests.fixtures.comissao import alocar_em, constituir, inscrever, rascunho_com_etapas
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.mesa import concluir_como, distribuir_para
from tests.fixtures.publicacao import publish_original

MARCO = "00000000-0000-4000-8000-000000000461"
ENTREVISTA = "00000000-0000-4000-8000-000000000462"


def regra(**overrides):
    base = {
        "targetKind": "FIXED",
        "targetCount": 2,
        "surplusCount": 0,
        "tieOutcome": "STRICT",
        "governedStage": ENTREVISTA,
        "continuation": "NONE",
    }
    base.update(overrides)
    return base


def rascunho(cut=None):
    base = rascunho_com_etapas(avaliacoes=1, maxima="100.0000", minima="60.0000")
    pontuada = base["stages"][1]
    pontuada["weight"] = "1.0000"
    base["stages"].append(
        {
            "id": ENTREVISTA,
            "name": "Entrevista",
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
            "name": "Classificação por títulos",
            "stages": [pontuada["id"]],
            "operation": "SOMA_PONDERADA",
            "normalization": "NENHUMA",
            "rounding": {"scale": 2, "mode": "MEIO_PARA_CIMA"},
            "tiebreakers": [],
            "cutRule": cut if cut is not None else regra(),
        }
    ]
    return base, pontuada


def montar_cenario_do_corte(gestor, api_client, manager_headers, process_payload):
    """Quatro inscritos, três pontuados, ordem emitida — e um alvo de dois."""
    draft, pontuada = rascunho()
    edital = publish_original(api_client, manager_headers, process_payload, draft=draft)
    membros = constituir(
        gestor,
        edital.processo,
        [("maria", Funcao.PRESIDENTE), ("joao", Funcao.MEMBRO)],
        prefixo="corte-014",
    )
    alocar_em(gestor, edital.processo, membros["joao"], edital, pontuada["id"])
    contexto = {
        "edital": edital,
        "processo": edital.processo,
        "membros": membros,
        "etapa": pontuada["id"],
    }
    inscricoes = inscrever(edital, 4, primeiro=601)
    distribuir_para(contexto, gestor, ["joao"], inscricoes[:3], chave="corte-014-lote")
    for indice, pontuacao in enumerate(["90.0000", "80.0000", "70.0000"]):
        concluir_como(contexto, "joao", inscricoes[indice], pontuacao=pontuacao)
    consolidar(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        etapa_id=pontuada["id"],
        inscricao_ids=[item.id for item in inscricoes[:3]],
        idempotency_key="corte-014-consolidar",
        correlation_id="teste-corte-014",
    )
    emitir_ordem(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        idempotency_key="corte-014-ordem",
        correlation_id="teste-corte-014",
        confirmacao_do_calculo=assinatura_da_proposta(
            calcular_ordem(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)
        ),
    )
    return edital, pontuada, inscricoes


def confirmacao(edital, *, geracao=()):
    proposta = calcular_corte(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)
    return assinatura_do_corte(proposta, geracao=geracao)


def emitir(edital, gestor, *, chave="corte-014-emitir", motivo="", geracao=()):
    return emitir_corte(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        idempotency_key=chave,
        correlation_id="teste-corte-014",
        confirmacao_do_calculo=confirmacao(edital, geracao=geracao),
        motivo=motivo,
    )
