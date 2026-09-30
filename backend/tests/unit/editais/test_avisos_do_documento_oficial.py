"""Os dois avisos da Revisão sobre o texto das seções, sem impeditivo.

Desde 28/09 o PDF do sistema é o documento oficial do piloto, e o que ele cala ou inventa é norma
publicada. A DP-20 pediu dois avisos (decisão do usuário de 28/09): a remissão a um anexo que o
Edital não publica (RC-21) e a seção com a redação padrão do catálogo, que ninguém revisou. A `054`
tirou a redação padrão do catálogo (FR-983), e o segundo aviso perdeu o objeto: no lugar dele entrou
o das duas seções que todo Edital do Cefor tem, quando vão vazias (FR-986). Os dois são **aviso**:
a remissão pode ser a anexo de outro ato, e publicar sem preâmbulo é estranho, e não inválido.
"""

import pytest

from processo_seletivo.editais.domain import secoes
from processo_seletivo.editais.domain.validation import (
    ANEXO_CITADO_SEM_ROTULO,
    ATO_DE_PUBLICACAO,
    ATO_DE_RETIFICACAO,
    SECAO_UNIVERSAL_VAZIA,
    Severity,
    blocking_findings,
    validate_for_publication,
)


def _secoes(**redigidas):
    """O catálogo inteiro, vazio onde nada foi redigido — como `_sections` o publica."""
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


def _conteudo(*, anexos=(), **redigidas):
    return {
        "schemaVersion": 17,
        "sections": _secoes(**redigidas),
        "attachments": [
            {"id": f"a{indice}", "label": rotulo, "order": indice}
            for indice, rotulo in enumerate(anexos, 1)
        ],
    }


def _com_codigo(achados, codigo):
    return [achado for achado in achados if achado.code == codigo]


# --- RC-21 · anexo citado sem rótulo ------------------------------------------------------------


def test_a_remissao_a_anexo_que_nao_existe_e_aviso_na_publicacao():
    conteudo = _conteudo(
        anexos=["ANEXO I — REQUERIMENTO DE INSCRIÇÃO"],
        inscricao="Preencher o Anexo I e o ANEXO IV, conforme o Anexo IV.",
    )
    achados = _com_codigo(validate_for_publication(conteudo), ANEXO_CITADO_SEM_ROTULO)

    # O ANEXO IV uma vez só, embora citado duas; o ANEXO I existe e não é dito.
    assert len(achados) == 1
    assert achados[0].severity == Severity.WARNING
    assert "ANEXO IV" in achados[0].message
    assert "«Da Inscrição»" in achados[0].message
    # A Inscrição é a 7ª do catálogo desde a `054` (FR-980).
    assert achados[0].path == "/sections/id=00000000-0000-0000-0000-000000000007/content"


def test_o_rotulo_do_anexo_pode_ser_escrito_em_qualquer_caixa():
    conteudo = _conteudo(anexos=["Anexo II: autodeclaração"], inscricao="Conforme o ANEXO II.")
    assert _com_codigo(validate_for_publication(conteudo), ANEXO_CITADO_SEM_ROTULO) == []


@pytest.mark.parametrize("rotulo", ["IV — Formulário de inscrição", "IV. Formulário", "IV"])
def test_o_rotulo_que_abre_pelo_identificador_conta_como_o_anexo(rotulo):
    """Revisão do PR 221: o autor não é obrigado a repetir a palavra "Anexo" no rótulo."""
    conteudo = _conteudo(anexos=[rotulo], inscricao="Preencha o ANEXO IV.")
    assert _com_codigo(validate_for_publication(conteudo), ANEXO_CITADO_SEM_ROTULO) == []


def test_rotulo_que_so_comeca_por_letra_romana_nao_e_identificador():
    """ "Modelo de declaração" abre por M, e não é o Anexo M."""
    conteudo = _conteudo(anexos=["Modelo de declaração"], inscricao="Preencha o ANEXO IV.")
    assert len(_com_codigo(validate_for_publication(conteudo), ANEXO_CITADO_SEM_ROTULO)) == 1


def test_numeral_em_minusculas_nao_e_remissao():
    """ "Anexo civil" não é o Anexo CIVIL: o numeral romano dos Editais é escrito em maiúsculas."""
    conteudo = _conteudo(inscricao="O documento anexo civil e o anexo dim não são remissões.")
    assert _com_codigo(validate_for_publication(conteudo), ANEXO_CITADO_SEM_ROTULO) == []


def test_a_remissao_a_anexo_de_outro_ato_tambem_avisa_e_nao_impede():
    """A razão de ser aviso: o sistema não distingue o anexo deste Edital do de outro ato."""
    conteudo = _conteudo(disposicoes_finais="Observado o Anexo III da Resolução CS nº 1/2020.")
    achados = validate_for_publication(conteudo)

    assert len(_com_codigo(achados, ANEXO_CITADO_SEM_ROTULO)) == 1
    assert not _com_codigo(blocking_findings(achados), ANEXO_CITADO_SEM_ROTULO)


def test_na_retificacao_a_remissao_nao_e_conferida():
    conteudo = _conteudo(inscricao="Conforme o ANEXO IV.")
    achados = validate_for_publication(conteudo, ato=ATO_DE_RETIFICACAO)
    assert _com_codigo(achados, ANEXO_CITADO_SEM_ROTULO) == []


# --- 054, FR-986 · as seções universais vazias -------------------------------------------------


def test_apresentacao_e_disposicoes_finais_vazias_recebem_um_aviso_cada():
    achados = _com_codigo(validate_for_publication(_conteudo()), SECAO_UNIVERSAL_VAZIA)

    assert len(achados) == 2
    assert {achado.severity for achado in achados} == {Severity.WARNING}
    assert any("«Apresentação»" in achado.message for achado in achados)
    assert any("«Disposições Finais»" in achado.message for achado in achados)


def test_as_demais_vazias_nao_avisam():
    """Dezesseis avisos por Edital seriam o aviso que se aprende a ignorar."""
    conteudo = _conteudo(
        apresentacao="A Diretora do Cefor faz saber.", disposicoes_finais="Casos omissos."
    )
    assert _com_codigo(validate_for_publication(conteudo), SECAO_UNIVERSAL_VAZIA) == []


def test_a_secao_universal_vazia_nunca_impede_e_so_e_dita_na_publicacao():
    achados = validate_for_publication(_conteudo(), ato=ATO_DE_PUBLICACAO)
    assert not _com_codigo(blocking_findings(achados), SECAO_UNIVERSAL_VAZIA)
    retificacao = validate_for_publication(_conteudo(), ato=ATO_DE_RETIFICACAO)
    assert _com_codigo(retificacao, SECAO_UNIVERSAL_VAZIA) == []


def test_o_aviso_da_redacao_padrao_nao_existe_mais():
    """FR-986: sem redação padrão no catálogo, o aviso de 28/09 perdeu o objeto e saiu."""
    from processo_seletivo.editais.domain import validation

    assert not hasattr(validation, "SECAO_COM_REDACAO_PADRAO")
    codigos = {achado.code for achado in validate_for_publication(_conteudo())}
    assert "section_default_text" not in codigos


def test_os_codigos_novos_nao_coincidem_com_impeditivo_nenhum():
    """`advertencias_do_ato` descarta aviso cujo código coincida com o de um impeditivo."""
    conteudo = _conteudo(inscricao="Conforme o ANEXO IV.")
    achados = validate_for_publication(conteudo)
    impeditivos = {achado.code for achado in blocking_findings(achados)}
    assert not ({ANEXO_CITADO_SEM_ROTULO, SECAO_UNIVERSAL_VAZIA} & impeditivos)
