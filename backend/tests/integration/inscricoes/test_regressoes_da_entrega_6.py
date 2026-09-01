"""Os problemas temporais que a revisão da entrega 6 encontrou.

Todos da mesma família: o tempo passando entre duas leituras, ou entre a leitura e a entrega.
Nenhum quebra nada no caminho normal — aparecem quando alguém retifica, quando dois arquivos
disputam o mesmo caminho, ou quando a lista é aberta meses depois.
"""

import pytest
from django.urls import reverse

from processo_seletivo.inscricoes.application.consulta import inscricoes_do_edital
from processo_seletivo.inscricoes.application.rascunho import anexar_documento, gravar_dados
from processo_seletivo.inscricoes.application.submissao import (
    documentos_que_a_retificacao_invalida,
    enviar_inscricao,
    reconhecer_versao,
)
from processo_seletivo.inscricoes.models import DocumentoSubmetido
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from processo_seletivo.seguranca.domain import Actor
from tests.fixtures.candidato import MARIA, MODALIDADE_AC, MODALIDADE_PPP, identificar, pdf
from tests.fixtures.publicacao import create_retification, publish_retification
from tests.fixtures.selecao import (
    DOCUMENTO_DA_MODALIDADE,
    DOCUMENTO_DE_TODOS,
    DOCUMENTO_DO_PERFIL,
)
from tests.interface.conftest import identificar as identificar_servidor

DECLARACOES = {"veracidade": True, "ciencia": True}
GESTOR = Actor("bruno.gestor", "cefor", frozenset({"inscricao:consultar"}))


def _completar(inscricao, modalidade=MODALIDADE_AC):
    inscricao = gravar_dados(
        identidade=MARIA, inscricao=inscricao, dados={"modality_id": modalidade}
    )
    requisitos = [(DOCUMENTO_DE_TODOS, "rg.pdf"), (DOCUMENTO_DO_PERFIL, "diploma.pdf")]
    if modalidade == MODALIDADE_PPP:
        requisitos.append((DOCUMENTO_DA_MODALIDADE, "autodeclaracao.pdf"))
    for requisito, nome in requisitos:
        anexar_documento(
            identidade=MARIA, inscricao=inscricao, requirement_id=requisito, arquivo=pdf(nome)
        )
    inscricao.refresh_from_db()
    return inscricao


def _retificar(api_client, edital, caminho, valor, sufixo):
    retificacao = create_retification(
        api_client,
        edital,
        [
            {
                "targetPath": caminho,
                "operation": "REPLACE",
                "newValue": valor,
                "expectedPreviousHash": "",
            }
        ],
        suffix=sufixo,
    )
    publish_retification(api_client, retificacao, suffix=sufixo)
    return VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")


# ---------------------------------------------------------------------------
# A lista não reescreve o passado
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_lista_usa_a_versao_aceita_de_cada_inscricao(
    inscricao_de_maria, api_client, selecao
):
    """Renomear o Perfil depois do envio não pode mudar o que a lista diz daquela inscrição."""
    enviada = enviar_inscricao(
        identidade=MARIA,
        inscricao=_completar(inscricao_de_maria),
        declaracoes=DECLARACOES,
        idempotency_key="envio-lista",
    )
    _retificar(
        api_client,
        selecao,
        f"/profiles/id={enviada.profile_id}/name",
        "Professor de Informática (denominação retificada)",
        "perfil",
    )

    _, linhas = inscricoes_do_edital(actor=GESTOR, edital_id=selecao.id)

    assert linhas[0]["perfil"] == "Professor de Informática", (
        "a inscrição responde à versão que aceitou, e não à que passou a vigorar depois"
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_comprovante_nao_muda_depois_de_retificado(
    client, inscricao_de_maria, api_client, selecao
):
    enviada = enviar_inscricao(
        identidade=MARIA,
        inscricao=_completar(inscricao_de_maria),
        declaracoes=DECLARACOES,
        idempotency_key="envio-comprovante",
    )
    identificar(client, MARIA)
    _retificar(
        api_client,
        selecao,
        f"/profiles/id={enviada.profile_id}/name",
        "Outro nome de Perfil",
        "comprovante",
    )

    corpo = client.get(reverse("portal:comprovante", args=[enviada.id])).content.decode()

    assert "Professor de Informática" in corpo
    assert "Outro nome de Perfil" not in corpo, "um comprovante que se reescreve não prova nada"


# ---------------------------------------------------------------------------
# A Retificação não deixa o candidato preso
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_documento_que_deixou_de_ser_exigido_e_listado_e_descartado(
    client, inscricao_de_maria, api_client, selecao
):
    """Sem isto: envio recusado por documento inaplicável, e nenhuma tela oferece removê-lo."""
    completa = _completar(inscricao_de_maria, modalidade=MODALIDADE_PPP)
    versao = _retificar(
        api_client,
        selecao,
        f"/documentRequirements/id={DOCUMENTO_DA_MODALIDADE}/modalityId",
        MODALIDADE_AC,
        "restringe",
    )

    a_descartar = documentos_que_a_retificacao_invalida(completa, versao)
    assert [item["arquivo"] for item in a_descartar] == ["autodeclaracao.pdf"]

    identificar(client, MARIA)
    aviso = client.get(reverse("portal:revisao", args=[completa.id])).content.decode()
    assert "deixaram de ser exigidos" in aviso
    assert "autodeclaracao.pdf" in aviso

    client.post(reverse("portal:revisao", args=[completa.id]), {"reconhecer_versao": "1"})

    assert not DocumentoSubmetido.objects.filter(
        inscricao=completa, requirement_id=DOCUMENTO_DA_MODALIDADE
    ).exists()
    enviada = client.post(
        reverse("portal:revisao", args=[completa.id]), {"veracidade": "on", "ciencia": "on"}
    )
    assert enviada.status_code == 302, "e o envio deixa de ser um beco"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_reconhecer_versao_sem_descarte_nao_remove_nada(
    inscricao_de_maria, api_client, selecao
):
    completa = _completar(inscricao_de_maria)
    versao = _retificar(api_client, selecao, "/description", "Outra descrição.", "descricao")

    reconhecer_versao(identidade=MARIA, inscricao=completa, versao=versao)

    assert DocumentoSubmetido.objects.filter(inscricao=completa).count() == 2


# ---------------------------------------------------------------------------
# Imutabilidade depois do envio
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_inscricao_enviada_nao_e_alterada_nem_por_fora_da_aplicacao(inscricao_de_maria):
    enviada = enviar_inscricao(
        identidade=MARIA,
        inscricao=_completar(inscricao_de_maria),
        declaracoes=DECLARACOES,
        idempotency_key="envio-imutavel",
    )

    enviada.telefone = "(27) 90000-0000"
    with pytest.raises(TypeError):
        enviada.save()


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_documento_de_inscricao_enviada_nao_e_removido(inscricao_de_maria):
    enviada = enviar_inscricao(
        identidade=MARIA,
        inscricao=_completar(inscricao_de_maria),
        declaracoes=DECLARACOES,
        idempotency_key="envio-doc-imutavel",
    )
    documento = DocumentoSubmetido.objects.filter(inscricao=enviada).first()

    with pytest.raises(TypeError):
        documento.delete()
    with pytest.raises(TypeError):
        documento.nome_original = "outro.pdf"
        documento.save()


# ---------------------------------------------------------------------------
# A entrega serve os bytes que conferiu
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_arquivo_servido_e_o_arquivo_conferido(
    client, settings, inscricao_de_maria, raiz_de_arquivos
):
    """A cópia verificada é a que vai para a resposta — não o caminho, que pode mudar no meio."""
    enviada = enviar_inscricao(
        identidade=MARIA,
        inscricao=_completar(inscricao_de_maria),
        declaracoes=DECLARACOES,
        idempotency_key="envio-toctou",
    )
    settings.INTERFACE_SELETOR_IDENTIDADE = True
    identificar_servidor(client, "bruno.gestor", ["gestor"])
    documento = DocumentoSubmetido.objects.get(requirement_id=DOCUMENTO_DE_TODOS)

    resposta = client.get(
        reverse("interface:documento-da-inscricao", args=[enviada.id, DOCUMENTO_DE_TODOS])
    )
    # A troca acontece **depois** da conferência e antes de a resposta ser consumida — é a janela
    # que a segunda abertura do arquivo criava.
    (raiz_de_arquivos / documento.arquivo.name).write_bytes(b"%PDF-1.4\nconteudo trocado")
    servido = b"".join(resposta.streaming_content)
    resposta.close()

    assert b"conteudo trocado" not in servido
    assert servido.startswith(b"%PDF-1.4")
