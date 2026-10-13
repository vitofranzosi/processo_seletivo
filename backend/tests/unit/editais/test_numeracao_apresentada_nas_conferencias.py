"""As conferências da 065 sobre a numeração apresentada (069, R-003, FR-1399).

Na apresentação por perguntas, uma chave textual pode sair como subseção ("3.1 Público-alvo") e uma
seção pode imprimir subseções geradas dentro dela. A regra de conflito passa a comparar o **prefixo
apresentado**: o dono de um número digitado é o número impresso mais longo que o prefixa, e o
subitem é coerente quando o dono é a própria seção ou subseção e o número não é ele mesmo um item
impresso. Na plana, ela se reduz à da `065` — os casos dela continuam em
`test_conflito_de_numeracao.py` e `test_remissoes.py`, pelo catálogo da `054`.
"""

from processo_seletivo.editais.domain import secoes
from processo_seletivo.editais.domain.validation import (
    CONFLITO_DE_NUMERACAO,
    REMISSAO_AMBIGUA,
    REMISSAO_SEM_DESTINO,
    REMISSAO_SUSPEITA,
    validate_for_publication,
)
from processo_seletivo.publicacoes.infrastructure import pdf

REMISSOES = {REMISSAO_AMBIGUA, REMISSAO_SEM_DESTINO, REMISSAO_SUSPEITA}


def _secoes(catalogo, **redigidas):
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
        for secao in catalogo
    ]


def _conteudo(catalogo=secoes.CATALOGO_DA_069, **redigidas):
    return {"schemaVersion": 17, "sections": _secoes(catalogo, **redigidas)}


# "Quem pode se inscrever?" sai como 2, com Público-alvo em 2.1 e Requisitos gerais em 2.2;
# "Como se inscrever?" sai como 3, com o Atendimento em 3.1.
BASE = {
    "disposicoes_preliminares": "O processo seletivo será conduzido pela Comissão.",
    "publico_alvo": "Graduados.",
    "requisitos_gerais": "Ter disponibilidade.",
    "inscricao": "A inscrição é gratuita.",
    "atendimento_pcd": "Há atendimento especializado.",
}


def _achados(conteudo, codigos):
    return [achado for achado in validate_for_publication(conteudo) if achado.code in codigos]


def test_a_base_sai_com_os_numeros_esperados():
    numeros = pdf.numeracao_impressa(_conteudo(**BASE))
    assert (numeros["publico-alvo"], numeros["requisitos-gerais"]) == ("2.1", "2.2")
    assert (numeros["inscricao"], numeros["atendimento-pcd"]) == ("3", "3.1")
    assert _achados(_conteudo(**BASE), {CONFLITO_DE_NUMERACAO}) == []


def test_subitem_da_propria_subsecao_e_coerente():
    conteudo = _conteudo(**{**BASE, "publico_alvo": "2.1.1 Graduados.\n2.1.2 Licenciados."})
    assert _achados(conteudo, {CONFLITO_DE_NUMERACAO}) == []


def test_o_numero_da_propria_subsecao_digitado_dentro_dela_e_conflito():
    """ "3.1" dentro da subseção 3.1 não pode passar por coerente: seriam dois itens 3.1."""
    conteudo = _conteudo(**{**BASE, "atendimento_pcd": "3.1 Há atendimento especializado."})
    [achado] = _achados(conteudo, {CONFLITO_DE_NUMERACAO})
    assert "A subseção «Atendimento à pessoa com deficiência» sai no documento como 3.1" in (
        achado.message
    )
    assert "começam por 3.1" in achado.message
    assert achado.path == "/sections/id=00000000-0000-0000-0000-000000000009/content"


def test_subitem_da_secao_que_e_numero_de_subsecao_impressa_e_conflito():
    """ "3.1" no texto da Inscrição, que imprime a subseção 3.1: dois itens 3.1 no ato."""
    conteudo = _conteudo(**{**BASE, "inscricao": "3.1 A inscrição é gratuita.\n3.2 É online."})
    [achado] = _achados(conteudo, {CONFLITO_DE_NUMERACAO})
    assert "A seção «Como se inscrever?» sai no documento como 3" in achado.message
    assert "«3.1 A inscrição é gratuita.»" in achado.message
    assert "«3.2 " not in achado.message, "3.2 não é item impresso, e é da própria seção"
    assert "3.1 já é subseção dela" in achado.message


def test_subitem_de_subsecao_digitado_no_texto_da_secao_e_conflito():
    conteudo = _conteudo(**{**BASE, "inscricao": "3.1.4 A inscrição é gratuita."})
    [achado] = _achados(conteudo, {CONFLITO_DE_NUMERACAO})
    assert "«3.1.4 " in achado.message


def test_subitem_de_outra_secao_continua_conflito():
    conteudo = _conteudo(**{**BASE, "requisitos_gerais": "4.1 Ter disponibilidade."})
    [achado] = _achados(conteudo, {CONFLITO_DE_NUMERACAO})
    assert "A subseção «Requisitos gerais» sai no documento como 2.2" in achado.message


def test_na_plana_os_numeros_sao_os_do_original():
    """FR-1399: o mesmo texto, no catálogo da `054`, conferido pelos números da plana."""
    conteudo = _conteudo(
        secoes.CATALOGO_DA_054, **{**BASE, "inscricao": "4.1 A inscrição é gratuita."}
    )
    numeros = pdf.numeracao_impressa(conteudo)
    assert numeros["inscricao"] == 4
    assert _achados(conteudo, {CONFLITO_DE_NUMERACAO}) == []


def test_remissao_a_subsecao_apresentada_se_resolve_pela_apresentacao():
    """ "item 2.1" aponta para a subseção Público-alvo, e não gera achado."""
    conteudo = _conteudo(**{**BASE, "inscricao": "Atendidos os requisitos do item 2.1."})
    assert _achados(conteudo, REMISSOES) == []


def test_remissao_a_numero_que_so_existia_no_original_fica_sem_destino():
    conteudo = _conteudo(**{**BASE, "inscricao": "Atendidos os requisitos do item 8.2."})
    [achado] = _achados(conteudo, REMISSOES)
    assert achado.code == REMISSAO_SEM_DESTINO
    assert "item 8.2" in achado.message


def test_remissao_ambigua_nomeia_a_subsecao_apresentada():
    conteudo = _conteudo(
        **{
            **BASE,
            "inscricao": "3.1 A inscrição é gratuita.",
            "disposicoes_finais": "Ver item 3.1.",
        }
    )
    [achado] = [a for a in _achados(conteudo, REMISSOES) if a.code == REMISSAO_AMBIGUA]
    assert "a subseção 3.1, «Atendimento à pessoa com deficiência»" in achado.message
    assert "o parágrafo 1 da seção «Como se inscrever?»" in achado.message


def test_a_ordem_dos_achados_e_a_do_documento():
    """Atendimento (9 no catálogo) sai em 3.1, antes de Disposições finais: a ordem é a impressa."""
    conteudo = _conteudo(
        **{
            **BASE,
            "atendimento_pcd": "3.1 Há atendimento.",
            "disposicoes_preliminares": "5.1 O processo será conduzido.",
        }
    )
    caminhos = [achado.path for achado in _achados(conteudo, {CONFLITO_DE_NUMERACAO})]
    assert caminhos == [
        "/sections/id=00000000-0000-0000-0000-000000000002/content",
        "/sections/id=00000000-0000-0000-0000-000000000009/content",
    ]
