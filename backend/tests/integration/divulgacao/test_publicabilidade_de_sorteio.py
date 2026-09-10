"""Ato de sorteio não se afere recomputando — e o ato computado sai igual (021, FR-069, R-014).

**O defeito que este arquivo fecha.** `estado_do_marco` chamava `calcular_ordem` sempre e comparava
o resultado com `vigente.universo`. Um ato constituído por sorteio não veio de Etapa nenhuma, e a
comparação acusaria divergência a cada mudança de Etapa num marco que não depende delas: a
publicabilidade recusaria toda ordem sorteada como obsoleta, e o certame com sorteio jamais
divulgaria o que sorteou. E `ato_vigente` procurava um ato por `(edital, marco)`, de modo que, com
três listas, ele devolvia uma das três pela ordem de emissão.

**A metade que importa tanto quanto a outra** é a regressão: o caminho de hoje — marco sem lista,
ato computado — precisa sair degrau por degrau igual ao que saía antes. É ela que autoriza a
alteração.
"""

import pytest
from django.utils import timezone

from processo_seletivo.classificacao.application.selectors import ato_vigente, estado_do_marco
from processo_seletivo.classificacao.models import AtoDeOrdenacao, OrigemDaOrdem
from processo_seletivo.divulgacao.domain.publicabilidade import IMPEDIMENTO, aferir
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.comissao import inscrever, rascunho_com_etapas
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.publicacao import publish_original
from tests.fixtures.sorteio import (
    LISTA_PCD,
    LISTA_PPI,
    MARCO,
    marco_com_metodo,
    relacao,
    universo_de_sorteio,
)

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


@pytest.fixture
def cenario(api_client, manager_headers, process_payload):
    rascunho = rascunho_com_etapas()
    marco_com_metodo(rascunho, perfil_id=PROFILE_ID, etapa_id=rascunho["stages"][1]["id"])
    edital = publish_original(api_client, manager_headers, process_payload, draft=rascunho)
    versao = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    return edital, versao, inscricoes_do(edital)


@pytest.fixture
def cenario_computado(api_client, manager_headers, process_payload):
    """O mesmo certame, com um marco que **não** declara método: o caminho de sempre."""
    rascunho = rascunho_com_etapas()
    marco_sem_metodo(rascunho, perfil_id=PROFILE_ID, etapa_id=rascunho["stages"][1]["id"])
    edital = publish_original(api_client, manager_headers, process_payload, draft=rascunho)
    versao = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    return edital, versao, inscricoes_do(edital)


def marco_sem_metodo(rascunho, *, perfil_id, etapa_id):
    """O marco da fixture do sorteio, menos o `drawMethod` — que é a única diferença que importa."""
    marco_com_metodo(rascunho, perfil_id=perfil_id, etapa_id=etapa_id)
    for perfil in rascunho["profiles"]:
        if str(perfil["id"]) == str(perfil_id):
            for marco in perfil["classificationMilestones"]:
                marco.pop("drawMethod", None)
    return rascunho


def inscricoes_do(edital):
    return inscrever(edital, 3, primeiro=801)


def _ato_de_sorteio(edital, versao, relacao_publicada, *, lista_id=None):
    return AtoDeOrdenacao.objects.create(
        edital=edital,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        lista_id=lista_id,
        origem=OrigemDaOrdem.SORTEIO,
        versao=versao,
        universo=universo_de_sorteio(
            edital, versao=versao, perfil_id=PROFILE_ID, relacao=relacao_publicada
        ),
        emitido_por="cpf:presidente",
        emitido_em=timezone.now(),
    )


def test_o_vigente_e_procurado_por_lista_e_nao_por_marco(cenario):
    """Com três listas, "o vigente do marco" não é pergunta com uma resposta."""
    edital, versao, inscricoes = cenario
    atos = {}
    for lista in (None, LISTA_PPI, LISTA_PCD):
        publicada = relacao(
            edital, versao=versao, perfil_id=PROFILE_ID, lista_id=lista, inscricoes=inscricoes
        )
        atos[lista] = _ato_de_sorteio(edital, versao, publicada, lista_id=lista)

    for lista, esperado in atos.items():
        encontrado = ato_vigente(edital=edital, marco_id=MARCO, lista_id=lista)
        assert encontrado is not None and encontrado.id == esperado.id


def test_o_estado_de_um_marco_sorteado_nao_recomputa_por_etapas(cenario):
    edital, versao, inscricoes = cenario
    publicada = relacao(edital, versao=versao, perfil_id=PROFILE_ID, inscricoes=inscricoes)
    ato = _ato_de_sorteio(edital, versao, publicada)

    estado = estado_do_marco(edital=edital, marco_id=MARCO)

    assert estado["origem"] == "SORTEIO"
    assert estado["proposta"] is None, "não há o que recalcular sem semente nova"
    assert estado["recomputavel"] is False
    assert estado["obsoleto"] is False
    assert estado["vigente"].id == ato.id


def test_o_sorteio_e_publicavel_e_nao_e_recusado_como_marco_removido(cenario):
    """O degrau que o defeito atingia primeiro: `recomputavel=False` virava "marco removido"."""
    edital, versao, inscricoes = cenario
    publicada = relacao(edital, versao=versao, perfil_id=PROFILE_ID, inscricoes=inscricoes)
    ato = _ato_de_sorteio(edital, versao, publicada)

    afericao = aferir(edital=edital, marco_id=MARCO, ato=ato)

    assert afericao.nivel != IMPEDIMENTO, afericao.mensagem


def test_relacao_sucedida_torna_a_ordem_sorteada_obsoleta(cenario):
    """A obsolescência do sorteado é a da relação.

    A pergunta continua sendo "o ato reflete o fato que o originou?"; só o fato de origem é outro.
    """
    edital, versao, inscricoes = cenario
    publicada = relacao(edital, versao=versao, perfil_id=PROFILE_ID, inscricoes=inscricoes)
    ato = _ato_de_sorteio(edital, versao, publicada)
    relacao(
        edital,
        versao=versao,
        perfil_id=PROFILE_ID,
        inscricoes=inscricoes,
        anterior=publicada,
        motivo="Resultado de origem sucedido.",
    )

    estado = estado_do_marco(edital=edital, marco_id=MARCO)
    afericao = aferir(edital=edital, marco_id=MARCO, ato=ato)

    assert estado["obsoleto"] is True
    assert [d["tipo"] for d in estado["divergencias"]] == ["relacao_sucedida"]
    assert afericao.nivel == IMPEDIMENTO


def test_a_regressao_do_ato_computado(cenario_computado):
    """**A metade que autoriza a alteração**: marco sem lista e sem sorteio sai como antes.

    O cenário deste teste era o do sorteio, e a premissa estava errada: ele afirmava que um marco
    **de sorteio** sem ato continuava recomputável, com proposta calculada por Etapas. Era a
    descrição do defeito, não da regressão — a tela lia esse estado e oferecia "Emitir ordem" num
    marco cuja ordem só nasce da semente. A regressão de verdade é a de um marco que **não** declara
    método, e é ela que este teste passa a guardar.
    """
    edital, _versao, _inscricoes = cenario_computado

    estado = estado_do_marco(edital=edital, marco_id=MARCO)

    assert estado["recomputavel"] is True
    assert estado["proposta"] is not None
    assert "origem" not in estado
    assert estado["vigente"] is None


def test_o_marco_que_sorteia_nao_recomputa_nem_sem_ato(cenario):
    """**O buraco por onde o certame se travava** (021, D-001, FR-034).

    O detalhe do Edital manda todo marco para a tela de ordenação. Sem ato, o estado dizia
    `recomputavel=True`, a tela oferecia "Emitir ordem", e o cálculo por Etapas de um marco que não
    ordena por Etapas produzia o ato raiz do recorte — depois do quê `constituir_sorteio` recusava,
    corretamente, e o sucessor exigia um sorteio anterior que nunca existiu. O sorteio ficava
    inalcançável pela própria interface.
    """
    edital, _versao, _inscricoes = cenario

    estado = estado_do_marco(edital=edital, marco_id=MARCO)

    assert estado["proposta"] is None, "não há o que calcular sem semente"
    assert estado["recomputavel"] is False, "e nada aqui recompõe uma ordem sorteada"
    assert estado["origem"] == "SORTEIO", "e `aferir` não deve chamá-lo de marco removido"
    assert estado["obsoleto"] is False, "sem ato não há ordem obsoleta — há ordem por vir"


def test_o_ato_computado_num_marco_que_sorteia_e_divergencia_nomeada(cenario):
    """O defeito consumado não fica em silêncio: quem o vê precisa saber o que aconteceu."""
    edital, versao, inscricoes = cenario
    computado = AtoDeOrdenacao.objects.create(
        edital=edital,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        versao=versao,
        universo={
            "editalId": str(edital.id),
            "profileId": PROFILE_ID,
            "milestoneId": MARCO,
            "versionId": str(versao.id),
            "stageResults": [],
        },
        emitido_por="cpf:presidente",
        emitido_em=timezone.now(),
    )

    estado = estado_do_marco(edital=edital, marco_id=MARCO)

    assert estado["obsoleto"] is True
    assert [d["tipo"] for d in estado["divergencias"]] == ["ordem_computada_em_marco_de_sorteio"]
    assert aferir(edital=edital, marco_id=MARCO, ato=computado).nivel == IMPEDIMENTO
    assert len(inscricoes) == 3


def test_ato_de_sorteio_sem_proveniencia_e_divergencia_e_nao_silencio(cenario):
    """**Falhar aberto era o pior lugar para falhar** (FR-069).

    `_divergencias_do_sorteio` devolvia `[]` quando o `universo` não citava relação alguma ou
    citava uma que não existe — exatamente as duas situações em que ninguém consegue conferir a
    ordem. Um ato assim era apresentado como não obsoleto, isto é, como publicável.
    """
    edital, versao, _inscricoes = cenario
    universo = universo_de_sorteio(edital, versao=versao, perfil_id=PROFILE_ID, relacao=None)
    universo.pop("relacaoId")
    sem_relacao = AtoDeOrdenacao.objects.create(
        edital=edital,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        origem=OrigemDaOrdem.SORTEIO,
        versao=versao,
        universo=universo,
        emitido_por="cpf:presidente",
        emitido_em=timezone.now(),
    )

    estado = estado_do_marco(edital=edital, marco_id=MARCO)

    assert estado["vigente"].id == sem_relacao.id
    assert estado["obsoleto"] is True
    assert [d["tipo"] for d in estado["divergencias"]] == ["proveniencia_ausente"]
    assert aferir(edital=edital, marco_id=MARCO, ato=sem_relacao).nivel == IMPEDIMENTO


def test_ato_de_sorteio_citando_relacao_inexistente_e_divergencia(cenario):
    edital, versao, _inscricoes = cenario
    universo = universo_de_sorteio(edital, versao=versao, perfil_id=PROFILE_ID, relacao=None)
    universo["relacaoId"] = "00000000-0000-4000-8000-0000000000ff"
    fantasma = AtoDeOrdenacao.objects.create(
        edital=edital,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        origem=OrigemDaOrdem.SORTEIO,
        versao=versao,
        universo=universo,
        emitido_por="cpf:presidente",
        emitido_em=timezone.now(),
    )

    estado = estado_do_marco(edital=edital, marco_id=MARCO)

    assert estado["vigente"].id == fantasma.id
    assert estado["obsoleto"] is True
    assert [d["tipo"] for d in estado["divergencias"]] == ["proveniencia_inexistente"]
