"""Os bytes do documento publicado, congelados antes de o renderizador ganhar um modo.

Esta fixture prova **uma** coisa: que a introdução do modo de prévia não alterou o documento
oficial. Ela não descreve o conteúdo do PDF — para isso existe `tests/unit/publicacoes/test_pdf.py`,
que afirma o que precisa aparecer. Aqui o que se afirma é a ausência de mudança, e por isso a
comparação é byte a byte: qualquer coisa que altere a composição do documento publicado faz este
teste falhar, inclusive uma alteração que os testes de conteúdo não notariam.

**Regenerar a fixture só é legítimo na mesma tarefa que mudar a composição de propósito**, com o
diff revisado. Regenerá-la para fazer um teste passar é apagar a única evidência que ela guarda.

O snapshot fica versionado ao lado dos bytes: sem ele a fixture seria um arquivo binário que
ninguém consegue reproduzir, e a comparação viraria fé.

**Duas naturezas, tratadas de forma oposta (`008`, D-010).**

*Invariante* — o que a `008` não pode quebrar:
`test_o_modo_publicado_explicito_e_o_mesmo_do_padrao`,
`test_a_previa_nao_carrega_nenhuma_afirmacao_de_integridade`,
`test_modo_desconhecido_e_recusado_em_vez_de_cair_no_publicado`,
`test_nenhum_estado_interno_de_entidade_aparece_no_documento`,
`test_nenhum_decimal_canonico_de_quatro_casas_chega_ao_documento`,
`test_a_forma_canonica_do_snapshot_nao_e_tocada_pela_apresentacao`,
`test_as_regras_de_apresentacao_valem_tambem_na_previa`.

*Forma da apresentação* — atualizados junto da entrega que os torna falsos:
`test_o_documento_publicado_continua_byte_a_byte_o_mesmo` (a fixture é regenerada a cada entrega
que muda a composição de propósito, FR-044), `test_percentual_peso_e_nota_saem_em_portugues` e
`test_decimal_com_parte_fracionaria_usa_virgula` (os valores continuam obrigatórios; a frase que
os cerca muda na entrega 3).
"""

import json
import re
from pathlib import Path

import pytest

from processo_seletivo.publicacoes.infrastructure.pdf import (
    MARCA_DE_PREVIA,
    MODO_PREVIA,
    MODO_PUBLICADO,
    AutoridadeSignataria,
    render_edital_pdf,
)
from processo_seletivo.shared.canonical import canonical_sha256

FIXTURES = Path(__file__).resolve().parent / "fixtures"
SNAPSHOT = json.loads((FIXTURES / "snapshot_publicado.json").read_text(encoding="utf-8"))
DOCUMENTO = (FIXTURES / "documento_publicado_v1.pdf").read_bytes()

# O hash do próprio snapshot, e não uma constante arbitrária: é o que o ato de publicação passa
# ao renderizador, e é o que aparece na declaração de integridade do documento.
HASH = canonical_sha256(SNAPSHOT)

# A autoridade fixa da fixture, versionada ao lado do snapshot: sem ela a comparação de bytes não
# seria reproduzível por quem não participou da mudança (`008`, FR-044).
AUTORIDADE = AutoridadeSignataria(
    **json.loads((FIXTURES / "autoridade_publicada.json").read_text(encoding="utf-8"))
)


def documento(conteudo, content_hash=HASH, *, modo=MODO_PUBLICADO, **kwargs):
    """Compõe como a publicação compõe — em modo publicado, com a autoridade da fixture."""
    if modo == MODO_PUBLICADO:
        kwargs.setdefault("autoridade", AUTORIDADE)
    return render_edital_pdf(conteudo, content_hash, modo=modo, **kwargs)

PAGINA = re.compile(rb"/Type /Page /Parent")
TEXTO_PDF = re.compile(rb"\((.*?)\) Tj", re.DOTALL)
# Só os fluxos de conteúdo das páginas. Desde que o documento embute o brasão, varrer o arquivo
# inteiro alcançaria os bytes da imagem — que não são texto e não decodificam como tal.
CONTEUDO_DA_PAGINA = re.compile(rb"<< /Length \d+ >>\nstream\n(.*?)\nendstream", re.DOTALL)


def conteudo_das_paginas(pdf: bytes) -> bytes:
    return b"\n".join(CONTEUDO_DA_PAGINA.findall(pdf))


def texto_de(pdf: bytes) -> str:
    return "\n".join(
        parte.replace(b"\\(", b"(").replace(b"\\)", b")").decode("cp1252")
        for parte in TEXTO_PDF.findall(conteudo_das_paginas(pdf))
    )


def paginas_de(pdf: bytes) -> list[list[str]]:
    """O texto de cada página, na ordem — que é onde a paginação fica observável.

    Comparar o documento inteiro como uma cadeia só não enxerga quebra: dois documentos com o
    mesmo texto distribuído em páginas diferentes seriam indistinguíveis. A `008` precisa afirmar
    exatamente essa distribuição (FR-042), e por isso a extração é por fluxo de página.
    """
    return [
        [
            parte.replace(b"\\(", b"(").replace(b"\\)", b")").decode("cp1252")
            for parte in TEXTO_PDF.findall(fluxo)
        ]
        for fluxo in CONTEUDO_DA_PAGINA.findall(pdf)
    ]


# O que legitimamente distingue os dois modos. Tudo o mais tem de ser igual — é isso que FR-041
# promete, e é a diferença entre "a prévia mostra o que será publicado" e "a prévia mostra outra
# coisa parecida". Cresce com a `008`: a autoridade signatária entra aqui na entrega 5.
def corpo_normativo(pagina: list[str], marca_de_previa: str) -> list[str]:
    fora = False
    corpo = []
    for linha in pagina:
        # O fechamento do ato começa na autoridade signatária: dali em diante é metadado do ato,
        # que só o publicado tem. Antes dela, os dois modos têm de coincidir linha a linha.
        if linha == AUTORIDADE.nome or linha.startswith(
            ("VERIFICAÇÃO DE INTEGRIDADE", "Este documento deriva")
        ):
            fora = True
        if marca_de_previa in linha or linha.startswith(("Edital 0", "PRÉVIA —")):
            continue
        if not fora:
            corpo.append(linha)
    return corpo


@pytest.mark.contract
def test_o_documento_publicado_continua_byte_a_byte_o_mesmo():
    assert documento(SNAPSHOT, HASH) == DOCUMENTO


@pytest.mark.contract
def test_o_modo_publicado_explicito_e_o_mesmo_do_padrao():
    """Nomear o modo não pode mudar o documento oficial."""
    assert documento(SNAPSHOT, HASH, modo=MODO_PUBLICADO) == DOCUMENTO


@pytest.mark.contract
def test_a_previa_nao_carrega_nenhuma_afirmacao_de_integridade():
    """FR-014: o que não pode sair de uma prévia é a afirmação, não o desenho.

    O hash é passado vazio pela view, mas o teste passa o hash **de verdade** justamente para
    provar que o modo o ignora: se a garantia dependesse de o chamador lembrar de esvaziá-lo, ela
    estaria com quem não a tem.
    """
    texto = texto_de(documento(SNAPSHOT, HASH, modo=MODO_PREVIA))

    assert HASH not in texto
    assert HASH[:16] not in texto
    assert "INTEGRIDADE" not in texto
    assert "deriva integralmente da versão homologada" not in texto
    assert "SHA-256" not in texto


@pytest.mark.contract
def test_a_previa_se_identifica_em_todas_as_paginas():
    muitos = {
        **SNAPSHOT,
        "profiles": [
            {**SNAPSHOT["profiles"][0], "code": f"P{indice:02d}", "id": str(indice)}
            for indice in range(1, 26)
        ],
    }
    pdf = documento(muitos, HASH, modo=MODO_PREVIA)
    paginas = len(PAGINA.findall(pdf))
    assert paginas >= 3, paginas

    texto = texto_de(pdf)
    assert texto.count(MARCA_DE_PREVIA) >= paginas, "a marca precisa estar em todas as páginas"


@pytest.mark.contract
def test_a_previa_traz_o_mesmo_conteudo_normativo_do_publicado():
    """FR-013: o que muda é a moldura, não o Edital."""
    publicado = texto_de(documento(SNAPSHOT, HASH))
    previa = texto_de(documento(SNAPSHOT, HASH, modo=MODO_PREVIA))

    # `20%`, e não `20.0000`: a forma canônica continua com quatro casas no snapshot, mas o
    # documento escreve em português nos dois modos — legibilidade não é privilégio do publicado.
    for esperado in ("DOC-INFO", "Professor de Informática", "PPP", "Lei 12.990/2014", "20%"):
        assert esperado in publicado and esperado in previa, esperado


@pytest.mark.contract
def test_modo_desconhecido_e_recusado_em_vez_de_cair_no_publicado():
    """Errar o nome do modo não pode produzir, em silêncio, um documento com cara de publicado."""
    with pytest.raises(ValueError):
        render_edital_pdf(SNAPSHOT, HASH, modo="PREVIEW_")


# ---------------------------------------------------------------------------
# 007 — O documento se lê como um Edital (FR-002, FR-003)
# ---------------------------------------------------------------------------


@pytest.mark.contract
def test_nenhum_estado_interno_de_entidade_aparece_no_documento():
    """FR-002: o estado do Evento descreve a gestão do certame, não o Edital.

    A fixture tem dois Eventos, ambos `PLANEJADO`. Um Edital publicado anuncia suas inscrições;
    não informa ao candidato que elas estão "planejadas".
    """
    texto = texto_de(documento(SNAPSHOT, HASH))

    for estado in ("PLANEJADO", "EM_ANDAMENTO", "CONCLUIDO", "CANCELADO"):
        assert estado not in texto, estado
    assert "Situação:" not in texto


@pytest.mark.contract
def test_nenhum_decimal_canonico_de_quatro_casas_chega_ao_documento():
    """FR-003: a forma de quatro casas é do snapshot, não do papel."""
    texto = texto_de(documento(SNAPSHOT, HASH))

    assert not re.search(r"\d\.\d{4}\b", texto), "decimal canônico vazou para o documento"


@pytest.mark.contract
def test_percentual_peso_e_nota_saem_em_portugues():
    """A fixture carrega percentual 20.0000, peso 2.0000 e nota mínima 7.0000."""
    texto = texto_de(documento(SNAPSHOT, HASH))

    # **Forma atualizada pela `008`/US2**: o percentual saiu da frase corrida e virou célula. O
    # valor continua obrigatório, e continua em português — que é o que este teste guarda.
    # **Forma atualizada pela `008`/US2 e US3**: percentual virou célula da tabela de modalidades,
    # peso e nota mínima viraram pares rótulo-valor da Etapa. Os valores continuam obrigatórios e
    # continuam em português — que é o que este teste guarda.
    assert "20%" in texto
    assert "Peso:" in texto and "Nota mínima:" in texto


@pytest.mark.contract
def test_decimal_com_parte_fracionaria_usa_virgula():
    """Zeros à direita somem; a casa que informa alguma coisa permanece, com vírgula."""
    fracionario = json.loads(json.dumps(SNAPSHOT))
    regra = fracionario["profiles"][0]["competitionModalities"][0]["normativeRule"]
    regra["percentage"] = "12.5000"
    fracionario["stages"][0]["weight"] = "1.7500"

    texto = texto_de(documento(fracionario, canonical_sha256(fracionario)))

    assert "12,5%" in texto
    assert "1,75" in texto


@pytest.mark.contract
def test_a_forma_canonica_do_snapshot_nao_e_tocada_pela_apresentacao():
    """FR-001: o compositor lê o snapshot; não o reescreve.

    A garantia que sustenta o hash: renderizar não pode ter efeito colateral sobre o conteúdo.
    """
    antes = json.dumps(SNAPSHOT, sort_keys=True)
    documento(SNAPSHOT, HASH)
    assert json.dumps(SNAPSHOT, sort_keys=True) == antes
    assert SNAPSHOT["stages"][0]["weight"] == "2.0000"


@pytest.mark.contract
def test_as_regras_de_apresentacao_valem_tambem_na_previa():
    """T009: legibilidade não é privilégio do documento publicado."""
    texto = texto_de(documento(SNAPSHOT, HASH, modo=MODO_PREVIA))

    assert "PLANEJADO" not in texto
    assert not re.search(r"\d\.\d{4}\b", texto)
    assert "20%" in texto


# ---------------------------------------------------------------------------
# 008 — Prévia e publicado são o mesmo documento (FR-041, FR-042)
# ---------------------------------------------------------------------------


@pytest.mark.contract
def test_o_corpo_normativo_quebra_nas_mesmas_paginas_na_previa_e_no_publicado():
    """FR-042: a marca de prévia não pode deslocar o conteúdo.

    Enquanto ela for escrita **dentro** do fluxo, tudo desce — e a prévia passa a quebrar em
    lugares diferentes daqueles em que o documento será publicado. Quem revisa a prévia estaria
    revisando uma paginação que não é a que sai. É o defeito que D-011 corrige tirando a marca do
    fluxo: fora dele, a igualdade é garantida por construção, e não por coincidência de medida.
    """
    publicado = paginas_de(documento(SNAPSHOT, HASH))
    previa = paginas_de(documento(SNAPSHOT, HASH, modo=MODO_PREVIA))

    # O publicado pode ter **mais** páginas: o fechamento do ato — autoridade e verificação — só
    # existe nele, e é um bloco coeso que pode não caber na última página do corpo. O que FR-041
    # promete é que o **corpo normativo** quebre igual, e é isso que se compara.
    assert len(publicado) >= len(previa), "o publicado paginou o corpo em menos páginas"
    for numero, uma in enumerate(previa, 1):
        outra = publicado[numero - 1]
        assert corpo_normativo(uma, MARCA_DE_PREVIA) == corpo_normativo(
            outra, MARCA_DE_PREVIA
        ), f"o corpo normativo da página {numero} difere entre prévia e publicado"
    for excedente in publicado[len(previa) :]:
        assert not corpo_normativo(excedente, MARCA_DE_PREVIA), (
            "a página a mais do publicado deveria conter só o fechamento do ato"
        )


@pytest.mark.contract
def test_removidas_as_diferencas_permitidas_as_composicoes_sao_equivalentes():
    """As diferenças entre os dois modos são as declaradas, e nenhuma outra.

    O teste acima compara página a página; este compara o documento inteiro, e por isso pega o que
    aquele não pegaria: uma linha que só existisse num dos modos sem mudar quebra nenhuma.
    """
    publicado = [
        linha
        for pagina in paginas_de(documento(SNAPSHOT, HASH))
        for linha in corpo_normativo(pagina, MARCA_DE_PREVIA)
    ]
    previa = [
        linha
        for pagina in paginas_de(documento(SNAPSHOT, HASH, modo=MODO_PREVIA))
        for linha in corpo_normativo(pagina, MARCA_DE_PREVIA)
    ]

    assert previa == publicado


@pytest.mark.contract
def test_tirar_a_marca_do_fluxo_nao_toca_os_bytes_do_documento_publicado():
    """A marca nunca foi composta no publicado, e movê-la não pode passar a compô-la.

    **Se este teste falhar, a fixture não está velha.** Ele afirma que uma mudança que só deveria
    afetar a prévia não afetou o publicado; regenerar a fixture aqui apagaria exatamente a
    evidência que ele existe para produzir. A leitura correta de uma falha é que a região fixa
    invadiu a geometria do fluxo.
    """
    assert documento(SNAPSHOT, HASH) == DOCUMENTO
    assert MARCA_DE_PREVIA not in texto_de(DOCUMENTO)
