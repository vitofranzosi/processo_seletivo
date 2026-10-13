"""A apresentação por perguntas sobre os cenários da auditoria (069, contrato do documento §1–§5).

Os snapshots congelados de A e B são levados ao catálogo da `069` — o título e a ordem das seções,
e nada mais (`levado_ao_catalogo_novo`): é o que o mesmo Edital teria se fosse submetido depois da
`069`. O documento deles sai pela apresentação por perguntas, e estes testes afirmam onde cada coisa
sai, o que não sai mais, e que o texto de quem redigiu continua palavra por palavra.
"""

import re

import pytest

from processo_seletivo.publicacoes.domain import grafia
from processo_seletivo.publicacoes.infrastructure import pdf
from tests.unit.publicacoes.cenarios_da_auditoria import (
    congelado,
    levado_ao_catalogo_novo,
    por_perguntas,
)
from tests.unit.publicacoes.test_pdf import paginas_de, texto_de

RODAPE = re.compile(r"^(Edital \d+/\d+( · Verificação [0-9a-f]+…)?|Página \d+ de \d+)$")


def _linhas(documento):
    """As linhas desenhadas, sem o rodapé e sem a marca de prévia."""
    return [
        linha
        for linha in texto_de(documento).splitlines()
        if linha.strip() and not RODAPE.match(linha) and linha != pdf.MARCA_DE_PREVIA
    ]


def _corrido(documento):
    return " ".join(" ".join(_linhas(documento)).split())


def _secao(documento, numero):
    """As linhas da seção N: do título dela ao título da seguinte, sem o sumário."""
    linhas = [linha for linha in _linhas(documento) if " . ." not in linha]
    inicio = next(i for i, linha in enumerate(linhas) if linha.startswith(f"{numero}. "))
    fim = next(
        (
            i
            for i, linha in enumerate(linhas[inicio + 1 :], inicio + 1)
            if re.match(r"^\d+\. \S", linha) and not re.match(r"^\d+\.\d", linha)
        ),
        len(linhas),
    )
    return linhas[inicio:fim]


@pytest.fixture(scope="module")
def a():
    return por_perguntas("A")


@pytest.fixture(scope="module")
def b():
    return por_perguntas("B")


def test_o_snapshot_levado_ao_catalogo_novo_sai_por_perguntas():
    for cenario in "AB":
        assert pdf.por_perguntas(levado_ao_catalogo_novo(congelado(cenario)["content"]))
        assert not pdf.por_perguntas(congelado(cenario)["content"])


# --- seções reunidas (FR-1368) --------------------------------------------------------------


def test_as_secoes_reunidas_saem_como_subsecoes(a):
    quem = _secao(a, 3)
    assert quem[0] == "3. Quem pode se inscrever?"
    subsecoes = [linha for linha in quem if re.match(r"^3\.\d ", linha)]
    assert subsecoes == ["3.1 Público-alvo", "3.2 Requisitos gerais", "3.3 Requisitos dos Perfis"]
    selecao = [linha for linha in _secao(a, 8) if re.match(r"^8\.\d ", linha)]
    assert selecao == [
        "8.1 Sorteio",
        "8.2 Dados para conferir o sorteio",
        "8.3 Análise documental",
        "8.4 Verificação da autodeclaração",
    ]


def test_o_atendimento_sai_dentro_da_inscricao(b):
    inscricao = _secao(b, 5)
    assert inscricao[0] == "5. Como se inscrever?"
    assert "5.1 Atendimento à pessoa com deficiência" in inscricao


# --- cada regra na seção que trata dela (FR-1369) --------------------------------------------


def test_o_recurso_do_marco_sai_em_como_recorrer(a):
    recorrer = " ".join(_secao(a, 9))
    assert recorrer.startswith("9. Como recorrer?")
    assert "Contra o resultado de “Classificação por sorteio eletrônico”" in recorrer
    assert _corrido(a).count("Contra o resultado de “Classificação por sorteio eletrônico”") == 1
    # A regra do sistema antes do texto de quem redigiu (contrato §5).
    assert recorrer.index("Contra o resultado") < recorrer.index("Caberá recurso")


def test_a_forma_de_convocacao_sai_em_como_sera_a_convocacao(a):
    convocacao = " ".join(_secao(a, 10))
    assert convocacao.startswith("10. Como será a convocação?")
    assert "A convocação dos classificados será feita por publicação." in convocacao
    assert _corrido(a).count("A convocação dos classificados será feita por publicação.") == 1


def test_os_requisitos_dos_perfis_saem_em_quem_pode_se_inscrever(a, b):
    assert "• Acesso a computador com conexão à internet" in _secao(a, 3)
    quem = _secao(b, 2)
    assert "2.2 Requisitos dos Perfis" in quem
    assert any(linha.startswith("Para os Perfis TP-01 a TP-16") for linha in quem)


def test_o_periodo_e_os_dados_declarados_saem_em_como_se_inscrever(b):
    inscricao = " ".join(_secao(b, 5))
    assert "Período de inscrições: de 14/10/2026, às 09h, a 28/10/2026, às 23h59" in inscricao
    assert "Na inscrição, informe também:" in inscricao
    assert "Esses dados são usados no desempate (item 7.1)." in inscricao


def test_o_requerimento_e_lembrado_em_documentos_e_na_inscricao(a):
    assert "A inscrição inclui o Requerimento de Matrícula (item 11)." in _secao(a, 6)
    documentos = " ".join(_secao(a, 7))
    assert "Além destes documentos, a inscrição inclui o Requerimento de Matrícula (item 11)." in (
        documentos
    )
    matricula = " ".join(_secao(a, 11))
    assert "O Requerimento de Matrícula é enviado no ato da inscrição." in matricula


# --- o que não sai mais, e o que fica (FR-1377 a FR-1379) ------------------------------------


@pytest.mark.parametrize("cenario", ["A", "B"])
def test_a_descricao_do_edital_nao_sai_no_ato(cenario):
    """FR-1378: a descrição é nota da equipe, e não norma."""
    descricao = congelado(cenario)["content"]["description"]
    assert descricao
    assert " ".join(descricao.split()) not in _corrido(por_perguntas(cenario))


def test_as_siglas_ficam_no_anuncio_em_caixa_alta(a, b):
    """FR-1377: "EaD" e "Cefor/Ifes" não viram "EAD" e "CEFOR/IFES"."""
    assert "INFORMÁTICA NA EDUCAÇÃO NA MODALIDADE EaD (DEMONSTRAÇÃO)" in _linhas(a)
    assert "OFERTADOS PELO Cefor/Ifes (DEMONSTRAÇÃO)" in _linhas(b)


def test_o_hifen_tambem_separa_a_sigla():
    """ "Cefor-Ifes" não vira "CEFOR-IFES": o hífen separa como a barra."""
    assert pdf.anuncio_em_caixa_alta("Curso do Cefor-Ifes", "Cefor") == "CURSO DO Cefor-Ifes"
    assert pdf.anuncio_em_caixa_alta("pró-reitoria", "Cefor") == "PRÓ-REITORIA"


@pytest.mark.parametrize("cenario", ["A", "B"])
def test_o_fecho_diz_autenticidade(cenario):
    """FR-1379."""
    texto = _corrido(por_perguntas(cenario))
    assert "Autenticidade — este documento corresponde integralmente" in texto
    assert "INTEGRIDADE" not in texto


# --- o texto livre, literal (FR-1395) --------------------------------------------------------


@pytest.mark.parametrize("cenario", ["A", "B"])
def test_cada_paragrafo_de_texto_livre_sai_literalmente(cenario):
    """Sem palavra trocada, acrescentada ou tirada — inclusive dentro das seções reunidas."""
    conteudo = congelado(cenario)["content"]
    texto = _corrido(por_perguntas(cenario))
    conferidos = 0
    for secao in conteudo["sections"]:
        if secao.get("type") != "TEXT":
            continue
        for paragrafo in pdf._paragrafos(grafia.normalizar(secao.get("content") or "")):
            assert " ".join(paragrafo.split()) in texto, (secao["key"], paragrafo[:60])
            conferidos += 1
    assert conferidos > 10


# --- a prévia (FR-1393) ----------------------------------------------------------------------


@pytest.mark.parametrize("cenario", ["A", "B"])
def test_a_previa_compoe_pela_apresentacao_por_perguntas(cenario):
    previa = por_perguntas(cenario, modo=pdf.MODO_PREVIA)
    linhas = _linhas(previa)
    assert "Resumo deste Edital" in linhas
    assert "Sumário" in linhas
    assert b"/Subtype /TrueType" in previa and b"/BaseFont /Helvetica" not in previa
    assert pdf.MARCA_DE_PREVIA in texto_de(previa)
    corrido = _corrido(previa)
    assert "Autoridade responsável pelo ato" not in corrido
    assert "SHA-256" not in corrido and "Autenticidade" not in corrido


@pytest.mark.parametrize("cenario", ["A", "B"])
def test_a_previa_e_o_publicado_tem_as_mesmas_paginas(cenario):
    """As mesmas seções, frases e quebras, até a última seção.

    A prévia não tem o fecho (FR-014 da `008`), e a última seção vai com ele no publicado (069,
    contrato do documento §7): só ela pode mudar de página entre os dois. Tudo antes dela — e o
    sumário, salvo a página dela — quebra igual.
    """

    def corpo(documento):
        return [
            [linha for linha in pagina if not RODAPE.match(linha) and linha != pdf.MARCA_DE_PREVIA]
            for pagina in paginas_de(documento)
        ]

    previa = corpo(por_perguntas(cenario, modo=pdf.MODO_PREVIA))
    publicado = corpo(por_perguntas(cenario))
    titulos = [
        linha
        for pagina in publicado
        for linha in pagina
        if re.match(r"^\d+\. \S", linha) and " . ." not in linha
    ]
    ultima = titulos[-1]

    def sem_a_pagina_da_ultima(linhas):
        """Sem a entrada do sumário da última seção, nem a página que ela diz."""
        saida, pular = [], False
        for linha in linhas:
            if pular:
                pular = False
                continue
            if linha.startswith(f"{ultima} . ."):
                pular = True
                continue
            saida.append(linha)
        return saida

    pagina_da_ultima = next(numero for numero, pagina in enumerate(previa) if ultima in pagina)
    for numero in range(pagina_da_ultima):
        assert sem_a_pagina_da_ultima(publicado[numero]) == sem_a_pagina_da_ultima(
            previa[numero]
        ), f"página {numero + 1}"
    corrido = [linha for pagina in publicado for linha in pagina]
    fecho = next(i for i, linha in enumerate(corrido) if linha.startswith("Vitória (ES), 8 de"))
    assert corrido.index(ultima) < fecho - 1, "a última seção tem texto antes do fecho"
