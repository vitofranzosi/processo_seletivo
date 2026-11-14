"""A faixa do corte conta a retirada da reserva só pela ampla (164, FR-7013).

O Edital da `163` com um marco que corta:

```text
1  Análise documental   pontuada, classificatória      todas      ← o marco a enumera
2  Heteroidentificação  decisória, eliminatória         só PPI
3  Prova didática       pontuada                        todas      ← o corte do marco a governa
```

O corte tem alvo de uma pessoa por lista. Bia (ampla) tem 95, Maria (`PPI`) 90 e Ana (`PPI`) 80:
a faixa da ampla é Bia, e a da `PPI` é Maria. Maria está na Prova **só pela faixa da `PPI`**.
Retirada da reserva na Heteroidentificação, ela não concorre mais pela `PPI`, e a faixa dela não a
faz participar da Prova. Confirmada, participa.
"""

import pytest

from processo_seletivo.classificacao.application.calculo import calcular_ordem
from processo_seletivo.classificacao.application.corte import calcular_corte
from processo_seletivo.classificacao.application.emissao import (
    assinatura_da_proposta,
    emitir_ordem,
)
from processo_seletivo.classificacao.application.emissao_do_corte import (
    assinatura_da_proposta as assinatura_do_corte,
)
from processo_seletivo.classificacao.application.emissao_do_corte import emitir_corte
from processo_seletivo.comissoes.domain.funcoes import Funcao
from processo_seletivo.resultados.application.consolidacao import consolidar
from processo_seletivo.resultados.application.prontidao import (
    fora_do_corte,
    participa_da_etapa,
    participacao,
)
from tests.conftest import ator_institucional
from tests.fixtures.alcance import MODALIDADE_PPI, rascunho_com_alcance
from tests.fixtures.comissao import alocar_em, constituir, inscrever
from tests.fixtures.edital import identificador
from tests.fixtures.mesa import concluir_como, distribuir_para
from tests.fixtures.publicacao import publish_original

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


def _consolidar(cenario, etapa, inscricoes, chave):
    consolidar(
        actor=ator_institucional("maria"),
        processo_id=cenario["processo"].id,
        edital_id=cenario["edital"].id,
        etapa_id=etapa,
        inscricao_ids=[i.id for i in inscricoes],
        idempotency_key=chave,
        correlation_id="teste",
    )


def _montar(gestor, api_client, manager_headers, *, seed):
    rascunho = rascunho_com_alcance(seed)
    analise, hetero, prova = rascunho["stages"]
    analise["classificatory"] = True
    analise["weight"] = "1.0000"
    perfil = rascunho["profiles"][0]
    marco = identificador(1689, seed)
    perfil["classificationMilestones"] = [
        {
            "id": marco,
            "code": "A-ANALISE",
            "name": "Classificação da análise",
            "orderProduction": "POR_PONTUACAO",
            "stages": [analise["id"]],
            "operation": "SOMA_PONDERADA",
            "normalization": "NENHUMA",
            "rounding": {"scale": 2, "mode": "MEIO_PARA_CIMA"},
            "tiebreakers": [],
            "cutRule": {
                "targetKind": "FIXED",
                "targetCount": 1,
                "surplusCount": 0,
                "tieOutcome": "STRICT",
                "governedStage": prova["id"],
                "continuation": "NONE",
            },
        }
    ]
    edital = publish_original(
        api_client,
        {**manager_headers, "HTTP_IDEMPOTENCY_KEY": f"faixa-com-retirada-{seed:04d}"},
        {
            "institutionalCode": f"PS-2026-{seed}",
            "title": f"Processo {seed}",
            "firstEdital": {"number": str(seed), "year": 2026, "title": f"Edital {seed}"},
        },
        draft=rascunho,
    )
    membros = constituir(
        gestor,
        edital.processo,
        [("maria", Funcao.PRESIDENTE), ("joao", Funcao.MEMBRO)],
        prefixo=f"faixa-{seed}",
    )
    for etapa in (analise["id"], hetero["id"], prova["id"]):
        alocar_em(gestor, edital.processo, membros["joao"], edital, etapa, chave=f"f{seed}-{etapa}")
    bia, maria, ana = inscrever(
        edital,
        3,
        primeiro=1,
        modalidades={1: MODALIDADE_PPI, 2: MODALIDADE_PPI},
        perfil=perfil["id"],
    )
    cenario = {
        "edital": edital,
        "processo": edital.processo,
        "membros": membros,
        "etapa": analise["id"],
    }
    distribuir_para(cenario, gestor, ["joao"], [bia, maria, ana], chave=f"f{seed}-analise")
    for inscricao, nota in ((bia, "95"), (maria, "90"), (ana, "80")):
        concluir_como(cenario, "joao", inscricao, pontuacao=nota)
    _consolidar(cenario, analise["id"], [bia, maria, ana], f"f{seed}-consolidar-analise")
    for lista in (None, MODALIDADE_PPI):
        emitir_ordem(
            actor=gestor,
            processo_id=edital.processo_id,
            edital_id=edital.id,
            perfil_id=perfil["id"],
            marco_id=marco,
            lista_id=lista,
            idempotency_key=f"f{seed}-ordem-{lista}",
            correlation_id="teste",
            confirmacao_do_calculo=assinatura_da_proposta(
                calcular_ordem(
                    edital=edital, perfil_id=perfil["id"], marco_id=marco, lista_id=lista
                )
            ),
        )
        emitir_corte(
            actor=gestor,
            processo_id=edital.processo_id,
            edital_id=edital.id,
            perfil_id=perfil["id"],
            marco_id=marco,
            lista_id=lista,
            idempotency_key=f"f{seed}-corte-{lista}",
            correlation_id="teste",
            confirmacao_do_calculo=assinatura_do_corte(
                calcular_corte(
                    edital=edital, perfil_id=perfil["id"], marco_id=marco, lista_id=lista
                ),
                geracao=(),
            ),
        )
    return {
        **cenario,
        "hetero": hetero["id"],
        "prova": prova["id"],
        "bia": bia,
        "maria": maria,
        "ana": ana,
    }


def _hetero(cenario, gestor, sentido, *, seed):
    na_hetero = {**cenario, "etapa": cenario["hetero"]}
    distribuir_para(na_hetero, gestor, ["joao"], [cenario["maria"]], chave=f"f{seed}-hetero")
    concluir_como(na_hetero, "joao", cenario["maria"], sentido=sentido)
    _consolidar(cenario, cenario["hetero"], [cenario["maria"]], f"f{seed}-consolidar-hetero")


def test_a_retirada_nao_entra_na_etapa_governada_pela_faixa_reservada(
    gestor, api_client, manager_headers
):
    """FR-7013: Maria só estava na faixa da PPI; retirada, a faixa não a faz participar."""
    cenario = _montar(gestor, api_client, manager_headers, seed=1681)
    _hetero(cenario, gestor, "DESFAVORAVEL", seed=1681)

    participantes, _, _ = participacao(edital=cenario["edital"], etapa_id=cenario["prova"])

    assert cenario["bia"].id in participantes
    assert cenario["maria"].id not in participantes
    assert not participa_da_etapa(
        edital=cenario["edital"], etapa_id=cenario["prova"], inscricao_id=cenario["maria"].id
    )
    # Fora pela faixa, e não por eliminação: a pessoa continua no certame pela ampla, onde a faixa
    # não a alcançou. É a mesma situação de Ana, que nunca esteve em faixa nenhuma.
    assert cenario["maria"].id in fora_do_corte(
        cenario["edital"], cenario["prova"], [cenario["maria"].id]
    )


def test_confirmada_ela_entra_pela_faixa_reservada(gestor, api_client, manager_headers):
    """A contraprova: sem retirada, a faixa da PPI a leva à Prova, como sempre levou."""
    cenario = _montar(gestor, api_client, manager_headers, seed=1682)
    _hetero(cenario, gestor, "FAVORAVEL", seed=1682)

    participantes, _, _ = participacao(edital=cenario["edital"], etapa_id=cenario["prova"])

    assert cenario["maria"].id in participantes
    assert cenario["ana"].id not in participantes
