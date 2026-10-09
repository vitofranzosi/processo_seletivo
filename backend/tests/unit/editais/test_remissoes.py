"""As remissões internas que não apontam para um item só (065, User Story 2).

O sistema não sabe o que o autor quis citar; ele sabe só quais números o documento imprime. Por isso
acusa o que a estrutura prova — mais de um item com o número (FR-1206), nenhum (FR-1207) — e o que é
suspeito (FR-1208), sempre como aviso (FR-1211, D-003). E nunca diz que uma remissão está certa: o
destino único não prova nada (FR-1209).
"""

import json
from pathlib import Path

import pytest

from processo_seletivo.editais.domain import secoes
from processo_seletivo.editais.domain.validation import (
    ATO_DE_PUBLICACAO,
    ATO_DE_RETIFICACAO,
    CODIGOS_DA_NUMERACAO_DIGITADA,
    REMISSAO_AMBIGUA,
    REMISSAO_SEM_DESTINO,
    REMISSAO_SUSPEITA,
    Severity,
    validate_for_publication,
)
from processo_seletivo.publicacoes.infrastructure import pdf

RAIZ = Path(__file__).resolve().parents[4]
CONGELADOS = RAIZ / "doc" / "auditoria-edital-pdf-2026-10-08" / "snapshots"
REMISSOES = {REMISSAO_AMBIGUA, REMISSAO_SEM_DESTINO, REMISSAO_SUSPEITA}
ANTES = {
    "disposicoes_preliminares": "O processo seletivo será conduzido pela Comissão.",
    "informacoes_gerais": "O curso é a distância.",
    "publico_alvo": "Graduados.",
}
ETAPA = {"id": "00000000-0000-0000-0000-0000000000e1", "name": "Prova de títulos", "order": 1}
EVENTO = {
    "id": "00000000-0000-0000-0000-0000000000c1",
    "type": "Inscrições",
    "description": "Período de inscrições",
    "startAt": "2026-10-13T09:00:00-03:00",
    "endAt": None,
    "order": 1,
    "location": "",
}


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


def _conteudo(*, etapas=(), eventos=(), perfis=(), documentos=(), **redigidas):
    return {
        "schemaVersion": 17,
        "sections": _secoes(**redigidas),
        "stages": list(etapas),
        "schedule": list(eventos),
        "profiles": list(perfis),
        "documentRequirements": list(documentos),
    }


def _remissoes(conteudo, ato=ATO_DE_PUBLICACAO):
    return [a for a in validate_for_publication(conteudo, ato=ato) if a.code in REMISSOES]


def _numero(conteudo, chave):
    return pdf.numeracao_impressa(conteudo)[chave]


def _congelado(nome):
    return json.loads((CONGELADOS / nome).read_text(encoding="utf-8"))["content"]


# --- as três espécies (FR-1206, FR-1207, FR-1208, FR-1216) ------------------------------------


def test_numero_com_dois_itens_e_remissao_ambigua_que_nomeia_os_dois():
    base = _conteudo(etapas=[ETAPA], recursos="Texto.", **ANTES)
    etapas = _numero(base, "etapas")
    texto = f"{etapas}.1 Os recursos serão enviados pelo sistema.\nVale o item {etapas}.1."
    [achado] = _remissoes(_conteudo(etapas=[ETAPA], recursos=texto, **ANTES))
    assert achado.code == REMISSAO_AMBIGUA
    assert achado.severity == Severity.WARNING
    assert f"«item {etapas}.1»" in achado.message
    assert "a Etapa «Prova de títulos»" in achado.message
    assert "o parágrafo 1 da seção «Dos Recursos»" in achado.message
    assert "parágrafo 2" in achado.message, "onde a remissão está"
    assert "não sabe" in achado.message


def test_numero_sem_item_e_remissao_sem_destino():
    [achado] = _remissoes(_conteudo(recursos="Vale o disposto no item 7.3.", **ANTES))
    assert achado.code == REMISSAO_SEM_DESTINO
    assert achado.severity == Severity.WARNING
    assert "não tem item 7.3" in achado.message
    assert "do Edital nº" in achado.message, "ensina a explicitar a remissão a outro ato"


def test_quadro_e_suspeita():
    [achado] = _remissoes(_conteudo(inscricao="As vagas estão no Quadro 2.", **ANTES))
    assert achado.code == REMISSAO_SUSPEITA
    assert "suspeita" in achado.message
    assert "«Tabela N»" in achado.message


def test_destino_unico_em_paragrafo_em_conflito_e_suspeita():
    texto = "9.4 O prazo é de três dias.\nConforme o item 9.4, não cabe recurso por e-mail."
    [achado] = _remissoes(_conteudo(recursos=texto, **ANTES))
    assert achado.code == REMISSAO_SUSPEITA
    assert "o parágrafo 1 da seção «Dos Recursos»" in achado.message
    assert "fora da sua seção" in achado.message


def test_remissao_a_secao_so_e_acusada_acima_do_total():
    total = max(n for n in pdf.numeracao_impressa(_conteudo(**ANTES)).values() if n)
    assert _remissoes(_conteudo(inscricao=f"Conforme o item {total}.", **ANTES)) == []
    [achado] = _remissoes(_conteudo(inscricao=f"Conforme o item {total + 20}.", **ANTES))
    assert achado.code == REMISSAO_SEM_DESTINO


def test_tabela_so_e_acusada_acima_do_total():
    conteudo = _conteudo(eventos=[EVENTO], inscricao="Conforme a Tabela 1.", **ANTES)
    assert pdf.tabelas_do_documento(conteudo) == 1
    assert _remissoes(conteudo) == []
    [achado] = _remissoes(_conteudo(eventos=[EVENTO], inscricao="Conforme a Tabela 3.", **ANTES))
    assert achado.code == REMISSAO_SEM_DESTINO


def test_remissao_a_outro_ato_ou_anexo_nao_e_conferida():
    texto = (
        "Conforme o item 4.1 da Resolução CS nº 10/2017.\n"
        "Conforme o item 2.3 do Anexo II.\n"
        "Conforme o Quadro 2 do Anexo III."
    )
    assert _remissoes(_conteudo(recursos=texto, **ANTES)) == []


def test_a_mesma_remissao_na_mesma_secao_sai_uma_vez():
    texto = "Vale o item 7.3.\nReitera-se o item 7.3."
    assert len(_remissoes(_conteudo(recursos=texto, **ANTES))) == 1


def test_na_retificacao_as_remissoes_continuam_avisos():
    for achado in _remissoes(_conteudo(recursos="Vale o item 7.3.", **ANTES), ATO_DE_RETIFICACAO):
        assert achado.severity == Severity.WARNING


# --- nada afirma correção (FR-1209, SC-467) ---------------------------------------------------


def test_destino_unico_coerente_nao_gera_achado():
    base = _conteudo(inscricao="Texto.", recursos="Texto.", **ANTES)
    inscricao = _numero(base, "inscricao")
    conteudo = _conteudo(
        inscricao=f"{inscricao}.1 A inscrição é gratuita.",
        recursos=f"Vale o disposto no item {inscricao}.1.",
        **ANTES,
    )
    assert _remissoes(conteudo) == []


PALAVRAS_DE_CORRECAO = ("correta", "correto", "conferida", "conferido", "verificada", "válida")


@pytest.mark.parametrize(
    "conteudo",
    [
        _conteudo(recursos="Vale o disposto no item 7.3.", **ANTES),
        _conteudo(inscricao="As vagas estão no Quadro 2.", **ANTES),
        _conteudo(recursos="9.4 O prazo.\nConforme o item 9.4.", **ANTES),
        _conteudo(etapas=[ETAPA], recursos="5.1 Os recursos.\nVale o item 4.1.", **ANTES),
    ],
)
def test_nenhuma_mensagem_diz_que_a_remissao_esta_certa(conteudo):
    for achado in validate_for_publication(conteudo):
        if achado.code in CODIGOS_DA_NUMERACAO_DIGITADA:
            mensagem = achado.message.casefold()
            for palavra in PALAVRAS_DE_CORRECAO:
                assert palavra not in mensagem, (palavra, achado.message)


# --- o alcance: todo texto livre impresso (FR-1204, D-003) ------------------------------------


def _perfil(**campos):
    return {
        "id": "00000000-0000-0000-0000-0000000000b1",
        "code": "TP-01",
        "name": "Tutor presencial",
        "immediateVacancies": 0,
        "reserveType": "NONE",
        "competitionModalities": [],
        "classificationMilestones": [],
        "requirements": [],
        **campos,
    }


@pytest.mark.parametrize(
    ("dados", "caminho", "lugar"),
    [
        (
            {"perfis": [_perfil(duties="Mediar, conforme o item 7.3.")]},
            "/profiles/id=00000000-0000-0000-0000-0000000000b1/duties",
            "nas atribuições do Perfil «Tutor presencial»",
        ),
        (
            {"perfis": [_perfil(requirements=["Experiência, conforme o item 7.3"])]},
            "/profiles/id=00000000-0000-0000-0000-0000000000b1/requirements/0",
            "no 1º requisito do Perfil «Tutor presencial»",
        ),
        (
            {
                "documentos": [
                    {
                        "id": "00000000-0000-0000-0000-0000000000d1",
                        "key": "diploma",
                        "name": "Diploma",
                        "instructions": "Conforme o item 7.3.",
                    }
                ]
            },
            "/documentRequirements/id=00000000-0000-0000-0000-0000000000d1/instructions",
            "nas instruções do documento exigido «Diploma»",
        ),
        (
            {"eventos": [{**EVENTO, "description": "Inscrições, conforme o item 7.3"}]},
            "/schedule/id=00000000-0000-0000-0000-0000000000c1/description",
            "na descrição do Evento «Inscrições, conforme o item 7.3»",
        ),
    ],
)
def test_a_remissao_e_procurada_em_todo_texto_impresso(dados, caminho, lugar):
    [achado] = _remissoes(_conteudo(**dados, **ANTES))
    assert achado.code == REMISSAO_SEM_DESTINO
    assert achado.path == caminho
    assert lugar[0].upper() + lugar[1:] in achado.message


def test_o_rotulo_do_anexo_e_o_titulo_da_secao_nao_sao_remissao():
    conteudo = _conteudo(**ANTES)
    conteudo["attachments"] = [
        {"id": "00000000-0000-0000-0000-0000000000a1", "label": "ANEXO II — QUADRO 2", "order": 1}
    ]
    assert _remissoes(conteudo) == []


# --- o cenário B da auditoria (SC-463) --------------------------------------------------------


def test_no_cenario_b_o_item_8_1_e_a_unica_remissao_ambigua():
    achados = _remissoes(_congelado("B-conteudo-publicado.json"))
    ambiguas = [a for a in achados if a.code == REMISSAO_AMBIGUA]
    assert len(ambiguas) == 1
    [achado] = ambiguas
    assert "«item 8.1»" in achado.message
    assert "«Dos Recursos»" in achado.message
    assert "a Etapa «Prova de títulos" in achado.message
    assert "o parágrafo 1 da seção «Dos Recursos»" in achado.message


def test_no_cenario_a_nao_ha_remissao_a_acusar():
    assert _remissoes(_congelado("A-conteudo-publicado.json")) == []


# --- o contrato G1: nenhum aviso com código de impeditivo (D-006) -----------------------------


def test_os_codigos_de_aviso_nao_coincidem_com_impeditivo_nenhum():
    """`advertencias_do_ato` descarta o aviso cujo código é o de um impeditivo de publicação."""
    from processo_seletivo.editais.domain.validation import (
        CONFLITO_DE_NUMERACAO,
        CONFLITO_DE_NUMERACAO_NA_RETIFICACAO,
        TITULO_TRANSCRITO,
        blocking_findings,
    )

    texto = (
        "9.4 O prazo é de três dias.\n11. DOS RECURSOS\nConforme o item 9.4.\n"
        "Vale o item 7.3.\nAs vagas estão no Quadro 2."
    )
    base = _conteudo(etapas=[ETAPA], recursos="Texto.", **ANTES)
    etapas = _numero(base, "etapas")
    texto += f"\n{etapas}.1 Repetido.\nConforme o item {etapas}.1."
    conteudo = _conteudo(etapas=[ETAPA], recursos=texto, **ANTES)

    publicacao = validate_for_publication(conteudo, ato=ATO_DE_PUBLICACAO)
    retificacao = validate_for_publication(conteudo, ato=ATO_DE_RETIFICACAO)
    impeditivos = {achado.code for achado in blocking_findings(publicacao)}
    avisos = {
        achado.code
        for achado in publicacao + retificacao
        if achado.code in CODIGOS_DA_NUMERACAO_DIGITADA and achado.severity == Severity.WARNING
    }
    assert avisos == {
        CONFLITO_DE_NUMERACAO_NA_RETIFICACAO,
        TITULO_TRANSCRITO,
        REMISSAO_AMBIGUA,
        REMISSAO_SEM_DESTINO,
        REMISSAO_SUSPEITA,
    }
    assert CONFLITO_DE_NUMERACAO in impeditivos
    assert not (avisos & impeditivos)
    assert not blocking_findings(
        [a for a in retificacao if a.code in CODIGOS_DA_NUMERACAO_DIGITADA]
    ), "na Retificação nada desta feature impede (D-002)"
