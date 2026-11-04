"""O arquivo que sumiu do disco não derruba as views de documento que já existiam (117, FR-3695).

**Antes da `117` as três respondiam 500, sem evento** (§2.9 do diagnóstico): `copia_verificada`
abria o arquivo antes de qualquer tratamento, e o `FileNotFoundError` subia cru. Quem abria via a
página de falha do servidor, e a trilha não sabia que um documento tinha sumido.

Agora a resposta é a recusa da área, 409, com *"Arquivo indisponível"*, e o evento vai para a trilha
**sem o nome do arquivo** — que é do candidato, e não da trilha.
"""

from pathlib import Path

import pytest
from django.urls import reverse

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.avaliacoes.application.distribuicao import distribuir
from processo_seletivo.inscricoes.models import DocumentoSubmetido
from processo_seletivo.portal.arquivos import ARQUIVO_INDISPONIVEL
from tests.fixtures import documentos_da_convocacao as cenarios
from tests.fixtures.comissao import DOCUMENTO_A, abrir_arquivo, alocar_em, inscrever
from tests.fixtures.corte import MARCO
from tests.fixtures.documentos_da_convocacao import CERTIDAO, apresentar
from tests.fixtures.edital import identificador
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.integration]


def _apagar(arquivo):
    Path(arquivo.path).unlink()


def _confere_a_recusa(resposta):
    assert resposta.status_code == 409
    assert "Arquivo indisponível" in resposta.content.decode()
    assert ARQUIVO_INDISPONIVEL.split(".")[0] in resposta.content.decode()


def _evento_sem_nome_de_arquivo(nome_original):
    evento = RegistroAuditoria.objects.get(operation="ARQUIVO_INDISPONIVEL")
    assert nome_original not in evento.reason
    assert nome_original not in str(evento.detalhe or "")
    return evento


@pytest.fixture
def documento_na_mesa(
    raiz_de_arquivos,
    gestor,
    processo_com_documentos,
    edital_com_documentos,
    comissao_com_documentos,
    etapa_a1,
):
    membro = comissao_com_documentos["joao"]
    alocar_em(gestor, processo_com_documentos, membro, edital_com_documentos, etapa_a1)
    inscricao = inscrever(edital_com_documentos, 1, documentos=[identificador(DOCUMENTO_A, 0)])[0]
    distribuir(
        actor=gestor,
        processo_id=processo_com_documentos.id,
        edital_id=edital_com_documentos.id,
        etapa_id=etapa_a1,
        membro_ids=[membro.id],
        inscricao_ids=[inscricao.id],
        idempotency_key="indisponivel-117",
        correlation_id="teste-117",
    )
    return inscricao, DocumentoSubmetido.objects.get(inscricao=inscricao)


@pytest.mark.django_db
def test_a_consulta_da_inscricao_responde_indisponivel_e_registra(
    client, seletor_ligado, documento_na_mesa
):
    inscricao, documento = documento_na_mesa
    _apagar(documento.arquivo)
    identificar(client, "carlos", ["gestor"])

    resposta = abrir_arquivo(
        client,
        reverse("interface:documento-da-inscricao", args=[inscricao.id, documento.requirement_id]),
    )

    _confere_a_recusa(resposta)
    evento = _evento_sem_nome_de_arquivo(documento.nome_original)
    assert evento.aggregate_id == inscricao.id


@pytest.mark.django_db
def test_a_mesa_responde_indisponivel_e_registra_sob_a_atribuicao(
    client, seletor_ligado, edital_com_documentos, etapa_a1, documento_na_mesa
):
    inscricao, documento = documento_na_mesa
    _apagar(documento.arquivo)
    identificar(client, "joao", [])

    resposta = abrir_arquivo(
        client,
        reverse(
            "interface:mesa-documento",
            args=[edital_com_documentos.id, etapa_a1, inscricao.id, documento.requirement_id],
        ),
    )

    _confere_a_recusa(resposta)
    evento = _evento_sem_nome_de_arquivo(documento.nome_original)
    assert evento.aggregate_type == "Atribuicao"


@pytest.mark.django_db(transaction=True)
def test_a_pagina_da_convocacao_responde_indisponivel_e_registra(
    client, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos, settings
):
    settings.INTERFACE_SELETOR_IDENTIDADE = True
    cenario = cenarios.montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        documentos=cenarios.documentos_do_aluno(),
        prefixo="indisponivel-117",
    )
    edital, _, _ = cenario
    pessoa, convocacao = cenarios.convocar_primeira(cenario, gestor)
    feita = apresentar(pessoa, convocacao, CERTIDAO).apresentacao
    _apagar(feita.arquivo)
    identificar(client, "carlos", ["gestor"])

    resposta = abrir_arquivo(
        client,
        reverse(
            "interface:documento-da-convocacao", args=[edital.id, MARCO, convocacao.id, feita.id]
        ),
    )

    _confere_a_recusa(resposta)
    evento = _evento_sem_nome_de_arquivo(feita.nome_original)
    assert evento.aggregate_id == feita.id
