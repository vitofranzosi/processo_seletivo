"""O efeito do corte sobre a Etapa governada — e a não regressão de quem não corta (014).

É o que a feature existe para entregar: a Etapa seguinte deixa de receber todos os habilitados e
passa a receber a faixa. E é aqui que a assimetria com a `013` precisa valer: o corte **soma** às
regras de progressão que já existem, e não as revoga.
"""

from uuid import uuid4

import pytest

from processo_seletivo.classificacao.application.calculo import calcular_ordem
from processo_seletivo.classificacao.application.corte import calcular_corte
from processo_seletivo.classificacao.application.emissao import assinatura_da_proposta, emitir_ordem
from processo_seletivo.classificacao.application.emissao_do_corte import (
    assinatura_da_proposta as assinatura_do_corte,
)
from processo_seletivo.classificacao.application.emissao_do_corte import (
    emitir_corte,
)
from processo_seletivo.comissoes.domain.funcoes import Funcao
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.resultados.application.consolidacao import consolidar
from processo_seletivo.resultados.application.prontidao import (
    contagens,
    fora_do_corte,
    panorama_da_etapa,
    participa_da_etapa,
    participacao,
    restringir_a_participantes,
)
from tests.fixtures.comissao import alocar_em, constituir, inscrever, rascunho_com_etapas
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.mesa import concluir_como, distribuir_para
from tests.fixtures.publicacao import publish_original

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

MARCO = "00000000-0000-4000-8000-000000000471"
ENTREVISTA = "00000000-0000-4000-8000-000000000472"


def rascunho(*, com_regra=True, alvo=2):
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
    marco = {
        "id": MARCO,
        "code": "FINAL",
        "name": "Classificação por títulos",
        "stages": [pontuada["id"]],
        "operation": "SOMA_PONDERADA",
        "normalization": "NENHUMA",
        "rounding": {"scale": 2, "mode": "MEIO_PARA_CIMA"},
        "tiebreakers": [],
    }
    if com_regra:
        marco["cutRule"] = {
            "targetKind": "FIXED",
            "targetCount": alvo,
            "surplusCount": 0,
            "tieOutcome": "STRICT",
            "governedStage": ENTREVISTA,
            "continuation": "NONE",
        }
    base["profiles"][0]["classificationMilestones"] = [marco]
    return base, pontuada


def montar(gestor, api_client, manager_headers, process_payload, *, com_regra=True, prefixo="p"):
    """Quatro inscritos, três pontuados e a ordem emitida — sem o corte ainda."""
    draft, pontuada = rascunho(com_regra=com_regra)
    edital = publish_original(api_client, manager_headers, process_payload, draft=draft)
    membros = constituir(
        gestor,
        edital.processo,
        [("maria", Funcao.PRESIDENTE), ("joao", Funcao.MEMBRO)],
        prefixo=f"prog-014-{prefixo}",
    )
    alocar_em(gestor, edital.processo, membros["joao"], edital, pontuada["id"])
    contexto = {
        "edital": edital,
        "processo": edital.processo,
        "membros": membros,
        "etapa": pontuada["id"],
    }
    inscricoes = inscrever(edital, 4, primeiro=801)
    distribuir_para(contexto, gestor, ["joao"], inscricoes[:3], chave=f"prog-014-{prefixo}-lote")
    for indice, pontuacao in enumerate(["90.0000", "80.0000", "70.0000"]):
        concluir_como(contexto, "joao", inscricoes[indice], pontuacao=pontuacao)
    consolidar(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        etapa_id=pontuada["id"],
        inscricao_ids=[item.id for item in inscricoes[:3]],
        idempotency_key=f"prog-014-{prefixo}-consolidar",
        correlation_id="teste-prog-014",
    )
    emitir_ordem(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        idempotency_key=f"prog-014-{prefixo}-ordem",
        correlation_id="teste-prog-014",
        confirmacao_do_calculo=assinatura_da_proposta(
            calcular_ordem(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)
        ),
    )
    return edital, inscricoes


def cortar(edital, gestor, *, chave="prog-014-corte"):
    proposta = calcular_corte(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)
    return emitir_corte(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        idempotency_key=chave,
        correlation_id="teste-prog-014",
        confirmacao_do_calculo=assinatura_do_corte(proposta),
    )


@pytest.fixture
def cortado(gestor, api_client, manager_headers, process_payload):
    edital, inscricoes = montar(gestor, api_client, manager_headers, process_payload)
    cortar(edital, gestor)
    return edital, inscricoes


def participantes(edital):
    participa, _, _ = participacao(edital=edital, etapa_id=ENTREVISTA)
    return participa


# --- T059 · participa quem a faixa alcançou (FR-208, SC-056) ---------------------------------


def test_a_etapa_governada_recebe_apenas_quem_progrediu(cortado):
    edital, inscricoes = cortado

    assert participantes(edital) == {inscricoes[0].id, inscricoes[1].id}


def test_a_contagem_confere_com_o_alvo_apurado(cortado):
    edital, _ = cortado

    assert len(participantes(edital)) == 2


def test_a_pergunta_individual_da_a_mesma_resposta(cortado):
    edital, inscricoes = cortado

    dentro = participa_da_etapa(edital=edital, etapa_id=ENTREVISTA, inscricao_id=inscricoes[0].id)
    fora = participa_da_etapa(edital=edital, etapa_id=ENTREVISTA, inscricao_id=inscricoes[2].id)

    assert dentro is True
    assert fora is False


def test_a_restricao_em_conjunto_da_a_mesma_resposta(cortado):
    edital, inscricoes = cortado

    consulta = restringir_a_participantes(
        Inscricao.objects.filter(edital=edital), edital=edital, etapa_id=ENTREVISTA, prefixo=""
    )

    assert {item.id for item in consulta} == {inscricoes[0].id, inscricoes[1].id}


# --- T061 · quem ficou fora é nomeado, e não some (FR-210, UX-026) ---------------------------


def test_quem_ficou_fora_e_nomeado_como_fora_do_corte(cortado):
    edital, inscricoes = cortado
    submetidas = {item.id for item in inscricoes}

    assert fora_do_corte(edital, ENTREVISTA, submetidas) == {
        inscricoes[2].id,
        inscricoes[3].id,
    }


# --- T064 · a não regressão (FR-214, SC-069) -------------------------------------------------


def test_marco_sem_regra_conduz_a_etapa_exatamente_como_antes(
    gestor, api_client, manager_headers, process_payload
):
    edital, inscricoes = montar(
        gestor, api_client, manager_headers, process_payload, com_regra=False, prefixo="sem-regra"
    )

    assert participantes(edital) == {inscricoes[0].id, inscricoes[1].id, inscricoes[2].id}
    assert fora_do_corte(edital, ENTREVISTA, {item.id for item in inscricoes}) == set()


def test_marco_com_regra_e_sem_corte_emitido_conduz_a_etapa_como_antes(
    gestor, api_client, manager_headers, process_payload
):
    """A condição é dormente enquanto ninguém emite: é o gate que impede a feature de esvaziar."""
    edital, inscricoes = montar(
        gestor, api_client, manager_headers, process_payload, prefixo="sem-corte"
    )

    assert participantes(edital) == {inscricoes[0].id, inscricoes[1].id, inscricoes[2].id}


# --- T060 · o corte soma, e não revoga (FR-209) ----------------------------------------------


def test_a_etapa_anterior_continua_valendo_junto_com_o_corte(cortado):
    """Quem não foi habilitado na Etapa anterior não entra, ainda que dentro da faixa.

    O quarto inscrito não tem Resultado na Etapa pontuada e nunca teve posição na ordem: ele está
    fora por **duas** razões independentes, e é isso que a assimetria da `013` preserva.
    """
    edital, inscricoes = cortado

    assert inscricoes[3].id not in participantes(edital)


# --- o recorte é (Perfil, marco, lista), e não só o Perfil (FR-232, SC-075) -------------------


def test_o_corte_de_uma_lista_nao_desperta_o_gate_para_as_outras(
    gestor, api_client, manager_headers, process_payload
):
    """Um marco de cotas tem três atos raiz e três cortes, emitidos em instantes diferentes.

    **O cenário começa sem corte geral**, e é isso que o torna uma prova: um corte sem lista governa
    o Perfil inteiro e mascararia exatamente a dormência que se quer verificar. Aqui existe **só** o
    corte da PPI — e quem declarou PcD tem de continuar participando, porque corte nenhum a cortou.

    O corte por lista é **construído aqui**, e não emitido: ordenar por lista exige a máquina de
    sorteio da `021`, e o que este teste verifica é a condição do gate, que é da `014`.
    """
    from processo_seletivo.classificacao.application.selectors import ato_vigente
    from processo_seletivo.classificacao.models import Corte, ItemDoCorte
    from processo_seletivo.publicacoes.application.selectors import effective_version

    edital, inscricoes = montar(
        gestor, api_client, manager_headers, process_payload, prefixo="por-lista"
    )
    ppi, pcd = uuid4(), uuid4()
    Inscricao.objects.filter(pk=inscricoes[0].id).update(modality_id=ppi)
    Inscricao.objects.filter(pk=inscricoes[1].id).update(modality_id=pcd)
    ato = ato_vigente(edital=edital, marco_id=MARCO)
    da_ppi = Corte.objects.create(
        edital=edital,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        lista_id=ppi,
        ato=ato,
        versao=effective_version(edital_id=edital.id),
        etapa_governada_id=ENTREVISTA,
        universo={},
        primeira_posicao=1,
        ultima_posicao=1,
        emitido_por="maria",
        emitido_em=ato.emitido_em,
    )
    ItemDoCorte.objects.create(
        corte=da_ppi,
        inscricao=inscricoes[0],
        posicao=1,
        consequencia=ItemDoCorte.Consequencia.PROGREDIU,
    )

    participantes, _, _ = participacao(edital=edital, etapa_id=ENTREVISTA)

    assert inscricoes[0].id in participantes, "alcançada pelo corte da própria lista"
    assert inscricoes[1].id in participantes, (
        "a lista PcD não tem corte: o recorte dela continua dormente"
    )
    assert inscricoes[2].id in participantes, "sem Modalidade declarada, e sem corte sem lista"


def test_a_particao_da_etapa_governada_fecha_com_o_total_submetido(cortado):
    """Os que a faixa não alcançou têm contagem própria, e a soma da tela fecha (E2E14-007).

    O estado existia no panorama e nenhuma tela o contava: a Mesa da Etapa governada mostrava o
    total submetido de um lado e só os participantes do outro, sem número algum que explicasse a
    diferença. Quem conduz a Etapa soma o painel e tem de chegar ao total — é isso que torna a
    partição verificável, e é isso que a `UX-026` chama de não sumir da tela.
    """
    edital, inscricoes = cortado
    etapa = next(
        item
        for item in edital.versoes_consolidadas.latest("materialized_at").content["stages"]
        if str(item["id"]) == ENTREVISTA
    )

    resumo = contagens(panorama_da_etapa(edital=edital, etapa=etapa))

    # Um só: das duas que a faixa não alcançou, a que nunca foi avaliada na Etapa anterior
    # continua **aguardando** aquela Etapa, e cada inscrição ocupa um estado só.
    assert resumo["fora_do_corte"] == 1
    soma = (
        resumo["participantes"]
        + resumo["eliminadas_antes"]
        + resumo["aguardando_anterior"]
        + resumo["fora_do_corte"]
    )
    assert soma == resumo["total"] == len(inscricoes)


def test_a_recusa_de_distribuir_quem_ficou_fora_diz_o_corte_e_nao_a_eliminacao(cortado, gestor):
    """A frase era anterior à feature e passou a mentir (E2E14-008).

    Quem a faixa não alcançou não foi eliminado e não aguarda Etapa alguma: foi considerado, tem
    posição na ordem e a norma publicada o deixou de fora. Dizer o contrário manda quem conduz o
    certame procurar uma eliminação que não existe — e é a diferença que o candidato lê como "não
    fui chamado" em vez de "não sei por quê" (FR-210, UX-025).
    """
    from processo_seletivo.resultados.application.prontidao import motivo_de_nao_participar

    edital, inscricoes = cortado

    recusa = motivo_de_nao_participar(edital, ENTREVISTA, [inscricoes[2].id])

    assert "fora do corte" in recusa
    assert "eliminadas" not in recusa
