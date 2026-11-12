"""A lista em que ninguém concorreu sai junto da publicação do marco (155, US5, T040, FR-6330).

O cenário é o 7/1/2 da `034` com um autodeclarado PPI: a ampla e a PPI têm quem concorra, e a PcD
não. A PcD tem a ordem vazia; a publicação da ampla, pedida pela prévia, a leva junto — na mesma
transação, na mesma natureza, com um registro por ato e nenhuma linha de candidato.
"""

import json

import pytest

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.classificacao.application.selectors import ato_vigente
from processo_seletivo.divulgacao.application.publicar import (
    assinatura_da_previa,
    listas_sem_concorrente_do_marco,
    publicar_resultado,
)
from processo_seletivo.divulgacao.application.selectors import vigente_do_marco
from processo_seletivo.divulgacao.domain.conteudo import compor
from processo_seletivo.divulgacao.models import PublicacaoResultado, SituacaoDivulgada
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.autoridades import AUTORIDADE_DO_RESULTADO
from tests.fixtures.corte import MARCO
from tests.fixtures.divulgacao import ator_publicador
from tests.fixtures.recortes import (
    MODALIDADE_PCD,
    MODALIDADE_PPI,
    emitir_recorte,
    montar_cenario_7_1_2,
)

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

DECLARACAO = "O prazo recursal encerrou-se sem interposição, conforme o Edital."


@pytest.fixture
def marco(gestor, api_client, manager_headers, process_payload):
    edital, _, _ = montar_cenario_7_1_2(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="conjunta-155",
        autodeclarar=False,
        modalidades={0: MODALIDADE_PPI},
    )
    emitir_recorte(edital, gestor, lista_id=MODALIDADE_PPI, chave="conjunta-155-ppi")
    emitir_recorte(edital, gestor, lista_id=MODALIDADE_PCD, chave="conjunta-155-pcd")
    return edital


def _ato(edital, lista_id=None):
    return ato_vigente(edital=edital, marco_id=MARCO, lista_id=lista_id)


def _confirmacao(edital, ato, *, com_acompanhantes=True):
    """A assinatura como a prévia da tela a compõe: com as listas que vão junto."""
    return assinatura_da_previa(
        ato=ato,
        publicacao_anterior=vigente_do_marco(edital=edital, marco_id=MARCO, lista_id=ato.lista_id),
        projecao=compor(ato),
        acompanhantes=listas_sem_concorrente_do_marco(edital=edital, marco_id=MARCO, ato=ato)
        if com_acompanhantes
        else (),
    )


def _publicar(edital, ato, *, natureza="PRELIMINAR", chave="conjunta-155", confirmacao=None):
    return publicar_resultado(
        actor=ator_publicador(),
        processo_id=edital.processo_id,
        edital_id=edital.id,
        marco_id=MARCO,
        ato_id=ato.id,
        natureza=natureza,
        autoridade=str(AUTORIDADE_DO_RESULTADO),
        confirmacao_da_previa=confirmacao or _confirmacao(edital, ato),
        idempotency_key=chave,
        correlation_id="teste-155",
        declaracao_de_encerramento=DECLARACAO if natureza == "DEFINITIVA" else "",
        com_as_listas_sem_concorrente=True,
    )


def test_a_lista_vazia_sai_na_mesma_transacao_com_registro_proprio(marco):
    """Um registro por ato, na mesma natureza, dito «ninguém concorreu», sem linha de candidato;
    a lista com quem concorre não vai junto."""
    publicacao = _publicar(marco, _ato(marco))

    vazia = PublicacaoResultado.objects.get(ato=_ato(marco, MODALIDADE_PCD))
    assert vazia.natureza == publicacao.natureza == "PRELIMINAR"
    assert vazia.publicado_em == publicacao.publicado_em
    assert not SituacaoDivulgada.objects.filter(publicacao=vazia).exists()
    conteudo = json.loads(bytes(vazia.conteudo_publico).decode())
    assert conteudo["posicoes"] == [] and conteudo["ninguemConcorreu"] is True
    assert "ninguemConcorreu" not in json.loads(bytes(publicacao.conteudo_publico).decode())
    assert not PublicacaoResultado.objects.filter(ato=_ato(marco, MODALIDADE_PPI)).exists()
    trilha = RegistroAuditoria.objects.get(operation="RESULTADO_PUBLICAR", aggregate_id=vazia.id)
    assert f"junto da publicação {publicacao.id}" in trilha.reason


def test_a_assinatura_cobre_as_listas_que_vao_junto(marco):
    """A confirmação composta sem as acompanhantes não confere: a pessoa não leu o que iria."""
    ato = _ato(marco)
    with pytest.raises(DomainError) as recusa:
        _publicar(marco, ato, confirmacao=_confirmacao(marco, ato, com_acompanhantes=False))
    assert recusa.value.code == "publication_preview_stale"
    assert not PublicacaoResultado.objects.filter(edital=marco).exists()


def test_a_ordem_vazia_emitida_depois_da_previa_e_leitura_nova(
    gestor, api_client, manager_headers, process_payload
):
    edital, _, _ = montar_cenario_7_1_2(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="conjunta-155-depois",
        autodeclarar=False,
    )
    ato = _ato(edital)
    confirmacao = _confirmacao(edital, ato)
    emitir_recorte(edital, gestor, lista_id=MODALIDADE_PCD, chave="conjunta-155-depois-pcd")

    with pytest.raises(DomainError) as recusa:
        _publicar(edital, ato, confirmacao=confirmacao)
    assert recusa.value.code == "publication_preview_stale"


def test_a_natureza_e_a_mesma_e_nada_se_republica(marco):
    """A definitiva leva a lista vazia como definitiva, sucedendo a preliminar dela; a repetição do
    envio não publica nada de novo."""
    _publicar(marco, _ato(marco), chave="conjunta-155-p")
    confirmacao = _confirmacao(marco, _ato(marco))
    for _ in range(2):
        _publicar(
            marco,
            _ato(marco),
            natureza="DEFINITIVA",
            chave="conjunta-155-d",
            confirmacao=confirmacao,
        )

    vazias = PublicacaoResultado.objects.filter(ato=_ato(marco, MODALIDADE_PCD)).order_by(
        "publicado_em"
    )
    assert [p.natureza for p in vazias] == ["PRELIMINAR", "DEFINITIVA"]
    assert vazias[1].publicacao_anterior_id == vazias[0].id
    assert PublicacaoResultado.objects.filter(edital=marco).count() == 4


def test_a_lista_ja_publicada_nesta_natureza_nao_vai_de_novo(marco):
    """A ordem vazia publicada à parte, antes, não é republicada pela do marco."""
    vazia = _ato(marco, MODALIDADE_PCD)
    _publicar(marco, vazia, chave="conjunta-155-a-parte")
    assert listas_sem_concorrente_do_marco(edital=marco, marco_id=MARCO, ato=_ato(marco))

    _publicar(marco, _ato(marco), chave="conjunta-155-ampla")

    assert PublicacaoResultado.objects.filter(ato=vazia).count() == 1


def test_sem_o_pedido_a_publicacao_e_a_de_antes(marco):
    """O gesto do marco da `049` publica cada lista na sua conferência e não pede a conjunta."""
    ato = _ato(marco)
    publicar_resultado(
        actor=ator_publicador(),
        processo_id=marco.processo_id,
        edital_id=marco.id,
        marco_id=MARCO,
        ato_id=ato.id,
        natureza="PRELIMINAR",
        autoridade=str(AUTORIDADE_DO_RESULTADO),
        confirmacao_da_previa=_confirmacao(marco, ato, com_acompanhantes=False),
        idempotency_key="conjunta-155-sem",
        correlation_id="teste-155",
    )
    assert PublicacaoResultado.objects.filter(edital=marco).count() == 1


def test_a_pagina_publica_diz_que_ninguem_concorreu(marco, client):
    """FR-6330: a página da lista vazia diz «ninguém concorreu», sem tabela de candidatos."""
    from django.urls import reverse

    _publicar(marco, _ato(marco))
    vazia = PublicacaoResultado.objects.get(ato=_ato(marco, MODALIDADE_PCD))

    pagina = client.get(reverse("portal:resultado", args=[vazia.id])).content.decode()

    assert "Ninguém concorreu por esta lista." in pagina
    assert "<table" not in pagina


def test_a_previa_lista_a_lista_que_vai_junto_e_a_tela_publica_as_duas(marco, client, settings):
    """A prévia da tela diz «e a lista PcD: ninguém concorreu», e a confirmação dela publica as
    duas numa vez."""
    import re

    from django.urls import reverse

    from tests.interface.conftest import identificar

    settings.INTERFACE_SELETOR_IDENTIDADE = True
    identificar(client, "paula.publicadora", ["publicador"])
    ato = _ato(marco)
    previa = client.get(reverse("interface:previa-de-publicacao", args=[marco.id, MARCO, ato.id]))
    pagina = previa.content.decode()
    assert "Também nesta publicação" in pagina
    assert "ninguém concorreu — sai junto desta publicação" in pagina
    campos = dict(
        re.findall(r'name="(confirmacao_da_previa|chave_idempotencia)" value="([^"]*)"', pagina)
    )
    resposta = client.post(
        reverse("interface:publicar-resultado", args=[marco.id, MARCO, ato.id]),
        {
            "natureza": "PRELIMINAR",
            "autoridade": str(AUTORIDADE_DO_RESULTADO),
            **campos,
        },
    )
    assert resposta.status_code == 302, resposta.content.decode()[:2000]
    assert PublicacaoResultado.objects.filter(ato=_ato(marco, MODALIDADE_PCD)).exists()


def _celula_do_resultado(edital, lista_id):
    from processo_seletivo.interface import andamento as a

    leitura = a.do_edital(edital, ator_publicador())
    [perfil] = leitura.perfis
    ponto = next(p for p in perfil.pontos if p.tipo == a.RESULTADO)
    return ponto.celula(lista_id)


def test_no_andamento_a_lista_vazia_sai_junto_e_nao_e_providencia_propria(marco):
    """R-006: a célula do resultado da lista vazia diz que ela sai junto da publicação do marco;
    publicadas as outras como definitivas, nada mais a levaria, e ela volta a ser providência."""
    from processo_seletivo.interface import andamento as a

    celula = _celula_do_resultado(marco, MODALIDADE_PCD)
    assert celula.situacao == a.DEPOIS and celula.razao == a.SAI_JUNTO_DO_MARCO
    assert not celula.em_aberto
    assert _celula_do_resultado(marco, MODALIDADE_PPI).situacao == a.PENDENTE

    for lista, chave in ((None, "ampla"), (MODALIDADE_PPI, "ppi")):
        ato = _ato(marco, lista)
        publicar_resultado(
            actor=ator_publicador(),
            processo_id=marco.processo_id,
            edital_id=marco.id,
            marco_id=MARCO,
            ato_id=ato.id,
            natureza="DEFINITIVA",
            autoridade=str(AUTORIDADE_DO_RESULTADO),
            confirmacao_da_previa=_confirmacao(marco, ato, com_acompanhantes=False),
            idempotency_key=f"conjunta-155-andamento-{chave}",
            correlation_id="teste-155",
            declaracao_de_encerramento=DECLARACAO,
        )

    assert _celula_do_resultado(marco, MODALIDADE_PCD).situacao == a.PENDENTE
