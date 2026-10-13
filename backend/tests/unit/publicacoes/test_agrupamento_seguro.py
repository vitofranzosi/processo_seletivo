"""O agrupamento seguro da apresentação por perguntas (069, FR-1365, FR-1373 a FR-1375, R-009).

Agrupa-se só por **identidade** do dado e da frase impressa, nunca por semelhança. O que é igual em
todos os Perfis sai uma vez; o que difere sai por grupo, e as unidades que não se separam — o corte
com o empate, os suplentes e a continuação; os critérios de desempate de um marco — saem inteiras em
cada grupo quando diferem. A faixa de códigos ("TP-01 a TP-16") só se usa quando é contígua.
"""

import copy
import re

import pytest

from processo_seletivo.editais.domain import secoes as catalogo
from processo_seletivo.publicacoes.infrastructure import apresentacao
from tests.unit.publicacoes.cenarios_da_auditoria import (
    congelado,
    levado_ao_catalogo_novo,
    por_perguntas,
)
from tests.unit.publicacoes.test_pdf import documento, secoes, snapshot, texto_de
from tests.unit.publicacoes.test_pdf_classificacao import ETAPAS, marco

RODAPE = re.compile(r"^(Edital \d+/\d+( · Verificação [0-9a-f]+…)?|Página \d+ de \d+)$")


def _linhas(documento_):
    return [
        linha
        for linha in texto_de(documento_).splitlines()
        if linha.strip() and not RODAPE.match(linha) and " . ." not in linha
    ]


def _corrido(documento_):
    return " ".join(" ".join(_linhas(documento_)).split())


def _do_cenario(cenario):
    return levado_ao_catalogo_novo(congelado(cenario)["content"])


def _por_perguntas(**alteracoes):
    return snapshot(sections=secoes(catalogo_=catalogo.CATALOGO_DA_069), **alteracoes)


def _sorteio(code, *, ocorrencia="Concurso 6100", **alteracoes):
    return marco(
        code=code,
        name=f"Sorteio {code}",
        orderProduction="POR_SORTEIO",
        stages=[],
        tiebreakers=[],
        drawMethod={
            "algorithm": "IFES-SORTEIO-SHA256-v1",
            "source": "Loteria Federal",
            "occurrence": ocorrencia,
            "occurrenceAt": "2026-11-20T20:00:00-03:00",
            "derivation": "o primeiro concurso após a data do sorteio",
            "normalization": {"rule": "DIGITOS_EM_SEQUENCIA", "text": "os dígitos em sequência"},
            "substitutionRule": {
                "rule": "OCORRENCIA_SEGUINTE_DA_MESMA_FONTE",
                "text": "a ocorrência seguinte",
            },
        },
        **alteracoes,
    )


def _dois_perfis(conteudo, **segundo):
    primeiro = conteudo["profiles"][0]
    outro = copy.deepcopy(primeiro)
    outro.update(
        id="33333333-3333-3333-3333-333333333334",
        code="DOC-MAT",
        name="Professor de Matemática",
        locality="Campus Vitória",
        **segundo,
    )
    conteudo["profiles"].append(outro)
    return conteudo


# --- as vagas pelo dado (FR-1373) ------------------------------------------------------------


def test_matriz_unica_quando_todo_perfil_tem_vaga():
    linhas = _linhas(por_perguntas("A"))
    legendas = [linha for linha in linhas if linha.startswith("Tabela ")]
    assert legendas[0] == "Tabela 1 — Vagas por Perfil e lista de concorrência"
    assert not any("Vagas imediatas por lista" in legenda for legenda in legendas)


def test_perfis_de_mesmo_nome_em_tabela_propria_com_o_nome_na_legenda():
    linhas = _linhas(por_perguntas("B"))
    legendas = [linha for linha in linhas if linha.startswith("Tabela ")]
    assert legendas[:3] == [
        "Tabela 1 — Perfis",
        "Tabela 2 — Tutor presencial — Perfis TP-01 a TP-16",
        "Tabela 3 — Vagas imediatas por lista de concorrência",
    ]
    assert "São 10 vagas imediatas, nos Perfis TD-ADM e TD-INFO-EDU." in _corrido(
        por_perguntas("B")
    )


# --- atributos comuns uma vez (FR-1374) ------------------------------------------------------


def test_em_todos_os_perfis_so_com_o_que_e_igual():
    texto = _corrido(por_perguntas("A"))
    assert (
        "Em todos os Perfis: Especialização em Informática na Educação; carga horária de 480 "
        "horas; não há cadastro de reserva."
    ) in texto
    conteudo = _do_cenario("A")
    conteudo["profiles"][0]["workload"] = "360 horas"
    texto = _corrido(pdf_de(conteudo))
    assert "carga horária de 480 horas" not in texto.split("Em todos os Perfis:")[1].split(".")[0]
    assert "Carga horária" in _linhas(pdf_de(conteudo)), "o que difere vai à tabela"


def pdf_de(conteudo):
    return por_perguntas("A", conteudo)


def test_a_tabela_de_reserva_sem_ampla_concorrencia():
    linhas = _linhas(por_perguntas("A"))
    inicio = linhas.index("Tabela 3 — Reserva de vagas")
    tabela = linhas[inicio : inicio + 10]
    assert "PPI — Pretos, pardos e indígenas" in tabela
    assert "PcD — Pessoas com deficiência" in tabela
    assert not any("Ampla" in linha for linha in tabela)


def test_a_lista_sem_percentual_sai_com_travessao():
    conteudo = _por_perguntas()
    regra = conteudo["profiles"][0]["competitionModalities"][0]["normativeRule"]
    regra["percentage"] = None
    linhas = _linhas(documento(conteudo))
    inicio = next(i for i, linha in enumerate(linhas) if "Reserva de vagas" in linha)
    tabela = linhas[inicio : inicio + 8]
    assert "—" in tabela
    assert not any(linha.endswith("%") and linha != "—" for linha in tabela)


# --- faixa de códigos (FR-1375) --------------------------------------------------------------


def test_a_faixa_so_quando_os_codigos_sao_contiguos():
    assert apresentacao.faixa_de_codigos(["TP-01", "TP-02", "TP-03"]) == "TP-01 a TP-03"
    assert apresentacao.faixa_de_codigos(["TP-01", "TP-03", "TP-04"]) == "TP-01, TP-03 e TP-04"
    assert apresentacao.faixa_de_codigos(["TP-1", "TP-02", "TP-03"]) == "TP-1, TP-02 e TP-03"
    assert apresentacao.faixa_de_codigos(["TP-01", "TD-02", "TP-03"]) == "TP-01, TD-02 e TP-03"
    assert apresentacao.faixa_de_codigos(["TP-01", "TP-02"]) == "TP-01 e TP-02"


def test_um_perfil_so_sem_em_todos_os_perfis_nem_faixa():
    texto = _corrido(documento(_por_perguntas()))
    assert "Em todos os Perfis" not in texto
    assert "Para todos os Perfis" not in texto
    assert not re.search(r"Perfis \S+ a \S+", texto)


# --- a partilha parcial e as unidades indivisíveis (R-009) -----------------------------------


@pytest.fixture(scope="module")
def variante_de_b():
    """B com os suplentes dos tutores presenciais diferentes: o corte difere, o resto é igual."""
    conteudo = _do_cenario("B")
    for perfil in conteudo["profiles"]:
        if perfil["code"].startswith("TP-"):
            perfil["classificationMilestones"][0]["cutRule"]["surplusCount"] = 3
    return _corrido(por_perguntas("B", conteudo))


def test_partilha_parcial_o_comum_sai_uma_vez(variante_de_b):
    selecao = variante_de_b.split("Como será a seleção?")[-1]
    assert selecao.count("A ordem de classificação segue a nota final.") == 1
    assert selecao.count("Critérios de desempate, nesta ordem:") == 1
    comum = selecao.index("Para todos os Perfis:")
    assert comum < selecao.index("A ordem de classificação segue a nota final.")


def test_partilha_parcial_a_unidade_do_corte_sai_inteira_em_cada_grupo(variante_de_b):
    selecao = variante_de_b.split("Como será a seleção?")[-1]
    td = selecao.index("Para os Perfis TD-ADM e TD-INFO-EDU:")
    tp = selecao.index("Para os Perfis TP-01 a TP-16:")
    empate = "Se houver empate na última posição, passam todos os empatados"
    continuacao = "Depois, poderão ser chamados outros candidatos"
    for inicio, suplentes in ((td, "mais 5 (cinco) suplentes"), (tp, "mais 3 (três) suplentes")):
        trecho = selecao[inicio : inicio + 700]
        assert suplentes in trecho
        assert empate in trecho, "o empate no corte não se separa do corte"
        assert continuacao in trecho, "a continuação não se separa do corte"


def test_partilha_parcial_o_desempate_inteiro(variante_de_b):
    selecao = variante_de_b.split("Como será a seleção?")[-1]
    desempate = selecao[selecao.index("Critérios de desempate, nesta ordem:") :]
    assert desempate.index("1º") < desempate.index("2º") < desempate.index("3º")


def test_dois_marcos_no_mesmo_perfil_saem_nomeados():
    conteudo = _por_perguntas(stages=ETAPAS)
    conteudo["profiles"][0]["classificationMilestones"] = [
        marco(code="PARCIAL", name="Classificação parcial"),
        marco(code="FINAL", name="Classificação final", id="66666666-6666-6666-6666-666666666667"),
    ]
    linhas = _linhas(documento(conteudo))
    assert "PARCIAL — Classificação parcial" in linhas
    assert "FINAL — Classificação final" in linhas
    assert linhas.index("PARCIAL — Classificação parcial") < linhas.index(
        "FINAL — Classificação final"
    )


def test_o_metodo_proprio_de_um_marco_sai_com_os_dados_proprios():
    conteudo = _dois_perfis(_por_perguntas())
    conteudo["profiles"][0]["classificationMilestones"] = [_sorteio("S1")]
    conteudo["profiles"][1]["classificationMilestones"] = [
        _sorteio("S2", ocorrencia="Concurso 6200", id="66666666-6666-6666-6666-666666666668")
    ]
    texto = _corrido(documento(conteudo))
    dados = texto.split("Dados para conferir o sorteio")[-1]
    assert "Para o Perfil DOC-INFO — Professor de Informática:" in dados
    assert "Para o Perfil DOC-MAT — Professor de Matemática:" in dados
    assert dados.index("“Concurso 6100”") < dados.index("Para o Perfil DOC-MAT")
    assert dados.index("Para o Perfil DOC-MAT") < dados.index("“Concurso 6200”")


def test_o_metodo_comum_sai_uma_vez():
    conteudo = _dois_perfis(_por_perguntas())
    for indice, perfil in enumerate(conteudo["profiles"]):
        perfil["classificationMilestones"] = [
            _sorteio("S1", id=f"66666666-6666-6666-6666-66666666667{indice}")
        ]
    dados = _corrido(documento(conteudo)).split("Dados para conferir o sorteio")[-1]
    assert dados.count("“Concurso 6100”") == 1
    assert "Para o Perfil" not in dados


# --- o vocabulário pelo dado (FR-1365) -------------------------------------------------------

INTERNOS = re.compile(r"\b(polos?|turmas?|cursos?)\b", re.IGNORECASE)


def test_polo_turma_e_curso_so_onde_o_dado_os_traz():
    conteudo = _por_perguntas()
    for secao in conteudo["sections"]:
        if secao["type"] == catalogo.TEXTUAL:
            secao["content"] = "" if secao["key"] == "acesso-ao-curso" else "Texto transcrito."
    dado = repr({chave: valor for chave, valor in conteudo.items() if chave != "sections"})
    assert not INTERNOS.search(dado), "o caso precisa de um dado sem essas palavras"
    texto = _corrido(documento(conteudo))
    assert not INTERNOS.search(texto), INTERNOS.search(texto)
    assert "Localidade" in texto
    assert "DOC-INFO" in texto


def test_o_perfil_e_referido_pelo_codigo_e_a_localidade_pelo_rotulo():
    linhas = _linhas(por_perguntas("A"))
    inicio = linhas.index("Tabela 1 — Vagas por Perfil e lista de concorrência")
    assert linhas[inicio + 1 : inicio + 3] == ["Código", "Localidade"]


# --- o que a revisão de código encontrou -----------------------------------------------------


def test_um_perfil_so_imprime_o_nome_a_descricao_e_o_cadastro():
    """Sem "todos os Perfis" e sem tabela de características, a frase diz o Perfil — antes, o corpo
    do Edital de um Perfil calava o nome, a descrição e o cadastro, que a plana imprime."""
    texto = _corrido(documento(_por_perguntas()))
    assert "Perfil DOC-INFO: Professor de Informática — docência em Informática" in texto
    vagas = texto.split("Quantas vagas há, e onde?")[-1].split("Cronograma")[0]
    assert "cadastro de reserva" in vagas


def test_a_descricao_igual_sob_nomes_diferentes_vai_para_a_tabela():
    """A frase P1 só leva a descrição com o nome comum; sem ele, a descrição não saía em lugar
    nenhum."""
    conteudo = _por_perguntas()
    _dois_perfis(conteudo)
    texto = _corrido(documento(conteudo))
    assert "Docência em Informática" in texto


def test_a_ordem_do_marco_nao_se_parte_entre_grupos():
    """A normalização ("Depois, o resultado é dividido…") vem antes do arredondamento, no mesmo
    grupo: partilhadas frase a frase, a comum saía primeiro e a divisão, depois dela."""
    conteudo = _do_cenario("B")
    for perfil in conteudo["profiles"]:
        if perfil["code"].startswith("TP-"):
            perfil["classificationMilestones"][0]["normalization"] = "PELA_SOMA_DOS_PESOS"
    selecao = _corrido(por_perguntas("B", conteudo)).split("Como será a seleção?")[-1]
    tp = selecao[selecao.index("Para os Perfis TP-01 a TP-16:") :]
    divisao = tp.index("Depois, o resultado é dividido pela soma dos pesos.")
    assert divisao < tp.index("arredondad")


def test_a_frase_do_uso_no_desempate_so_para_quem_usa():
    """Os dados declarados se agrupam pelo que se imprime, inclusive a frase do uso no desempate."""
    conteudo = _do_cenario("B")
    for perfil in conteudo["profiles"]:
        if perfil["code"].startswith("TD-"):
            perfil["classificationMilestones"][0]["tiebreakers"] = [
                criterio
                for criterio in perfil["classificationMilestones"][0]["tiebreakers"]
                if "factId" not in (criterio.get("parameters") or {})
            ]
    texto = _corrido(por_perguntas("B", conteudo))
    inscricao = texto.split("Como se inscrever?")[-1].split("Quais documentos enviar?")[0]
    assert "Para os Perfis TD-ADM e TD-INFO-EDU, informe também na inscrição:" in inscricao
    assert "Para os Perfis TP-01 a TP-16, informe também na inscrição:" in inscricao
