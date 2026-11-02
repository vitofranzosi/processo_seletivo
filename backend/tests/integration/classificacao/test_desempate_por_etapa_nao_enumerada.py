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
from processo_seletivo.classificacao.models import AtoDeOrdenacao, PosicaoNaOrdem
from processo_seletivo.comissoes.models import MembroComissao
from processo_seletivo.interface.supervisao import candidato_a_obsoleto
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from processo_seletivo.resultados.application.consolidacao import consolidar
from processo_seletivo.resultados.models import ResultadoEtapa
from tests.fixtures.comissao import alocar_em
from tests.fixtures.corte import ENTREVISTA, MARCO, montar_cenario_do_corte, rascunho, regra
from tests.fixtures.corte import emitir as emitir_corte
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.mesa import concluir_como, distribuir_para
from tests.fixtures.recursos import deferir_corrigindo

pytestmark = pytest.mark.django_db(transaction=True)

CRITERIO = "00000000-0000-4000-8000-000000001101"


def rascunho_com_desempate_pela_entrevista(cut=None):
    """O marco enumera só a Etapa pontuada, e desempata pela nota da Entrevista."""
    base, pontuada = rascunho(cut=cut)
    base["profiles"][0]["classificationMilestones"][0]["tiebreakers"] = [
        {
            "id": CRITERIO,
            "order": 1,
            "type": "MAIOR_PONTUACAO_NA_ETAPA",
            "parameters": {"stageId": ENTREVISTA},
            "whenMissing": "ULTIMO_NO_CRITERIO",
        }
    ]
    return base, pontuada


@pytest.fixture
def montar(gestor, api_client, manager_headers, process_payload):
    """Prova com `pontuacoes`; Entrevista com `entrevista[i]` para a inscrição `i`, consolidada.

    Sem Etapa governada: a Entrevista recebe todos os habilitados, e o cenário não depende de emitir
    o corte para que os empatados cheguem a ela. A Entrevista do rascunho do 14/2026 é eliminatória
    com mínima 60 — uma nota abaixo dela é como o produto elimina.
    """

    def _montar(prefixo, pontuacoes, entrevista):
        edital, _pontuada, inscricoes = montar_cenario_do_corte(
            gestor,
            api_client,
            manager_headers,
            process_payload,
            cut=regra(governedStage="NONE"),
            prefixo=prefixo,
            pontuacoes=pontuacoes,
            draft_factory=rascunho_com_desempate_pela_entrevista,
            emitir_a_ordem=False,
        )
        avaliados = [inscricoes[indice] for indice in sorted(entrevista)]
        if avaliados:
            joao = MembroComissao.objects.get(processo=edital.processo, identity_subject="joao")
            alocar_em(gestor, edital.processo, joao, edital, ENTREVISTA)
            contexto = {
                "edital": edital,
                "processo": edital.processo,
                "membros": {"joao": joao},
                "etapa": ENTREVISTA,
            }
            distribuir_para(contexto, gestor, ["joao"], avaliados, chave=f"{prefixo}-entrevista")
            for indice in sorted(entrevista):
                concluir_como(contexto, "joao", inscricoes[indice], pontuacao=entrevista[indice])
            consolidar(
                actor=gestor,
                processo_id=edital.processo_id,
                edital_id=edital.id,
                etapa_id=ENTREVISTA,
                inscricao_ids=[item.id for item in avaliados],
                idempotency_key=f"{prefixo}-consolidar-entrevista",
                correlation_id="teste-114",
            )
        return edital, inscricoes

    return _montar


def _emitir(edital, gestor, chave, *, motivo=""):
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
    )


def _ato_vigente(edital):
    return AtoDeOrdenacao.objects.get(edital=edital, marco_id=MARCO, sucessores__isnull=True)


def _posicoes(proposta):
    return {str(item["inscricao_id"]): item for item in proposta["posicoes"]}


def _sinalizado_pela_supervisao(edital):
    """O filtro barato que a Supervisão e a condução do marco aplicam antes de recalcular."""
    versao = effective_version(edital_id=edital.id)
    perfil = next(p for p in versao.content["profiles"] if str(p["id"]) == str(PROFILE_ID))
    marco = next(m for m in perfil["classificationMilestones"] if str(m["id"]) == MARCO)
    return candidato_a_obsoleto(edital, _ato_vigente(edital), marco, versao)


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

    joao = MembroComissao.objects.get(processo=edital.processo, identity_subject="joao")
    alocar_em(gestor, edital.processo, joao, edital, ENTREVISTA)
    contexto = {
        "edital": edital,
        "processo": edital.processo,
        "membros": {"joao": joao},
        "etapa": ENTREVISTA,
    }
    distribuir_para(contexto, gestor, ["joao"], inscricoes[:1], chave="a11-chega-entrevista")
    concluir_como(contexto, "joao", inscricoes[0], pontuacao="70.0000")
    consolidar(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        etapa_id=ENTREVISTA,
        inscricao_ids=[inscricoes[0].id],
        idempotency_key="a11-chega-consolidar-entrevista",
        correlation_id="teste-114",
    )

    estado = estado_do_marco(edital=edital, marco_id=MARCO)
    assert estado["obsoleto"]
    assert "resultados_alterados" in {item["tipo"] for item in estado["divergencias"]}
    # A Supervisão e a condução do marco só recalculam quem o filtro barato admite: sem a Etapa do
    # desempate nele, as duas diriam "feito" desta ordem obsoleta.
    assert _sinalizado_pela_supervisao(edital)


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

    _emitir(edital, gestor, "a11-recurso-sucessora", motivo="Nota da Entrevista corrigida.")
    sucessora = _ato_vigente(edital)
    posicoes = {
        str(item.inscricao_id): item.posicao
        for item in PosicaoNaOrdem.objects.filter(ato=sucessora)
    }
    assert posicoes[str(primeiro.id)] == 1
    assert posicoes[str(segundo.id)] == 2
    assert not estado_do_marco(edital=edital, marco_id=MARCO)["obsoleto"]
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
