"""A remissão a uma seção pelo título que ela não tem no documento (069, FR-1400, R-013).

O texto transcrito do Word cita seções pelo título do original, e o catálogo da `069` mudou os
títulos e reuniu seções: "conforme o método publicado na seção Perfis de Vaga" aponta, num Edital
novo, para um lugar que não existe com esse nome — e a matéria de "Perfis de Vaga" foi repartida
entre vagas, requisitos e seleção. A conferência avisa, **sem impedir e sem reescrever**: traz o
trecho, sugere a seção quando o destino é único, e diz que houve partilha quando não é.
"""

from processo_seletivo.editais.domain import secoes
from processo_seletivo.editais.domain.numeracao_digitada import remissoes_por_titulo
from processo_seletivo.editais.domain.validation import (
    ATO_DE_PUBLICACAO,
    ATO_DE_RETIFICACAO,
    REMISSAO_PELO_TITULO,
    Severity,
    blocking_findings,
    validate_for_publication,
)

TITULOS = ("Perfis de Vaga", "Da Inscrição", "Etapas de Avaliação")


# --- o leitor ---------------------------------------------------------------------------------


def test_le_a_secao_citada_pelo_titulo():
    [achada] = remissoes_por_titulo(
        "Conforme o método publicado na seção Perfis de Vaga, o sorteio será público.", TITULOS
    )
    assert achada.titulo == "Perfis de Vaga"
    assert achada.literal == "seção Perfis de Vaga"


def test_le_o_titulo_entre_aspas_e_em_caixa_alta():
    assert [r.titulo for r in remissoes_por_titulo("Ver «Da Inscrição».", TITULOS)] == [
        "Da Inscrição"
    ]
    assert [r.titulo for r in remissoes_por_titulo("Ver “etapas de avaliação”.", TITULOS)] == [
        "Etapas de Avaliação"
    ]
    assert [r.titulo for r in remissoes_por_titulo("conforme ETAPAS DE AVALIAÇÃO.", TITULOS)] == [
        "Etapas de Avaliação"
    ]
    assert [r.titulo for r in remissoes_por_titulo("no item Da Inscrição", TITULOS)] == [
        "Da Inscrição"
    ]


def test_o_titulo_solto_no_meio_da_frase_nao_e_remissao():
    """ "da inscrição" é palavra comum: sem "seção", aspas ou caixa alta, não é citação."""
    assert remissoes_por_titulo("O prazo da inscrição termina no dia 30.", TITULOS) == []
    assert remissoes_por_titulo("Os perfis de vaga são dois.", TITULOS) == []


def test_item_seguido_de_prosa_nao_e_remissao():
    """Depois de "item", a inicial minúscula é prosa: "cada item da inscrição" não cita a seção."""
    assert remissoes_por_titulo("Cada item da inscrição deve ser conferido.", TITULOS) == []
    assert remissoes_por_titulo("O item do certificado vem depois.", ("Do Certificado",)) == []


def test_duas_grafias_do_mesmo_titulo_vence_a_primeira_dada():
    """O empate de comprimento não pode depender da ordem de um `set` (`PYTHONHASHSEED`)."""
    titulos = ("Etapas de Avaliação", "Etapas de avaliação")
    texto = "Conforme a seção Etapas de Avaliação."
    assert [r.titulo for r in remissoes_por_titulo(texto, titulos)] == ["Etapas de Avaliação"]
    assert [r.titulo for r in remissoes_por_titulo(texto, titulos[::-1])] == ["Etapas de avaliação"]


# --- o aviso ----------------------------------------------------------------------------------


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
        for secao in secoes.CATALOGO_DA_069
    ]


def _achados(ato=ATO_DE_PUBLICACAO, **redigidas):
    conteudo = {"schemaVersion": 17, "sections": _secoes(**redigidas)}
    return [
        achado
        for achado in validate_for_publication(conteudo, ato=ato)
        if achado.code == REMISSAO_PELO_TITULO
    ]


TEXTO_DO_ORIGINAL = "Havendo mais inscritos, vale o método publicado na seção Perfis de Vaga."


def test_secao_repartida_avisa_com_o_trecho_e_os_destinos():
    achados = _achados(classificacao=TEXTO_DO_ORIGINAL, publico_alvo="Graduados.")
    [achado] = achados
    assert achado.severity == Severity.WARNING
    assert achado.path == "/sections/id=00000000-0000-0000-0000-000000000011/content"
    assert "«seção Perfis de Vaga»" in achado.message
    assert "repartida" in achado.message
    assert "«Quem pode se inscrever?»" in achado.message
    assert "«Como será a seleção?»" in achado.message
    assert "confira" in achado.message.lower()
    impeditivos = blocking_findings(
        validate_for_publication({"sections": _secoes(classificacao=TEXTO_DO_ORIGINAL)})
    )
    assert REMISSAO_PELO_TITULO not in {achado.code for achado in impeditivos}


def test_destino_unico_sugere_a_secao():
    [achado] = _achados(
        disposicoes_finais="Os prazos são os da seção Da Inscrição.",
        inscricao="A inscrição é gratuita.",
    )
    assert "«seção Da Inscrição»" in achado.message
    assert "«Como se inscrever?»" in achado.message
    assert "repartida" not in achado.message


def test_titulo_com_grafia_nos_dois_catalogos_sugere_o_destino():
    """ "Etapas de Avaliação" (054) e "Etapas de avaliação" (vigente) casam o mesmo trecho; a
    mensagem sugere o destino qualquer que seja a grafia que o leitor devolva."""
    [achado] = _achados(
        disposicoes_finais="Conforme a seção Etapas de Avaliação.",
        classificacao="A ordem segue a nota final.",
    )
    assert "«Como será a seleção?»" in achado.message


def test_titulo_que_existe_no_documento_nao_avisa():
    assert (
        _achados(
            disposicoes_preliminares="Texto.",
            disposicoes_finais="Conforme a seção «Disposições preliminares».",
        )
        == []
    )
    assert (
        _achados(disposicoes_finais="Conforme a seção Como se inscrever?", inscricao="Gratuita.")
        == []
    )


def test_so_no_ato_de_publicacao():
    assert _achados(ATO_DE_RETIFICACAO, classificacao=TEXTO_DO_ORIGINAL) == []


def test_o_texto_nao_muda():
    conteudo = {"schemaVersion": 17, "sections": _secoes(classificacao=TEXTO_DO_ORIGINAL)}
    validate_for_publication(conteudo)
    [classificacao] = [s for s in conteudo["sections"] if s["key"] == "classificacao"]
    assert classificacao["content"] == TEXTO_DO_ORIGINAL


def test_na_apresentacao_plana_o_titulo_existe_e_nao_avisa():
    """O Edital no catálogo da `054` imprime "PERFIS DE VAGA": a remissão tem destino."""
    conteudo = {
        "schemaVersion": 17,
        "sections": [
            {**secao, "title": anterior.title, "order": anterior.order}
            for secao, anterior in zip(
                _secoes(classificacao=TEXTO_DO_ORIGINAL),
                sorted(secoes.CATALOGO_DA_054, key=lambda s: secoes.POR_CHAVE[s.key].order),
                strict=True,
            )
        ],
        "profiles": [{"id": "p", "code": "P1", "name": "Perfil"}],
    }
    assert not [
        achado
        for achado in validate_for_publication(conteudo)
        if achado.code == REMISSAO_PELO_TITULO
    ]
