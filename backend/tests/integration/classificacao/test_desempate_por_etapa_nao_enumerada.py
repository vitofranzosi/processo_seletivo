"""Desempate pela nota de uma Etapa que o marco não enumera (achado A11; spec 114).

O achado é do estudo da configuração da classificação
(`doc/estudo-configuracao-classificacao-2026-11-01/diario-de-construcao.md`, A11), e nasceu da
leitura do código: `calcular_ordem` só buscava os Resultados das Etapas que o marco enumera, e um
critério `MAIOR_PONTUACAO_NA_ETAPA` que apontasse outra Etapa encontrava o valor vazio para todos —
e não separava ninguém, mesmo com as notas lançadas.

O primeiro teste é o do achado, e nasceu marcado `xfail(strict=True)`: afirmava o que o edital diz,
e prendia a evidência do defeito. A `114` o corrigiu no cálculo — decisão do usuário, contra a
alternativa de recusar o critério na validação —, e a marca saiu.

Os demais prendem o que a correção ingênua quebraria: ler os Resultados da Entrevista como se ela
fosse enumerada tiraria da ordem quem foi eliminado nela (FR-3548), e lê-los sem citá-los no
universo deixaria o recurso que corrige a nota sem obsoletar nada (FR-3550). Todos percorrem o
caminho normal — publicar, avaliar, consolidar —, e o recurso é o da jornada (`deferir_corrigindo`).
"""

from decimal import Decimal

import pytest

from processo_seletivo.classificacao.application.calculo import calcular_ordem
from processo_seletivo.classificacao.application.corte import estado_do_corte
from processo_seletivo.classificacao.application.emissao import (
    assinatura_da_proposta,
    emitir_ordem,
)
from processo_seletivo.classificacao.application.reproducao import divergencias_da_reproducao
from processo_seletivo.classificacao.application.selectors import estado_do_marco
from processo_seletivo.classificacao.models import AtoDeOrdenacao, CitacaoDeDecisao, PosicaoNaOrdem
from processo_seletivo.divulgacao.domain.publicabilidade import (
    PROVIDENCIA_PENDENTE,
    REAVALIACAO_PENDENTE,
    RECURSO_PENDENTE,
    aferir,
)
from processo_seletivo.interface.conducao_do_marco import _ordem_obsoleta
from processo_seletivo.interface.supervisao import atos_obsoletos, candidato_a_obsoleto
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from processo_seletivo.recursos.application.selectors import decisoes_a_citar
from processo_seletivo.recursos.models import DecisaoRecurso
from processo_seletivo.resultados.models import ResultadoEtapa
from tests.fixtures.corte import CRITERIO_DA_ENTREVISTA as CRITERIO
from tests.fixtures.corte import (
    ENTREVISTA,
    MARCO,
    entrevistar,
    montar_cenario_do_corte,
    rascunho,
    rascunho_com_desempate,
    regra,
)
from tests.fixtures.corte import emitir as emitir_corte
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.recursos import admitir, decidir, deferir_corrigindo, interpor

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def montar(gestor, api_client, manager_headers, process_payload):
    """Prova com `pontuacoes`; Entrevista com `entrevista[i]` para a inscrição `i`, consolidada.

    Sem Etapa governada: a Entrevista recebe todos os habilitados, e o cenário não depende de emitir
    o corte para que os empatados cheguem a ela. A Entrevista do rascunho do 14/2026 é eliminatória
    com mínima 60 — uma nota abaixo dela é como o produto elimina.

    `desempate=False` monta o mesmo Edital sem o critério: é o controle de que a Entrevista só
    alcança a ordem porque um critério a compara.
    """

    def _montar(prefixo, pontuacoes, entrevista, *, desempate=True):
        edital, _pontuada, inscricoes = montar_cenario_do_corte(
            gestor,
            api_client,
            manager_headers,
            process_payload,
            cut=regra(governedStage="NONE"),
            prefixo=prefixo,
            pontuacoes=pontuacoes,
            draft_factory=rascunho_com_desempate if desempate else rascunho,
            emitir_a_ordem=False,
        )
        if entrevista:
            entrevistar(
                edital,
                gestor,
                [(inscricoes[indice], nota) for indice, nota in sorted(entrevista.items())],
                chave=f"{prefixo}-entrevista",
            )
        return edital, inscricoes

    return _montar


def _emitir(edital, gestor, chave, *, motivo="", decisoes=()):
    return emitir_ordem(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        idempotency_key=chave,
        correlation_id="teste-114",
        confirmacao_do_calculo=assinatura_da_proposta(
            calcular_ordem(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO),
            ato_vigente=AtoDeOrdenacao.objects.filter(
                edital=edital, marco_id=MARCO, sucessores__isnull=True
            ).first(),
        ),
        motivo=motivo,
        decisoes=decisoes,
    )


def _ato_vigente(edital):
    return AtoDeOrdenacao.objects.get(edital=edital, marco_id=MARCO, sucessores__isnull=True)


def _posicoes(proposta):
    return {str(item["inscricao_id"]): item for item in proposta["posicoes"]}


def _marco_vigente(edital):
    versao = effective_version(edital_id=edital.id)
    perfil = next(p for p in versao.content["profiles"] if str(p["id"]) == str(PROFILE_ID))
    return next(m for m in perfil["classificationMilestones"] if str(m["id"]) == MARCO), versao


def _sinalizado_pela_supervisao(edital):
    """O filtro barato que a Supervisão e a condução do marco aplicam antes de recalcular."""
    marco, versao = _marco_vigente(edital)
    return candidato_a_obsoleto(edital, _ato_vigente(edital), marco, versao)


def _obsoleta_nas_tres_telas(edital):
    """`(tela da classificação, condução do marco, Supervisão)` — as três precisam concordar.

    A tela da classificação recalcula sempre (`estado_do_marco`); as outras duas só recalculam o
    que o filtro barato admite. Uma Etapa fora do filtro faria as duas dizerem "feito" de uma ordem
    que a primeira dá por obsoleta.
    """
    marco, versao = _marco_vigente(edital)
    ato = _ato_vigente(edital)
    sinais = list(atos_obsoletos(edital, marco, MARCO, None, "", ato, versao, lambda *_, **__: ""))
    return (
        estado_do_marco(edital=edital, marco_id=MARCO)["obsoleto"],
        _ordem_obsoleta(edital, marco, None, ato, versao),
        bool(sinais),
    )


def _versao(edital):
    return VersaoConsolidada.objects.filter(edital=edital).latest("valid_from")


def _recurso_contra_a_entrevista(edital, inscricao, protocolo):
    """A peça admitida contra o Resultado da Entrevista, ainda sem decisão."""
    peca = interpor(
        inscricao=inscricao,
        versao=_versao(edital),
        resultado=_entrevista(edital, inscricao),
        protocolo=protocolo,
    )
    admitir(peca)
    return peca


def _definitiva(edital, ato=None):
    return aferir(
        edital=edital, marco_id=MARCO, ato=ato or _ato_vigente(edital), natureza="DEFINITIVA"
    )


def _entrevista(edital, inscricao):
    return ResultadoEtapa.vigentes.get(edital=edital, etapa_id=ENTREVISTA, inscricao=inscricao)


def test_a_nota_de_etapa_nao_enumerada_desfaz_o_empate(montar):
    """FR-3546, FR-3547, SC-1073 — o cenário do achado."""
    edital, inscricoes = montar(
        "a11", ("80.0000", "80.0000", "70.0000"), {0: "70.0000", 1: "90.0000"}
    )
    primeiro, segundo, terceiro = inscricoes[:3]

    # A guarda é do preparo, e não do achado: sem os dois Resultados vigentes na Entrevista, a falha
    # abaixo diria nada sobre o cálculo.
    notas = dict(
        ResultadoEtapa.vigentes.filter(edital=edital, etapa_id=ENTREVISTA).values_list(
            "inscricao_id", "pontuacao"
        )
    )
    if notas.get(primeiro.id) != Decimal("70") or notas.get(segundo.id) != Decimal("90"):
        pytest.fail(f"o preparo não produziu as notas da Entrevista: {notas}")

    proposta = calcular_ordem(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)
    posicao = _posicoes(proposta)

    # A ordem de protocolo põe `primeiro` à frente; a Entrevista o põe atrás. A inversão não pode
    # vir de desempate oculto por protocolo.
    assert posicao[str(segundo.id)]["posicao"] == 1
    assert posicao[str(primeiro.id)]["posicao"] == 2
    assert posicao[str(terceiro.id)]["posicao"] == 3
    assert not any(item["empate_residual"] for item in proposta["posicoes"])
    assert posicao[str(segundo.id)]["separado_por"]["id"] == CRITERIO
    # A Entrevista desempata sem entrar na nota final: os dois continuam com os 80 da Prova.
    assert posicao[str(segundo.id)]["pontuacao"] == Decimal("80")
    assert posicao[str(primeiro.id)]["pontuacao"] == Decimal("80")


def test_o_ato_cita_a_nota_que_desempatou_e_se_reproduz(montar, gestor):
    """FR-3549, FR-3552, FR-3554 — o universo e a proveniência dizem o que decidiu a ordem."""
    edital, inscricoes = montar(
        "a11-ato", ("80.0000", "80.0000", "70.0000"), {0: "70.0000", 1: "90.0000"}
    )
    primeiro, segundo = inscricoes[:2]

    _emitir(edital, gestor, "a11-ato-emitir")
    ato = _ato_vigente(edital)

    citados = {item["id"] for item in ato.universo["stageResults"]}
    assert str(_entrevista(edital, primeiro).id) in citados
    assert str(_entrevista(edital, segundo).id) in citados

    gravadas = {str(item.inscricao_id): item for item in PosicaoNaOrdem.objects.filter(ato=ato)}
    valor = {
        chave: next(c["value"] for c in item.desempate if c["criterionId"] == CRITERIO)
        for chave, item in gravadas.items()
    }
    assert Decimal(valor[str(segundo.id)]) == Decimal("90")
    assert Decimal(valor[str(primeiro.id)]) == Decimal("70")
    assert gravadas[str(segundo.id)].pontuacao_combinada == Decimal("80")
    assert divergencias_da_reproducao(ato) == []


def test_eliminado_na_entrevista_continua_classificado_pela_prova(montar, gestor):
    """FR-3548, FR-3552, SC-1074 — a Entrevista contribui com a nota, e não com a consequência."""
    edital, inscricoes = montar(
        "a11-elim", ("80.0000", "75.0000", "70.0000"), {0: "90.0000", 1: "50.0000"}
    )
    eliminado = inscricoes[1]
    if _entrevista(edital, eliminado).consequencia != ResultadoEtapa.Consequencia.ELIMINADA:
        pytest.fail("o preparo não eliminou na Entrevista: 50 deveria ficar abaixo da mínima")

    proposta = calcular_ordem(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)
    posicao = _posicoes(proposta)

    assert str(eliminado.id) not in {str(item["inscricao_id"]) for item in proposta["sem_posicao"]}
    assert posicao[str(eliminado.id)]["posicao"] == 2
    assert posicao[str(eliminado.id)]["consequencia"] == ResultadoEtapa.Consequencia.HABILITADA
    assert posicao[str(eliminado.id)]["motivo"] == ""

    # A reprodução lê o universo, que agora cita a eliminação da Entrevista — e não a reaplica.
    _emitir(edital, gestor, "a11-elim-emitir")
    assert divergencias_da_reproducao(_ato_vigente(edital)) == []


def test_sem_nota_na_entrevista_vale_o_quando_falta_e_a_ordem_sai(montar, gestor):
    """FR-3553 — decisão do usuário (D-004): emite-se, e a ausência é a que o critério declara."""
    edital, inscricoes = montar("a11-ausente", ("80.0000", "80.0000", "70.0000"), {1: "60.0000"})
    primeiro, segundo = inscricoes[:2]

    posicao = _posicoes(calcular_ordem(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO))

    # `ULTIMO_NO_CRITERIO`: quem não tem nota na Entrevista fica atrás de quem tem, neste critério —
    # e a nota de quem tem é baixa de propósito, para que a ordem não venha de "maior nota".
    assert posicao[str(segundo.id)]["posicao"] == 1
    assert posicao[str(primeiro.id)]["posicao"] == 2

    _emitir(edital, gestor, "a11-ausente-emitir")
    assert AtoDeOrdenacao.objects.filter(edital=edital, marco_id=MARCO).count() == 1


def test_a_nota_que_chega_depois_obsoleta_a_ordem(montar, gestor):
    """FR-3550, D-004 — a ordem emitida sem a nota fica para trás quando ela chega."""
    edital, inscricoes = montar("a11-chega", ("80.0000", "80.0000", "70.0000"), {})
    _emitir(edital, gestor, "a11-chega-emitir")
    assert not estado_do_marco(edital=edital, marco_id=MARCO)["obsoleto"]

    assert _obsoleta_nas_tres_telas(edital) == (False, False, False)

    entrevistar(edital, gestor, [(inscricoes[0], "70.0000")], chave="a11-chega-entrevista")

    estado = estado_do_marco(edital=edital, marco_id=MARCO)
    assert estado["obsoleto"]
    assert "resultados_alterados" in {item["tipo"] for item in estado["divergencias"]}
    # A Supervisão e a condução do marco só recalculam quem o filtro barato admite: sem a Etapa do
    # desempate nele, as duas diriam "feito" desta ordem obsoleta.
    assert _sinalizado_pela_supervisao(edital)
    assert _obsoleta_nas_tres_telas(edital) == (True, True, True)


def test_recurso_deferido_na_entrevista_obsoleta_a_ordem_e_a_sucessora_inverte(montar, gestor):
    """FR-3550, FR-3552, SC-1075 — a correção da nota chega à ordem pela obsolescência."""
    edital, inscricoes = montar(
        "a11-recurso", ("80.0000", "80.0000", "70.0000"), {0: "70.0000", 1: "90.0000"}
    )
    primeiro, segundo = inscricoes[:2]
    _emitir(edital, gestor, "a11-recurso-emitir")
    original = _ato_vigente(edital)
    assert not estado_do_marco(edital=edital, marco_id=MARCO)["obsoleto"]

    deferir_corrigindo(
        _entrevista(edital, primeiro),
        versao=VersaoConsolidada.objects.filter(edital=edital).latest("valid_from"),
        pontuacao=Decimal("95.0000"),
        consequencia=ResultadoEtapa.Consequencia.HABILITADA,
    )

    estado = estado_do_marco(edital=edital, marco_id=MARCO)
    assert estado["obsoleto"]
    alterados = [item for item in estado["divergencias"] if item["tipo"] == "resultados_alterados"]
    assert alterados, estado["divergencias"]
    assert _sinalizado_pela_supervisao(edital)
    assert _obsoleta_nas_tres_telas(edital) == (True, True, True)

    _emitir(edital, gestor, "a11-recurso-sucessora", motivo="Nota da Entrevista corrigida.")
    sucessora = _ato_vigente(edital)
    posicoes = {
        str(item.inscricao_id): item.posicao
        for item in PosicaoNaOrdem.objects.filter(ato=sucessora)
    }
    assert posicoes[str(primeiro.id)] == 1
    assert posicoes[str(segundo.id)] == 2
    assert _obsoleta_nas_tres_telas(edital) == (False, False, False)
    # Cada ato se reproduz do que gravou: o original, com a nota antiga, continua íntegro.
    assert divergencias_da_reproducao(original) == []
    assert divergencias_da_reproducao(sucessora) == []


def test_recurso_deferido_na_entrevista_obsoleta_o_corte_que_leu_a_ordem(montar, gestor):
    """Pesquisa R-005 — a nota corrigida na Etapa do desempate alcança o ato que a faixa leu.

    `corte._reingressou` mede pelas Etapas que o `stageResults` do ato cita, e a Entrevista passou a
    estar lá. A regra da `014` — o deferimento que não alcança o ato não obsoleta o corte — continua
    a mesma; o que mudou é que este deferimento alcança, porque move posição.
    """
    edital, inscricoes = montar(
        "a11-corte", ("80.0000", "80.0000", "70.0000"), {0: "70.0000", 1: "90.0000"}
    )
    _emitir(edital, gestor, "a11-corte-ordem")
    emitir_corte(edital, gestor, chave="a11-corte-emitir")
    assert not estado_do_corte(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)["obsoleto"]

    deferir_corrigindo(
        _entrevista(edital, inscricoes[0]),
        versao=VersaoConsolidada.objects.filter(edital=edital).latest("valid_from"),
        pontuacao=Decimal("95.0000"),
        consequencia=ResultadoEtapa.Consequencia.HABILITADA,
    )

    estado = estado_do_corte(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)
    assert estado["obsoleto"]
    assert "participante_reingressou" in {item["tipo"] for item in estado["causas"]}


# --- Os recursos sobre a nota que desempata (114, D-005; FR-3559 a FR-3561) ---------------------
#
# A nota da Entrevista entra na ordem do marco que só soma a Prova. Um recurso contra ela é uma
# disputa **dentro** daquela ordem, e a definitiva não pode sair enquanto ela corre — como já não
# saía com recurso contra a nota da Prova. O controle é o mesmo Edital sem o critério: ali a
# Entrevista não decide nada desta ordem, e a disputa sobre ela não a segura.


def test_recurso_pendente_contra_a_nota_do_desempate_impede_a_definitiva(montar, gestor):
    """FR-3559 — e só a definitiva: o preliminar é o caminho normal enquanto a disputa corre."""
    edital, inscricoes = montar(
        "a11-rec", ("80.0000", "80.0000", "70.0000"), {0: "70.0000", 1: "90.0000"}
    )
    _emitir(edital, gestor, "a11-rec-emitir")
    assert _definitiva(edital).publicavel, "o cenário precisa nascer publicável"

    _recurso_contra_a_entrevista(edital, inscricoes[0], "REC-2026-A11R001")

    assert _definitiva(edital).codigo == RECURSO_PENDENTE
    assert aferir(
        edital=edital, marco_id=MARCO, ato=_ato_vigente(edital), natureza="PRELIMINAR"
    ).publicavel


def test_reavaliacao_determinada_na_entrevista_impede_a_definitiva(montar, gestor):
    """FR-3559 — a nota que desempata vai mudar, e a ordem com ela."""
    edital, inscricoes = montar(
        "a11-reav", ("80.0000", "80.0000", "70.0000"), {0: "70.0000", 1: "90.0000"}
    )
    _emitir(edital, gestor, "a11-reav-emitir")
    peca = _recurso_contra_a_entrevista(edital, inscricoes[0], "REC-2026-A11R002")

    decidir(
        peca,
        especie=DecisaoRecurso.Especie.REAVALIACAO_DETERMINADA,
        protegido=_entrevista(edital, inscricoes[0]),
    )

    assert _definitiva(edital).codigo == REAVALIACAO_PENDENTE


def test_providencia_sobre_a_nota_do_desempate_se_cumpre_pela_ordem_que_a_cita(montar, gestor):
    """FR-3560 — pertinente ao marco, oferecida na emissão, aceita no banco e cumprida pela citação.

    Sem a ampliação da `citacao_coerente`, o ato sucessor que a cita seria recusado no banco, e a
    definitiva deste marco ficaria impedida para sempre por uma providência que nenhum ato dele
    consegue cumprir.
    """
    edital, inscricoes = montar(
        "a11-prov", ("80.0000", "80.0000", "70.0000"), {0: "70.0000", 1: "90.0000"}
    )
    _emitir(edital, gestor, "a11-prov-emitir")
    peca = _recurso_contra_a_entrevista(edital, inscricoes[0], "REC-2026-A11R003")
    decisao = decidir(peca, especie=DecisaoRecurso.Especie.PROVIDENCIA_A_JUSANTE)

    marco, _versao_vigente = _marco_vigente(edital)
    oferecidas = decisoes_a_citar(
        edital=edital, marco_id=MARCO, marco=marco, publicacoes_do_marco=[]
    )
    assert [item.pk for item in oferecidas] == [decisao.pk]
    assert _definitiva(edital).codigo == PROVIDENCIA_PENDENTE

    _emitir(
        edital,
        gestor,
        "a11-prov-sucessora",
        motivo="Providência determinada no recurso contra a nota da Entrevista.",
        decisoes=[decisao.pk],
    )
    citante = _ato_vigente(edital)

    assert CitacaoDeDecisao.objects.filter(ato=citante, decisao=decisao).exists()
    assert _definitiva(edital, ato=citante).publicavel


def test_a_disputa_sobre_etapa_que_a_ordem_nao_le_nao_a_segura(montar, gestor):
    """O controle: sem o critério, a Entrevista não está nesta ordem (FR-3561).

    "Que a ordem lê" é a dependência efetiva, e não "todas as Etapas do Edital": uma disputa sobre
    nota que não muda posição nenhuma não pode parar a definitiva, e a citação da providência que
    ela gerar continua recusada no banco para este marco.
    """
    from django.db.utils import ProgrammingError

    edital, inscricoes = montar(
        "a11-ctrl",
        ("80.0000", "80.0000", "70.0000"),
        {0: "70.0000", 1: "90.0000"},
        desempate=False,
    )
    _emitir(edital, gestor, "a11-ctrl-emitir")
    peca = _recurso_contra_a_entrevista(edital, inscricoes[0], "REC-2026-A11R004")

    assert _definitiva(edital).publicavel

    decisao = decidir(peca, especie=DecisaoRecurso.Especie.PROVIDENCIA_A_JUSANTE)
    marco, _versao_vigente = _marco_vigente(edital)
    oferecidas = decisoes_a_citar(
        edital=edital, marco_id=MARCO, marco=marco, publicacoes_do_marco=[]
    )
    assert oferecidas == []
    with pytest.raises(ProgrammingError, match="pertinent to another milestone"):
        CitacaoDeDecisao.objects.create(ato=_ato_vigente(edital), decisao=decisao)
