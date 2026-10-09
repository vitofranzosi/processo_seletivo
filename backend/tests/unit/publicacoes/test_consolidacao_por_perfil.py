"""068 — O que se repete por Perfil sai uma vez no Edital em PDF (ED-04, ED-11).

Com dois ou mais Perfis, a seção de Perfis passa a ter, logo depois da tabela de Perfis, a tabela
de vagas Perfil × lista e as tabelas de modalidades agrupadas; abaixo delas, as frases de reversão
e de convocação, uma vez; e, depois do último Perfil, as subseções comuns de requisitos e de
marcos, junto das atribuições comuns da `064`. O Perfil agrupado remete a elas.

**Duas famílias de teste.** O plano de consolidação é provado como estrutura — quem se junta com
quem, que número cada subseção tem —, sem compor PDF. A forma do documento é provada **lendo o
documento composto**: o que a spec afirma é sobre o artefato que o candidato lê.

A prova de que nenhuma regra se perdeu, Perfil a Perfil, está em
`test_equivalencia_da_consolidacao.py`.
"""

import copy
import json

import pytest

from processo_seletivo.publicacoes.infrastructure import pdf
from tests.unit.publicacoes.test_pdf import documento, paginas_de, snapshot, texto_de

# ---------------------------------------------------------------------------
# Cenário: o do cenário A da auditoria, reduzido ao que importa
# ---------------------------------------------------------------------------

ANALISE = "a0000000-0000-0000-0000-000000000001"
EVENTO = "e0000000-0000-0000-0000-000000000001"
METODO = {
    "source": "Loteria Federal",
    "algorithm": "IFES-SORTEIO-SHA256-v1",
    "derivation": "A extração de sábado imediatamente anterior à data publicada do sorteio.",
    "occurrence": "Concurso 6010",
    "occurrenceAt": "2026-11-14T19:00:00-03:00",
    "normalization": {
        "rule": "DIGITOS_EM_SEQUENCIA",
        "text": "Os cinco números sorteados, na ordem dos prêmios, separados por espaço.",
    },
    "substitutionRule": {
        "rule": "OCORRENCIA_SEGUINTE_DA_MESMA_FONTE",
        "text": "Não havendo extração na data prevista, vale a extração seguinte da mesma fonte.",
    },
}
LINHAS_DO_METODO = ("Algoritmo:", "Fonte:", "Ocorrência:", "Quando:", "Derivação:", "Semente:")
REQUISITOS = (
    "Diploma de curso superior de graduação reconhecido pelo MEC",
    "Acesso a computador com conexão à internet",
)
NOMES = {
    "PPI": "Pretos, pardos e indígenas",
    "PcD": "Pessoas com deficiência",
    "PTT": "Pessoas transgênero e travestis",
}
PERCENTUAIS = {"PPI": "25.0000", "PcD": "5.0000", "PTT": None}
FUNDAMENTO = "Resolução CS nº 10/2017 do Ifes"
REVERSAO_ESGOTAMENTO = (
    "Havendo ausência de candidatos aprovados na reserva de vagas, o quantitativo será destinado "
    "à respectiva ampla concorrência."
)
REVERSAO_SALDO = (
    "Na hipótese do não preenchimento total das vagas reservadas, o quantitativo não preenchido "
    "será destinado à respectiva ampla concorrência."
)
CONVOCACAO_PUBLICACAO = (
    "A convocação dos classificados será feita por publicação no endereço eletrônico do certame."
)
SEPARADAMENTE = (
    "Os marcos abaixo se aplicam a cada um desses Perfis separadamente, sobre as inscrições do "
    "próprio Perfil: cada Perfil tem a sua própria classificação e o seu próprio resultado."
)


def marco(codigo, **alteracoes):
    base = {
        "id": f"{codigo}-marco",
        "code": "SORTEIO",
        "name": "Classificação por sorteio eletrônico",
        "stages": [],
        "orderProduction": "POR_SORTEIO",
        "operation": "SOMA_PONDERADA",
        "normalization": "NENHUMA",
        "rounding": {},
        "tiebreakers": [],
        "drawMethod": None,
        "appealWindow": {"unit": "DIAS_CORRIDOS", "admits": True, "durationDays": 2},
        "cutRule": {
            "targetKind": "FROM_VACANCY_TABLE",
            "tieOutcome": "STRICT",
            "targetCount": None,
            "continuation": "ALLOWED",
            "surplusCount": 15,
            "governedStage": ANALISE,
        },
    }
    return {**base, **alteracoes}


def perfil(
    codigo,
    *,
    vagas=(28, 10, 2),
    quadro=("PPI", "PcD"),
    modalidades=("PcD", "PPI"),
    percentuais=None,
    reversao="ON_EXHAUSTION",
    convocacao="PUBLICATION",
    requisitos=REQUISITOS,
    marcos=None,
    atribuicoes="",
):
    """Um polo do cenário A: AC, PPI e PcD, quadro 28/10/2, um marco por sorteio pelo método comum.

    `quadro` é a ordem declarada das listas reservadas no quadro; `modalidades`, a do snapshot (por
    código, como `edital_snapshot` as ordena). As duas diferem de propósito: é o ED-11.
    """
    percentuais = {**PERCENTUAIS, **(percentuais or {})}
    ids = {sigla: f"{codigo}-{sigla}" for sigla in ("AC", *NOMES)}
    declaradas = [
        {
            "id": ids["AC"],
            "code": "AC",
            "name": "Ampla concorrência",
            "description": "",
            "normativeRule": None,
        }
    ] + [
        {
            "id": ids[sigla],
            "code": sigla,
            "name": NOMES[sigla],
            "description": "",
            "normativeRule": {"foundation": FUNDAMENTO, "percentage": percentuais[sigla]},
        }
        for sigla in modalidades
    ]
    linhas = []
    if vagas is not None:
        linhas = [{"id": f"{codigo}-l0", "modalityId": None, "immediateVacancies": vagas[0]}] + [
            {"id": f"{codigo}-l{n}", "modalityId": ids[sigla], "immediateVacancies": quantidade}
            for n, (sigla, quantidade) in enumerate(zip(quadro, vagas[1:], strict=True), 1)
        ]
    return {
        "id": f"{codigo}-id",
        "code": codigo,
        "name": "Especialização em Informática na Educação",
        "description": f"Curso a distância. Polo {codigo}.",
        "duties": atribuicoes,
        "locality": f"Polo {codigo}",
        "workload": "480 horas",
        "compensation": "",
        "immediateVacancies": sum(vagas) if vagas is not None else 0,
        "reserveType": "NONE",
        "reserveLimit": None,
        "requirements": list(requisitos),
        "declaredFacts": [],
        "callForm": convocacao,
        "vacancyReversion": {"kind": reversao} if reversao else {},
        "vacancyTable": linhas,
        "generalCompetitionModalityId": ids["AC"],
        "competitionModalities": declaradas,
        "classificationMilestones": [marco(codigo)] if marcos is None else marcos,
        "classificationInformation": {},
        "callInformation": {},
    }


def edital(*perfis, metodo=METODO):
    etapas = [
        {
            "id": ANALISE,
            "name": "Análise documental",
            "order": 1,
            "weight": None,
            "eliminatory": True,
            "classificatory": False,
            "minimumScore": None,
            "scheduleEventId": None,
            "forma": "DECISORIA",
        }
    ]
    conteudo = snapshot(profiles=list(perfis), stages=etapas)
    if metodo is not None:
        conteudo["drawMethod"] = metodo
    return conteudo


QUATRO = ("INF-BJN", "INF-IUN", "INF-SMT", "INF-VAL")


def cenario_a(**por_perfil):
    """Os quatro polos iguais; `por_perfil` troca o que o chamador pedir, por código."""
    return edital(*(perfil(codigo, **por_perfil.get(codigo, {})) for codigo in QUATRO))


# ---------------------------------------------------------------------------
# Leitura
# ---------------------------------------------------------------------------


def plano(conteudo, secao=5):
    return pdf.plano_de_consolidacao(pdf._grafado(conteudo, previa=False), secao)


def materias(plano_):
    return [(item.numero, item.materia, item.codigos) for item in plano_.subsecoes]


def linhas(conteudo):
    """Cada linha do documento, na ordem: o texto desenhado, sem rodapé."""
    return [
        linha
        for linha in texto_de(documento(conteudo)).splitlines()
        if linha.strip() and not linha.startswith("Edital ")
    ]


def corrido(conteudo):
    return " ".join(" ".join(linhas(conteudo)).split())


def secao_de_perfis(conteudo):
    """As linhas da seção de Perfis — do título dela ao título da seção seguinte."""
    todas = linhas(conteudo)
    inicio = next(i for i, linha in enumerate(todas) if linha.endswith(". PERFIS DE VAGA"))
    fim = next(
        i
        for i, linha in enumerate(todas[inicio + 1 :], inicio + 1)
        if linha[:1].isdigit() and ". " in linha[:4] and linha.split(". ", 1)[1].isupper()
    )
    return todas[inicio:fim]


def bloco_do_perfil(conteudo, codigo):
    """As linhas da subseção de um Perfil, do título dela ao próximo título N.k."""
    secao = secao_de_perfis(conteudo)
    inicio = next(i for i, linha in enumerate(secao) if f" {codigo} — " in linha[:20])
    fim = next(
        (
            i
            for i, linha in enumerate(secao[inicio + 1 :], inicio + 1)
            if linha.split(" ", 1)[0].count(".") == 1 and linha[:1].isdigit()
        ),
        len(secao),
    )
    return secao[inicio:fim]


# ---------------------------------------------------------------------------
# Phase 2 — o plano de consolidação (FR-1340, FR-1359, R-001, R-002, R-005)
# ---------------------------------------------------------------------------


def test_um_perfil_nao_tem_plano():
    assert plano(edital(perfil("INF-BJN"))) is None


def test_marcos_e_requisitos_identicos_agrupam_todos():
    assert materias(plano(cenario_a())) == [
        ("5.5", "requisitos", QUATRO),
        ("5.6", "marcos", QUATRO),
    ]


@pytest.mark.parametrize(
    "diferenca",
    [
        {"appealWindow": {"unit": "DIAS_CORRIDOS", "admits": True, "durationDays": 3}},
        {"name": "Sorteio público"},
        {"code": "SORT-2"},
        {"cutRule": {**marco("x")["cutRule"], "surplusCount": 10}},
        {"cutRule": {**marco("x")["cutRule"], "continuation": "FORBIDDEN"}},
    ],
    ids=["prazo de recurso", "nome do marco", "código do marco", "suplentes", "continuação"],
)
def test_qualquer_linha_diferente_separa_os_marcos(diferenca):
    conteudo = cenario_a(**{"INF-SMT": {"marcos": [marco("INF-SMT", **diferenca)]}})
    assert ("5.6", "marcos", ("INF-BJN", "INF-IUN", "INF-VAL")) in materias(plano(conteudo))
    assert all(
        "INF-SMT" not in codigos for _, m, codigos in materias(plano(conteudo)) if m == "marcos"
    )


def test_o_titulo_que_nomeia_o_perfil_nao_entra_na_comparacao():
    """O título "Marcos classificatórios — INF-BJN" difere em todo Perfil, e não é regra."""
    assert ("5.6", "marcos", QUATRO) in materias(plano(cenario_a()))


@pytest.mark.parametrize(
    "requisitos",
    [
        (*REQUISITOS, "Disponibilidade aos sábados"),
        REQUISITOS[:1],
        tuple(reversed(REQUISITOS)),
        (REQUISITOS[0] + ".", REQUISITOS[1]),
    ],
    ids=["um a mais", "um a menos", "outra ordem", "pontuação"],
)
def test_requisitos_diferentes_nao_agrupam(requisitos):
    conteudo = cenario_a(**{"INF-IUN": {"requisitos": requisitos}})
    assert ("5.5", "requisitos", ("INF-BJN", "INF-SMT", "INF-VAL")) in materias(plano(conteudo))


def test_requisitos_vazios_nao_agrupam_e_perfil_sem_marco_nao_entra():
    conteudo = cenario_a(**{codigo: {"requisitos": ()} for codigo in QUATRO})
    conteudo["profiles"][0]["classificationMilestones"] = []
    assert materias(plano(conteudo)) == [("5.5", "marcos", QUATRO[1:])]


def test_grupo_de_um_nao_existe_e_os_grupos_seguem_o_primeiro_perfil():
    outro = {"marcos": [marco("x", name="Sorteio público")]}
    conteudo = cenario_a(**{"INF-BJN": outro, "INF-SMT": outro})
    assert [item for item in materias(plano(conteudo)) if item[1] == "marcos"] == [
        ("5.6", "marcos", ("INF-BJN", "INF-SMT")),
        ("5.7", "marcos", ("INF-IUN", "INF-VAL")),
    ]


def test_as_subsecoes_seguem_atribuicoes_requisitos_e_marcos():
    """As atribuições da `064` mantêm os números de antes desta feature (FR-1359, D-001)."""
    conteudo = cenario_a(**{codigo: {"atribuicoes": "Mediar.\nAcompanhar."} for codigo in QUATRO})
    assert materias(plano(conteudo)) == [
        ("5.5", "atribuicoes", QUATRO),
        ("5.6", "requisitos", QUATRO),
        ("5.7", "marcos", QUATRO),
    ]
    sem = cenario_a(**{codigo: {"atribuicoes": "Mediar.\nAcompanhar."} for codigo in QUATRO})
    for item in sem["profiles"]:
        item["requirements"], item["classificationMilestones"] = [], []
    assert materias(plano(sem)) == [("5.5", "atribuicoes", QUATRO)]


def test_a_remissao_de_cada_perfil_e_o_numero_da_subsecao_do_grupo_dele():
    conteudo = pdf._grafado(cenario_a(), previa=False)
    plano_ = pdf.plano_de_consolidacao(conteudo, 5)
    for item in conteudo["profiles"]:
        assert plano_.remissao(item, "requisitos") == "5.5"
        assert plano_.remissao(item, "marcos") == "5.6"
        assert plano_.remissao(item, "atribuicoes") is None


def test_a_ordem_das_listas_e_a_do_quadro_e_nao_a_do_codigo():
    """ED-11: o quadro declara PPI, PcD; o snapshot ordena PcD, PPI por código."""
    assert plano(cenario_a()).listas == ("Ampla concorrência", "PPI", "PcD")


def test_a_lista_que_so_um_quadro_declara_vem_depois_e_a_que_nenhum_declara_por_ultimo():
    conteudo = cenario_a(
        **{
            "INF-IUN": {
                "vagas": (27, 10, 2, 1),
                "quadro": ("PPI", "PcD", "PTT"),
                "modalidades": ("PTT", "PcD", "PPI"),
            },
            "INF-VAL": {"modalidades": ("PTT", "PcD", "PPI")},
        }
    )
    assert plano(conteudo).listas == ("Ampla concorrência", "PPI", "PcD", "PTT")
    sem_quadro = cenario_a(**{"INF-VAL": {"modalidades": ("PTT", "PcD", "PPI")}})
    assert plano(sem_quadro).listas == ("Ampla concorrência", "PPI", "PcD", "PTT")


def test_o_plano_nao_muda_o_snapshot():
    conteudo = cenario_a()
    antes = json.dumps(conteudo, sort_keys=True)
    plano(conteudo)
    assert json.dumps(conteudo, sort_keys=True) == antes


def test_as_linhas_por_pedacos_nunca_partem_um_codigo():
    pedacos = pdf._codigos_enumerados([f"ADS - P{n:02d}" for n in range(1, 13)])
    linhas_ = pdf._linhas_sem_partir("Nos Perfis", pedacos, pdf.CORPO_TEXTO, pdf.REGULAR)
    assert len(linhas_) > 1
    for linha in linhas_:
        assert not linha.endswith("ADS") and not linha.startswith("- P")


# ---------------------------------------------------------------------------
# US1 — As vagas numa tabela só (FR-1342 a FR-1345, FR-1356, D-002)
# ---------------------------------------------------------------------------


def _depois_da_legenda(secao, legenda, quantas):
    inicio = next(i for i, linha in enumerate(secao) if linha.endswith(legenda))
    return secao[inicio + 1 : inicio + 1 + quantas]


def test_a_tabela_de_vagas_e_uma_matriz_perfil_por_lista():
    secao = secao_de_perfis(cenario_a())
    assert "Tabela 2 — Vagas por lista de concorrência" in secao
    celulas = _depois_da_legenda(secao, "Vagas por lista de concorrência", 4 + 4 * 4)
    assert celulas[:4] == ["Perfil", "Ampla concorrência", "PPI", "PcD"]
    assert celulas[4:] == [valor for codigo in QUATRO for valor in (codigo, "28", "10", "2")]


def test_nenhum_perfil_imprime_o_proprio_quadro_nem_a_propria_tabela_de_modalidades():
    conteudo = cenario_a()
    texto = corrido(conteudo)
    assert "Quadro de vagas" not in texto
    for codigo in QUATRO:
        assert f"Modalidades de concorrência — {codigo}" not in texto
        assert not any("Tabela" in linha for linha in bloco_do_perfil(conteudo, codigo))


def test_lista_que_o_perfil_nao_declara_sai_com_traco_e_nao_com_zero():
    conteudo = cenario_a(
        **{
            "INF-IUN": {
                "vagas": (27, 10, 2, 1),
                "quadro": ("PPI", "PcD", "PTT"),
                "modalidades": ("PTT", "PcD", "PPI"),
            }
        }
    )
    celulas = _depois_da_legenda(
        secao_de_perfis(conteudo), "Vagas por lista de concorrência", 5 + 4 * 5
    )
    assert celulas[:5] == ["Perfil", "Ampla concorrência", "PPI", "PcD", "PTT"]
    assert celulas[5:15] == ["INF-BJN", "28", "10", "2", "—", "INF-IUN", "27", "10", "2", "1"]


def test_perfil_sem_vaga_imediata_ou_sem_quadro_nao_tem_linha():
    conteudo = cenario_a(
        **{"INF-IUN": {"vagas": (0, 0, 0)}, "INF-SMT": {"vagas": None, "reversao": None}}
    )
    secao = secao_de_perfis(conteudo)
    celulas = _depois_da_legenda(secao, "Vagas por lista de concorrência", 4 + 2 * 4)
    assert [celulas[4], celulas[8]] == ["INF-BJN", "INF-VAL"]
    assert "INF-IUN" not in _depois_da_legenda(secao, "Vagas por lista de concorrência", 30)[:12]


def test_nenhum_perfil_com_quadro_nao_tem_tabela_de_vagas_e_as_tabelas_seguem_sem_lacuna():
    conteudo = cenario_a(**{codigo: {"vagas": None, "reversao": None} for codigo in QUATRO})
    texto = corrido(conteudo)
    assert "Vagas por lista de concorrência" not in texto
    assert "Tabela 2 — Modalidades de concorrência" in texto
    assert "Tabela 3 — Cronograma" in texto


def test_uma_tabela_de_modalidades_quando_todas_sao_iguais_na_ordem_das_colunas():
    secao = secao_de_perfis(cenario_a())
    assert "Tabela 3 — Modalidades de concorrência" in secao
    celulas = _depois_da_legenda(secao, "— Modalidades de concorrência", 3 + 3 * 3)
    assert celulas == [
        "Modalidade",
        "Percentual",
        "Fundamento normativo",
        "AC — Ampla concorrência",
        "—",
        "—",
        "PPI — Pretos, pardos e indígenas",
        "25%",
        FUNDAMENTO,
        "PcD — Pessoas com deficiência",
        "5%",
        FUNDAMENTO,
    ]
    assert sum("Modalidades de concorrência" in linha for linha in secao) == 1


def test_modalidades_diferentes_saem_em_tabelas_por_grupo_com_os_codigos():
    conteudo = cenario_a(
        **{codigo: {"percentuais": {"PPI": "30.0000"}} for codigo in ("INF-SMT", "INF-VAL")}
    )
    secao = secao_de_perfis(conteudo)
    assert "Tabela 3 — Modalidades de concorrência — Perfis INF-BJN e INF-IUN" in secao
    assert "Tabela 4 — Modalidades de concorrência — Perfis INF-SMT e INF-VAL" in secao


def test_grupo_de_um_perfil_e_nomeado_no_singular():
    conteudo = cenario_a(**{"INF-VAL": {"percentuais": {"PPI": "30.0000"}}})
    secao = secao_de_perfis(conteudo)
    assert "Tabela 4 — Modalidades de concorrência — Perfil INF-VAL" in secao


def test_a_matriz_que_nao_cabe_sai_na_forma_longa():
    """Dez listas de códigos longos não cabem lado a lado; nenhuma coluna é cortada (R-004)."""
    siglas = [f"RESERVA-LONGA-{n:02d}" for n in range(1, 11)]
    NOMES.update({sigla: f"Lista {sigla}" for sigla in siglas})
    PERCENTUAIS.update({sigla: "1.0000" for sigla in siglas})
    try:
        conteudo = cenario_a(
            **{
                codigo: {"vagas": (10, *([1] * 10)), "quadro": siglas, "modalidades": siglas}
                for codigo in QUATRO
            }
        )
        secao = secao_de_perfis(conteudo)
    finally:
        for sigla in siglas:
            NOMES.pop(sigla)
            PERCENTUAIS.pop(sigla)
    celulas = _depois_da_legenda(secao, "Vagas por lista de concorrência", 3 + 3 + 2 * 10 + 1)
    assert celulas[:6] == [
        "Perfil",
        "Lista de concorrência",
        "Vagas imediatas",
        "INF-BJN",
        "Ampla concorrência",
        "10",
    ]
    # O código do Perfil só na primeira linha dele; as demais trazem a lista e as vagas.
    assert celulas[6:26] == [
        valor for sigla in siglas for valor in (f"Lista {sigla} ({sigla})", "1")
    ]
    assert celulas[26] == "INF-IUN"


def test_o_cabecalho_da_tabela_de_vagas_se_repete_na_quebra_de_pagina():
    muitos = [perfil(f"P-{n:02d}") for n in range(1, 61)]
    paginas = paginas_de(documento(edital(*muitos)))
    com_a_tabela = [
        pagina
        for pagina in paginas
        if any(linha.startswith("P-") for linha in pagina) and "Ampla concorrência" in pagina
    ]
    assert len(com_a_tabela) >= 2


def test_edital_de_um_perfil_sai_como_antes():
    """Sem tabela de vagas, com o quadro e as modalidades no Perfil (FR-1356, R-003)."""
    texto = corrido(edital(perfil("INF-BJN")))
    assert "Vagas por lista de concorrência" not in texto
    assert "Tabela 1 — Quadro de vagas" in texto
    assert "Tabela 2 — Modalidades de concorrência" in texto
    assert "comuns aos Perfis" not in texto


def test_compor_nao_muda_o_snapshot_nem_o_hash():
    from processo_seletivo.shared.canonical import canonical_sha256

    conteudo = cenario_a()
    antes, hash_antes = copy.deepcopy(conteudo), canonical_sha256(conteudo)
    documento(conteudo)
    assert conteudo == antes
    assert canonical_sha256(conteudo) == hash_antes


# ---------------------------------------------------------------------------
# US2 — A regra de classificação uma vez, para cada Perfil (FR-1346 a FR-1349, FR-1354)
# ---------------------------------------------------------------------------


def _subsecao(conteudo, numero):
    """As linhas de uma subseção N.k da seção de Perfis, do título ao próximo título."""
    secao = secao_de_perfis(conteudo)
    inicio = next(i for i, linha in enumerate(secao) if linha.startswith(f"{numero} "))
    fim = next(
        (
            i
            for i, linha in enumerate(secao[inicio + 1 :], inicio + 1)
            if linha[:1].isdigit() and linha.split(" ", 1)[0].count(".") == 1
        ),
        len(secao),
    )
    return secao[inicio:fim]


def _marcos_do_perfil_sozinho(perfil_):
    """O texto dos marcos que um Perfil imprime no próprio bloco — o "antes" da consolidação."""
    rascunho = pdf.Composicao()
    pdf._marcos(rascunho, pdf._grafado(cenario_a(), previa=False), perfil_, False)
    return " ".join(item[1] for item in rascunho.itens if item[0] == "texto" and item[1])


def test_os_marcos_iguais_saem_uma_vez_numa_subsecao_que_nomeia_os_perfis():
    conteudo = cenario_a()
    subsecao = _subsecao(conteudo, "5.6")
    assert subsecao[0] == (
        "5.6 Marcos classificatórios comuns aos Perfis INF-BJN, INF-IUN, INF-SMT e INF-VAL"
    )
    assert corrido(conteudo).count("SORTEIO — Classificação por sorteio eletrônico") == 1


def test_a_frase_que_aplica_os_marcos_a_cada_perfil_vem_antes_deles():
    """Sem ela, a regra impressa uma vez se leria como classificação conjunta (FR-1347)."""
    texto = " ".join(_subsecao(cenario_a(), "5.6"))
    assert SEPARADAMENTE in " ".join(texto.split())
    assert texto.index("separadamente") < texto.index("SORTEIO —")


def test_os_marcos_da_subsecao_sao_linha_a_linha_os_do_perfil():
    """FR-1348: o mesmo texto, sem acrescentar, suprimir nem reordenar."""
    conteudo = cenario_a()
    # O rótulo "Marcos classificatórios" do Perfil é o que o título da subseção substitui.
    antes = _marcos_do_perfil_sozinho(perfil("INF-BJN")).removeprefix("Marcos classificatórios ")
    depois = " ".join(" ".join(_subsecao(conteudo, "5.6")[1:]).split())
    assert depois == " ".join(f"{SEPARADAMENTE} {antes}".split())


def test_cada_perfil_do_grupo_remete_a_subsecao_e_nenhum_outro_remete():
    outro = {"marcos": [marco("x", name="Sorteio público")]}
    conteudo = cenario_a(**{"INF-VAL": outro})
    for codigo in QUATRO[:3]:
        assert "Marcos classificatórios: os descritos no item 5.6." in " ".join(
            bloco_do_perfil(conteudo, codigo)
        )
    proprio = bloco_do_perfil(conteudo, "INF-VAL")
    assert "Marcos classificatórios — INF-VAL" in proprio
    assert not any("os descritos no item 5.6" in linha for linha in proprio)
    assert "5.6 Marcos classificatórios comuns aos Perfis INF-BJN, INF-IUN e INF-SMT" in (
        secao_de_perfis(conteudo)
    )


def test_marcos_diferentes_em_todos_nao_criam_subsecao():
    conteudo = cenario_a(
        **{
            codigo: {"marcos": [marco(codigo, name=f"Sorteio do polo {codigo}")]}
            for codigo in QUATRO
        }
    )
    assert "Marcos classificatórios comuns" not in corrido(conteudo)
    for codigo in QUATRO:
        assert f"Marcos classificatórios — {codigo}" in bloco_do_perfil(conteudo, codigo)


def test_perfil_sem_marco_nao_remete_nem_imprime_marcos():
    conteudo = cenario_a(**{"INF-IUN": {"marcos": []}})
    bloco = bloco_do_perfil(conteudo, "INF-IUN")
    assert not any("Marcos classificatórios" in linha for linha in bloco)


def test_o_metodo_comum_sai_uma_vez_quando_todos_os_marcos_sao_iguais():
    texto = corrido(cenario_a())
    for rotulo in LINHAS_DO_METODO:
        assert texto.count(rotulo) == 1, rotulo
    assert "descrito no item" not in texto


def test_dois_grupos_pelo_metodo_comum_imprimem_as_linhas_uma_vez_e_o_segundo_remete():
    outro = {"marcos": [marco("x", name="Sorteio público")]}
    conteudo = cenario_a(**{"INF-SMT": outro, "INF-VAL": outro})
    texto = corrido(conteudo)
    for rotulo in LINHAS_DO_METODO:
        assert texto.count(rotulo) == 1, rotulo
    primeiro, segundo = _subsecao(conteudo, "5.6"), _subsecao(conteudo, "5.7")
    assert any(linha.startswith("Algoritmo:") for linha in primeiro)
    assert "Método:" in segundo
    assert "o comum a este Edital, descrito no item 5.6." in segundo
    assert "Habilitação:" in segundo
    assert not any(linha.startswith("Algoritmo:") for linha in segundo)


def test_o_perfil_com_marco_proprio_imprime_o_metodo_e_o_grupo_seguinte_remete_a_ele():
    """O primeiro lugar, na ordem do documento, é o Perfil 5.1 — antes das subseções."""
    outro = {"marcos": [marco("x", name="Sorteio público")]}
    conteudo = cenario_a(**{"INF-BJN": outro})
    assert any(linha.startswith("Algoritmo:") for linha in bloco_do_perfil(conteudo, "INF-BJN"))
    assert "o comum a este Edital, descrito no item 5.1." in _subsecao(conteudo, "5.6")


def test_metodo_proprio_continua_no_marco_e_agrupa_quando_identico():
    proprio = {**METODO, "occurrence": "Concurso 6101"}
    conteudo = cenario_a(
        **{codigo: {"marcos": [marco(codigo, drawMethod=proprio)]} for codigo in QUATRO}
    )
    subsecao = " ".join(_subsecao(conteudo, "5.6"))
    assert "Método: próprio deste marco" in subsecao
    assert "Concurso 6101" in subsecao
    assert "descrito no item" not in corrido(conteudo)


def test_marcos_com_metodo_proprio_e_com_o_comum_nao_se_juntam():
    proprio = {**METODO, "occurrence": "Concurso 6101"}
    conteudo = cenario_a(**{"INF-VAL": {"marcos": [marco("INF-VAL", drawMethod=proprio)]}})
    assert ("5.6", "marcos", QUATRO[:3]) in materias(plano(conteudo))


def test_um_bloco_coeso_por_marco_na_subsecao_comum():
    """A cascata do Perfil vale na subseção (FR-1357): o marco não se parte entre páginas."""
    ruido = "\n".join(
        f"Atribuição {n} do polo, com texto suficiente para ocupar a linha." for n in range(40)
    )
    conteudo = cenario_a(**{codigo: {"atribuicoes": ruido} for codigo in QUATRO})
    paginas = paginas_de(documento(conteudo))
    onde = {
        numero
        for numero, pagina in enumerate(paginas, 1)
        for linha in pagina
        if linha.startswith("SORTEIO —") or linha.startswith("Continuação:")
    }
    assert len(onde) == 1


def test_a_conferencia_de_remissoes_le_as_subsecoes_novas():
    """`item 5.6` é destino único e nomeado; nenhum `KeyError` na descrição (R-009)."""
    from processo_seletivo.editais.domain.validation import _itens_impressos

    mapa, _, tabelas = _itens_impressos(pdf._grafado(cenario_a(), previa=False), [])
    assert mapa[(5, 6)] == [
        (
            "a subseção «Marcos classificatórios comuns aos Perfis INF-BJN, INF-IUN, INF-SMT e "
            "INF-VAL»",
            None,
            False,
        )
    ]
    assert mapa[(5, 5)][0][0].startswith("a subseção «Requisitos comuns aos Perfis")
    assert tabelas == 4


# ---------------------------------------------------------------------------
# US3 — Frases e requisitos uma vez (FR-1350 a FR-1352, D-003)
# ---------------------------------------------------------------------------


def test_cada_frase_sai_uma_vez_sem_prefixo_quando_vale_para_todos():
    conteudo = cenario_a()
    texto = corrido(conteudo)
    assert texto.count(REVERSAO_ESGOTAMENTO) == 1
    assert texto.count(CONVOCACAO_PUBLICACAO) == 1
    for codigo in QUATRO:
        bloco = " ".join(bloco_do_perfil(conteudo, codigo))
        assert "Havendo ausência" not in bloco and "A convocação" not in bloco


def test_a_reversao_vem_logo_abaixo_da_tabela_de_vagas_e_a_convocacao_depois_das_modalidades():
    secao = secao_de_perfis(cenario_a())
    reversao = next(i for i, linha in enumerate(secao) if linha.startswith("Havendo ausência"))
    convocacao = next(i for i, linha in enumerate(secao) if linha.startswith("A convocação"))
    vagas = next(i for i, linha in enumerate(secao) if "Vagas por lista" in linha)
    modalidades = next(i for i, linha in enumerate(secao) if "Modalidades de concorrência" in linha)
    primeiro_perfil = next(i for i, linha in enumerate(secao) if linha.startswith("5.1 "))
    assert vagas < reversao < modalidades < convocacao < primeiro_perfil


def test_especies_diferentes_saem_uma_por_especie_com_os_codigos():
    conteudo = cenario_a(
        **{codigo: {"reversao": "ON_BALANCE"} for codigo in ("INF-SMT", "INF-VAL")}
    )
    texto = corrido(conteudo)
    minuscula = REVERSAO_ESGOTAMENTO[0].lower() + REVERSAO_ESGOTAMENTO[1:]
    assert f"Nos Perfis INF-BJN e INF-IUN, {minuscula}" in texto
    saldo = REVERSAO_SALDO[0].lower() + REVERSAO_SALDO[1:]
    assert f"Nos Perfis INF-SMT e INF-VAL, {saldo}" in texto


def test_perfil_sem_reversao_nao_e_alcancado_e_os_outros_sao_nomeados():
    conteudo = cenario_a(**{"INF-IUN": {"reversao": None}})
    texto = corrido(conteudo)
    minuscula = REVERSAO_ESGOTAMENTO[0].lower() + REVERSAO_ESGOTAMENTO[1:]
    assert f"Nos Perfis INF-BJN, INF-SMT e INF-VAL, {minuscula}" in texto
    assert texto.count("Havendo ausência") + texto.count("havendo ausência") == 1


def test_perfil_fora_da_tabela_de_vagas_nao_e_alcancado_pela_reversao():
    """Sem vaga imediata, nem quadro nem reversão (`067`); a frase vale para os outros três."""
    conteudo = cenario_a(**{"INF-IUN": {"vagas": (0, 0, 0)}})
    assert corrido(conteudo).count(REVERSAO_ESGOTAMENTO) == 1


def test_um_perfil_so_e_nomeado_no_singular():
    conteudo = cenario_a(**{"INF-VAL": {"convocacao": "INDIVIDUAL_MESSAGE"}})
    texto = corrido(conteudo)
    assert "No Perfil INF-VAL, a convocação dos classificados será feita por mensagem" in texto
    assert (
        "Nos Perfis INF-BJN, INF-IUN e INF-SMT, a convocação dos classificados será feita por "
        "publicação" in texto
    )


def test_perfil_sem_forma_declarada_nao_e_alcancado_pela_convocacao():
    conteudo = cenario_a(**{"INF-BJN": {"convocacao": None}})
    assert "Nos Perfis INF-IUN, INF-SMT e INF-VAL, a convocação" in corrido(conteudo)


def test_o_codigo_com_espaco_nunca_se_parte_na_frase():
    codigos = [f"ADS - P{n:02d}" for n in range(1, 13)]
    conteudo = edital(
        *(perfil(codigo) for codigo in codigos),
        perfil("ADS - P13", reversao="ON_BALANCE"),
    )
    frase = [
        linha
        for linha in secao_de_perfis(conteudo)
        if "ADS" in linha and not linha.startswith(("ADS - P", "Tabela", "5."))
    ]
    assert frase, "a frase com os códigos não saiu"
    for linha in frase:
        assert not linha.rstrip().endswith("ADS") and not linha.lstrip().startswith("- P")


def test_os_requisitos_iguais_saem_uma_vez_e_cada_perfil_remete():
    conteudo = cenario_a()
    assert _subsecao(conteudo, "5.5")[0] == (
        "5.5 Requisitos comuns aos Perfis INF-BJN, INF-IUN, INF-SMT e INF-VAL"
    )
    texto = corrido(conteudo)
    for requisito in REQUISITOS:
        assert texto.count(requisito) == 1
    for codigo in QUATRO:
        assert "Requisitos: os descritos no item 5.5." in " ".join(
            bloco_do_perfil(conteudo, codigo)
        )


def test_requisitos_diferentes_saem_no_proprio_perfil():
    conteudo = cenario_a(**{"INF-IUN": {"requisitos": (*REQUISITOS, "Residir no polo")}})
    bloco = bloco_do_perfil(conteudo, "INF-IUN")
    assert "Requisitos" in bloco and "• Residir no polo" in bloco
    assert "5.5 Requisitos comuns aos Perfis INF-BJN, INF-SMT e INF-VAL" in secao_de_perfis(
        conteudo
    )


def test_as_subsecoes_saem_na_ordem_atribuicoes_requisitos_marcos():
    conteudo = cenario_a(**{codigo: {"atribuicoes": "Mediar.\nAcompanhar."} for codigo in QUATRO})
    titulos = [
        linha for linha in secao_de_perfis(conteudo) if linha[:4] in ("5.5 ", "5.6 ", "5.7 ")
    ]
    assert [titulo.split(" comuns")[0] for titulo in titulos] == [
        "5.5 Atribuições",
        "5.6 Requisitos",
        "5.7 Marcos classificatórios",
    ]
