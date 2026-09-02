"""`Minha inscrição` — o que o sistema recebeu, conferido sem redigitar e sem reenviar nada.

A promessa da US4 é essa: a pessoa abre a inscrição enviada e vê exatamente o que chegou. Sem ela,
o candidato continua guardando cópias por fora, porque não confia no que enviou — que é o problema
que a `009` resolveu pela metade.
"""

import pytest
from django.urls import reverse

from processo_seletivo.inscricoes.application.rascunho import anexar_documento, gravar_dados
from processo_seletivo.inscricoes.application.submissao import enviar_inscricao
from processo_seletivo.inscricoes.models import DocumentoSubmetido, Inscricao
from tests.fixtures.candidato import MARIA, MODALIDADE_AC, identificar, pdf
from tests.fixtures.selecao import DOCUMENTO_DE_TODOS, DOCUMENTO_DO_PERFIL

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def enviada(inscricao_de_maria):
    inscricao = gravar_dados(
        identidade=MARIA,
        inscricao=inscricao_de_maria,
        dados={"modality_id": MODALIDADE_AC, "telefone": "(27) 99999-0000"},
    )
    for requisito, nome in ((DOCUMENTO_DE_TODOS, "rg.pdf"), (DOCUMENTO_DO_PERFIL, "diploma.pdf")):
        anexar_documento(
            identidade=MARIA, inscricao=inscricao, requirement_id=requisito, arquivo=pdf(nome)
        )
    inscricao.refresh_from_db()
    return enviar_inscricao(
        identidade=MARIA,
        inscricao=inscricao,
        declaracoes={"veracidade": True, "ciencia": True},
        idempotency_key="envio-conferencia",
    )


def abrir(client, inscricao):
    identificar(client, MARIA)
    return client.get(reverse("portal:inscricao", args=[inscricao.id])).content.decode()


def test_a_tela_traz_o_que_foi_enviado(client, enviada):
    corpo = abrir(client, enviada)

    assert "✓ Inscrição enviada" in corpo
    assert enviada.protocolo in corpo
    assert "Maria Silva" in corpo
    assert "99999-0000" in corpo


def test_a_tela_traz_os_documentos_com_nome_tamanho_e_instante(client, enviada):
    corpo = abrir(client, enviada)

    assert "rg.pdf" in corpo and "diploma.pdf" in corpo
    assert "Visualizar" in corpo and "Baixar" in corpo
    assert "enviado em" in corpo


def test_cada_documento_diz_qual_requisito_atende(client, enviada):
    """Um documento **é** o requisito que ele atende (P-006 da `009`).

    Esta asserção existe porque a sua ausência deixou passar um defeito: o nome do requisito era
    renderizado em branco sobre branco, porque o cartão reusava uma classe que na `009` é um botão
    de fundo sólido. O teste afirmava o nome do arquivo, que continuava visível — e o rótulo que
    diz o que aquele arquivo **é** tinha sumido da tela.
    """
    from processo_seletivo.inscricoes.application.rascunho import requisitos_da_inscricao

    versao = enviada.versao_aceita
    nomes = [
        requisito.get("name", "")
        for requisito in requisitos_da_inscricao(versao.content, enviada)
    ]
    corpo = abrir(client, enviada)

    assert nomes, "o teste pressupõe requisitos declarados no conteúdo publicado"
    for nome in nomes:
        assert nome in corpo, nome


def test_a_tela_traz_a_versao_aceita(client, enviada):
    corpo = abrir(client, enviada)
    assert "Versão do Edital" in corpo


def test_enviada_nao_abre_o_formulario_de_edicao(client, enviada):
    """Enviada não se edita (FR-075): a tela deixa de oferecer o que não pode acontecer."""
    corpo = abrir(client, enviada)

    assert "<select" not in corpo
    assert 'name="telefone"' not in corpo
    assert "Enviar inscrição" not in corpo


def test_o_comprovante_continua_a_um_clique(client, enviada):
    corpo = abrir(client, enviada)
    assert reverse("portal:comprovante", args=[enviada.id]) in corpo
    assert "Baixar comprovante" in corpo


def test_a_integridade_existe_e_fica_recolhida(client, enviada):
    """Ela permanece disponível, e não vira protagonista da tela (FR-072, FR-073)."""
    corpo = abrir(client, enviada)

    assert "<details" in corpo
    assert "Ver dados de integridade" in corpo
    resumo = DocumentoSubmetido.objects.filter(inscricao=enviada).first().content_hash
    assert resumo in corpo


def test_visualizar_entrega_o_arquivo_vigente(client, enviada):
    identificar(client, MARIA)
    resposta = client.get(
        reverse("portal:documento-do-candidato", args=[enviada.id, DOCUMENTO_DE_TODOS])
    )

    assert resposta.status_code == 200
    assert b"".join(resposta.streaming_content).startswith(b"%PDF")
    assert "attachment" not in resposta.get("Content-Disposition", "")


def test_baixar_entrega_o_mesmo_arquivo_como_anexo(client, enviada):
    identificar(client, MARIA)
    ver = client.get(
        reverse("portal:documento-do-candidato", args=[enviada.id, DOCUMENTO_DE_TODOS])
    )
    endereco = reverse("portal:documento-do-candidato", args=[enviada.id, DOCUMENTO_DE_TODOS])
    baixar = client.get(f"{endereco}?baixar=1")

    assert b"".join(ver.streaming_content) == b"".join(baixar.streaming_content)
    assert "attachment" in baixar["Content-Disposition"]
    assert "rg.pdf" in baixar["Content-Disposition"]


def test_visualizar_e_baixar_nao_alteram_a_inscricao(client, enviada):
    antes = Inscricao.objects.values().get(pk=enviada.pk)
    identificar(client, MARIA)

    endereco = reverse("portal:documento-do-candidato", args=[enviada.id, DOCUMENTO_DE_TODOS])
    for resposta in (client.get(endereco), client.get(f"{endereco}?baixar=1")):
        # Consumir e fechar: `FileResponse` mantém o arquivo aberto até alguém drená-lo, e o
        # projeto trata descritor pendurado como erro — ver os filtros de aviso do `pyproject`.
        b"".join(resposta.streaming_content)
        resposta.close()
    client.get(reverse("portal:inscricao", args=[enviada.id]))

    assert Inscricao.objects.values().get(pk=enviada.pk) == antes
