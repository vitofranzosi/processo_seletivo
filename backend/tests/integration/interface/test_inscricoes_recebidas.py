"""A consulta administrativa do que chegou (US6 da 009, FR-066 a FR-070).

É a metade institucional do objetivo: sem ela o sistema recebe e a equipe continua baixando tudo
para o Drive. O que se prova aqui é o que substitui a planilha — e o que **não** aparece, porque a
`009` termina em "recebido e consultável".
"""

import pytest
from django.urls import reverse

from processo_seletivo.inscricoes.application.rascunho import anexar_documento, gravar_dados
from processo_seletivo.inscricoes.application.submissao import enviar_inscricao
from processo_seletivo.inscricoes.models import DocumentoSubmetido
from tests.fixtures.candidato import MARIA, MODALIDADE_AC, pdf
from tests.fixtures.selecao import DOCUMENTO_DE_TODOS, DOCUMENTO_DO_PERFIL
from tests.interface.conftest import identificar


@pytest.fixture
def inscricao_enviada(inscricao_de_maria):
    inscricao = gravar_dados(
        identidade=MARIA, inscricao=inscricao_de_maria, dados={"modality_id": MODALIDADE_AC}
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
        idempotency_key="envio-consulta",
    )


@pytest.fixture
def gestor(client, settings):
    settings.INTERFACE_SELETOR_IDENTIDADE = True
    identificar(client, "bruno.gestor", ["gestor"])
    return client


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_lista_mostra_o_total_e_as_colunas_minimas(gestor, selecao, inscricao_enviada):
    corpo = gestor.get(reverse("interface:inscricoes", args=[selecao.id])).content.decode()

    assert "Inscrições — 1" in corpo
    assert inscricao_enviada.protocolo in corpo
    assert "Maria Silva" in corpo
    assert "Professor de Informática" in corpo
    assert "Ampla concorrência" in corpo
    assert "2 de 2" in corpo, "recebidos dos esperados **daquela** inscrição"
    assert "Enviada em" in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_cpf_aparece_mascarado_e_os_digitos_ocultos_nao_estao_no_html(
    gestor, selecao, inscricao_enviada
):
    """FR-073: seis dígitos bastam para conferir contra um documento em mãos."""
    corpo = gestor.get(reverse("interface:inscricoes", args=[selecao.id])).content.decode()

    assert "***.456.789-**" in corpo
    assert "123.456.789-09" not in corpo
    assert "12345678909" not in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_detalhe_agrupa_cada_documento_sob_o_requisito(gestor, inscricao_enviada):
    corpo = gestor.get(
        reverse("interface:inscricao-recebida", args=[inscricao_enviada.id])
    ).content.decode()

    identificacao = corpo.index("Documento de identificação")
    diploma = corpo.index("Diploma de graduação")
    assert identificacao < corpo.index("rg.pdf") < diploma, "cada arquivo sob o seu requisito"
    assert "diploma.pdf" in corpo
    assert "Versão do Edital aceita" in corpo, "sob qual regra a pessoa se inscreveu (FR-068)"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_requisito_sem_arquivo_aparece_como_nao_apresentado(gestor, inscricao_de_maria):
    """Requisito sem arquivo é informação — não uma linha que some."""
    corpo = gestor.get(
        reverse("interface:inscricao-recebida", args=[inscricao_de_maria.id])
    ).content.decode()

    assert "Não apresentado" in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_documento_abre_no_navegador_e_o_download_e_secundario(gestor, inscricao_enviada):
    endereco = reverse(
        "interface:documento-da-inscricao", args=[inscricao_enviada.id, DOCUMENTO_DE_TODOS]
    )

    inline = gestor.get(endereco)
    anexo = gestor.get(f"{endereco}?baixar=1")

    assert inline.headers["Content-Type"] == "application/pdf"
    assert "inline" in inline.headers["Content-Disposition"]
    assert "no-store" in inline.headers["Cache-Control"]
    assert "attachment" in anexo.headers["Content-Disposition"]
    inline.close()
    anexo.close()


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_as_telas_nao_sao_armazenaveis_pelo_navegador(gestor, selecao, inscricao_enviada):
    lista = gestor.get(reverse("interface:inscricoes", args=[selecao.id]))
    detalhe = gestor.get(reverse("interface:inscricao-recebida", args=[inscricao_enviada.id]))

    assert "no-store" in lista.headers["Cache-Control"]
    assert "no-store" in detalhe.headers["Cache-Control"]


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_edital_oferece_inscricoes_depois_de_publicado(gestor, selecao, inscricao_enviada):
    corpo = gestor.get(reverse("interface:detalhe", args=[selecao.id])).content.decode()

    assert "Inscrições recebidas" in corpo
    assert reverse("interface:inscricoes", args=[selecao.id]) in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_nenhuma_tela_oferece_avaliacao(gestor, selecao, inscricao_enviada):
    """FR-070: a `009` termina em "recebido e consultável"; a próxima jornada é que avalia."""
    proibidos = (
        "Deferir",
        "Indeferir",
        "deferimento",
        "Nota",
        "Parecer",
        "Classificação",
        "Baixar todos",
        "Exportar",
    )
    telas = (
        gestor.get(reverse("interface:inscricoes", args=[selecao.id])),
        gestor.get(reverse("interface:inscricao-recebida", args=[inscricao_enviada.id])),
    )

    for tela in telas:
        corpo = tela.content.decode()
        for proibido in proibidos:
            assert proibido not in corpo, f"{proibido} pertence à jornada da comissão, não a esta"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_arquivo_corrompido_no_disco_nao_e_entregue_como_integro(
    gestor, inscricao_enviada, raiz_de_arquivos
):
    """FR-053a: o resumo é verificado, e a conferência acontece **antes** de sair um byte.

    Uma vez enviados, os bytes não voltam: descobrir a divergência no meio do arquivo deixaria
    quem consulta com meio documento e nenhuma explicação.
    """
    from processo_seletivo.auditoria.models import RegistroAuditoria

    documento = DocumentoSubmetido.objects.get(requirement_id=DOCUMENTO_DE_TODOS)
    (raiz_de_arquivos / documento.arquivo.name).write_bytes(b"%PDF-1.4\noutro conteudo")

    resposta = gestor.get(
        reverse("interface:documento-da-inscricao", args=[inscricao_enviada.id, DOCUMENTO_DE_TODOS])
    )

    assert resposta.status_code == 409
    assert b"%PDF" not in resposta.content, "nem um byte do arquivo divergente"
    assert "não confere" in resposta.content.decode()
    assert RegistroAuditoria.objects.filter(operation="INTEGRIDADE").exists(), "o fato é registrado"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_rascunho_nao_conta_como_inscricao_recebida(
    gestor, selecao, inscricao_enviada, inscricao_de_maria
):
    """FR-066: o total é do que foi **entregue**.

    Um rascunho aberto e abandonado não foi recebido por ninguém. Somá-lo faria o painel anunciar
    centenas de inscrições numa seleção que recebeu dezenas — e a decisão de quem conduz a seleção
    ("já dá para começar a conferir?") passa por esse número.
    """
    from processo_seletivo.inscricoes.application.rascunho import abrir_inscricao
    from tests.fixtures.candidato import JOAO, PERFIL_DOCENTE

    abrir_inscricao(identidade=JOAO, edital_id=selecao.id, profile_id=PERFIL_DOCENTE)
    corpo = gestor.get(reverse("interface:inscricoes", args=[selecao.id])).content.decode()

    assert "Inscrições — 1" in corpo, "uma enviada, um rascunho — o total é das enviadas"
    assert "Em preenchimento — 1" in corpo, "o rascunho continua visível, sob o nome do que é"
    assert corpo.index("Inscrições recebidas neste Edital") < corpo.index(
        "Rascunhos em preenchimento"
    ), "o que chegou vem primeiro"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_acao_do_edital_conta_apenas_as_inscricoes_enviadas(
    gestor, selecao, inscricao_enviada, inscricao_de_maria
):
    """O rótulo diz "recebidas", e o número precisa concordar com a lista que ele abre."""
    corpo = gestor.get(reverse("interface:lista")).content.decode()

    assert "Inscrições recebidas (1)" in corpo
    assert "Inscrições recebidas (2)" not in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_tabela_larga_rola_dentro_de_si_mesma(gestor, selecao, inscricao_enviada):
    """Sete colunas não cabem em 375px, e sem contêiner a **página** inteira rola na horizontal."""
    corpo = gestor.get(reverse("interface:inscricoes", args=[selecao.id])).content.decode()

    assert '<div class="tabela-rolavel">' in corpo
    assert ".tabela-rolavel{overflow-x:auto}" in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_abrir_documento_de_candidato_deixa_rastro(gestor, inscricao_enviada):
    """L10 da auditoria de percurso: quem abriu o documento de quem.

    FR-077 audita os atos do candidato e dispensa a consulta pública; sobre a consulta
    administrativa a spec é silenciosa, e o silêncio deixava o sistema sem resposta para a
    pergunta que uma auditoria de dados pessoais faz primeiro. Documento de candidato inclui
    autodeclaração étnico-racial — dado sensível, e acesso a dado sensível deixa rastro.
    """
    from processo_seletivo.auditoria.models import RegistroAuditoria

    resposta = gestor.get(
        reverse("interface:documento-da-inscricao", args=[inscricao_enviada.id, DOCUMENTO_DE_TODOS])
    )

    assert resposta.status_code == 200
    conteudo = b"".join(resposta.streaming_content)
    resposta.close()

    assert conteudo.startswith(b"%PDF")
    registro = RegistroAuditoria.objects.get(operation="CONSULTAR_DOCUMENTO")
    assert registro.aggregate_id == inscricao_enviada.id
    assert str(DOCUMENTO_DE_TODOS) in registro.reason
    assert "rg.pdf" not in registro.reason, "o nome do arquivo é do candidato, não da trilha"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_quem_confere_ve_tamanho_e_resumo_de_cada_arquivo(gestor, inscricao_enviada):
    """O sistema já confere sozinho a cada abertura e recusa o que divergir.

    Isto é o que permite a quem confere afirmar o mesmo **por fora**: comparar o arquivo que tem em
    mãos com o que foi recebido, sem depender do sistema — e é o mesmo resumo que vai no
    comprovante do candidato.
    """
    documento = DocumentoSubmetido.objects.get(requirement_id=DOCUMENTO_DE_TODOS)

    corpo = gestor.get(
        reverse("interface:inscricao-recebida", args=[inscricao_enviada.id])
    ).content.decode()

    assert documento.content_hash in corpo
    assert "SHA-256" in corpo
    assert "bytes" in corpo or "KB" in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_quem_confere_ve_o_mesmo_codigo_do_comprovante(gestor, inscricao_enviada):
    """É comparando os dois que se recusa um papel alterado.

    O comprovante é um HTML impresso: qualquer pessoa edita a página antes de imprimir. Sem um
    código calculado pelo servidor, conferir significaria ler linha por linha.
    """
    from processo_seletivo.inscricoes.domain.autenticidade import codigo_de_verificacao

    esperado = codigo_de_verificacao(
        inscricao_enviada, DocumentoSubmetido.objects.filter(inscricao=inscricao_enviada)
    )

    corpo = gestor.get(
        reverse("interface:inscricao-recebida", args=[inscricao_enviada.id])
    ).content.decode()

    assert esperado in corpo
    assert "Código de verificação" in corpo
