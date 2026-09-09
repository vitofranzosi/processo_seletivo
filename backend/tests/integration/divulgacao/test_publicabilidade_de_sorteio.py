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


def test_a_regressao_do_ato_computado(cenario):
    """**A metade que autoriza a alteração**: marco sem lista e ato computado saem como antes."""
    edital, versao, _inscricoes = cenario

    estado = estado_do_marco(edital=edital, marco_id=MARCO)

    # Sem ato nenhum, o marco continua recomputável e a proposta continua sendo calculada — o
    # despacho por origem só existe quando há ato de sorteio vigente.
    assert estado["recomputavel"] is True
    assert estado["proposta"] is not None
    assert "origem" not in estado
    assert estado["vigente"] is None


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
