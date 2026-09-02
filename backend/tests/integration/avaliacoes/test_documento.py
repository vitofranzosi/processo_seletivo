"""O documento como instrumento de trabalho: mediado, conferido e auditado (US3).

A mecânica é a que a 009 construiu, e a `012` a reutiliza inteira — o que ela **não** reutiliza é a
permissão. Aqui os três invariantes que a spec cobra: cada abertura deixa rastro, divergência de
integridade é recusa registrada, e não existe caminho de lote.
"""

import pytest
from django.urls import reverse

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.avaliacoes.application.distribuicao import distribuir
from processo_seletivo.avaliacoes.application.mesa import BASE_DA_MESA
from processo_seletivo.avaliacoes.models import Atribuicao
from processo_seletivo.inscricoes.application.consulta import CONSULTAR
from processo_seletivo.inscricoes.models import DocumentoSubmetido
from tests.fixtures.comissao import DOCUMENTO_A, abrir_arquivo, alocar_em, inscrever
from tests.fixtures.edital import identificador
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


@pytest.fixture
def cenario(raiz_de_arquivos, gestor, processo_a, edital_com_documentos, comissao_de_a, etapa_a1):
    membro = comissao_de_a["joao"]
    alocar_em(gestor, processo_a, membro, edital_com_documentos, etapa_a1)
    inscricao = inscrever(edital_com_documentos, 1, documentos=[identificador(DOCUMENTO_A, 0)])[0]
    distribuir(
        actor=gestor,
        processo_id=processo_a.id,
        edital_id=edital_com_documentos.id,
        etapa_id=etapa_a1,
        membro_ids=[membro.id],
        inscricao_ids=[inscricao.id],
        idempotency_key="doc",
        correlation_id="teste",
    )
    return inscricao


@pytest.fixture
def como_joao(client, seletor_ligado):
    identificar(client, "joao", [])
    return client


def arquivo(edital, etapa_id, inscricao):
    return reverse(
        "interface:mesa-documento",
        args=[edital.id, etapa_id, inscricao.id, identificador(DOCUMENTO_A, 0)],
    )


def test_cada_abertura_registra_ator_etapa_inscricao_e_requisito(
    como_joao, edital_com_documentos, etapa_a1, cenario
):
    """FR-027 e FR-053. E a base registrada é a da Mesa: ela diz **por que** o acesso foi dado.

    O agregado é a **Atribuição**, e não a Inscrição, porque o registro precisa identificar quatro
    coisas — quem, qual inscrição, qual Etapa e por qual vínculo — e a Inscrição identifica uma.
    """
    abrir_arquivo(como_joao, arquivo(edital_com_documentos, etapa_a1, cenario))

    evento = RegistroAuditoria.objects.get(operation="CONSULTAR_DOCUMENTO")
    assert evento.actor_subject == "joao"
    assert evento.aggregate_type == "Atribuicao"
    atribuicao = Atribuicao.objects.get(pk=evento.aggregate_id)
    assert atribuicao.inscricao_id == cenario.id
    assert str(atribuicao.etapa_id) == str(etapa_a1)
    assert atribuicao.membro.identity_subject == "joao"
    assert str(identificador(DOCUMENTO_A, 0)) in evento.reason
    assert evento.permission == BASE_DA_MESA
    assert evento.permission != CONSULTAR


def test_a_abertura_da_mesa_nao_se_confunde_com_a_consulta_administrativa(
    como_joao, client, gestor, seletor_ligado, edital_com_documentos, etapa_a1, cenario
):
    """As duas registram `CONSULTAR_DOCUMENTO` sobre a mesma inscrição — e não são o mesmo ato.

    Enquanto o agregado da abertura era a Inscrição, os dois eventos eram indistinguíveis por
    identificador, e a trilha da Etapa exibia a consulta administrativa da 009 como se fosse
    trabalho da Mesa. Um histórico que mistura origens é pior que um incompleto: parece verdadeiro.
    """
    abrir_arquivo(como_joao, arquivo(edital_com_documentos, etapa_a1, cenario))
    identificar(client, "carlos", ["gestor"])
    abrir_arquivo(
        client,
        reverse(
            "interface:documento-da-inscricao",
            args=[cenario.id, identificador(DOCUMENTO_A, 0)],
        ),
    )

    por_agregado = {
        evento.aggregate_type
        for evento in RegistroAuditoria.objects.filter(operation="CONSULTAR_DOCUMENTO")
    }
    assert por_agregado == {"Atribuicao", "Inscricao"}


def test_a_trilha_nao_guarda_o_nome_do_arquivo(como_joao, edital_com_documentos, etapa_a1, cenario):
    """O requisito basta para saber o que foi aberto; o nome do arquivo é do candidato (FR-054)."""
    abrir_arquivo(como_joao, arquivo(edital_com_documentos, etapa_a1, cenario))

    evento = RegistroAuditoria.objects.get(operation="CONSULTAR_DOCUMENTO")
    assert "documento.pdf" not in evento.reason


def test_divergencia_de_integridade_e_recusa_registrada(
    como_joao, edital_com_documentos, etapa_a1, cenario
):
    """FR-029, EC-008: não é aviso silencioso — é recusa, e ela fica na trilha.

    O que sustenta "o que o avaliador abre é o que o candidato enviou" precisa falhar alto quando
    deixa de ser verdade.
    """
    documento = DocumentoSubmetido.objects.get(inscricao=cenario)
    with documento.arquivo.storage.open(documento.arquivo.name, "wb") as destino:
        destino.write(b"%PDF-1.4\nconteudo trocado")

    resposta = abrir_arquivo(como_joao, arquivo(edital_com_documentos, etapa_a1, cenario))

    assert resposta.status_code == 409
    assert RegistroAuditoria.objects.filter(operation="INTEGRIDADE").count() == 1
    assert not RegistroAuditoria.objects.filter(operation="CONSULTAR_DOCUMENTO").exists()


def test_o_arquivo_servido_e_o_conferido(como_joao, edital_com_documentos, etapa_a1, cenario):
    """Os bytes conferidos e os bytes servidos são os **mesmos bytes**, e não o mesmo caminho.

    Conferir o arquivo e reabri-lo para servir deixaria uma janela entre as duas leituras, e uma
    verificação que aprova um conteúdo e serve outro é pior do que verificação nenhuma (FR-029).
    """
    import hashlib

    resposta = abrir_arquivo(como_joao, arquivo(edital_com_documentos, etapa_a1, cenario))

    documento = DocumentoSubmetido.objects.get(inscricao=cenario)
    assert hashlib.sha256(resposta.conteudo_servido).hexdigest() == documento.content_hash


def test_as_duas_respostas_nao_sao_armazenaveis(
    como_joao, edital_com_documentos, etapa_a1, cenario
):
    """Página **e** arquivo: a página carrega dado pessoal, e não só o anexo (FR-056)."""
    pagina = como_joao.get(
        reverse("interface:mesa-inscricao", args=[edital_com_documentos.id, etapa_a1, cenario.id])
    )
    anexo = abrir_arquivo(como_joao, arquivo(edital_com_documentos, etapa_a1, cenario))

    assert "no-store" in pagina["Cache-Control"]
    assert "no-store" in anexo["Cache-Control"]


def test_a_lista_e_a_dos_requisitos_e_nao_a_dos_arquivos(
    como_joao, edital_com_documentos, etapa_a1, cenario
):
    """Requisito sem arquivo aparece como requisito sem arquivo — é informação (FR-025)."""
    corpo = como_joao.get(
        reverse("interface:mesa-inscricao", args=[edital_com_documentos.id, etapa_a1, cenario.id])
    ).content.decode()

    assert "Documento de identificação" in corpo
    assert "Não apresentado" in corpo


def test_nao_existe_caminho_de_lote(como_joao, edital_com_documentos, etapa_a1, cenario):
    """FR-028: a ausência é o requisito.

    Não existe download em lote, exportação do acervo nem navegação por inscrição alheia — e é
    disso que a feature existe para tirar a equipe.
    """
    corpo = como_joao.get(
        reverse("interface:mesa-inscricao", args=[edital_com_documentos.id, etapa_a1, cenario.id])
    ).content.decode()

    for proibido in ("baixar todos", "Baixar todos", "exportar", "Exportar", ".zip"):
        assert proibido not in corpo


def test_o_dado_pessoal_exibido_e_o_minimo(como_joao, edital_com_documentos, etapa_a1, cenario):
    """FR-030: o necessário ao trabalho, e nada além.

    O nome fica — avaliação cega está fora do escopo, e meia anonimização é pior que nenhuma. O
    CPF vai mascarado, e e-mail e telefone não aparecem: não decidem avaliação nenhuma.
    """
    corpo = como_joao.get(
        reverse("interface:mesa-inscricao", args=[edital_com_documentos.id, etapa_a1, cenario.id])
    ).content.decode()

    assert cenario.nome in corpo
    assert cenario.cpf not in corpo
    assert cenario.email not in corpo
