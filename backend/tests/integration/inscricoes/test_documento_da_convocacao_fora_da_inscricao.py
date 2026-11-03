"""O documento pedido na convocação não é pedido na inscrição (115, US7, FR-3568, SC-1084).

O Edital publica um documento obrigatório **na convocação**. A inscrição é enviada sem ele, a lista
exigida não o grava — nem como "não se aplica" —, e o portal não o anuncia nem o pede.
"""

from datetime import timedelta

import pytest
from django.utils import timezone

from processo_seletivo.inscricoes.application.rascunho import (
    abrir_inscricao,
    anexar_documento,
    gravar_dados,
)
from processo_seletivo.inscricoes.application.submissao import enviar_inscricao
from processo_seletivo.inscricoes.models import ItemDaListaExigida
from processo_seletivo.portal.views import _documentos_anunciados, _requisitos_pedidos
from tests.fixtures.candidato import MARIA, MODALIDADE_AC, PERFIL_DOCENTE, pdf
from tests.fixtures.edital import identificador
from tests.fixtures.selecao import (
    DOCUMENTO_DE_TODOS,
    DOCUMENTO_DO_PERFIL,
    publicar_selecao,
    rascunho_aberto_com_documentos,
)

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

DOCUMENTO_NA_CONVOCACAO = identificador(415, 0)


@pytest.fixture
def selecao_com_documento_na_convocacao(
    raiz_de_arquivos, api_client, manager_headers, process_payload
):
    rascunho = rascunho_aberto_com_documentos(timezone.now() - timedelta(seconds=1))
    rascunho["documentRequirements"].append(
        {
            "id": DOCUMENTO_NA_CONVOCACAO,
            "key": "certidao",
            "name": "Certidão de nascimento ou casamento",
            "required": True,
            "order": 4,
            "moment": "AT_CALL",
        }
    )
    return publicar_selecao(api_client, manager_headers, process_payload, rascunho=rascunho)


def test_a_inscricao_e_enviada_sem_o_documento_da_convocacao(
    selecao_com_documento_na_convocacao, candidatos_registrados
):
    edital = selecao_com_documento_na_convocacao
    inscricao = abrir_inscricao(identidade=MARIA, edital_id=edital.id, profile_id=PERFIL_DOCENTE)
    inscricao = gravar_dados(
        identidade=MARIA,
        inscricao=inscricao,
        dados={
            "nome": MARIA.nome,
            "cpf": MARIA.cpf,
            "email": MARIA.email,
            "modality_id": MODALIDADE_AC,
        },
    )
    for requisito in (DOCUMENTO_DE_TODOS, DOCUMENTO_DO_PERFIL):
        anexar_documento(
            identidade=MARIA, inscricao=inscricao, requirement_id=requisito, arquivo=pdf()
        )
    inscricao.refresh_from_db()

    enviada = enviar_inscricao(
        identidade=MARIA,
        inscricao=inscricao,
        declaracoes={"veracidade": True, "ciencia": True},
        idempotency_key="envio-115",
    )

    gravados = set(
        str(r)
        for r in ItemDaListaExigida.objects.filter(inscricao=enviada).values_list(
            "requisito_id", flat=True
        )
    )
    assert DOCUMENTO_NA_CONVOCACAO not in gravados
    assert DOCUMENTO_DE_TODOS in gravados
    conteudo = enviada.versao_aceita.content
    pedidos = [str(item["id"]) for item, _ in _requisitos_pedidos(conteudo, enviada)]
    assert DOCUMENTO_NA_CONVOCACAO not in pedidos


def test_o_documento_da_convocacao_nao_aceita_arquivo_na_inscricao(
    selecao_com_documento_na_convocacao, candidatos_registrados
):
    from processo_seletivo.shared.api.problems import DomainError

    edital = selecao_com_documento_na_convocacao
    inscricao = abrir_inscricao(identidade=MARIA, edital_id=edital.id, profile_id=PERFIL_DOCENTE)

    with pytest.raises(DomainError) as recusa:
        anexar_documento(
            identidade=MARIA,
            inscricao=inscricao,
            requirement_id=DOCUMENTO_NA_CONVOCACAO,
            arquivo=pdf(),
        )
    assert recusa.value.status == 404


def test_a_pagina_publica_nao_anuncia_o_documento_da_convocacao_como_da_inscricao(
    selecao_com_documento_na_convocacao,
):
    from processo_seletivo.publicacoes.application import selectors

    conteudo = selectors.selecao_publica(edital_id=selecao_com_documento_na_convocacao.id).content
    perfil = next(p for p in conteudo["profiles"] if p["id"] == PERFIL_DOCENTE)
    anunciados = _documentos_anunciados(conteudo, perfil)

    # Não é pedido na inscrição, e é anunciado à parte, como o que a convocação pedirá (115, e a
    # revisão do #369).
    assert "Certidão de nascimento ou casamento" not in anunciados["sempre"]
    assert "Documento de identificação" in anunciados["sempre"]
    assert anunciados["na_convocacao"] == ["Certidão de nascimento ou casamento"]
