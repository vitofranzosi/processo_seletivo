"""Os dois avisos da Revisão que a DP-20 pediu, sem impeditivo (decisão do usuário de 28/09).

Desde 28/09 o PDF do sistema é o documento oficial do piloto, e o que ele cala ou inventa é norma
publicada. Duas coisas iam ao ato sem ninguém dizer: a remissão a um anexo que o Edital não publica
(RC-21) e a seção textual com a redação padrão do catálogo, que ninguém revisou (DP-20, §1). As duas
são **aviso**: a remissão pode ser a anexo de outro ato, e o padrão pode valer como está.
"""

from processo_seletivo.editais.domain import secoes
from processo_seletivo.editais.domain.validation import (
    ANEXO_CITADO_SEM_ROTULO,
    ATO_DE_PUBLICACAO,
    ATO_DE_RETIFICACAO,
    SECAO_COM_REDACAO_PADRAO,
    Severity,
    blocking_findings,
    validate_for_publication,
)


def _secoes(**redigidas):
    """O catálogo inteiro, com o padrão onde nada foi redigido — como `_sections` o publica."""
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
                else {"content": redigidas.get(secao.key.replace("-", "_"), secao.default_text)}
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
    assert achados[0].path == "/sections/id=00000000-0000-0000-0000-000000000004/content"


def test_o_rotulo_do_anexo_pode_ser_escrito_em_qualquer_caixa():
    conteudo = _conteudo(anexos=["Anexo II: autodeclaração"], inscricao="Conforme o ANEXO II.")
    assert _com_codigo(validate_for_publication(conteudo), ANEXO_CITADO_SEM_ROTULO) == []


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


# --- DP-20, §1 · redação padrão sem revisão ----------------------------------------------------


def test_cada_secao_com_a_redacao_padrao_recebe_um_aviso():
    achados = _com_codigo(validate_for_publication(_conteudo()), SECAO_COM_REDACAO_PADRAO)

    textuais = [secao for secao in secoes.CATALOGO if not secao.gerada]
    assert len(achados) == len(textuais)
    assert {achado.severity for achado in achados} == {Severity.WARNING}
    assert any("«Critérios de Classificação»" in achado.message for achado in achados)


def test_a_secao_redigida_nao_recebe_o_aviso():
    conteudo = _conteudo(classificacao="A classificação será por sorteio eletrônico.")
    achados = _com_codigo(validate_for_publication(conteudo), SECAO_COM_REDACAO_PADRAO)

    assert not any("«Critérios de Classificação»" in achado.message for achado in achados)
    assert len(achados) == len([secao for secao in secoes.CATALOGO if not secao.gerada]) - 1


def test_a_redacao_padrao_nunca_impede_e_so_e_dita_na_publicacao():
    achados = validate_for_publication(_conteudo(), ato=ATO_DE_PUBLICACAO)
    assert not _com_codigo(blocking_findings(achados), SECAO_COM_REDACAO_PADRAO)
    retificacao = validate_for_publication(_conteudo(), ato=ATO_DE_RETIFICACAO)
    assert _com_codigo(retificacao, SECAO_COM_REDACAO_PADRAO) == []


def test_os_codigos_novos_nao_coincidem_com_impeditivo_nenhum():
    """`advertencias_do_ato` descarta aviso cujo código coincida com o de um impeditivo."""
    conteudo = _conteudo(inscricao="Conforme o ANEXO IV.")
    achados = validate_for_publication(conteudo)
    impeditivos = {achado.code for achado in blocking_findings(achados)}
    assert not ({ANEXO_CITADO_SEM_ROTULO, SECAO_COM_REDACAO_PADRAO} & impeditivos)
