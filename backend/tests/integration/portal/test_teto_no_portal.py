"""O teto de inscrições por candidato, dito e antecipado pelo portal (015, FR-063 a FR-066; RC-12).

O envio já recusava a inscrição além do teto (`test_teto_por_candidato.py`). O que faltava era a
tela: o portal não dizia o teto em lugar nenhum, e continuava oferecendo "Inscrever-se" em outra
vaga depois de ele atingido. A pessoa abria o rascunho, preenchia, revisava, e só no envio
descobria a norma.

Os testes afirmam as duas pontas: a frase aparece onde se escolhe a vaga e onde se envia, e a tela
deixa de oferecer o que o comando vai recusar — sem apagar nem mudar o estado de rascunho nenhum.
"""

import pytest
from django.urls import reverse

from processo_seletivo.inscricoes.application.rascunho import (
    abrir_inscricao,
    anexar_documento,
    gravar_dados,
)
from processo_seletivo.inscricoes.application.submissao import enviar_inscricao
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.candidato import (
    MARIA,
    MODALIDADE_AC,
    PERFIL_DOCENTE,
    PERFIL_TECNICO,
    identificar,
    pdf,
)
from tests.fixtures.publicacao import retify
from tests.fixtures.selecao import DOCUMENTO_DE_TODOS, DOCUMENTO_DO_PERFIL

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

FRASE = "Cada candidato poderá ter apenas 1 inscrição enviada neste Edital."


def _com_teto(api_client, edital, teto, *, suffix="teto"):
    """Por Retificação, que é o caminho real: o conteúdo publicado não se reescreve."""
    retify(
        api_client,
        edital,
        [{"targetPath": "/maxInscricoesPorCandidato", "operation": "REPLACE", "newValue": teto}],
        suffix=suffix,
    )
    return edital


def _pronta(edital, perfil):
    inscricao = abrir_inscricao(identidade=MARIA, edital_id=edital.id, profile_id=perfil)
    inscricao = gravar_dados(
        identidade=MARIA, inscricao=inscricao, dados={"modality_id": MODALIDADE_AC}
    )
    exigidos = [(DOCUMENTO_DE_TODOS, "rg.pdf")]
    if perfil == PERFIL_DOCENTE:
        exigidos.append((DOCUMENTO_DO_PERFIL, "dip.pdf"))
    for requisito, nome in exigidos:
        anexar_documento(
            identidade=MARIA, inscricao=inscricao, requirement_id=requisito, arquivo=pdf(nome)
        )
    inscricao.refresh_from_db()
    return inscricao


def _enviar(inscricao):
    return enviar_inscricao(
        identidade=MARIA,
        inscricao=inscricao,
        declaracoes={"veracidade": True, "ciencia": True},
        idempotency_key=f"teto-{inscricao.id}",
    )


def _pagina(client, edital):
    return client.get(reverse("portal:selecao", args=[edital.id])).content.decode()


def _revisao(client, inscricao):
    return client.get(reverse("portal:revisao", args=[inscricao.id])).content.decode()


def test_sem_teto_o_portal_nao_fala_de_limite(client, selecao, candidatos_registrados):
    """A ausência é *sem limite* (FR-063), e sem limite não há frase a dizer."""
    tecnico = _pronta(selecao, PERFIL_TECNICO)
    _enviar(_pronta(selecao, PERFIL_DOCENTE))
    identificar(client, MARIA)

    pagina = _pagina(client, selecao)
    revisao = _revisao(client, tecnico)

    for corpo in (pagina, revisao):
        assert "Cada candidato poderá" not in corpo
        assert "Limite atingido" not in corpo
    assert "Enviar inscrição" in revisao


def test_a_pagina_da_selecao_diz_o_teto_antes_da_escolha(
    client, api_client, selecao, candidatos_registrados
):
    """Antes de qualquer inscrição, e para quem nem se identificou: é norma publicada."""
    _com_teto(api_client, selecao, 1)

    corpo = _pagina(client, selecao)

    assert FRASE in corpo
    assert corpo.count("Inscrever-se nesta vaga") == 2, "abaixo do teto, toda vaga convida"
    assert "Limite atingido" not in corpo


def test_atingido_o_teto_a_outra_vaga_deixa_de_convidar(
    client, api_client, selecao, candidatos_registrados
):
    _com_teto(api_client, selecao, 1)
    _enviar(_pronta(selecao, PERFIL_DOCENTE))
    identificar(client, MARIA)

    corpo = _pagina(client, selecao)

    assert "✓ Inscrição enviada" in corpo
    assert "Inscrever-se nesta vaga" not in corpo
    assert reverse("portal:inscrever", args=[selecao.id, PERFIL_TECNICO]) not in corpo
    assert "Limite atingido: você já enviou 1 inscrição neste Edital." in corpo


def test_o_rascunho_aberto_continua_e_a_revisao_antecipa_a_recusa(
    client, api_client, selecao, candidatos_registrados
):
    """O rascunho de outra vaga fica como está (FR-064), e a tela não promete o envio."""
    _com_teto(api_client, selecao, 1)
    tecnico = _pronta(selecao, PERFIL_TECNICO)
    _enviar(_pronta(selecao, PERFIL_DOCENTE))
    identificar(client, MARIA)

    pagina = _pagina(client, selecao)
    revisao = _revisao(client, tecnico)

    assert reverse("portal:inscricao", args=[tecnico.id]) in pagina
    assert "Continuar inscrição" in pagina
    assert "e esta não poderá ser enviada" in pagina
    assert "Esta inscrição não pode ser enviada." in revisao
    assert FRASE in revisao
    assert "Enviar inscrição" not in revisao
    assert "Declarações" not in revisao, "não se pede aceite do que não se pode enviar"
    tecnico.refresh_from_db()
    assert tecnico.status == Inscricao.Status.RASCUNHO
    # A tela diz o que o comando faz: é a mesma regra, e não uma segunda.
    with pytest.raises(DomainError) as recusa:
        _enviar(tecnico)
    assert recusa.value.code == "registration_limit_reached"


def test_abaixo_do_teto_a_revisao_diz_a_frase_junto_do_envio(
    client, api_client, selecao, candidatos_registrados
):
    _com_teto(api_client, selecao, 1)
    docente = _pronta(selecao, PERFIL_DOCENTE)
    identificar(client, MARIA)

    corpo = _revisao(client, docente)

    assert "Enviar inscrição" in corpo
    assert FRASE in corpo
    assert "Esta inscrição não pode ser enviada." not in corpo


def test_a_leitura_segue_a_versao_vigente(client, api_client, selecao, candidatos_registrados):
    """Retificação que sobe o teto devolve o convite e o envio (FR-066), como faz no comando."""
    _com_teto(api_client, selecao, 1)
    tecnico = _pronta(selecao, PERFIL_TECNICO)
    _enviar(_pronta(selecao, PERFIL_DOCENTE))
    _com_teto(api_client, selecao, 2, suffix="teto-2")
    identificar(client, MARIA)

    pagina = _pagina(client, selecao)
    revisao = _revisao(client, tecnico)

    assert "Cada candidato poderá ter no máximo 2 inscrições enviadas neste Edital." in pagina
    assert "Limite atingido" not in pagina
    assert "Esta inscrição não pode ser enviada." not in revisao
