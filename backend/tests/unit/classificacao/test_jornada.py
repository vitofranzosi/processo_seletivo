"""A jornada do Perfil: a sequência e o estado de cada ponto, derivados só da configuração (094).

O Perfil de referência é o do protótipo e do roteiro de compreensão: Prova Escrita, Prova de
Títulos, Análise documental (decisória) e Entrevista; um marco que corta para a Entrevista e uma
classificação final sobre as vagas, que não alimenta Etapa (FR-2247 a FR-2251, SC-852).
"""

from processo_seletivo.classificacao.domain.jornada import (
    CONTEXTO,
    INDETERMINADO,
    PARCIAL,
    SIMULADO,
    jornada,
)

ETAPAS = [
    {"id": "e1", "name": "Prova Escrita", "order": 1, "forma": "PONTUADA"},
    {"id": "e2", "name": "Prova de Títulos", "order": 2, "forma": "PONTUADA"},
    {"id": "e3", "name": "Análise documental", "order": 3, "forma": "DECISORIA"},
    {"id": "e4", "name": "Entrevista", "order": 4, "forma": "PONTUADA"},
]
PARA_A_ENTREVISTA = {
    "sub": "0",
    "name": "Classificação para a Entrevista",
    "stages": ["e1", "e2"],
    "cutRule": {"targetKind": "FIXED", "governedStage": "e4", "continuation": "ALLOWED"},
}
FINAL = {
    "sub": "1",
    "name": "Classificação final",
    "stages": ["e1", "e2", "e4"],
    "cutRule": {"targetKind": "FROM_VACANCY_TABLE", "governedStage": "NONE"},
}


def resumo(pontos):
    def nome(p):
        if p["tipo"] == "avaliacoes":
            return "+".join(e["name"] for e in p["etapas"])
        if p["tipo"] == "marco":
            return p["marco"]["name"]
        return p["etapa"]["name"]

    return [(p["tipo"], nome(p), p["estado"]) for p in pontos]


def test_a_jornada_pelo_primeiro_marco():
    assert resumo(jornada(ETAPAS, [PARA_A_ENTREVISTA, FINAL], "0")) == [
        ("avaliacoes", "Prova Escrita+Prova de Títulos", SIMULADO),
        ("marco", "Classificação para a Entrevista", SIMULADO),
        ("porta", "Análise documental", INDETERMINADO),
        ("etapa_alimentada", "Entrevista", PARCIAL),
        ("marco", "Classificação final", INDETERMINADO),
    ]


def test_a_jornada_pela_classificacao_final():
    assert resumo(jornada(ETAPAS, [PARA_A_ENTREVISTA, FINAL], "1")) == [
        ("avaliacoes", "Prova Escrita+Prova de Títulos", SIMULADO),
        ("marco", "Classificação para a Entrevista", CONTEXTO),
        ("porta", "Análise documental", CONTEXTO),
        ("etapa_alimentada", "Entrevista", CONTEXTO),
        ("marco", "Classificação final", SIMULADO),
    ]


def test_a_porta_entre_o_corte_e_a_etapa_faz_o_ate():
    entrevista = next(
        p
        for p in jornada(ETAPAS, [PARA_A_ENTREVISTA, FINAL], "0")
        if p["tipo"] == "etapa_alimentada"
    )
    assert [e["name"] for e in entrevista["portas_antes"]] == ["Análise documental"]


def test_o_marco_posterior_diz_quais_notas_faltam():
    final = jornada(ETAPAS, [PARA_A_ENTREVISTA, FINAL], "0")[-1]
    assert [e["name"] for e in final["nao_simuladas"]] == ["Entrevista"]
    assert final["terminal"]


def test_a_etapa_em_dois_marcos_aparece_uma_vez():
    pontos = jornada(ETAPAS, [PARA_A_ENTREVISTA, FINAL], "1")
    nomes = [
        e["name"]
        for p in pontos
        for e in (p.get("etapas") or ([p["etapa"]] if "etapa" in p else []))
    ]
    assert nomes.count("Prova Escrita") == 1


def test_toda_etapa_e_todo_marco_aparecem_na_ordem():
    pontos = jornada(ETAPAS, [PARA_A_ENTREVISTA, FINAL], "0")
    marcos = [p["marco"]["name"] for p in pontos if p["tipo"] == "marco"]
    etapas = [
        e["name"]
        for p in pontos
        for e in (p.get("etapas") or ([p["etapa"]] if "etapa" in p else []))
    ]
    assert marcos == ["Classificação para a Entrevista", "Classificação final"]
    assert etapas == [e["name"] for e in ETAPAS]


def test_marco_que_nao_corta_e_etapa_fora_de_marco():
    sem_corte = {"sub": "0", "name": "Ordem", "stages": ["e1"], "cutRule": None}
    pontos = jornada(ETAPAS[:2], [sem_corte], "0")
    assert resumo(pontos) == [
        ("avaliacoes", "Prova Escrita", SIMULADO),
        ("marco", "Ordem", SIMULADO),
        ("fora", "Prova de Títulos", CONTEXTO),
    ]
    assert not pontos[1]["corta"]


def test_marco_sem_etapa_entra_no_comeco():
    sorteio = {"sub": "1", "name": "Sorteio", "stages": [], "orderProduction": "POR_SORTEIO"}
    pontos = jornada(ETAPAS, [PARA_A_ENTREVISTA, sorteio], "0")
    assert pontos[0]["tipo"] == "marco"
    assert pontos[0]["por_sorteio"]


def test_marcos_que_se_cruzam_fora_da_ordem_ficam_na_ordem_das_etapas():
    """R-013: o caso fica preso como está, até haver um Edital assim para decidir o desenho."""
    cruzado = {
        "sub": "0",
        "name": "Cruzado",
        "stages": ["e4"],
        "cutRule": {"targetKind": "FIXED", "governedStage": "e2"},
    }
    pontos = jornada(ETAPAS, [cruzado], "0")
    assert [p["tipo"] for p in pontos] == [
        "fora",
        "etapa_alimentada",
        "porta",
        "avaliacoes",
        "marco",
    ]
