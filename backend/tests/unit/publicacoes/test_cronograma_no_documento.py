"""O Cronograma no PDF com Evento oculto (144, FR-5106 a FR-5109, D-002, D-003, SC-1588).

**Tudo o que se afirma sobre o documento é lido do PDF composto**, e não do HTML nem do estado de
botão nenhum (SC-1588). O conteúdo é o do cenário A da auditoria do PDF: um Edital real, de versão
17 — anterior ao degrau 20, sem a chave em Evento nenhum —, que sai na apresentação plana tal como
está e na apresentação por perguntas levado ao catálogo da `069`. As duas apresentações perguntam
"a seção sai?" por caminhos diferentes, e é por isso que cada caso roda nas duas.

As descrições viram marcadores (`Marco01`…): a célula da tabela quebra linha conforme a largura, e
procurar a descrição original no texto extraído dependeria da quebra, e não do filtro.
"""

import copy
import re

import pytest

from processo_seletivo.interface import revisao
from processo_seletivo.publicacoes.infrastructure import pdf
from tests.unit.publicacoes.cenarios_da_auditoria import (
    composto,
    congelado,
    levado_ao_catalogo_novo,
    por_perguntas,
)
from tests.unit.publicacoes.test_pdf import texto_de

APRESENTACOES = {"plana": composto, "por_perguntas": por_perguntas}
# No cenário A, o quinto Evento é a "Análise documental dos sorteados", e a Etapa "Análise
# documental" se vincula a ele: é o caso do Evento operacional que não precisa sair na tabela.
VINCULADO_A_ETAPA = 4


def conteudo(**ajustes):
    """O cenário A com as descrições trocadas por marcadores e os ajustes por posição."""
    base = copy.deepcopy(congelado("A")["content"])
    for posicao, evento in enumerate(base["schedule"], 1):
        evento["description"] = f"Marco{posicao:02d}"
    for posicao in ajustes.get("ocultos", ()):
        base["schedule"][posicao]["shownInPdf"] = False
    return base


def linhas_da_tabela(texto):
    """`[(número impresso, marcador)]`, na ordem em que a tabela os desenhou."""
    linhas = texto.splitlines()
    return [
        (linhas[indice - 1], linha)
        for indice, linha in enumerate(linhas)
        if re.fullmatch(r"Marco\d\d", linha)
    ]


def texto(apresentacao, base):
    return texto_de(APRESENTACOES[apresentacao]("A", base))


def como_composto(apresentacao, base):
    """O conteúdo que a composição lê: na por perguntas, levado ao catálogo da `069`."""
    return levado_ao_catalogo_novo(base) if apresentacao == "por_perguntas" else base


# --- a função que decide (D-002, D-003) ---------------------------------------------------------


def test_sem_chave_nenhum_evento_e_oculto_e_o_numero_e_o_order():
    """Conteúdo anterior ao degrau 20, sem elevar: todos saem, com o número de sempre."""
    base = congelado("A")["content"]
    assert all("shownInPdf" not in evento for evento in base["schedule"])

    numerados = pdf.eventos_no_documento(base)

    assert [numero for numero, _ in numerados] == [e["order"] for e in base["schedule"]]


def test_sem_oculto_imprime_o_order_com_zero_e_lacunas():
    """FR-5106, SC-1580: a API admite `0` e lacunas, e o documento de antes as imprimia."""
    base = conteudo()
    for evento, ordem in zip(base["schedule"], [0, 2, 5, 6, 7, 8, 9, 10, 11, 20], strict=True):
        evento["order"] = ordem

    assert [numero for numero, _ in pdf.eventos_no_documento(base)] == [
        0, 2, 5, 6, 7, 8, 9, 10, 11, 20,
    ]  # fmt: skip
    for apresentacao in APRESENTACOES:
        impressos = [numero for numero, _ in linhas_da_tabela(texto(apresentacao, base))]
        assert impressos == ["0", "2", "5", "6", "7", "8", "9", "10", "11", "20"], apresentacao


def test_com_oculto_os_exibidos_sao_numerados_de_um():
    """D-003: com algum oculto, "1, 3, 4" leria como item suprimido; numera-se de 1 a k."""
    base = conteudo(ocultos=[1])
    for evento, ordem in zip(base["schedule"], [0, 2, 5, 6, 7, 8, 9, 10, 11, 20], strict=True):
        evento["order"] = ordem

    assert [numero for numero, _ in pdf.eventos_no_documento(base)] == list(range(1, 10))


def test_fonte_presente_pergunta_pelo_que_sai():
    assert pdf.fonte_presente(conteudo(), "schedule")
    assert pdf.fonte_presente(conteudo(ocultos=[0, 1]), "schedule")
    assert not pdf.fonte_presente(conteudo(ocultos=range(10)), "schedule")
    assert not pdf.fonte_presente({"schedule": []}, "schedule")


# --- o PDF composto (SC-1588) -------------------------------------------------------------------


@pytest.mark.parametrize("apresentacao", APRESENTACOES)
def test_o_oculto_nao_sai_na_tabela_e_a_numeracao_fecha(apresentacao):
    """FR-5106, SC-1581: a linha some, e as seguintes sobem um número."""
    lido = texto(apresentacao, conteudo(ocultos=[VINCULADO_A_ETAPA]))

    assert "Marco05" not in lido
    assert linhas_da_tabela(lido) == [
        ("1", "Marco01"), ("2", "Marco02"), ("3", "Marco03"), ("4", "Marco04"),
        ("5", "Marco06"), ("6", "Marco07"), ("7", "Marco08"), ("8", "Marco09"), ("9", "Marco10"),
    ]  # fmt: skip


@pytest.mark.parametrize("apresentacao", APRESENTACOES)
def test_a_etapa_vinculada_ao_oculto_continua_dizendo_quando_sera_feita(apresentacao):
    """FR-5108, SC-1582: ocultar não é desativar — a Etapa lê o Evento pelo vínculo."""
    base = conteudo(ocultos=[VINCULADO_A_ETAPA])
    etapa = base["stages"][0]
    assert etapa["scheduleEventId"] == base["schedule"][VINCULADO_A_ETAPA]["id"]

    lido = " ".join(texto(apresentacao, base).split())

    assert "Será feita de 17/11/2026, às 08h, a 24/11/2026, às 17h." in lido


@pytest.mark.parametrize("apresentacao", APRESENTACOES)
def test_todos_ocultos_a_secao_nao_sai_e_as_tabelas_fecham(apresentacao):
    """FR-5109, SC-1587: sem Evento que saia, não há seção — e a contagem acompanha o impresso."""
    base = conteudo(ocultos=range(10))

    lido = texto(apresentacao, base)

    assert not linhas_da_tabela(lido)
    assert "— Cronograma" not in lido, "sem legenda de tabela do Cronograma"
    assert not re.search(r"^\d+\. Cronograma$", lido, re.M), "sem título da seção"
    composto_ = como_composto(apresentacao, base)
    legendas = sorted({int(n) for n in re.findall(r"^Tabela (\d+) —", lido, re.M)})
    assert legendas == list(range(1, pdf.tabelas_do_documento(composto_) + 1))
    assert pdf.numeracao(composto_).get("cronograma") is None
    assert pdf.numeracao(como_composto(apresentacao, conteudo())).get("cronograma") is not None
    # A Etapa continua com as datas do Evento, que continua valendo.
    assert "Será feita de 17/11/2026" in lido


def test_todos_ocultos_o_resumo_nao_aponta_para_o_cronograma():
    """FR-5109: "Datas: no Cronograma (item N)" apontaria para seção que não existe."""
    com = texto("por_perguntas", conteudo())
    sem = texto("por_perguntas", conteudo(ocultos=range(10)))

    assert "no Cronograma (item" in com
    assert "no Cronograma (item" not in sem


def test_a_remissao_do_periodo_usa_o_numero_impresso():
    """FR-5107: com um oculto antes dele, o período é o 2 da tabela, e não o 3 do `order`."""
    base = conteudo(ocultos=[1])
    for evento in base["schedule"]:
        evento["isRegistrationPeriod"] = False
    base["schedule"][2]["isRegistrationPeriod"] = True

    lido = " ".join(texto("por_perguntas", base).split())

    assert "(Cronograma, nº 2)." in lido
    assert ("2", "Marco03") in linhas_da_tabela(texto("por_perguntas", base))


def test_o_periodo_oculto_sai_sem_remissao_e_com_o_periodo():
    """FR-5107, caso-limite: o portal abre pelo período; só a remissão some."""
    lido = " ".join(texto("por_perguntas", conteudo(ocultos=[0])).split())

    assert "Período de inscrições: de 13/10/2026, às 09h, a 30/10/2026, às 23h59." in lido
    assert "(Cronograma, nº" not in lido


def test_o_documento_sem_oculto_e_o_de_antes():
    """SC-1580, FR-5114: a chave verdadeira em todo Evento não muda uma letra do documento."""
    sem_chave = congelado("A")["content"]
    com_chave = copy.deepcopy(sem_chave)
    for evento in com_chave["schedule"]:
        evento["shownInPdf"] = True

    for apresentacao in APRESENTACOES:
        assert texto(apresentacao, com_chave) == texto(apresentacao, sem_chave), apresentacao


# --- a Revisão (FR-5110, D-009) -----------------------------------------------------------------


def test_a_revisao_diz_qual_evento_nao_sai_no_pdf():
    base = conteudo(ocultos=[VINCULADO_A_ETAPA])

    [bloco] = revisao._cronograma(base)

    marcados = [item for item in bloco["itens"] if revisao.NAO_SAI_NO_PDF in item["linhas"]]
    assert len(marcados) == 1
    assert "nota" not in bloco


def test_a_revisao_com_todos_ocultos_diz_que_a_secao_nao_sai():
    [bloco] = revisao._cronograma(conteudo(ocultos=range(10)))

    assert bloco["nota"] == revisao.SECAO_DO_CRONOGRAMA_NAO_SAI
    assert len(bloco["itens"]) == 10, "os Eventos continuam listados: continuam valendo"


def test_a_revisao_sem_evento_nao_inventa_nota():
    [bloco] = revisao._cronograma({"schedule": []})

    assert "nota" not in bloco
