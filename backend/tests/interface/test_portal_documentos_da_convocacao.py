"""Os documentos da convocação no portal do candidato (115, US1, US2, US3, US4).

Pela tela da convocação da `059`, e pelo canal do ator: o titular vê a lista, envia, lê a pendência
e o resultado, e quem não é titular recebe a recusa de inexistente (FR-3577, FR-3582, FR-3584,
FR-3600, FR-3612, FR-3613).
"""

from datetime import timedelta
from unittest import mock

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.identidade.models import CandidateIdentity
from processo_seletivo.portal.identidade import CHAVE_SESSAO
from tests.fixtures import documentos_da_convocacao as cenarios
from tests.fixtures.comissao import abrir_arquivo
from tests.fixtures.documentos_da_convocacao import (
    CERTIDAO,
    CERTIFICADO,
    CERTIFICADO_NA_CONVOCACAO,
    FICHA,
    HISTORICO,
    IDENTIDADE,
    apresentar,
    comunicar,
    conferir,
    item,
)

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

TERMOS_DE_VINCULO = (
    "matriculad",
    "matrícula efetivada",
    "bolsa concedida",
    "vinculad",
    "contratad",
)


def entrar_como(client, inscricao):
    registro, _ = CandidateIdentity.objects.get_or_create(
        subject=inscricao.identity_subject, defaults={"created_at": timezone.now()}
    )
    sessao = client.session
    sessao[CHAVE_SESSAO] = str(registro.pk)
    sessao.save()


def tela(client, pessoa):
    resposta = client.get(reverse("portal:convocacao", args=[pessoa.id]))
    assert resposta.status_code == 200
    return resposta.content.decode()


@pytest.fixture
def aluno(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    return cenarios.montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        documentos=cenarios.documentos_do_aluno(),
        prefixo="portal-aluno-115",
    )


def test_a_convocada_ve_o_que_apresentar_e_ate_quando(aluno, gestor, client):
    pessoa, _ = cenarios.convocar_primeira(
        aluno, gestor, vencimento=timezone.now() + timedelta(days=3)
    )
    entrar_como(client, pessoa)

    corpo = tela(client, pessoa)

    # Os blocos da `118` (FR-3735) no lugar da lista única, e "Envie até…" saiu da lista. Esta
    # convocação não teve a comunicação enviada: a tela antiga mostrava a data como prazo de um
    # prazo que não corria (F12); a de agora diz que ele não começou, e a data fica só nos dados do
    # ato (FR-3749 da `118`).
    assert "O que fazer agora" in corpo and "O que falta" in corpo
    assert "Certidão de nascimento ou casamento" in corpo
    assert "Todas as páginas, em arquivo único." in corpo
    assert corpo.count("Falta enviar") == 4
    assert "O prazo ainda não começou a correr" in corpo
    assert "Você já pode enviar." in corpo
    assert "Envie até" not in corpo
    assert "Prazo desta convocação" not in corpo
    assert "Documento de identificação" not in corpo.split('id="o-que-fazer-agora"')[1]


def test_a_convocada_envia_pelo_portal_e_le_o_resultado(aluno, gestor, client):
    edital, _, _ = aluno
    pessoa, convocacao = cenarios.convocar_primeira(aluno, gestor)
    entrar_como(client, pessoa)
    alvo = item(convocacao, HISTORICO)

    resposta = client.post(
        reverse("portal:apresentar-documento-da-convocacao", args=[pessoa.id, alvo.id]),
        {"arquivo": cenarios.pdf(b"historico")},
    )
    assert resposta.status_code == 302
    corpo = tela(client, pessoa)
    assert "Documento recebido. A comissão vai conferir." in corpo
    # O selo e a frase da FR-3746 da `118`, no lugar do sufixo "aguardando conferência".
    assert "Aguardando conferência" in corpo
    assert "A comissão vai conferir; você não precisa fazer nada agora." in corpo

    conferir(gestor, convocacao, HISTORICO, "PENDENTE", chave="pp", motivo="Falta a página 2.")
    corpo = tela(client, pessoa)
    assert "Precisa de correção: Falta a página 2. Envie um novo arquivo" in corpo
    assert "carlos" not in corpo, "a tela não diz quem conferiu (FR-3584)"
    assert not any(termo in corpo.lower() for termo in TERMOS_DE_VINCULO)


def test_o_arquivo_invalido_volta_com_a_recusa_da_inscricao(aluno, gestor, client):
    from django.core.files.uploadedfile import SimpleUploadedFile

    pessoa, convocacao = cenarios.convocar_primeira(aluno, gestor)
    entrar_como(client, pessoa)
    alvo = item(convocacao, CERTIDAO)

    client.post(
        reverse("portal:apresentar-documento-da-convocacao", args=[pessoa.id, alvo.id]),
        {"arquivo": SimpleUploadedFile("foto.jpg", b"\xff\xd8\xff", content_type="image/jpeg")},
    )

    corpo = tela(client, pessoa)
    assert 'role="alert"' in corpo
    assert not alvo.apresentacoes.exists()


def test_outro_candidato_nao_alcanca_nem_a_lista_nem_o_arquivo(aluno, gestor, client):
    edital, _, inscricoes = aluno
    pessoa, convocacao = cenarios.convocar_primeira(aluno, gestor)
    feita = apresentar(pessoa, convocacao, CERTIDAO).apresentacao
    outra = next(i for i in inscricoes if i.id != pessoa.id)
    entrar_como(client, outra)

    envio = client.post(
        reverse(
            "portal:apresentar-documento-da-convocacao",
            args=[pessoa.id, item(convocacao, CERTIDAO).id],
        ),
        {"arquivo": cenarios.pdf()},
    )
    arquivo = client.get(reverse("portal:documento-da-convocacao", args=[pessoa.id, feita.id]))
    alheio = client.get(reverse("portal:documento-da-convocacao", args=[outra.id, feita.id]))

    assert envio.status_code == 404
    assert arquivo.status_code == 404
    assert alheio.status_code == 404, "a apresentação de outra inscrição é inexistente"


def test_o_titular_ve_o_arquivo_que_apresentou(aluno, gestor, client):
    pessoa, convocacao = cenarios.convocar_primeira(aluno, gestor)
    feita = apresentar(pessoa, convocacao, CERTIDAO, corpo=b"minha certidao").apresentacao
    entrar_como(client, pessoa)

    resposta = abrir_arquivo(
        client, reverse("portal:documento-da-convocacao", args=[pessoa.id, feita.id])
    )

    assert resposta.status_code == 200
    assert b"minha certidao" in resposta.conteudo_servido
    assert "no-store" in resposta["Cache-Control"]


def test_depois_do_vencimento_a_tela_diz_o_prazo_e_nao_oferece_envio(aluno, gestor, client):
    edital, _, _ = aluno
    pessoa, convocacao = cenarios.convocar_primeira(
        aluno, gestor, vencimento=timezone.now() + timedelta(minutes=1)
    )
    comunicar(edital, gestor, convocacao)
    entrar_como(client, pessoa)

    with mock.patch("django.utils.timezone.now", return_value=timezone.now() + timedelta(days=2)):
        corpo = tela(client, pessoa)

    # O núcleo único do vencido (FR-3748 da `118`), no lugar de "A comissão vai decidir.".
    assert "O prazo terminou em" in corpo
    assert (
        "O fim do prazo não decide nada sozinho: quem registra o resultado é a comissão." in corpo
    )
    assert "A comissão vai decidir." not in corpo
    assert "Escolher arquivo PDF" not in corpo


def test_mostrar_a_lista_nao_registra_leitura_alem_da_convocacao(aluno, gestor, client):
    """FR-3613: a tela da convocação já registra a leitura dela, e a lista não acrescenta outra."""
    pessoa, convocacao = cenarios.convocar_primeira(aluno, gestor)
    entrar_como(client, pessoa)

    tela(client, pessoa)

    operacoes = set(
        RegistroAuditoria.objects.filter(actor_subject=pessoa.identity_subject).values_list(
            "operation", flat=True
        )
    )
    assert operacoes == {"CONVOCACAO_LER"}


def test_sem_documento_na_convocacao_a_tela_e_a_de_antes(
    db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos, client
):
    cenario = cenarios.montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        documentos=[cenarios.documentos_do_aluno()[0]],
        prefixo="portal-sem-115",
    )
    pessoa, _ = cenarios.convocar_primeira(cenario, gestor)
    entrar_como(client, pessoa)

    corpo = tela(client, pessoa)
    # Sem documento, a estrutura de antes (FR-3574 da `115`; FR-3743 da `118`): nenhum bloco novo.
    assert "O que fazer agora" not in corpo
    assert "<h3>O que fazer</h3>" in corpo


def test_o_certificado_da_inscricao_aparece_atendido(
    db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos, client
):
    """US3 no portal: nenhum envio, e a frase do aproveitamento."""
    cenario = cenarios.montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        documentos=cenarios.documentos_do_certificado(),
        documentos_da_inscricao=(IDENTIDADE, CERTIFICADO),
        prefixo="portal-cert-115",
    )
    pessoa, convocacao = cenarios.convocar_primeira(cenario, gestor)
    entrar_como(client, pessoa)

    corpo = tela(client, pessoa)

    # "Atendido" antes da conferência era a falsa conclusão de um item (118, FR-3746): o texto diz
    # que a pessoa já o enviou e que a comissão vai conferir. A garantia de antes continua — nenhum
    # envio, e a referência é uma só.
    assert "Você já enviou este documento na inscrição, em " in corpo
    assert "Não precisa enviar de novo. A comissão vai conferir." in corpo
    assert "tendid" not in corpo.lower()
    assert item(convocacao, CERTIFICADO_NA_CONVOCACAO).apresentacoes.count() == 1


def test_o_bolsista_baixa_o_modelo_anexo_e_nada_diz_bolsa_concedida(
    db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos, client
):
    """US2: o modelo da Ficha/Termo é oferecido na própria tela, e não há requerimento."""
    from tests.fixtures.publicacao import publish_original

    def ligar_o_modelo(edital):
        from processo_seletivo.editais.models.documentos import DocumentoExigido
        from tests.fixtures.anexos import criar_anexo

        anexo = criar_anexo(edital, rotulo="ANEXO I — FICHA E TERMO DO BOLSISTA")
        DocumentoExigido.objects.filter(edital=edital, key="ficha-termo").update(anexo=anexo)

    def com_o_modelo(api_client, manager_headers, process_payload, *, draft=None):
        return publish_original(
            api_client,
            manager_headers,
            process_payload,
            draft=draft,
            antes_de_submeter=ligar_o_modelo,
        )

    cenario = cenarios.montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        documentos=cenarios.documentos_do_bolsista(),
        prefixo="portal-bolsista-115",
        publicar=com_o_modelo,
    )
    pessoa, convocacao = cenarios.convocar_primeira(cenario, gestor)
    entrar_como(client, pessoa)

    corpo = tela(client, pessoa)

    assert "Ficha de Cadastramento e Termo de Compromisso do Bolsista" in corpo
    assert "Baixar o modelo:" in corpo
    assert "Requerimento de Matrícula" not in corpo
    assert not any(termo in corpo.lower() for termo in TERMOS_DE_VINCULO)
    assert item(convocacao, FICHA).situacao == "OBRIGATORIO"


def test_a_pendencia_sobre_o_que_nao_chegou_mostra_o_motivo(aluno, gestor, client):
    """Revisão do #369: antes, o item dizia só "Falta enviar", e o motivo sumia."""
    pessoa, convocacao = cenarios.convocar_primeira(aluno, gestor)
    conferir(gestor, convocacao, CERTIDAO, "PENDENTE", chave="pp0", motivo="Envie a de casamento.")
    entrar_como(client, pessoa)

    corpo = tela(client, pessoa)

    # O motivo continua, agora com o convite certo: não há arquivo anterior (118, cenário J).
    assert "Precisa de correção: Envie a de casamento. Envie o arquivo" in corpo
    assert "outro arquivo" not in corpo.split("Envie a de casamento.")[1].split("</p>")[0]


def test_a_pagina_publica_avisa_o_que_a_convocacao_pedira(aluno, client):
    edital, _, _ = aluno

    corpo = client.get(reverse("portal:selecao", args=[edital.id])).content.decode()

    assert "Se for convocado, a convocação pedirá também:" in corpo
    assert "Certidão de nascimento ou casamento" in corpo
