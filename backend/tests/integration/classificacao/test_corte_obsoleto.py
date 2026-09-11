"""As causas da obsolescência, nomeadas — e o bloqueio que elas produzem (014, US5).

O corte obsoleto **continua definindo quem está dentro** (FR-217), e é justamente por isso que o
trabalho novo para: seguir construindo sobre uma faixa que o sistema já sabe estar para trás produz
trabalho que a sucessão invalida.
"""

import pytest

from processo_seletivo.classificacao.application.calculo import calcular_ordem
from processo_seletivo.classificacao.application.corte import calcular_corte, estado_do_corte
from processo_seletivo.classificacao.application.emissao import assinatura_da_proposta, emitir_ordem
from processo_seletivo.classificacao.models import Corte, ItemDoCorte
from processo_seletivo.resultados.application.prontidao import impedimento_do_corte, participacao
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.corte import ENTREVISTA, MARCO, emitir
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.publicacao import retify

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

CAMINHO_DA_REGRA = f"/profiles/id={PROFILE_ID}/classificationMilestones/id={MARCO}/cutRule"


def causas(edital):
    estado = estado_do_corte(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)
    return estado["obsoleto"], {item["tipo"] for item in estado["causas"]}


def suceder_a_ordem(edital, gestor):
    """Uma ordem nova sobre o mesmo marco: o corte emitido passa a citar a ordem anterior."""
    emitir_ordem(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        idempotency_key="corte-014-ordem-sucessora",
        correlation_id="teste-corte-014",
        confirmacao_do_calculo=assinatura_da_proposta(
            calcular_ordem(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO),
            ato_vigente=Corte.objects.first().ato,
        ),
        motivo="a comissão revisou uma pontuação",
    )


# --- T078 · as causas, nomeadas (FR-215, FR-216) ---------------------------------------------


def test_sem_mudanca_nenhuma_o_corte_nao_esta_obsoleto(cenario, gestor):
    edital, _, _ = cenario
    emitir(edital, gestor)

    obsoleto, tipos = causas(edital)

    assert obsoleto is False
    assert tipos == set()


def test_a_ordem_sucedida_e_nomeada_e_o_corte_vigente_nao_muda(cenario, gestor):
    edital, _, _ = cenario
    emitir(edital, gestor)
    corte = Corte.objects.get()
    antes = (corte.motivo, corte.primeira_posicao, corte.ultima_posicao, corte.universo)

    suceder_a_ordem(edital, gestor)

    obsoleto, tipos = causas(edital)
    depois = Corte.objects.get(pk=corte.pk)
    assert obsoleto is True
    assert "ordem_sucedida" in tipos
    assert (depois.motivo, depois.primeira_posicao, depois.ultima_posicao, depois.universo) == antes


def test_a_regra_retificada_e_nomeada(cenario, gestor, api_client):
    edital, _, _ = cenario
    emitir(edital, gestor)

    retify(
        api_client,
        edital,
        [
            {
                "targetPath": f"{CAMINHO_DA_REGRA}/targetCount",
                "operation": "REPLACE",
                "newValue": 3,
            }
        ],
    )

    obsoleto, tipos = causas(edital)
    assert obsoleto is True
    assert "regra_alterada" in tipos


# --- T079 · a obsolescência não altera o vigente (FR-217, SC-062) ----------------------------


def test_o_corte_obsoleto_continua_definindo_quem_esta_dentro(cenario, gestor):
    edital, _, inscricoes = cenario
    emitir(edital, gestor)
    suceder_a_ordem(edital, gestor)

    participantes, _, _ = participacao(edital=edital, etapa_id=ENTREVISTA)

    assert participantes == {inscricoes[0].id, inscricoes[1].id}


# --- T081a · o bloqueio de trabalho novo (FR-228, UX-030, SC-073) ----------------------------


def test_sem_obsolescencia_nao_ha_bloqueio(cenario, gestor):
    edital, _, _ = cenario
    emitir(edital, gestor)

    assert impedimento_do_corte(edital, ENTREVISTA) is None


def test_o_corte_obsoleto_bloqueia_trabalho_novo_e_diz_o_caminho(cenario, gestor):
    edital, _, _ = cenario
    emitir(edital, gestor)
    suceder_a_ordem(edital, gestor)

    impedimento = impedimento_do_corte(edital, ENTREVISTA)

    assert impedimento is not None
    codigo, frase = impedimento
    assert codigo == "corte-obsoleto"
    assert "geração sucessora" in frase, "a recusa diz o caminho, e não só que está bloqueado"


def test_o_bloqueio_nao_alcanca_etapa_que_nenhum_corte_governa(cenario, gestor):
    edital, pontuada, _ = cenario
    emitir(edital, gestor)
    suceder_a_ordem(edital, gestor)

    assert impedimento_do_corte(edital, pontuada["id"]) is None


# --- T081b · a sucessão alcança a geração inteira (FR-227, SC-072) ---------------------------


def test_sucedida_a_geracao_nenhuma_faixa_dela_autoriza_participante(cenario, gestor):
    """O cenário que o desenho anterior não tinha como satisfazer.

    Sucedendo a **faixa**, a outra metade da geração continuaria vigente e autorizando gente de uma
    ordem já substituída. Aqui a sucessão liga raiz a raiz, e a geração inteira deixa de valer.
    """
    edital, _, inscricoes = cenario
    emitir(edital, gestor)
    anterior = Corte.objects.get()

    emitir(
        edital,
        gestor,
        chave="corte-014-sucessao-geracao",
        motivo="a comissão revisou o alvo",
        geracao=[anterior],
    )

    sucessora = Corte.objects.exclude(pk=anterior.pk).get()
    participantes, _, _ = participacao(edital=edital, etapa_id=ENTREVISTA)
    alcancados = set(
        ItemDoCorte.objects.filter(
            corte=sucessora, consequencia=ItemDoCorte.Consequencia.PROGREDIU
        ).values_list("inscricao_id", flat=True)
    )
    assert participantes == alcancados
    assert anterior.itens.filter(consequencia=ItemDoCorte.Consequencia.PROGREDIU).exists()


# --- FR-198 · não se corta sobre ordem obsoleta -----------------------------------------------


def test_emitir_sobre_ordem_obsoleta_recusa(cenario, gestor, api_client):
    edital, _, _ = cenario
    retify(
        api_client,
        edital,
        [
            {
                "targetPath": f"{CAMINHO_DA_REGRA}/targetCount",
                "operation": "REPLACE",
                "newValue": 3,
            }
        ],
        suffix="b",
    )

    with pytest.raises(DomainError) as erro:
        calcular_corte(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)

    assert erro.value.code == "ato_obsoleto"


# --- T081 · corte obsoleto impede publicar o que dele depende (FR-219, SC-063) ---------------


def test_publicar_com_o_corte_obsoleto_e_impedido_e_a_recusa_diz_o_caminho(cenario, gestor):
    """O que se publicou não se despublica: divulgar uma faixa que a sucessão vai mudar é o erro."""
    from processo_seletivo.divulgacao.domain.publicabilidade import CORTE_OBSOLETO, aferir

    edital, _, _ = cenario
    emitir(edital, gestor)
    suceder_a_ordem(edital, gestor)

    afericao = aferir(
        edital=edital, marco_id=MARCO, ato=Corte.objects.first().ato, natureza="PRELIMINAR"
    )

    assert afericao.codigo in {CORTE_OBSOLETO, "publication_act_superseded"}
    assert afericao.mensagem


def test_sem_obsolescencia_a_publicacao_nao_e_impedida_pelo_corte(cenario, gestor):
    from processo_seletivo.divulgacao.domain.publicabilidade import CORTE_OBSOLETO, aferir

    edital, _, _ = cenario
    emitir(edital, gestor)

    afericao = aferir(
        edital=edital, marco_id=MARCO, ato=Corte.objects.get().ato, natureza="PRELIMINAR"
    )

    assert afericao.codigo != CORTE_OBSOLETO
