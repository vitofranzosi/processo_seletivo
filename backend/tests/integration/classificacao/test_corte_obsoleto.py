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
from processo_seletivo.resultados.application.consolidacao import consolidar
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
    """A Retificação que alcança a **regra da ordem** — aqui o arredondamento do marco."""
    edital, _, _ = cenario
    retify(
        api_client,
        edital,
        [
            {
                "targetPath": (
                    f"/profiles/id={PROFILE_ID}/classificationMilestones/id={MARCO}/rounding/scale"
                ),
                "operation": "REPLACE",
                "newValue": 4,
            }
        ],
        suffix="b",
    )

    with pytest.raises(DomainError) as erro:
        calcular_corte(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)

    assert erro.value.code == "ato_obsoleto"


def test_retificar_a_regra_de_corte_nao_obsoleta_a_ordem_e_permite_suceder(
    cenario, gestor, api_client
):
    """A `FR-205` prevê sucessão por Retificação da regra **sobre a mesma ordem**.

    A regra de corte mora no mesmo objeto do marco desde o degrau 13, e não é insumo da ordem: o
    corte **lê** a ordem, e não a produz. Enquanto ela entrava no recorte comparado, retificar
    `targetCount` obsoletava o ato de ordenação — e como não se corta sobre ordem obsoleta, a
    sucessão que a spec descreve ficava inalcançável: exigia emitir uma ordem nova que sairia byte a
    byte igual à anterior.
    """
    edital, _, _ = cenario
    emitir(edital, gestor)
    anterior = Corte.objects.get()
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
        suffix="d",
    )

    obsoleto, tipos = causas(edital)
    proposta = calcular_corte(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)

    assert obsoleto is True and "regra_alterada" in tipos, "o **corte** ficou para trás"
    assert proposta["ato"].id == anterior.ato_id, "e a ordem continua sendo a mesma"
    assert proposta["alvo"] == 3, "a sucessora já nasce sob a norma nova"


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


# --- os do terceiro review: a sucessora contra a norma vigente, e o `rowId` --------------------


def test_o_calculo_le_a_norma_vigente_e_nao_a_do_ato(cenario, gestor, api_client):
    """Nascer obsoleta é o defeito que a sucessão existe para não ter (achado do terceiro review).

    Lendo a regra e o quadro de `ato.versao`, a geração sucessora recalculava a norma **antiga** —
    e no alvo derivado a comparação com a versão vigente acusava a mesma divergência que ela deveria
    fechar. A Retificação aqui não alcança o marco de propósito: ela deixa a ordem em dia, que é o
    caso em que o defeito aparecia.
    """
    from processo_seletivo.publicacoes.application.selectors import effective_version

    edital, _, _ = cenario
    emitir(edital, gestor)
    da_ordem = Corte.objects.get().ato.versao_id
    retify(
        api_client,
        edital,
        [{"targetPath": "/title", "operation": "REPLACE", "newValue": "Edital retificado"}],
        suffix="c",
    )

    proposta = calcular_corte(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)

    vigente = effective_version(edital_id=edital.id)
    assert vigente.id != da_ordem, "a Retificação materializou versão nova"
    assert proposta["versao"].id == vigente.id, "o cálculo lê a norma vigente"


def test_a_linha_do_quadro_trocada_por_outra_de_mesma_quantidade_obsoleta(cenario, gestor):
    """O `rowId` foi gravado para isto: a fonte normativa citada mudou, e a quantidade não."""
    from processo_seletivo.classificacao.application.corte import _quadro_alterado

    edital, _, _ = cenario
    emitir(edital, gestor)
    corte = Corte.objects.get()
    corte.universo["target"] = {"count": 40, "source": "VACANCY_TABLE_ROW", "rowId": "linha-antiga"}

    class VersaoFalsa:
        content = {
            "profiles": [
                {
                    "id": str(corte.perfil_id),
                    "vacancyTable": [
                        {"id": "linha-nova", "modalityId": None, "immediateVacancies": 40}
                    ],
                }
            ]
        }

    causas_do_quadro = _quadro_alterado(
        corte, VersaoFalsa(), perfil_id=corte.perfil_id, lista_id=None
    )

    assert [item["tipo"] for item in causas_do_quadro] == ["quadro_alterado"]


# --- T078/T080 · o reingresso no universo do ato, nomeado (FR-216, FR-218) --------------------


def _superar_resultado(edital, inscricao_id, etapa_id):
    """Um Resultado sucessor por recurso deferido, pelo caminho que a `018` publica.

    Nada entra direto: a peça é interposta, admitida e decidida, e é a decisão que funda o
    sucessor — a trigger de coerência da origem recusa qualquer atalho.
    """
    from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
    from processo_seletivo.resultados.models import ResultadoEtapa
    from tests.fixtures.recursos import admitir, decidir, interpor, superar

    superado = ResultadoEtapa.vigentes.get(
        edital=edital, inscricao_id=inscricao_id, etapa_id=etapa_id
    )
    versao = VersaoConsolidada.objects.filter(edital=edital).latest("valid_from")
    recurso = interpor(
        inscricao=superado.inscricao,
        versao=versao,
        resultado=superado,
        protocolo=f"REC-2026-{str(inscricao_id)[:6]}",
    )
    admitir(recurso)
    decisao = decidir(
        recurso,
        protegido=superado,
        consequencia=superado.consequencia,
        forma=superado.forma,
        pontuacao=superado.pontuacao,
        sentido=superado.sentido,
        versao=versao,
    )
    return superar(superado, decisao, pontuacao=superado.pontuacao)


def test_o_reingresso_no_ato_de_ordenacao_e_nomeado_e_nao_vira_divergencia_generica(
    cenario, gestor
):
    """A causa tem nome próprio, e a `018` já pagou o preço de não ter (FR-216, FR-218).

    A divergência genérica escondia **o quê** havia mudado, e quem lia a tela não sabia se a faixa
    ficara para trás por norma nova ou por gente nova no universo. São providências diferentes.
    """
    edital, pontuada, inscricoes = cenario
    emitir(edital, gestor)

    _superar_resultado(edital, inscricoes[0].id, pontuada["id"])

    obsoleto, tipos = causas(edital)
    assert obsoleto is True
    assert tipos == {"participante_reingressou"}, tipos


def test_o_deferimento_na_etapa_governada_nao_obsoleta_o_corte(cenario, gestor):
    """A `FR-230` em código: medir no universo do corte pararia a Etapa para sempre.

    Todo participante considerado está no universo do corte — inclusive quem já está dentro da
    faixa. Se a medida fosse ali, **qualquer** deferimento o obsoletaria, e somado ao bloqueio de
    trabalho novo isso exigiria uma geração sucessora idêntica à anterior. No 77/2026, em que o
    recurso é julgado na própria Etapa que o corte governa, esse seria o caso normal.
    """
    from processo_seletivo.avaliacoes.application.avaliacao import concluir
    from processo_seletivo.avaliacoes.application.distribuicao import distribuir
    from processo_seletivo.comissoes.application.alocacao import alocar
    from processo_seletivo.comissoes.models import MembroComissao
    from tests.conftest import ator_institucional

    edital, _, inscricoes = cenario
    emitir(edital, gestor)
    # O trabalho real da Etapa governada, até o Resultado: é ele que o deferimento vai superar.
    membro = MembroComissao.objects.get(processo=edital.processo, identity_subject="joao")
    alocar(
        actor=gestor,
        processo_id=edital.processo_id,
        membro_id=membro.id,
        edital_id=edital.id,
        etapa_id=ENTREVISTA,
        idempotency_key="corte-014-alocar-entrevista",
        correlation_id="teste-corte-014",
    )
    distribuir(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        etapa_id=ENTREVISTA,
        membro_ids=[membro.id],
        inscricao_ids=[inscricoes[0].id],
        idempotency_key="corte-014-lote-entrevista",
        correlation_id="teste-corte-014",
    )
    concluir(
        ator=ator_institucional("joao"),
        edital=edital,
        etapa_id=ENTREVISTA,
        inscricao_id=inscricoes[0].id,
        pontuacao="88.0000",
        sentido=None,
        parecer="Entrevista realizada.",
        expected_revision=1,
        versao_reconhecida=edital.versoes_consolidadas.latest("materialized_at").id,
        correlation_id="teste-corte-014",
    )
    consolidar(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        etapa_id=ENTREVISTA,
        inscricao_ids=[inscricoes[0].id],
        idempotency_key="corte-014-entrevista",
        correlation_id="teste-corte-014",
    )

    _superar_resultado(edital, inscricoes[0].id, ENTREVISTA)

    obsoleto, tipos = causas(edital)
    assert (obsoleto, tipos) == (False, set())


# --- T082 · a Retificação que **remove** a regra ----------------------------------------------


def test_remover_a_regra_obsoleta_a_faixa_e_devolve_a_etapa_a_todos_os_habilitados(
    cenario, gestor, api_client
):
    """Remover a regra é decisão normativa, e o ato emitido sob ela continua legível.

    A faixa não é apagada — nada é —, mas deixa de governar: sem regra publicada não há corte, e a
    Etapa seguinte volta a receber todos os habilitados, exatamente como em todo Edital anterior a
    esta feature. É a segunda causa de dormência, e ela precisa ser a mesma coisa que a primeira.
    """
    edital, _, inscricoes = cenario
    emitir(edital, gestor)
    assert participacao(edital=edital, etapa_id=ENTREVISTA)[0] == {
        inscricoes[0].id,
        inscricoes[1].id,
    }

    retify(api_client, edital, [{"targetPath": CAMINHO_DA_REGRA, "operation": "REMOVE"}])

    assert Corte.objects.filter(edital=edital).exists(), "o ato emitido permanece"
    obsoleto, tipos = causas(edital)
    assert (obsoleto, tipos) == (True, {"regra_alterada"})
    participantes, _, _ = participacao(edital=edital, etapa_id=ENTREVISTA)
    assert participantes == {inscricoes[0].id, inscricoes[1].id, inscricoes[2].id}
    assert impedimento_do_corte(edital, ENTREVISTA) is None, "sem regra não há bloqueio"
