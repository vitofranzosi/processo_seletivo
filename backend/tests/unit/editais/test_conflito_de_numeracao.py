"""O subitem digitado com número de outra seção (065, User Story 1).

O texto das seções é transcrito do Word, com a numeração do original; o número da seção é calculado
(`054`, FR-985). Quando os dois divergem, o documento oficial imprime "3.1" dentro da seção 4. Este
arquivo prende a conferência sobre o snapshot: o que é conflito comprovado (FR-1200), o que é
suspeita (FR-1201), o que a mensagem diz (FR-1214 a FR-1217) e os casos-limite da spec.
"""

import json
from pathlib import Path

import pytest

from processo_seletivo.editais.domain import secoes
from processo_seletivo.editais.domain.validation import (
    ATO_DE_PUBLICACAO,
    ATO_DE_RETIFICACAO,
    CONFLITO_DE_NUMERACAO,
    CONFLITO_DE_NUMERACAO_NA_RETIFICACAO,
    TITULO_TRANSCRITO,
    Severity,
    validate_for_publication,
)
from processo_seletivo.publicacoes.infrastructure import pdf

RAIZ = Path(__file__).resolve().parents[4]
CONGELADOS = RAIZ / "doc" / "auditoria-edital-pdf-2026-10-08" / "snapshots"
CODIGOS = {CONFLITO_DE_NUMERACAO, CONFLITO_DE_NUMERACAO_NA_RETIFICACAO, TITULO_TRANSCRITO}


def _secoes(**redigidas):
    return [
        {
            "id": f"00000000-0000-0000-0000-{secao.order:012d}",
            "key": secao.key,
            "title": secao.title,
            "order": secao.order,
            "type": secao.type,
            **(
                {"source": secao.source}
                if secao.gerada
                else {"content": redigidas.get(secao.key.replace("-", "_"), "")}
            ),
        }
        for secao in secoes.CATALOGO
    ]


def _conteudo(**redigidas):
    """Só seções textuais: a numeração é a das que têm texto, na ordem do catálogo."""
    return {"schemaVersion": 17, "sections": _secoes(**redigidas)}


# Três seções antes da Inscrição: "Da Inscrição" sai como 4.
ANTES = {
    "disposicoes_preliminares": "O processo seletivo será conduzido pela Comissão.",
    "informacoes_gerais": "O curso é a distância.",
    "publico_alvo": "Graduados.",
}
INSCRICAO_DO_ORIGINAL = (
    "3.1 A inscrição será realizada exclusivamente pelo sistema de inscrições.\n"
    "3.2 O candidato deverá anexar, em arquivo PDF único, os documentos obrigatórios.\n"
    "3.3 Não haverá conferência de documentação no momento da inscrição.\n"
    "3.4 O candidato que enviar documentação incompleta terá a inscrição indeferida."
)


def _achados(conteudo, ato=ATO_DE_PUBLICACAO):
    return [
        achado for achado in validate_for_publication(conteudo, ato=ato) if achado.code in CODIGOS
    ]


def _congelado(nome):
    return json.loads((CONGELADOS / nome).read_text(encoding="utf-8"))["content"]


# --- o conflito comprovado (FR-1200, FR-1214, FR-1215, FR-1217) ------------------------------


def test_subitens_de_outra_secao_sao_um_conflito_comprovado_e_impeditivo():
    achados = _achados(_conteudo(**ANTES, inscricao=INSCRICAO_DO_ORIGINAL))
    assert len(achados) == 1, "um achado por seção, e não um por parágrafo"
    achado = achados[0]
    assert achado.code == CONFLITO_DE_NUMERACAO
    assert achado.severity == Severity.BLOCKING_ERROR
    assert achado.path == "/sections/id=00000000-0000-0000-0000-000000000007/content"
    mensagem = achado.message
    assert "comprovado" in mensagem
    assert "«Da Inscrição»" in mensagem
    assert "como 4" in mensagem
    for ordinal, numero in ((1, "3.1"), (2, "3.2"), (3, "3.3"), (4, "3.4")):
        assert f"parágrafo {ordinal}" in mensagem
        assert f"«{numero} " in mensagem
    assert "«3.1 A inscrição será realizada exclusivamente pelo sistema de inscrições.»" in mensagem
    assert "começam por 4" in mensagem


def test_subitens_da_propria_secao_nao_sao_conflito():
    texto = "2.1 Ser brasileiro.\n2.2 Estar quite com as obrigações eleitorais."
    conteudo = _conteudo(disposicoes_preliminares="Texto.", informacoes_gerais=texto)
    assert _achados(conteudo) == []


def test_subitem_no_preambulo_e_conflito():
    conteudo = _conteudo(apresentacao="A Diretora torna público.\n1.1 O processo será conduzido.")
    [achado] = _achados(conteudo)
    assert achado.code == CONFLITO_DE_NUMERACAO
    assert "O preâmbulo sai no documento sem número" in achado.message
    assert "parágrafo 2" in achado.message


def test_a_mensagem_nao_tem_codigo_caminho_nem_campo():
    [achado] = _achados(_conteudo(**ANTES, inscricao=INSCRICAO_DO_ORIGINAL))
    for interno in ("typed_numbering", "/sections", "content", "id="):
        assert interno not in achado.message


# --- os casos-limite (Edge Cases da spec) ----------------------------------------------------


def test_secao_misturada_acusa_so_os_de_outra_secao():
    """Subitens de três seções do original na mesma seção do catálogo — o caso do 89/2026."""
    provisorio = _conteudo(**ANTES, inscricao="Texto.", recursos="Texto.", convocacao="Texto.")
    numero = pdf.numeracao_impressa(provisorio)["convocacao"]
    texto = f"{numero + 1}.1 Primeiro.\n8.1 Segundo.\n{numero}.1 Terceiro."
    conteudo = _conteudo(**ANTES, inscricao="Texto.", recursos="Texto.", convocacao=texto)
    [achado] = _achados(conteudo)
    assert f"como {numero}," in achado.message
    assert f"«{numero + 1}.1 " in achado.message and "«8.1 " in achado.message
    assert f"«{numero}.1 " not in achado.message


def test_zero_a_esquerda_e_invisivel_colado_nao_sao_conflito():
    assert _achados(_conteudo(**ANTES, inscricao="04.1 A inscrição é gratuita.")) == []
    assert _achados(_conteudo(**ANTES, inscricao="4.1​ A inscrição é gratuita.")) == []


def test_secao_vazia_nao_e_conferida():
    assert _achados(_conteudo(**ANTES)) == []


def test_a_frase_do_teto_nao_e_lida_so_o_texto_do_autor():
    conteudo = {
        **_conteudo(**ANTES, inscricao="4.1 A inscrição é gratuita."),
        "maxInscricoesPorCandidato": 1,
    }
    assert _achados(conteudo) == []


def test_linha_em_branco_nao_conta_como_paragrafo():
    texto = "A inscrição é gratuita.\n\n\n3.1 O candidato anexará os documentos."
    [achado] = _achados(_conteudo(**ANTES, inscricao=texto))
    assert "parágrafo 2" in achado.message


def test_o_trecho_e_cortado_em_fim_de_palavra_com_reticencias():
    longo = "3.1 " + "A inscrição será realizada exclusivamente pelo sistema de inscrições " * 3
    [achado] = _achados(_conteudo(**ANTES, inscricao=longo))
    trecho = achado.message.split("«")[2].split("»")[0]
    assert trecho.endswith("…")
    assert len(trecho) <= 81
    assert longo.startswith(trecho[:-1].rstrip())


# --- a numeração refeita e o título transcrito (FR-1202, FR-1201) -----------------------------


def test_a_conferencia_acompanha_a_numeracao_do_momento():
    texto = "4.1 A inscrição é gratuita."
    assert _achados(_conteudo(**ANTES, inscricao=texto)) == []
    sem_uma = {**ANTES, "publico_alvo": ""}
    [achado] = _achados(_conteudo(**sem_uma, inscricao=texto))
    assert "como 3" in achado.message


def test_titulo_transcrito_com_outro_numero_e_suspeita():
    redigidas = {**ANTES, "inscricao": "11. DA INSCRIÇÃO\nA inscrição é gratuita."}
    [achado] = _achados(_conteudo(**redigidas))
    assert achado.code == TITULO_TRANSCRITO
    assert achado.severity == Severity.WARNING
    assert "suspeita" in achado.message
    assert "«11. DA INSCRIÇÃO»" in achado.message


def test_titulo_transcrito_com_o_mesmo_numero_fica_fora():
    assert _achados(_conteudo(**ANTES, inscricao="4. DA INSCRIÇÃO\nA inscrição é gratuita.")) == []


# --- a Retificação (D-002) --------------------------------------------------------------------


def test_na_retificacao_o_conflito_e_aviso_com_codigo_proprio():
    [achado] = _achados(_conteudo(**ANTES, inscricao=INSCRICAO_DO_ORIGINAL), ATO_DE_RETIFICACAO)
    assert achado.code == CONFLITO_DE_NUMERACAO_NA_RETIFICACAO
    assert achado.severity == Severity.WARNING
    assert "não impede" in achado.message


# --- o cenário B e o cenário A da auditoria (SC-462, SC-464, SC-468) --------------------------

ESPERADO_EM_B = {
    "Da Inscrição": ("4", ["3.1", "3.2", "3.3", "3.4"]),
    "Da Verificação da Autodeclaração": ("6", ["4.1", "4.2", "4.3"]),
    "Dos Recursos": ("11", ["8.1", "8.2", "8.3"]),
    "Da Convocação": ("12", ["11.1", "11.2"]),
    "Disposições Finais": ("15", ["14.1", "14.2", "14.3"]),
}


def test_o_cenario_b_tem_os_cinco_conflitos_da_auditoria():
    conteudo = _congelado("B-conteudo-publicado.json")
    achados = [a for a in _achados(conteudo) if a.code == CONFLITO_DE_NUMERACAO]
    assert len(achados) == 5
    por_secao = {}
    for achado in achados:
        titulo = achado.message.split("«")[1].split("»")[0]
        por_secao[titulo] = achado.message
    assert set(por_secao) == set(ESPERADO_EM_B)
    total = 0
    for titulo, (numero, digitados) in ESPERADO_EM_B.items():
        assert f"como {numero}," in por_secao[titulo]
        for digitado in digitados:
            assert f"«{digitado} " in por_secao[titulo]
        total += len(digitados)
    assert total == 15
    assert "Disposições Preliminares" not in por_secao
    assert "Requisitos Gerais de Participação" not in por_secao


def test_cada_trecho_do_cenario_b_esta_no_texto_cru_da_secao():
    """SC-468: o trecho da mensagem é achado por busca no campo da seção, 5 de 5."""
    conteudo = _congelado("B-conteudo-publicado.json")
    textos = {secao["title"]: secao.get("content", "") for secao in conteudo["sections"]}
    for achado in _achados(conteudo):
        titulo = achado.message.split("«")[1].split("»")[0]
        for trecho in achado.message.split("«")[2:]:
            literal = trecho.split("»")[0].removesuffix("…").rstrip()
            assert literal in textos[titulo], literal


def test_o_cenario_a_nao_tem_achado_de_numeracao():
    assert _achados(_congelado("A-conteudo-publicado.json")) == []


@pytest.mark.parametrize("ato", [ATO_DE_PUBLICACAO, ATO_DE_RETIFICACAO])
def test_a_conferencia_nao_quebra_sobre_conteudo_malformado(ato):
    for conteudo in ({}, {"sections": "x"}, {"sections": [None, {"type": "TEXT"}]}):
        assert _achados(conteudo, ato) == []
