"""Tela de situação e atos do Edital (US3 da 002).

É onde a interface passa a ter efeito jurídico. O que se verifica: confirmação antes de ato
irreversível com as consequências ditas, segregação de funções comunicada antes da tentativa,
e o duplo clique não praticando dois atos.
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.infrastructure.pdf import MARCA_DE_PREVIA
from processo_seletivo.publicacoes.models import (
    DocumentoPublicado,
    Publicacao,
    RevisaoEdital,
)
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.edital import caminho_perfil
from tests.fixtures.publicacao import publish_original, retify
from tests.interface.conftest import compor_rascunho, identificar

TEXTO_PDF = re.compile(rb"\((.*?)\) Tj", re.DOTALL)


def texto_de_pdf_bytes(pdf: bytes) -> str:
    """O texto realmente desenhado — não o que se supõe ter sido escrito."""
    return "\n".join(
        parte.replace(b"\\(", b"(").replace(b"\\)", b")").decode("cp1252")
        for parte in TEXTO_PDF.findall(pdf)
    )


def texto_do_pdf(resposta) -> str:
    assert resposta.status_code == 200, resposta.content
    return texto_de_pdf_bytes(resposta.content)


PERFIS = {
    "perfil-0-id": "cccccccc-0000-4000-8000-00000000f001",
    "perfil-0-code": "P1",
    "perfil-0-name": "Perfil",
    "perfil-0-immediateVacancies": "1",
    "perfil-0-reserveType": "NONE",
}
EVENTOS = {
    "evento-0-id": "cccccccc-0000-4000-8000-00000000f002",
    "evento-0-type": "INSCRICAO",
    "evento-0-description": "Inscrições",
    "evento-0-startAt": "2026-10-01T09:00",
}
SIGNATARIO = {
    "signatario_nome": "Reitora",
    "signatario_cargo": "Reitora",
    "signatario_id": "00000000-0000-0000-0000-0000000000a1",
}


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)
    return Edital.objects.get()


def praticar(client, edital, acao, **campos):
    """Percorre o caminho real: abre a confirmação, pega a chave e confirma."""
    url = reverse("interface:ato", args=[edital.id, acao])
    confirmacao = client.get(url)
    assert confirmacao.status_code == 200, confirmacao.content
    chave = confirmacao.context["chave_idempotencia"]
    return client.post(url, {"chave_idempotencia": chave, **campos}), chave


@pytest.mark.django_db
@pytest.mark.integration
def test_fluxo_completo_ate_a_publicacao(client, seletor_ligado, edital):
    identificar(client, "ana.elaboradora", ["elaborador"])
    compor_rascunho(client, edital, PERFIS, EVENTOS)
    praticar(client, Edital.objects.get(), "submeter")
    assert Edital.objects.get().status == Edital.Status.EM_REVISAO

    identificar(client, "bruno.homologador", ["homologador"])
    praticar(client, Edital.objects.get(), "homologar", motivo="Conferido pela comissão")
    assert Edital.objects.get().status == Edital.Status.HOMOLOGADO

    identificar(client, "carla.publicadora", ["publicador"])
    praticar(client, Edital.objects.get(), "publicar", **SIGNATARIO)
    assert Edital.objects.get().status == Edital.Status.PUBLICADO
    assert Publicacao.objects.filter(edital=edital).count() == 1


@pytest.mark.django_db
@pytest.mark.integration
def test_confirmacao_diz_o_que_o_ato_provoca_antes_de_praticar(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    """FR-010 e FR-011: consequências e irreversibilidade ditas antes da confirmação."""
    publicado = publish_original(api_client, manager_headers, process_payload)
    identificar(client, "marcia.gestora", ["gestor"])
    corpo = client.get(
        reverse("interface:ato", args=[publicado.id, "encerrar"])
    ).content.decode()

    assert "Este ato não pode ser desfeito" in corpo
    assert "conclusão regular" in corpo
    assert "permanecem disponíveis na consulta pública" in corpo
    assert "Confirmar: Encerrar" in corpo


@pytest.mark.django_db
@pytest.mark.integration
def test_confirmar_duas_vezes_pratica_um_ato_so(client, seletor_ligado, edital):
    """A chave de idempotência nasce no formulário: duplo clique não publica duas vezes."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    compor_rascunho(client, edital, PERFIS, EVENTOS)
    praticar(client, Edital.objects.get(), "submeter")
    identificar(client, "bruno.homologador", ["homologador"])
    praticar(client, Edital.objects.get(), "homologar", motivo="OK")

    identificar(client, "carla.publicadora", ["publicador"])
    atual = Edital.objects.get()
    url = reverse("interface:ato", args=[atual.id, "publicar"])
    chave = client.get(url).context["chave_idempotencia"]
    primeira = client.post(url, {"chave_idempotencia": chave, **SIGNATARIO})
    segunda = client.post(url, {"chave_idempotencia": chave, **SIGNATARIO})

    assert primeira.status_code == segunda.status_code == 302
    assert Publicacao.objects.filter(edital=edital).count() == 1


@pytest.mark.django_db
@pytest.mark.integration
def test_segregacao_e_avisada_antes_da_tentativa(client, seletor_ligado, edital):
    """FR-012: comunicar a exigência antes, e não apenas depois da recusa."""
    identificar(client, "joao.sozinho", ["elaborador", "homologador", "publicador"])
    compor_rascunho(client, edital, PERFIS, EVENTOS)
    praticar(client, Edital.objects.get(), "submeter")
    praticar(client, Edital.objects.get(), "homologar", motivo="OK")

    detalhe = client.get(reverse("interface:detalhe", args=[edital.id])).content.decode()
    assert "Você não poderá publicar este Edital" in detalhe

    confirmacao = client.get(
        reverse("interface:ato", args=[edital.id, "publicar"])
    ).content.decode()
    assert "Segregação de funções" in confirmacao
    assert "não pode publicá-la sozinho" in confirmacao
    # A previsão é exata — mesma regra do command —, então oferecer "Confirmar" logo abaixo
    # do aviso só adiaria a recusa para depois do clique.
    assert "Confirmar: " not in confirmacao

    resposta, _ = praticar(client, Edital.objects.get(), "publicar", **SIGNATARIO)
    assert resposta.status_code == 403, "e o domínio recusa de fato"
    assert not Publicacao.objects.filter(edital=edital).exists()


@pytest.mark.django_db
@pytest.mark.integration
def test_motivo_obrigatorio_e_exigido_antes_do_command(client, seletor_ligado, edital):
    identificar(client, "ana.elaboradora", ["elaborador"])
    compor_rascunho(client, edital, PERFIS, EVENTOS)
    praticar(client, Edital.objects.get(), "submeter")
    identificar(client, "bruno.homologador", ["homologador"])

    resposta, _ = praticar(client, Edital.objects.get(), "homologar", motivo="   ")
    assert resposta.status_code == 422
    assert "é obrigatório" in resposta.content.decode()
    assert Edital.objects.get().status == Edital.Status.EM_REVISAO


@pytest.mark.django_db
@pytest.mark.integration
def test_publicar_exige_autoridade_signataria(client, seletor_ligado, edital):
    identificar(client, "ana.elaboradora", ["elaborador"])
    compor_rascunho(client, edital, PERFIS, EVENTOS)
    praticar(client, Edital.objects.get(), "submeter")
    identificar(client, "bruno.homologador", ["homologador"])
    praticar(client, Edital.objects.get(), "homologar", motivo="OK")
    identificar(client, "carla.publicadora", ["publicador"])

    resposta, _ = praticar(client, Edital.objects.get(), "publicar", signatario_nome="Reitora")
    assert resposta.status_code == 422
    assert "Autoridade Signatária" in resposta.content.decode()
    assert not Publicacao.objects.exists()


@pytest.mark.django_db
@pytest.mark.integration
def test_detalhe_mostra_a_trilha_e_quem_atuou(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    publicado = publish_original(api_client, manager_headers, process_payload)
    identificar(client, "auditor", ["auditor"])
    corpo = client.get(reverse("interface:detalhe", args=[publicado.id])).content.decode()

    assert 'class="e-atual"' in corpo
    assert corpo.count('class="e-concluida"') == 3, "elaboração, revisão e homologação concluídas"
    assert "preparador" in corpo and "homologador" in corpo and "publicador" in corpo
    assert "Diretora-Geral" in corpo, "Autoridade Signatária aparece"


@pytest.mark.django_db
@pytest.mark.integration
def test_edital_publicado_anuncia_imutabilidade(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    """FR-013: publicado é imutável, e a Retificação é o caminho."""
    publicado = publish_original(api_client, manager_headers, process_payload)
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = client.get(reverse("interface:detalhe", args=[publicado.id])).content.decode()
    assert "Conteúdo imutável" in corpo
    assert "Retificação" in corpo


@pytest.mark.django_db
@pytest.mark.integration
def test_ato_sem_permissao_nao_e_oferecido_nem_aceito(client, seletor_ligado, edital):
    identificar(client, "ana.elaboradora", ["elaborador"])
    compor_rascunho(client, edital, PERFIS, EVENTOS)
    praticar(client, Edital.objects.get(), "submeter")

    corpo = client.get(reverse("interface:detalhe", args=[edital.id])).content.decode()
    assert "Homologar</a>" not in corpo, "o Elaborador não vê o ato de homologar"

    resposta, _ = praticar(client, Edital.objects.get(), "homologar", motivo="Tentativa")
    assert resposta.status_code == 403
    assert Edital.objects.get().status == Edital.Status.EM_REVISAO


@pytest.mark.django_db
@pytest.mark.integration
def test_cancelado_sai_da_trilha_em_vez_de_avancar(client, seletor_ligado, edital):
    identificar(client, "marcia.gestora", ["gestor"])
    praticar(client, edital, "cancelar", motivo="Desistência institucional")

    corpo = client.get(reverse("interface:detalhe", args=[edital.id])).content.decode()
    assert Edital.objects.get().status == Edital.Status.CANCELADO
    assert 'class="e-fora"' in corpo
    assert "não é o mesmo que encerramento" in corpo


@pytest.mark.django_db
@pytest.mark.integration
def test_encerrar_nao_se_parece_com_cancelar(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    """Encerrado é conclusão regular; só a interrupção recebe tratamento de perigo."""
    publicado = publish_original(api_client, manager_headers, process_payload)
    identificar(client, "marcia.gestora", ["gestor"])
    corpo = client.get(reverse("interface:detalhe", args=[publicado.id])).content.decode()

    import re

    botoes = dict(
        (rotulo, classe)
        for classe, rotulo in re.findall(
            r'class="botao ([^"]*)"\s+href="[^"]*">(Encerrar|Cancelar)</a>', corpo
        )
    )
    assert "perigoso" in botoes["Cancelar"], "cancelar é interrupção e recebe tratamento próprio"
    assert "perigoso" not in botoes["Encerrar"], "encerrar é conclusão regular"
    assert corpo.count("irreversível") >= 2, "ambos seguem marcados como irreversíveis"


@pytest.mark.django_db
@pytest.mark.integration
def test_detalhe_oferece_o_documento_de_cada_publicacao_sem_rotular_vigente(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    """FR-002: o documento pertence ao ato, e nenhum ato produz o "documento vigente".

    A Retificação abaixo é publicada com vigência **futura**, que é o caso que desfaz a tentação:
    a Publicação mais recente existe, tem documento, e não é a que vigora. A vigência é da Versão
    Consolidada, que não tem documento próprio — chamar qualquer um destes de vigente seria
    afirmar sobre o documento uma propriedade que ele não tem.
    """
    edital = publish_original(api_client, manager_headers, process_payload)
    retify(
        api_client,
        edital,
        [
            {
                "targetPath": caminho_perfil("immediateVacancies"),
                "operation": "REPLACE",
                "newValue": 5,
            }
        ],
        effective_at="2030-01-01T00:00:00-03:00",
    )

    identificar(client, "ana.elaboradora", ["elaborador"])
    resposta = client.get(reverse("interface:detalhe", args=[edital.id]))
    corpo = resposta.content.decode()

    documentos = resposta.context["documentos"]
    assert [item["ato"] for item in documentos] == ["Publicação original", "Retificação"]
    assert [item["ordem"] for item in documentos] == [1, 2]
    for publicacao in Publicacao.objects.filter(edital=edital):
        assert f"/api/v1/public/publicacoes/{publicacao.id}/documento" in corpo

    # Nenhum item da lista se apresenta como vigente. A verificação é sobre os itens, e não sobre
    # a página, porque a página **explica** que nenhum deles é o documento vigente — e essa frase
    # é justamente o que se quer manter.
    lista = corpo.split('id="documentos-titulo"')[1].split("</ul>")[0]
    itens = lista.split("<li>")[1:]
    assert len(itens) == 2
    assert [item for item in itens if "vigente" in item.lower()] == []


@pytest.mark.django_db
@pytest.mark.integration
def test_previa_nao_cria_registro_publicado_nem_muda_o_estado(client, seletor_ligado, edital):
    """FR-011: visualizar não é ato — e é isso que torna a prévia utilizável a qualquer hora."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    compor_rascunho(client, edital, PERFIS, EVENTOS)
    edital.refresh_from_db()

    antes = (
        Publicacao.objects.count(),
        RevisaoEdital.objects.count(),
        VersaoConsolidada.objects.count(),
        DocumentoPublicado.objects.count(),
    )
    resposta = client.get(reverse("interface:previa", args=[edital.id]))

    assert resposta.status_code == 200
    assert resposta["Content-Type"] == "application/pdf"
    assert "previa-edital-" in resposta["Content-Disposition"]
    assert resposta.content.startswith(b"%PDF-")
    assert (
        Publicacao.objects.count(),
        RevisaoEdital.objects.count(),
        VersaoConsolidada.objects.count(),
        DocumentoPublicado.objects.count(),
    ) == antes
    assert Edital.objects.get(pk=edital.pk).status == Edital.Status.EM_ELABORACAO


@pytest.mark.django_db
@pytest.mark.integration
def test_previa_reflete_o_rascunho_gravado_e_permite_continuar_editando(
    client, seletor_ligado, edital
):
    """FR-005 e FR-012: o que se vê é o que está gravado, e voltar não custa nada."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    compor_rascunho(client, edital, PERFIS, EVENTOS)
    edital.refresh_from_db()
    assert "Inscrições" in texto_do_pdf(client.get(reverse("interface:previa", args=[edital.id])))

    client.post(
        reverse("interface:compor-etapa", args=[edital.id, "cronograma"]),
        dict(EVENTOS, **{"evento-0-description": "Inscrições prorrogadas"}),
    )
    depois = texto_do_pdf(client.get(reverse("interface:previa", args=[edital.id])))
    assert "Inscrições prorrogadas" in depois

    # E a composição continua aberta: a prévia não fechou nada.
    voltando = client.get(reverse("interface:compor-etapa", args=[edital.id, "cronograma"]))
    assert voltando.status_code == 200


@pytest.mark.django_db
@pytest.mark.integration
def test_previa_acompanha_o_edital_ate_a_homologacao_e_para_na_publicacao(
    client, seletor_ligado, edital
):
    """FR-008: quem homologa e quem publica precisam ler o documento antes de decidir."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    compor_rascunho(client, edital, PERFIS, EVENTOS)
    assert client.get(reverse("interface:previa", args=[edital.id])).status_code == 200

    praticar(client, Edital.objects.get(), "submeter")
    identificar(client, "bruno.homologador", ["homologador"])
    detalhe = client.get(reverse("interface:detalhe", args=[edital.id])).content.decode()
    assert "Visualizar Edital" in detalhe
    assert client.get(reverse("interface:previa", args=[edital.id])).status_code == 200

    praticar(client, Edital.objects.get(), "homologar", motivo="Conferido")
    assert client.get(reverse("interface:previa", args=[edital.id])).status_code == 200

    identificar(client, "carla.publicadora", ["publicador"])
    praticar(client, Edital.objects.get(), "publicar", motivo="Publicação", **SIGNATARIO)
    assert Edital.objects.get().status == Edital.Status.PUBLICADO
    # Publicado tem documento de verdade; uma prévia ao lado dele seria um segundo documento
    # para o mesmo conteúdo.
    recusada = client.get(reverse("interface:previa", args=[edital.id]))
    assert recusada.status_code == 409
    assert "Visualizar Edital" not in client.get(
        reverse("interface:detalhe", args=[edital.id])
    ).content.decode()


@pytest.mark.django_db
@pytest.mark.integration
def test_previa_e_recusada_a_quem_nao_alcanca_o_edital(client, seletor_ligado, edital):
    """Anti-IDOR: a prévia é conteúdo normativo em construção, não página pública."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    sessao = client.session
    sessao["interface_identidade"] = {
        "subject": "ana.elaboradora",
        "escopo": "outra-instituicao",
        "papeis": ["elaborador"],
    }
    sessao.save()
    assert client.get(reverse("interface:previa", args=[edital.id])).status_code == 404


@pytest.mark.django_db
@pytest.mark.integration
def test_publicar_logo_apos_a_previa_produz_o_mesmo_conteudo_normativo(
    client, seletor_ligado, edital
):
    """FR-013: é o que faz a prévia valer alguma coisa — e a diferença é só a moldura."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    compor_rascunho(client, edital, PERFIS, EVENTOS)
    praticar(client, Edital.objects.get(), "submeter")
    identificar(client, "bruno.homologador", ["homologador"])
    praticar(client, Edital.objects.get(), "homologar", motivo="Conferido")

    visualizado = texto_do_pdf(client.get(reverse("interface:previa", args=[edital.id])))

    identificar(client, "carla.publicadora", ["publicador"])
    praticar(client, Edital.objects.get(), "publicar", motivo="Publicação", **SIGNATARIO)
    publicado = texto_de_pdf_bytes(bytes(DocumentoPublicado.objects.get().bytes))

    for esperado in ("P1", "Perfil", "INSCRICAO", "Inscrições"):
        assert esperado in visualizado and esperado in publicado, esperado
    assert MARCA_DE_PREVIA in visualizado
    assert MARCA_DE_PREVIA not in publicado
    assert "INTEGRIDADE" in publicado and "INTEGRIDADE" not in visualizado
