"""Linguagem, privacidade e verificação no documento (099, FR-2543, FR-2546, FR-2549 a FR-2551).

O texto conferido é o extraído do PDF: o que o relatório **diz** é o que foi desenhado.
"""

import re

import pytest

from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.interface import relatorio_pdf
from processo_seletivo.interface.relatorio_do_edital import FRASE_DE_PRIVACIDADE, Retificacao_
from processo_seletivo.publicacoes.models import DocumentoPublicado
from tests.fixtures.relatorio import REFERENCIA_ABERTA, montar_cenario
from tests.integration.relatorio.conftest import (
    SELECAO,
    executiva_e_anexo,
    ler,
    texto_do_documento,
)

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def test_nenhum_dado_pessoal_de_candidato(pendente):
    """FR-2549, SC-934: nem nome, nem CPF, nem e-mail, nem protocolo."""
    texto = texto_do_documento(ler(pendente))
    for inscricao in Inscricao.objects.filter(edital=pendente.edital):
        assert inscricao.nome not in texto
        assert inscricao.email not in texto
        if inscricao.protocolo:
            assert inscricao.protocolo not in texto
        if inscricao.cpf_normalizado:
            assert inscricao.cpf_normalizado not in re.sub(r"\D", "", texto)


def test_a_camada_executiva_nao_usa_termo_interno(pendente):
    """FR-2546: nem "aprovado" no documento inteiro; nem marco, corte ou pessoas no executivo."""
    texto = texto_do_documento(ler(pendente))
    executiva, anexo = executiva_e_anexo(texto)
    assert anexo, "o anexo técnico é composto depois da camada executiva"
    assert not re.search(r"\baprovad", texto, re.IGNORECASE)
    for termo in ("vaga ocupada", "participaram", "candidatos por vaga", "marco", "corte"):
        assert termo not in executiva.lower(), termo
    assert not re.search(r"\bpessoas?\b", executiva.replace("pessoas pretas", ""), re.IGNORECASE)


def test_fato_nao_publico_nao_cruza_com_a_lista(pendente):
    """FR-2550: a convocação pendente é dita pelo Perfil, e não pela lista reservada."""
    relatorio = ler(pendente)
    for pendencia in relatorio.pendencias:
        assert "pretas" not in pendencia
    for perfil in relatorio.perfis:
        for lista in perfil.listas:
            assert set(vars(lista)) == {"marco", "lista", "classificadas", "vagas", "natureza"}


def test_perfil_com_menos_de_cinco_inscricoes_omite_o_que_nao_e_publico(db):
    """FR-2551, D-006: o Técnico, com 3 inscrições no período aberto, tem o detalhe omitido."""
    cenario = montar_cenario(final="aberto")
    relatorio = ler(cenario, agora=REFERENCIA_ABERTA)
    tecnico = next(p for p in relatorio.perfis if p.nome == "Técnico de Laboratório")
    assert tecnico.inscricoes.valor == 3
    assert tecnico.omitido
    assert tecnico.etapas == () and tecnico.recursos is None and tecnico.convocacoes is None
    assert tecnico.rascunhos.ausencia.motivo == FRASE_DE_PRIVACIDADE
    assert FRASE_DE_PRIVACIDADE in texto_do_documento(relatorio).lower()


def test_documentos_com_resumo_endereco_e_frase_de_integridade(pendente):
    """FR-2539 e FR-2543: o resumo é o do arquivo publicado, e o endereço é clicável no PDF."""
    relatorio = ler(pendente)
    publicados = {
        d.publicacao.published_at: d.document_hash
        for d in DocumentoPublicado.objects.filter(publicacao__edital=pendente.edital)
    }
    for documento in relatorio.documentos:
        if documento.publicado_em in publicados:
            assert documento.sha256 == publicados[documento.publicado_em]
    texto = texto_do_documento(relatorio)
    assert relatorio_pdf.INTEGRIDADE.split(":")[0] in texto
    executiva, _ = executiva_e_anexo(texto)
    assert not re.search(r"\b[0-9a-f]{64}\b", executiva), "resumo no executivo"
    documento = relatorio_pdf.compor(relatorio, emissao=1)
    assert f"/URI ({SELECAO})".encode() in documento
    vigentes = [d for d in relatorio.documentos if d.resultado_vigente]
    assert documento.count(b"/S /URI") == 1 + len(vigentes)


def test_retificacao_nao_descrita_e_dita_assim(pendente):
    """Caso-limite: o que o leitor de alterações não sabe descrever não some."""
    relatorio = ler(pendente)
    original = relatorio.retificacoes[0]
    relatorio.retificacoes = [
        Retificacao_(
            numero=1,
            publicada_em=original.publicada_em,
            justificativa=original.justificativa,
            alteracoes=(),
        )
    ]
    assert "Alteração não descrita automaticamente." in texto_do_documento(relatorio)


def test_a_camada_executiva_aponta_so_os_resultados_vigentes(pendente):
    """FR-2539: o preliminar sucedido pelo definitivo não é referência; o definitivo é."""
    relatorio = ler(pendente)
    vigentes = [d.titulo for d in relatorio.documentos if d.resultado_vigente]
    assert len(vigentes) == 3
    assert all(t.startswith("Resultado definitivo") for t in vigentes)
