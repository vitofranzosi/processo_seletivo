"""O fecho do ato, a marca do consolidado, a Matrícula e o total (054).

FR-989 a FR-997; SC-364, SC-365, SC-367 (a parte do compositor), SC-368 e SC-369. O que chega do
banco — a data do `now`, o ato de nomeação copiado do catálogo, as datas das Retificações — está em
`tests/integration/publicacoes/test_fecho_publicado.py` e `test_consolidado_datado.py`.
"""

from datetime import date

import pytest

from processo_seletivo.publicacoes.infrastructure.pdf import (
    MODO_PREVIA,
    AutoridadeSignataria,
    Consolidacao,
    marca_de_consolidacao,
    render_edital_pdf,
)
from processo_seletivo.shared.canonical import canonical_sha256
from processo_seletivo.unidades.domain.rotulos import quem_assinou
from tests.fixtures.autoridades import UNIDADE_DA_SUITE
from tests.unit.publicacoes.test_pdf import documento, snapshot, texto_de

CARGO = "Diretora-Geral do Centro de Referência em Formação e em Educação a Distância"
DECLARACAO = (
    "Declaro, sob as penas da lei, que as informações prestadas são verdadeiras.\n"
    "Declaro ainda que conheço as condições deste Edital."
)


def _publicado(conteudo=None, **kwargs):
    conteudo = conteudo or snapshot()
    kwargs.setdefault("unidade", UNIDADE_DA_SUITE)
    kwargs.setdefault("autoridade", AutoridadeSignataria(nome="", cargo=CARGO))
    kwargs.setdefault("data_do_ato", date(2026, 9, 29))
    return texto_de(render_edital_pdf(conteudo, canonical_sha256(conteudo), **kwargs))


# --- O fecho (FR-989, FR-990, FR-993) -----------------------------------------------------------


def test_o_publicado_traz_local_e_data_antes_da_autoridade():
    texto = _publicado()
    assert "Vitória (ES), 29 de setembro de 2026." in texto
    assert texto.index("Vitória (ES)") < texto.index("Autoridade responsável pelo ato")
    assert texto.index("Autoridade responsável pelo ato") < texto.index(CARGO)


def test_a_previa_recusa_data_e_consolidacao():
    """FR-990: a data é contexto do ato, e a prévia não decorre de ato nenhum."""
    with pytest.raises(ValueError):
        render_edital_pdf(
            snapshot(),
            "",
            modo=MODO_PREVIA,
            unidade=UNIDADE_DA_SUITE,
            data_do_ato=date(2026, 9, 29),
        )
    with pytest.raises(ValueError):
        render_edital_pdf(
            snapshot(),
            "",
            modo=MODO_PREVIA,
            unidade=UNIDADE_DA_SUITE,
            consolidacao=Consolidacao(date(2026, 4, 7), (date(2026, 8, 24),)),
        )
    assert "Vitória (ES)" not in texto_de(documento(snapshot(), modo=MODO_PREVIA))


def test_o_publicado_sem_data_e_recusado():
    with pytest.raises(ValueError, match="data do ato"):
        render_edital_pdf(
            snapshot(),
            "a" * 64,
            unidade=UNIDADE_DA_SUITE,
            autoridade=AutoridadeSignataria(nome="", cargo=CARGO),
        )


def test_o_mesmo_conteudo_em_duas_datas_tem_o_mesmo_hash_e_so_o_fecho_muda():
    """SC-364: o SHA-256 é do conteúdo, e a data não é conteúdo."""
    conteudo = snapshot()
    antes = canonical_sha256(conteudo)
    um = _publicado(conteudo, data_do_ato=date(2026, 9, 29))
    outro = _publicado(conteudo, data_do_ato=date(2026, 10, 1))
    assert canonical_sha256(conteudo) == antes
    assert um.replace("29 de setembro", "1 de outubro") == outro


def test_sem_nome_o_fecho_diz_o_cargo_e_nada_no_lugar_do_nome():
    """SC-365, primeira metade: nenhuma designação de cargo ocupa o lugar do nome."""
    texto = _publicado()
    linhas = texto.splitlines()
    rubrica = linhas.index("Autoridade responsável pelo ato")
    assert linhas[rubrica + 1] == CARGO
    assert "Diretora do Cefor" not in texto


def test_com_nome_e_ato_de_nomeacao_o_fecho_os_imprime():
    """SC-365, segunda metade: nome, cargo e ato de nomeação, nessa ordem."""
    texto = _publicado(
        autoridade=AutoridadeSignataria(
            nome="Maria Exemplo", cargo=CARGO, ato_de_nomeacao="Portaria nº 1, de 2 de março"
        )
    )
    linhas = texto.splitlines()
    rubrica = linhas.index("Autoridade responsável pelo ato")
    assert linhas[rubrica + 1 : rubrica + 4] == [
        "Maria Exemplo",
        CARGO,
        "Portaria nº 1, de 2 de março",
    ]


def test_quem_assinou_nao_deixa_separador_pendurado():
    """FR-994. O catálogo de que a 054 falava saiu com a 060; o registro de autoridades admite o
    nome vazio pelo mesmo motivo, e é `tests/unidades/` que o prende."""
    assert quem_assinou("", CARGO) == CARGO
    assert quem_assinou("Maria", "Diretora") == "Maria — Diretora"


# --- A marca do consolidado (FR-995) -------------------------------------------------------------


def test_a_marca_diz_a_publicacao_original_e_cada_retificacao():
    assert marca_de_consolidacao(Consolidacao(date(2026, 4, 7), (date(2026, 8, 24),))) == (
        "Versão consolidada. Publicado em 7 de abril de 2026; retificado em 24 de agosto de 2026."
    )
    duas = marca_de_consolidacao(
        Consolidacao(date(2026, 4, 7), (date(2026, 8, 24), date(2026, 9, 1)), date(2026, 9, 5))
    )
    assert duas == (
        "Versão consolidada. Publicado em 7 de abril de 2026; retificado em 24 de agosto de 2026 "
        "e em 1 de setembro de 2026, com vigência a partir de 5 de setembro de 2026."
    )


def test_a_marca_sai_logo_abaixo_do_anuncio_e_so_quando_ha_consolidacao():
    """SC-367 no compositor: o original não tem marca."""
    original = _publicado()
    assert "Versão consolidada" not in original

    consolidado = _publicado(
        consolidacao=Consolidacao(date(2026, 4, 7), (date(2026, 8, 24),)),
        data_do_ato=date(2026, 8, 24),
    )
    linhas = consolidado.splitlines()
    anuncio = next(i for i, linha in enumerate(linhas) if linha.startswith("EDITAL Nº"))
    assert linhas[anuncio + 1].startswith("Versão consolidada. Publicado em 7 de abril")
    assert "Vitória (ES), 24 de agosto de 2026." in consolidado


# --- A Matrícula e a Inscrição (FR-984, FR-996) ---------------------------------------------------


def _com_requerimento(momento, matricula=""):
    conteudo = snapshot()
    conteudo["matriculationRequest"] = {"moment": momento, "declarationText": DECLARACAO}
    for secao in conteudo["sections"]:
        if secao["key"] == "matricula":
            secao["content"] = matricula
    return conteudo


@pytest.mark.parametrize(
    ("momento", "frase"),
    [
        ("AT_ENROLLMENT", "no ato da inscrição"),
        ("AT_CALL", "quando o candidato for convocado"),
    ],
)
def test_a_matricula_publica_o_momento_e_a_declaracao_mesmo_vazia(momento, frase):
    """SC-368: a declaração sai por extenso, parágrafo a parágrafo, como o portal a exibe."""
    texto = texto_de(documento(_com_requerimento(momento)))

    assert ". DA MATRÍCULA" in texto
    assert f"O Requerimento de Matrícula será enviado {frase}." in texto
    assert "Ao enviá-lo, o candidato declarará:" in texto
    for paragrafo in DECLARACAO.splitlines():
        assert paragrafo in texto.replace("\n", " ")


def test_o_texto_do_autor_vem_antes_da_norma_da_matricula():
    texto = texto_de(documento(_com_requerimento("AT_CALL", "A matrícula será online.")))
    assert texto.index("A matrícula será online.") < texto.index("O Requerimento de Matrícula")


def test_sem_requerimento_a_matricula_vazia_nao_sai():
    conteudo = snapshot()
    conteudo["matriculationRequest"] = None
    for secao in conteudo["sections"]:
        if secao["key"] == "matricula":
            secao["content"] = ""
    assert ". DA MATRÍCULA" not in texto_de(documento(conteudo))


def test_a_inscricao_vazia_com_teto_sai_com_a_frase_do_teto():
    conteudo = snapshot(maxInscricoesPorCandidato=1)
    for secao in conteudo["sections"]:
        if secao["key"] == "inscricao":
            secao["content"] = ""
    texto = texto_de(documento(conteudo))
    assert "DA INSCRIÇÃO" in texto
    assert "Cada candidato poderá ter apenas 1 inscrição enviada neste Edital." in texto


# --- O total (FR-997) ----------------------------------------------------------------------------


def _perfis(*vagas):
    base = snapshot()["profiles"][0]
    return [
        {
            **base,
            "id": f"33333333-3333-3333-3333-33333333333{i}",
            "code": f"P{i}",
            "immediateVacancies": n,
        }
        for i, n in enumerate(vagas)
    ]


def test_com_mais_de_um_perfil_a_tabela_termina_no_total():
    """SC-369: a soma das vagas imediatas; o cadastro reserva não soma."""
    texto = texto_de(documento(snapshot(profiles=_perfis(40, 40, 30))))
    linhas = texto.splitlines()
    total = linhas.index("Total")
    assert linhas[total + 1] == "110"


def test_com_um_perfil_nao_ha_linha_de_total():
    assert "Total" not in texto_de(documento(snapshot())).splitlines()


def test_sem_vaga_imediata_nao_ha_linha_de_total():
    """FR-997: no Edital só de cadastro de reserva, "Total 0" diria que ele não oferece nada.

    Visto no Edital 89/2026, de Mediadores UAB, cadastrado em 30/09: dois Perfis só de reserva.
    """
    perfis = [{**perfil, "reserveType": "UNLIMITED"} for perfil in _perfis(0, 0)]
    assert "Total" not in texto_de(documento(snapshot(profiles=perfis))).splitlines()
