"""Documentos e conferência na convocação, pelos serviços (115, US1, US3, US4).

O que se prova, na ordem da jornada:

- a raiz da chamada grava a lista, e a sucessora não grava outra (FR-3572, FR-3573);
- o documento da inscrição declarado aproveitado atende o item sem cópia (FR-3576, SC-1083);
- o titular apresenta, em versões, com as recusas da inscrição (FR-3577 a FR-3583);
- a conferência julga a versão vigente e exige abri-la para o "conforme" (FR-3585 a FR-3589,
  FR-3611);
- o aceite espera os obrigatórios conferidos, e nenhum desfecho nasce do vencimento (FR-3592 a
  FR-3594, SC-1086).
"""

import re
from datetime import timedelta
from unittest import mock

import pytest
from django.db import IntegrityError, ProgrammingError, connection, transaction
from django.utils import timezone

from processo_seletivo.convocacao.application import documentos as servico
from processo_seletivo.convocacao.domain import nomes
from processo_seletivo.convocacao.models import (
    ApresentacaoDeDocumento,
    ConferenciaDeDocumento,
    DesfechoDaConvocacao,
    ItemDaListaDaConvocacao,
)
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures import documentos_da_convocacao as cenarios
from tests.fixtures.documentos_da_convocacao import (
    CERTIDAO,
    CERTIFICADO,
    CERTIFICADO_DO_MEDIO,
    CERTIFICADO_NA_CONVOCACAO,
    HISTORICO,
    IDENTIDADE,
    RESIDENCIA,
    abrir,
    apresentar,
    arquivos_no_armazenamento,
    comunicar,
    conferir,
    convocar_primeira,
    desfechar,
    item,
    lido,
)

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


@pytest.fixture
def aluno(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    return cenarios.montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        documentos=cenarios.documentos_do_aluno(),
        prefixo="aluno-115",
    )


@pytest.fixture
def certificado_enviado(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    """Todas as inscritas enviaram o certificado na inscrição."""
    return cenarios.montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        documentos=cenarios.documentos_do_certificado(),
        documentos_da_inscricao=(IDENTIDADE, CERTIFICADO),
        prefixo="certificado-115",
    )


@pytest.fixture
def certificado_nao_enviado(
    db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos
):
    return cenarios.montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        documentos=cenarios.documentos_do_certificado(),
        documentos_da_inscricao=(IDENTIDADE,),
        prefixo="certificado-sem-115",
    )


def _corrigir(edital, gestor, pessoa, **kwargs):
    """A correção da convocação por sucessão: a **mesma** pessoa, com motivo."""
    from processo_seletivo.convocacao.models import Convocacao
    from tests.fixtures.convocacao import convocar

    declarado = convocar(edital, gestor, pessoa.id, idempotency_key=kwargs.pop("chave"), **kwargs)
    return Convocacao.objects.get(id=declarado["id"])


# --- a lista ------------------------------------------------------------------------------------


def test_a_raiz_da_chamada_grava_um_item_por_documento_da_convocacao(aluno, gestor):
    _, convocacao = convocar_primeira(aluno, gestor)

    itens = {str(i.requisito_id): i for i in convocacao.itens_da_lista.all()}

    assert set(itens) == {CERTIDAO, HISTORICO, CERTIFICADO_DO_MEDIO, RESIDENCIA}
    assert IDENTIDADE not in itens, "o documento da inscrição não entra na lista da convocação"
    assert {i.situacao for i in itens.values()} == {"OBRIGATORIO"}
    assert all(i.gravada_em == convocacao.criado_em for i in itens.values())
    assert all(i.versao_id == convocacao.versao_id for i in itens.values())


def test_a_sucessora_que_corrige_nao_grava_outra_lista(aluno, gestor):
    """D-009: corrigir o vencimento não refaz a lista, e o que foi apresentado continua com ela."""
    edital, _, _ = aluno
    pessoa, convocacao = convocar_primeira(aluno, gestor)
    apresentar(pessoa, convocacao, CERTIDAO)

    sucessora = _corrigir(
        edital,
        gestor,
        pessoa,
        chave="corrigir-115",
        motivo="Vencimento informado errado.",
        vencimento=timezone.now() + timedelta(days=5),
    )

    assert sucessora.convocacao_anterior_id == convocacao.id
    assert not sucessora.itens_da_lista.exists()
    assert servico.raiz_da_chamada(sucessora) == convocacao
    assert lido(sucessora, CERTIDAO).estado == nomes.ITEM_RECEBIDO


def test_sem_documento_na_convocacao_a_lista_fica_vazia(
    db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos
):
    """FR-3574: o Edital de antes continua sendo o Edital de antes."""
    cenario = cenarios.montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        documentos=[cenarios.documentos_do_aluno()[0]],
        prefixo="sem-115",
    )
    _, convocacao = convocar_primeira(cenario, gestor)

    assert not convocacao.itens_da_lista.exists()
    leitura = servico.leitura_da_chamada(convocacao)
    assert leitura.estado == nomes.DOCUMENTOS_SEM_EXIGENCIA
    assert leitura.pendencias_para_incluir == []


def test_o_item_da_lista_e_append_only(aluno, gestor):
    _, convocacao = convocar_primeira(aluno, gestor)
    linha = convocacao.itens_da_lista.first()

    with pytest.raises(TypeError):
        linha.save()
    with pytest.raises(TypeError):
        linha.delete()
    if connection.vendor == "postgresql":
        with pytest.raises(ProgrammingError), transaction.atomic():
            ItemDaListaDaConvocacao.objects.filter(pk=linha.pk).update(chave="outra")


# --- o aproveitamento ---------------------------------------------------------------------------


def test_o_certificado_enviado_na_inscricao_atende_a_convocacao_sem_copia(
    certificado_enviado, gestor, raiz_de_arquivos
):
    """SC-1083: a mesma identidade de arquivo, o mesmo hash, e nenhum arquivo novo."""
    pessoa, convocacao = convocar_primeira(certificado_enviado, gestor)
    arquivos_antes = arquivos_no_armazenamento(raiz_de_arquivos)

    alvo = lido(convocacao, CERTIFICADO_NA_CONVOCACAO)

    referencia = alvo.vigente
    original = pessoa.documentos.get(requirement_id=CERTIFICADO)
    assert referencia.documento_da_inscricao_id == original.id
    assert not referencia.arquivo
    assert referencia.content_hash == original.content_hash
    assert alvo.estado == nomes.ITEM_RECEBIDO
    assert alvo.aproveitada["de"] == "inscricao"
    assert arquivos_no_armazenamento(raiz_de_arquivos) == arquivos_antes


def test_sem_o_certificado_na_inscricao_o_item_nasce_a_apresentar(certificado_nao_enviado, gestor):
    _, convocacao = convocar_primeira(certificado_nao_enviado, gestor)

    assert lido(convocacao, CERTIFICADO_NA_CONVOCACAO).estado == nomes.ITEM_A_APRESENTAR


def test_o_arquivo_novo_sucede_a_referencia(certificado_enviado, gestor):
    pessoa, convocacao = convocar_primeira(certificado_enviado, gestor)

    nova = apresentar(pessoa, convocacao, CERTIFICADO_NA_CONVOCACAO, corpo=b"certificado novo")

    alvo = lido(convocacao, CERTIFICADO_NA_CONVOCACAO)
    assert [a.numero for a in alvo.apresentacoes] == [1, 2]
    assert alvo.vigente.id == nova.apresentacao.id
    assert alvo.apresentacoes[0].documento_da_inscricao_id is not None


def test_a_referencia_a_documento_de_outra_inscricao_e_recusada_pelo_banco(
    certificado_enviado, gestor
):
    if connection.vendor != "postgresql":
        pytest.skip("a coerência entre tabelas é do gatilho do PostgreSQL")
    edital, _, inscricoes = certificado_enviado
    pessoa, convocacao = convocar_primeira(certificado_enviado, gestor)
    outra = next(i for i in inscricoes if i.id != pessoa.id)
    alheio = outra.documentos.get(requirement_id=CERTIFICADO)
    alvo = item(convocacao, CERTIFICADO_NA_CONVOCACAO)

    with pytest.raises(ProgrammingError), transaction.atomic():
        ApresentacaoDeDocumento.objects.create(
            item=alvo,
            numero=9,
            documento_da_inscricao=alheio,
            content_hash=alheio.content_hash,
            apresentado_por="forjado",
            unidade_de_atuacao="cefor",
            apresentado_em=timezone.now(),
        )


# --- a apresentação -----------------------------------------------------------------------------


def test_o_titular_apresenta_e_cada_envio_e_uma_versao(aluno, gestor):
    pessoa, convocacao = convocar_primeira(aluno, gestor)

    primeira = apresentar(pessoa, convocacao, HISTORICO, corpo=b"historico 1")
    segunda = apresentar(pessoa, convocacao, HISTORICO, corpo=b"historico 2")

    alvo = lido(convocacao, HISTORICO)
    assert [a.numero for a in alvo.apresentacoes] == [1, 2]
    assert alvo.vigente.id == segunda.apresentacao.id
    assert primeira.apresentacao.arquivo.name != segunda.apresentacao.arquivo.name
    assert "documento" not in primeira.apresentacao.arquivo.name.rsplit("/", 1)[-1]


def test_o_mesmo_arquivo_de_novo_nao_cria_versao(aluno, gestor):
    """FR-3581: o duplo clique e a requisição repetida devolvem o que já foi recebido."""
    pessoa, convocacao = convocar_primeira(aluno, gestor)

    primeira = apresentar(pessoa, convocacao, CERTIDAO, corpo=b"certidao")
    repetida = apresentar(pessoa, convocacao, CERTIDAO, corpo=b"certidao")

    assert repetida.ja_recebido
    assert repetida.apresentacao.id == primeira.apresentacao.id
    assert item(convocacao, CERTIDAO).apresentacoes.count() == 1


def test_duas_apresentacoes_com_o_mesmo_numero_sao_recusadas_pelo_banco(aluno, gestor):
    pessoa, convocacao = convocar_primeira(aluno, gestor)
    feita = apresentar(pessoa, convocacao, CERTIDAO).apresentacao

    with pytest.raises(IntegrityError), transaction.atomic():
        ApresentacaoDeDocumento.objects.create(
            item=feita.item,
            numero=feita.numero,
            arquivo=feita.arquivo.name,
            content_hash="0" * 64,
            apresentado_por="forjado",
            unidade_de_atuacao="cefor",
            apresentado_em=timezone.now(),
        )


@pytest.mark.parametrize(
    "corpo, nome, codigo",
    [
        (b"\x89PNG\r\n", "foto.png", "file_not_pdf"),
        (b"\xff\xd8\xff", "documento.pdf", "file_is_an_image"),
        (b"", "vazio.pdf", "file_empty"),
    ],
)
def test_o_arquivo_invalido_e_recusado_com_as_recusas_da_inscricao(
    aluno, gestor, corpo, nome, codigo
):
    from django.core.files.uploadedfile import SimpleUploadedFile

    pessoa, convocacao = convocar_primeira(aluno, gestor)
    arquivo = SimpleUploadedFile(nome, corpo, content_type="application/octet-stream")

    with pytest.raises(DomainError) as recusa:
        servico.apresentar(
            identidade=cenarios.Titular(pessoa),
            inscricao_id=pessoa.id,
            item_id=item(convocacao, CERTIDAO).id,
            arquivo=arquivo,
            nome_original=nome,
            correlation_id="teste-115",
        )
    assert recusa.value.code == codigo
    assert not item(convocacao, CERTIDAO).apresentacoes.exists()


def test_o_arquivo_acima_do_limite_e_recusado(aluno, gestor, settings):
    settings.ARQUIVOS_CANDIDATOS_LIMITE_BYTES = 20
    pessoa, convocacao = convocar_primeira(aluno, gestor)

    with pytest.raises(DomainError) as recusa:
        apresentar(pessoa, convocacao, CERTIDAO, corpo=b"x" * 100)
    assert recusa.value.code == "file_too_large"


def test_outro_candidato_recebe_a_recusa_de_inexistente(aluno, gestor):
    """FR-3600: inscrição alheia é indistinguível de inexistente."""
    edital, _, inscricoes = aluno
    pessoa, convocacao = convocar_primeira(aluno, gestor)
    outra = next(i for i in inscricoes if i.id != pessoa.id)

    with pytest.raises(DomainError) as recusa:
        servico.apresentar(
            identidade=cenarios.Titular(outra),
            inscricao_id=pessoa.id,
            item_id=item(convocacao, CERTIDAO).id,
            arquivo=cenarios.pdf(),
            nome_original="documento.pdf",
            correlation_id="teste-115",
        )
    assert recusa.value.status == 404


def test_depois_do_vencimento_a_apresentacao_e_recusada_e_nada_e_gravado(aluno, gestor):
    edital, _, _ = aluno
    pessoa, convocacao = convocar_primeira(
        aluno, gestor, vencimento=timezone.now() + timedelta(minutes=1)
    )
    comunicar(edital, gestor, convocacao)

    with mock.patch("django.utils.timezone.now", return_value=timezone.now() + timedelta(days=2)):
        with pytest.raises(DomainError) as recusa:
            apresentar(pessoa, convocacao, CERTIDAO)

    assert recusa.value.code == nomes.PRAZO_DA_CONVOCACAO_DECORRIDO
    # O núcleo único do vencido (FR-3748 da `118`), o mesmo da recusa do Requerimento.
    assert recusa.value.detail == servico.frase_do_prazo_decorrido(convocacao)
    assert recusa.value.detail.endswith(
        "O fim do prazo não decide nada sozinho: quem registra o resultado é a comissão."
    )
    assert re.match(r"O prazo terminou em \d\d/\d\d/\d{4}, às \d\dh\d\d\.", recusa.value.detail)
    assert not item(convocacao, CERTIDAO).apresentacoes.exists()


def test_com_o_processo_encerrado_a_recusa_nao_diz_que_o_prazo_venceu(aluno, gestor):
    """M: com o Processo em estado final, a recusa é a do Processo, e não o núcleo do vencido.

    Mesmo com o vencimento decorrido junto, vale o Processo (D-015 da `118`): a frase do vencido
    diria que a comissão ainda registra o resultado, e com o Processo encerrado ninguém registra.
    """
    from processo_seletivo.processos.models import ProcessoSeletivo

    edital, _, _ = aluno
    pessoa, convocacao = convocar_primeira(
        aluno, gestor, vencimento=timezone.now() + timedelta(minutes=1)
    )
    comunicar(edital, gestor, convocacao)
    ProcessoSeletivo.objects.filter(editais__id=edital.id).update(
        status=ProcessoSeletivo.Status.ENCERRADO
    )

    for agora in (timezone.now(), timezone.now() + timedelta(days=2)):
        with mock.patch("django.utils.timezone.now", return_value=agora):
            with pytest.raises(DomainError) as recusa:
                apresentar(pessoa, convocacao, CERTIDAO)
        assert recusa.value.code != nomes.PRAZO_DA_CONVOCACAO_DECORRIDO
        assert "prazo terminou" not in recusa.value.detail.lower()
        assert "não decide nada sozinho" not in recusa.value.detail
    assert not item(convocacao, CERTIDAO).apresentacoes.exists()


def test_antes_do_envio_da_comunicacao_a_apresentacao_e_aceita(aluno, gestor):
    """D-011: o prazo não corre sem a comunicação, e o envio antecipado não prejudica ninguém."""
    pessoa, convocacao = convocar_primeira(
        aluno, gestor, vencimento=timezone.now() + timedelta(minutes=1)
    )

    with mock.patch("django.utils.timezone.now", return_value=timezone.now() + timedelta(days=2)):
        feita = apresentar(pessoa, convocacao, CERTIDAO)

    assert feita.apresentacao.numero == 1


def test_a_apresentacao_nao_toca_a_inscricao_enviada(aluno, gestor):
    """FR-3583: a inscrição enviada continua imutável, documento a documento."""
    pessoa, convocacao = convocar_primeira(aluno, gestor)
    antes = list(pessoa.documentos.values_list("id", "content_hash"))

    apresentar(pessoa, convocacao, CERTIDAO)

    assert list(pessoa.documentos.values_list("id", "content_hash")) == antes


# --- a conferência ------------------------------------------------------------------------------


def test_conforme_exige_ter_aberto_a_versao_vigente(aluno, gestor):
    """D-012, aprovada: a abertura vale para aquela versão e para quem a abriu."""
    pessoa, convocacao = convocar_primeira(aluno, gestor)
    apresentar(pessoa, convocacao, CERTIDAO, corpo=b"v1")
    abrir(gestor, item(convocacao, CERTIDAO).apresentacoes.get(numero=1))
    apresentar(pessoa, convocacao, CERTIDAO, corpo=b"v2")

    with pytest.raises(DomainError) as recusa:
        conferir(gestor, convocacao, CERTIDAO, "CONFORME", chave="c1", abrir_antes=False)
    assert recusa.value.code == nomes.CONFORME_SEM_ABERTURA

    conferencia = conferir(gestor, convocacao, CERTIDAO, "CONFORME", chave="c2")
    assert conferencia.apresentacao.numero == 2
    assert conferencia.hash_conferido == conferencia.apresentacao.content_hash
    assert conferencia.unidade_de_atuacao == gestor.institution_scope


def test_pendente_exige_motivo_e_o_motivo_volta_ao_estado(aluno, gestor):
    pessoa, convocacao = convocar_primeira(aluno, gestor)
    apresentar(pessoa, convocacao, HISTORICO)

    with pytest.raises(DomainError) as recusa:
        conferir(gestor, convocacao, HISTORICO, "PENDENTE", chave="p0")
    assert recusa.value.code == nomes.MOTIVO_DA_CONFERENCIA_OBRIGATORIO

    conferir(gestor, convocacao, HISTORICO, "PENDENTE", chave="p1", motivo="Falta a página 2.")
    assert lido(convocacao, HISTORICO).estado == nomes.ITEM_PENDENTE

    apresentar(pessoa, convocacao, HISTORICO, corpo=b"historico completo")
    assert lido(convocacao, HISTORICO).estado == nomes.ITEM_COMPLEMENTADO


def test_nao_se_aplica_sem_apresentacao_com_motivo(aluno, gestor):
    _, convocacao = convocar_primeira(aluno, gestor)

    conferir(
        gestor, convocacao, RESIDENCIA, "NAO_SE_APLICA", chave="n1", motivo="Mora no exterior."
    )

    assert lido(convocacao, RESIDENCIA).estado == nomes.ITEM_NAO_SE_APLICA


def test_conferencia_sobre_versao_superada_e_recusada(aluno, gestor):
    pessoa, convocacao = convocar_primeira(aluno, gestor)
    primeira = apresentar(pessoa, convocacao, CERTIDAO, corpo=b"v1").apresentacao
    apresentar(pessoa, convocacao, CERTIDAO, corpo=b"v2")
    abrir(gestor, primeira)

    with pytest.raises(DomainError) as recusa:
        conferir(
            gestor,
            convocacao,
            CERTIDAO,
            "CONFORME",
            chave="sup",
            abrir_antes=False,
            apresentacao_id=primeira.id,
        )
    assert recusa.value.code == nomes.VERSAO_SUPERADA
    assert not ConferenciaDeDocumento.objects.exists()


def test_mudar_a_conferencia_da_mesma_versao_exige_motivo(aluno, gestor):
    pessoa, convocacao = convocar_primeira(aluno, gestor)
    apresentar(pessoa, convocacao, CERTIDAO)
    conferir(gestor, convocacao, CERTIDAO, "CONFORME", chave="m1")

    with pytest.raises(DomainError) as recusa:
        conferir(gestor, convocacao, CERTIDAO, "PENDENTE", chave="m2", motivo="Ilegível.")
    assert recusa.value.code == nomes.MOTIVO_DA_SUBSTITUICAO_OBRIGATORIO

    conferir(
        gestor,
        convocacao,
        CERTIDAO,
        "PENDENTE",
        chave="m3",
        motivo="Ilegível.",
        motivo_da_substituicao="Revisto ao conferir de novo.",
    )
    assert lido(convocacao, CERTIDAO).estado == nomes.ITEM_PENDENTE
    assert ConferenciaDeDocumento.objects.count() == 2


def test_a_conferencia_continua_depois_do_vencimento(aluno, gestor):
    """FR-3588: o que chegou no prazo é julgado depois dele."""
    edital, _, _ = aluno
    pessoa, convocacao = convocar_primeira(
        aluno, gestor, vencimento=timezone.now() + timedelta(minutes=1)
    )
    comunicar(edital, gestor, convocacao)
    apresentar(pessoa, convocacao, CERTIDAO)

    with mock.patch("django.utils.timezone.now", return_value=timezone.now() + timedelta(days=2)):
        conferencia = conferir(gestor, convocacao, CERTIDAO, "CONFORME", chave="depois")

    assert conferencia.resultado == "CONFORME"


def test_a_conferencia_e_append_only(aluno, gestor):
    pessoa, convocacao = convocar_primeira(aluno, gestor)
    apresentar(pessoa, convocacao, CERTIDAO)
    conferencia = conferir(gestor, convocacao, CERTIDAO, "CONFORME", chave="ao")

    with pytest.raises(TypeError):
        conferencia.save()
    with pytest.raises(TypeError):
        conferencia.delete()


# --- o desfecho ---------------------------------------------------------------------------------


def _tudo_conforme(pessoa, convocacao, gestor, requisitos):
    for indice, requisito in enumerate(requisitos):
        apresentar(pessoa, convocacao, requisito, corpo=f"documento {indice}".encode())
        conferir(gestor, convocacao, requisito, "CONFORME", chave=f"tudo-{indice}")


def test_o_aceite_espera_os_obrigatorios_conferidos(aluno, gestor):
    """US1 de ponta a ponta nos serviços: envio, pendência, complementação, conformidade, aceite."""
    edital, _, _ = aluno
    pessoa, convocacao = convocar_primeira(aluno, gestor)
    _tudo_conforme(pessoa, convocacao, gestor, [CERTIDAO, CERTIFICADO_DO_MEDIO, RESIDENCIA])
    apresentar(pessoa, convocacao, HISTORICO, corpo=b"sem a pagina 2")
    conferir(gestor, convocacao, HISTORICO, "PENDENTE", chave="h1", motivo="Falta a página 2.")

    with pytest.raises(DomainError) as recusa:
        desfechar(edital, gestor, convocacao, nomes.ACEITE, "aceite-cedo")
    assert recusa.value.code == nomes.DOCUMENTOS_NAO_CONFERIDOS
    assert "Histórico escolar do ensino médio" in recusa.value.detail
    assert not DesfechoDaConvocacao.objects.filter(convocacao=convocacao).exists()

    apresentar(pessoa, convocacao, HISTORICO, corpo=b"historico completo")
    conferir(gestor, convocacao, HISTORICO, "CONFORME", chave="h2")
    desfechar(edital, gestor, convocacao, nomes.ACEITE, "aceite")

    assert DesfechoDaConvocacao.objects.get(convocacao=convocacao).especie == nomes.ACEITE
    assert servico.leitura_da_chamada(convocacao, decidida=True).estado == nomes.DOCUMENTOS_DECIDIDA


def test_os_outros_desfechos_nao_dependem_dos_documentos(aluno, gestor):
    """FR-3593: o indeferimento, a desistência e a reclassificação não leem o estado documental."""
    edital, _, _ = aluno
    _, convocacao = convocar_primeira(aluno, gestor)

    desfechar(edital, gestor, convocacao, nomes.INDEFERIMENTO, "indeferir", "Não apresentou.")

    assert DesfechoDaConvocacao.objects.get(convocacao=convocacao).especie == nomes.INDEFERIMENTO


def test_o_fundamento_do_indeferimento_vem_das_pendencias(aluno, gestor):
    pessoa, convocacao = convocar_primeira(aluno, gestor)
    apresentar(pessoa, convocacao, HISTORICO)
    conferir(gestor, convocacao, HISTORICO, "PENDENTE", chave="f1", motivo="Falta a página 2.")

    texto = servico.leitura_da_chamada(convocacao).fundamento_do_indeferimento()

    assert "Histórico escolar do ensino médio: Falta a página 2." in texto
    assert "Certidão de nascimento ou casamento" in texto


def test_o_vencimento_nao_produz_desfecho(aluno, gestor):
    """SC-1086: com o prazo vencido e a pendência aberta, nada nasce sem gesto."""
    edital, _, _ = aluno
    pessoa, convocacao = convocar_primeira(
        aluno, gestor, vencimento=timezone.now() + timedelta(minutes=1)
    )
    comunicar(edital, gestor, convocacao)
    apresentar(pessoa, convocacao, HISTORICO)
    conferir(gestor, convocacao, HISTORICO, "PENDENTE", chave="v1", motivo="Falta a página 2.")

    with mock.patch("django.utils.timezone.now", return_value=timezone.now() + timedelta(days=9)):
        servico.leitura_da_chamada(convocacao)

    assert not DesfechoDaConvocacao.objects.filter(convocacao=convocacao).exists()


def test_a_correcao_com_vencimento_novo_reabre_a_apresentacao(aluno, gestor):
    """FR-3618: dar mais prazo é corrigir a convocação, e a lista continua a mesma."""
    edital, _, _ = aluno
    pessoa, convocacao = convocar_primeira(
        aluno, gestor, vencimento=timezone.now() + timedelta(minutes=1)
    )
    comunicar(edital, gestor, convocacao)
    depois = timezone.now() + timedelta(days=2)
    with mock.patch("django.utils.timezone.now", return_value=depois):
        with pytest.raises(DomainError):
            apresentar(pessoa, convocacao, CERTIDAO)
        sucessora = _corrigir(
            edital,
            gestor,
            pessoa,
            chave="mais-prazo",
            motivo="Prazo reaberto por decisão da comissão.",
            vencimento=depois + timedelta(days=3),
        )
        comunicar(edital, gestor, sucessora, chave="comunicar-de-novo")
        feita = apresentar(pessoa, convocacao, CERTIDAO)

    assert feita.apresentacao.item.chamada_id == convocacao.id


# --- os limites ---------------------------------------------------------------------------------


def test_edital_encerrado_com_convocacao_em_aberto_continua_recebendo_e_conferindo(aluno, gestor):
    """FR-3616: a feature não muda o encerramento da `113`; a chamada em aberto segue como o
    desfecho segue."""
    from processo_seletivo.processos.models import Edital

    edital, _, _ = aluno
    pessoa, convocacao = convocar_primeira(aluno, gestor)
    Edital.objects.filter(pk=edital.pk).update(status=Edital.Status.ENCERRADO)

    apresentar(pessoa, convocacao, CERTIDAO)
    conferencia = conferir(gestor, convocacao, CERTIDAO, "CONFORME", chave="encerrado")

    assert conferencia.resultado == "CONFORME"


def test_o_documento_da_inscricao_aproveitado_nao_sai_com_a_referencia(certificado_enviado, gestor):
    """FR-3579 e FR-3615: a referência protege o que aponta, e nada se exclui."""
    from django.db.models import ProtectedError

    pessoa, convocacao = convocar_primeira(certificado_enviado, gestor)
    referencia = lido(convocacao, CERTIFICADO_NA_CONVOCACAO).vigente

    from processo_seletivo.inscricoes.models import DocumentoSubmetido

    with pytest.raises((ProtectedError, TypeError)):
        DocumentoSubmetido.objects.get(pk=referencia.documento_da_inscricao_id).delete()
    with pytest.raises(TypeError):
        referencia.delete()


# --- a revisão do #369 --------------------------------------------------------------------------


def test_pendencia_sobre_o_que_nao_chegou_e_pendencia(aluno, gestor):
    """O motivo de uma pendência registrada antes de qualquer envio é o que a pessoa precisa ler."""
    _, convocacao = convocar_primeira(aluno, gestor)

    conferir(
        gestor, convocacao, CERTIDAO, "PENDENTE", chave="sem-envio", motivo="Envie a de casamento."
    )

    assert lido(convocacao, CERTIDAO).estado == nomes.ITEM_PENDENTE
    assert servico.leitura_da_chamada(convocacao).estado == nomes.DOCUMENTOS_COM_PENDENCIA


def test_sem_versao_indicada_a_conferencia_julga_a_vigente(aluno, gestor):
    pessoa, convocacao = convocar_primeira(aluno, gestor)
    feita = apresentar(pessoa, convocacao, CERTIDAO).apresentacao

    conferencia = servico.conferir(
        actor=gestor,
        item_id=item(convocacao, CERTIDAO).id,
        apresentacao_id=None,
        resultado="PENDENTE",
        motivo="Ilegível.",
        idempotency_key="sem-versao",
        correlation_id="teste-115",
    )

    assert conferencia.apresentacao_id == feita.id
    assert lido(convocacao, CERTIDAO).estado == nomes.ITEM_PENDENTE


def test_o_documento_ja_conferido_nao_recebe_outro_arquivo(aluno, gestor):
    pessoa, convocacao = convocar_primeira(aluno, gestor)
    apresentar(pessoa, convocacao, CERTIDAO, corpo=b"v1")
    conferir(gestor, convocacao, CERTIDAO, "CONFORME", chave="ja-conforme")

    with pytest.raises(DomainError) as recusa:
        apresentar(pessoa, convocacao, CERTIDAO, corpo=b"v2")

    assert recusa.value.code == nomes.DOCUMENTO_JA_CONFERIDO
    assert item(convocacao, CERTIDAO).apresentacoes.count() == 1
    assert lido(convocacao, CERTIDAO).estado == nomes.ITEM_CONFORME


def test_processo_em_estado_final_nao_recebe_documento(aluno, gestor):
    from processo_seletivo.processos.models import ProcessoSeletivo

    edital, _, _ = aluno
    pessoa, convocacao = convocar_primeira(aluno, gestor)
    ProcessoSeletivo.objects.filter(pk=edital.processo_id).update(
        status=ProcessoSeletivo.Status.ENCERRADO
    )

    with pytest.raises(DomainError):
        apresentar(pessoa, convocacao, CERTIDAO)
    assert not item(convocacao, CERTIDAO).apresentacoes.exists()


def test_as_raizes_de_varias_convocacoes_saem_sem_subir_elo_a_elo(aluno, gestor):
    from django.db import connection
    from django.test.utils import CaptureQueriesContext

    edital, _, _ = aluno
    pessoa, convocacao = convocar_primeira(aluno, gestor)
    sucessora = _corrigir(
        edital, gestor, pessoa, chave="raizes", motivo="Corrigir o fundamento.", vencimento=None
    )
    from processo_seletivo.convocacao.models import Convocacao

    sucessora = Convocacao.objects.get(pk=sucessora.pk)
    with CaptureQueriesContext(connection) as consultas:
        raizes = servico.raizes_das([sucessora, convocacao])

    assert raizes[sucessora.id].id == convocacao.id
    assert raizes[convocacao.id].id == convocacao.id
    assert len(consultas) == 1


def test_a_leitura_le_a_versao_uma_vez_e_nao_consulta_ao_mostrar_a_conferencia(aluno, gestor):
    """Revisão do #369: a junção trazia o conteúdo inteiro do Edital em cada linha de item, e a
    página dos documentos perguntava ao banco a versão julgada de cada conferência."""
    from django.db import connection
    from django.test.utils import CaptureQueriesContext

    pessoa, convocacao = convocar_primeira(aluno, gestor)
    for requisito in (CERTIDAO, HISTORICO):
        apresentar(pessoa, convocacao, requisito, corpo=str(requisito).encode())
        conferir(
            gestor, convocacao, requisito, "PENDENTE", chave=f"v-{requisito}", motivo="Ilegível."
        )

    with CaptureQueriesContext(connection) as consultas:
        leitura = servico.leitura_da_chamada(convocacao)
    import re

    # A coluna `content`, e não `content_hash`: a versão é lida numa consulta própria, uma vez, e
    # não repetida em cada linha de item.
    versoes = [q["sql"] for q in consultas if re.search(r'\."content"[ ,]', q["sql"])]
    assert len(versoes) == 1, versoes
    assert 'FROM "convocacao_itemdalistadaconvocacao"' not in versoes[0]

    with CaptureQueriesContext(connection) as depois:
        numeros = [c.apresentacao.numero for lido in leitura.itens for c in lido.conferencias]
    assert numeros == [1, 1]
    assert len(depois) == 0
