"""A definição dos documentos para a formalização, pela condução (117, US1).

O que se prova: vazia por padrão (FR-3653, FR-3660), motivo obrigatório (FR-3655), versões com o
histórico da diferença (FR-3656, FR-3711), os dois avisos (FR-3658), quem grava e quem lê (FR-3654,
FR-3711) e que nada do conteúdo publicado muda (FR-3657).
"""

import pytest
from django.urls import reverse

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.editais.domain.documentos import recorte_de
from processo_seletivo.formalizacao.application import conjunto, definir
from processo_seletivo.formalizacao.application.definir import (
    AVISO_DA_INSCRICAO,
    AVISO_DE_MODALIDADE,
    FORMAS_POR_MODALIDADE,
)
from processo_seletivo.formalizacao.domain import nomes
from processo_seletivo.formalizacao.models import DefinicaoDosDocumentosDaFormalizacao
from processo_seletivo.publicacoes.models import DocumentoPublicado
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.documentos_da_convocacao import CERTIDAO, HISTORICO, IDENTIDADE
from tests.fixtures.formalizacao import (
    CERTIFICADO_DO_CURSO,
    TITULOS,
    definir_documentos,
    designar_direto,
)
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


def _pagina(edital):
    return reverse("interface:formalizacao-definicao", args=[edital.id])


def test_a_definicao_comeca_vazia_e_nada_fica_disponivel(cenario, client, seletor):
    """FR-3653, FR-3660: sem definição, nenhum documento; a página do setor diz por quê."""
    assert definir.vigente(cenario.edital) is None
    pessoas = conjunto.aptos(cenario.edital, definicao=None)
    assert len(pessoas) == 5
    assert all(pessoa.documentos == [] for pessoa in pessoas)

    designar_direto(cenario.edital, "rui")
    identificar(client, "rui", ["formalizacao"])
    corpo = client.get(
        reverse("interface:formalizacao-edital", args=[cenario.edital.id])
    ).content.decode()
    assert "A condução ainda não definiu os documentos" in corpo
    assert "Verificar e exportar" not in corpo


def test_a_gravacao_sem_motivo_e_recusada_e_nada_e_gravado(cenario, gestor):
    with pytest.raises(DomainError) as recusa:
        definir.definir(
            actor=gestor, edital_id=cenario.edital.id, requisitos=[IDENTIDADE], motivo="  "
        )

    assert recusa.value.code == nomes.MOTIVO_OBRIGATORIO
    assert not DefinicaoDosDocumentosDaFormalizacao.objects.exists()


def test_o_motivo_vazio_tambem_e_recusado_pelo_banco(cenario):
    """A constraint é a segunda camada (FR-3655): vale para quem chega por fora da aplicação."""
    from django.db import IntegrityError, transaction
    from django.utils import timezone

    with pytest.raises(IntegrityError), transaction.atomic():
        DefinicaoDosDocumentosDaFormalizacao.objects.create(
            edital=cenario.edital,
            requisitos=[],
            motivo="",
            definido_por="carlos",
            unidade_de_atuacao="cefor",
            definido_em=timezone.now(),
        )


def test_requisito_de_fora_do_edital_e_recusado(cenario, gestor):
    with pytest.raises(DomainError) as recusa:
        definir.definir(
            actor=gestor,
            edital_id=cenario.edital.id,
            requisitos=["00000000-0000-0000-0000-000000009999"],
            motivo="Portaria 1/2026",
        )

    assert recusa.value.code == nomes.REQUISITO_FORA_DO_EDITAL


def test_cada_gravacao_e_uma_versao_e_o_historico_diz_a_diferenca(cenario, gestor):
    """FR-3655, FR-3656, FR-3711: a vigente é a mais recente; o histórico mostra o que mudou."""
    primeira = definir_documentos(cenario.edital, gestor, requisitos=[IDENTIDADE, TITULOS])
    segunda = definir_documentos(
        cenario.edital, gestor, requisitos=[IDENTIDADE, CERTIDAO], motivo="Títulos não servem"
    )

    assert definir.vigente(cenario.edital) == segunda
    historico = definir.historico(cenario.edital)
    assert [v.definicao for v in historico] == [segunda, primeira]
    assert historico[0].acrescentados == ["Certidão de nascimento"]
    assert historico[0].retirados == ["Títulos para pontuação"]
    assert sorted(historico[1].acrescentados) == [
        "Documento de identificação",
        "Títulos para pontuação",
    ]
    evento = RegistroAuditoria.objects.filter(operation=nomes.DEFINIR).latest("occurred_at")
    assert evento.aggregate_id == cenario.edital.id
    assert str(segunda.id) in evento.reason


def test_a_versao_nova_vale_para_a_consulta_seguinte(cenario, gestor):
    """FR-3656: a versão nova alcança todos, inclusive de chamadas anteriores, na hora."""
    definir_documentos(cenario.edital, gestor, requisitos=[IDENTIDADE, TITULOS])
    antes = conjunto.aptos(cenario.edital, definicao=definir.vigente(cenario.edital))
    assert {d.chave for d in antes[0].documentos} == {"identidade", "titulos"}

    definir_documentos(cenario.edital, gestor, requisitos=[IDENTIDADE], motivo="Minimização")
    depois = conjunto.aptos(cenario.edital, definicao=definir.vigente(cenario.edital))
    assert {d.chave for d in depois[0].documentos} == {"identidade"}


def test_os_avisos_saem_do_momento_e_do_recorte(cenario):
    """FR-3658: o da inscrição pelo momento; o de modalidade pelo recorte que o Edital publica."""
    requisitos = {r.id: r for r in definir.requisitos_do_edital(cenario.edital)}

    assert requisitos[str(IDENTIDADE)].avisos == [AVISO_DA_INSCRICAO]
    assert requisitos[str(CERTIDAO)].avisos == []
    # O recorte por modalidade, lido pela mesma regra do Edital, em cada uma das formas.
    for campos in (
        {"modalityCode": "PPI"},
        {"profileId": "p", "modalityId": "m"},
        {"modalityId": "m"},
    ):
        assert recorte_de(campos).forma in FORMAS_POR_MODALIDADE
    assert recorte_de({"profileId": "p"}).forma not in FORMAS_POR_MODALIDADE
    assert AVISO_DE_MODALIDADE.startswith("Este documento é exigido só de candidatos")


def test_a_tela_mostra_os_avisos_sem_impedir_a_gravacao(cenario, client, seletor):
    identificar(client, "carlos", ["gestor"])
    corpo = client.get(_pagina(cenario.edital)).content.decode()
    assert AVISO_DA_INSCRICAO in corpo
    assert 'name="requisito"' in corpo
    assert "checked" not in corpo, "a lista começa sem marcação"

    resposta = client.post(
        _pagina(cenario.edital),
        {"requisito": [str(IDENTIDADE), str(TITULOS)], "motivo": "Memorando 3/2026"},
    )
    assert resposta.status_code == 302
    assert set(definir.vigente(cenario.edital).requisitos) == {str(IDENTIDADE), str(TITULOS)}


def test_a_tela_recusa_o_envio_sem_motivo_e_guarda_as_marcas(cenario, client, seletor):
    identificar(client, "carlos", ["gestor"])
    resposta = client.post(_pagina(cenario.edital), {"requisito": [str(HISTORICO)], "motivo": ""})

    assert resposta.status_code == 422
    corpo = resposta.content.decode()
    assert "Diga por que estes documentos vão ao setor" in corpo
    assert "checked" in corpo
    assert definir.vigente(cenario.edital) is None


@pytest.mark.parametrize(
    ("subject", "papeis", "esperado", "com_formulario"),
    [
        ("carlos", ["gestor"], 200, True),
        ("maria", [], 200, True),
        ("auditora", ["auditor"], 200, False),
        ("rui", ["formalizacao"], 403, False),
        ("joao", [], 403, False),
        ("exporta", ["exportador"], 403, False),
    ],
)
def test_quem_grava_quem_le_e_quem_e_recusado(
    cenario, client, seletor, gestor, subject, papeis, esperado, com_formulario
):
    """FR-3654, FR-3711, matriz: a condução grava; o auditor lê; o setor e os demais, 403."""
    definir_documentos(cenario.edital, gestor)
    identificar(client, subject, papeis)
    resposta = client.get(_pagina(cenario.edital))

    assert resposta.status_code == esperado
    if esperado == 200:
        corpo = resposta.content.decode()
        assert "Histórico da definição" in corpo
        assert "Portaria 1/2026" in corpo
        assert ("Gravar a definição" in corpo) is com_formulario


def test_o_auditor_nao_grava_nem_por_post_forjado(cenario, client, seletor):
    identificar(client, "auditora", ["auditor"])
    resposta = client.post(_pagina(cenario.edital), {"requisito": [str(IDENTIDADE)], "motivo": "x"})

    assert resposta.status_code == 403
    assert definir.vigente(cenario.edital) is None


def test_ator_de_outra_unidade_recebe_inexistente(cenario, client, seletor):
    identificar(client, "carlos", ["gestor"], escopo="outra")
    assert client.get(_pagina(cenario.edital)).status_code == 404


def test_o_conteudo_publicado_nao_muda(cenario, gestor):
    """FR-3657: nem snapshot, nem hash, nem PDF — e nenhum Documento Exigido novo."""
    edital = cenario.edital
    versoes = list(
        VersaoConsolidada.objects.filter(edital=edital).values_list("id", "content_hash")
    )
    documentos = DocumentoPublicado.objects.count()
    conteudo = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at").content
    edital.refresh_from_db()
    revisao = edital.revision

    definir_documentos(edital, gestor, requisitos=[IDENTIDADE, CERTIDAO, CERTIFICADO_DO_CURSO])

    assert (
        list(VersaoConsolidada.objects.filter(edital=edital).values_list("id", "content_hash"))
        == versoes
    )
    assert DocumentoPublicado.objects.count() == documentos
    novo = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at").content
    assert novo == conteudo
    edital.refresh_from_db()
    assert edital.revision == revisao


def test_a_definicao_e_append_only_por_gatilho(cenario, gestor):
    from django.db import connection

    if connection.vendor != "postgresql":
        pytest.skip("gatilho só no PostgreSQL")
    from django.db import transaction
    from django.db.utils import DatabaseError

    definicao = definir_documentos(cenario.edital, gestor)
    with (
        pytest.raises(DatabaseError, match="append-only"),
        transaction.atomic(),
        connection.cursor() as cursor,
    ):
        cursor.execute(
            "UPDATE formalizacao_definicaodosdocumentosdaformalizacao SET motivo = 'x' WHERE id = %s",
            [definicao.id],
        )
