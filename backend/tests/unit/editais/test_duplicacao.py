"""A transformação que cria um Perfil a partir de outro do mesmo Edital (043).

O risco é o da `023`, num lugar novo: **a cópia preserva a coerência interna do que copia**. Uma
referência da cópia que continue apontando a origem é consistente com os vizinhos, atravessa a
gravação e só falha na publicação — ou nunca, se a origem continuar existindo, que é exatamente o
caso aqui: origem e cópia moram no mesmo Edital. Os testes deste arquivo são a guarda.

A fixture tem a forma de `forms.ler_perfis` — é o que a tela entrega à duplicação (`FR-636`).
"""

import copy
import json
import uuid

import pytest

from processo_seletivo.editais.domain.duplicacao import duplicar_perfil
from processo_seletivo.editais.domain.perfis import identidade_da_linha_geral
from processo_seletivo.editais.domain.reaproveitamento import ReferenciaNaoMapeada

PERFIL = "00000000-0000-4000-8000-000000043001"
AC = "00000000-0000-4000-8000-000000043011"
PPI = "00000000-0000-4000-8000-000000043012"
PCD = "00000000-0000-4000-8000-000000043013"
QUI = "00000000-0000-4000-8000-000000043014"
REGRA_PPI = "00000000-0000-4000-8000-000000043021"
REGRA_PCD = "00000000-0000-4000-8000-000000043022"
REGRA_QUI = "00000000-0000-4000-8000-000000043023"
LINHA_GERAL = "00000000-0000-4000-8000-000000043031"
LINHA_PPI = "00000000-0000-4000-8000-000000043032"
LINHA_PCD = "00000000-0000-4000-8000-000000043033"
LINHA_QUI = "00000000-0000-4000-8000-000000043034"
FATO_EXPERIENCIA = "00000000-0000-4000-8000-000000043041"
FATO_NASCIMENTO = "00000000-0000-4000-8000-000000043042"
MARCO = "00000000-0000-4000-8000-000000043051"
CRITERIO_ETAPA = "00000000-0000-4000-8000-000000043061"
CRITERIO_FATO = "00000000-0000-4000-8000-000000043062"

# As Etapas são **do Edital**, e não do Perfil: a cópia é do mesmo Edital e as cita iguais.
ETAPA_TITULOS = "00000000-0000-4000-8000-000000043071"
ETAPA_DOCUMENTAL = "00000000-0000-4000-8000-000000043072"
ETAPAS_DO_EDITAL = (ETAPA_TITULOS, ETAPA_DOCUMENTAL)

INTERNAS = (
    PERFIL,
    AC,
    PPI,
    PCD,
    QUI,
    REGRA_PPI,
    REGRA_PCD,
    REGRA_QUI,
    LINHA_GERAL,
    LINHA_PPI,
    LINHA_PCD,
    LINHA_QUI,
    FATO_EXPERIENCIA,
    FATO_NASCIMENTO,
    MARCO,
    CRITERIO_ETAPA,
    CRITERIO_FATO,
)


def _regra(identidade, percentual):
    return {
        "id": identidade,
        "foundation": "Lei 12.711/2012",
        "version": "2023-11-13",
        "percentage": percentual,
    }


def perfil_de_origem():
    """O LP01 do 140/2025, na forma que a tela entrega: tudo o que se copia, **usado**."""
    return {
        "id": PERFIL,
        "code": "LP01",
        "name": "Tutor a distância — Letras",
        "description": "Tutoria do curso de Letras",
        "requirements": ["Licenciatura em Letras", "Experiência em EaD"],
        "immediateVacancies": 0,
        "generalCompetitionModalityId": AC,
        "vacancyReversion": {"kind": "AMPLA_CONCORRENCIA"},
        "callForm": "PUBLICATION",
        "reserveType": "UNLIMITED",
        "reserveLimit": None,
        "locality": "Vitória",
        "duties": "Acompanhar os estudantes",
        "workload": "20 horas semanais",
        "compensation": "R$ 1.100,00",
        "competitionModalities": [
            {"id": AC, "code": "AC", "name": "Ampla concorrência", "description": ""},
            {
                "id": PPI,
                "code": "PPI",
                "name": "Pretos e pardos",
                "description": "",
                "normativeRule": _regra(REGRA_PPI, "25"),
            },
            {
                "id": PCD,
                "code": "PCD",
                "name": "Pessoa com deficiência",
                "description": "",
                "normativeRule": _regra(REGRA_PCD, "5"),
            },
            {
                "id": QUI,
                "code": "QUI",
                "name": "Quilombolas",
                "description": "",
                "normativeRule": _regra(REGRA_QUI, "1"),
            },
        ],
        "declaredFacts": [
            {"id": FATO_EXPERIENCIA, "code": "EXP", "label": "Meses em EaD", "type": "INTEIRO"},
            {"id": FATO_NASCIMENTO, "code": "NASC", "label": "Nascimento", "type": "DATA"},
        ],
        "classificationMilestones": [
            {
                "id": MARCO,
                "code": "LP01",
                "name": "Classificação final — Tutor a distância — Letras",
                "orderProduction": "PELA_PONTUACAO",
                "stages": [ETAPA_TITULOS],
                "operation": "SOMA_PONDERADA",
                "normalization": "NENHUMA",
                "rounding": {"scale": 2, "mode": "MEIO_PARA_CIMA"},
                "appealWindow": {"admits": True, "durationDays": 2, "unit": "DIAS_CORRIDOS"},
                "drawMethod": {"source": "LOTERIA", "qualifyingStageId": ETAPA_TITULOS},
                "cutRule": {
                    "targetKind": "FIXED",
                    "targetCount": 3,
                    "surplusCount": 0,
                    "tieOutcome": "STRICT",
                    "governedStage": ETAPA_DOCUMENTAL,
                    "continuation": "NONE",
                },
                "tiebreakers": [
                    {
                        "id": CRITERIO_ETAPA,
                        "order": 1,
                        "type": "MAIOR_PONTUACAO_NA_ETAPA",
                        "parameters": {"stageId": ETAPA_TITULOS},
                        "whenMissing": "IGNORA",
                    },
                    {
                        "id": CRITERIO_FATO,
                        "order": 2,
                        "type": "MAIOR_VALOR_DO_FATO",
                        "parameters": {"factId": FATO_EXPERIENCIA},
                        "whenMissing": "IGNORA",
                    },
                ],
            }
        ],
        "vacancyTable": [
            {"id": LINHA_GERAL, "modalityId": None, "immediateVacancies": 10},
            {"id": LINHA_PPI, "modalityId": PPI, "immediateVacancies": 3},
            {"id": LINHA_PCD, "modalityId": PCD, "immediateVacancies": 1},
            {"id": LINHA_QUI, "modalityId": QUI, "immediateVacancies": 1},
        ],
        # Os dois campos que nenhuma etapa desenha, e que por isso a cópia não leva (FR-643).
        "classificationInformation": {"texto": "sem tela"},
        "callInformation": {"texto": "também sem tela"},
    }


def duplicar(origem=None, **argumentos):
    padrao = {"codigo": "LP02", "localidade": "Serra", "etapas_do_edital": ETAPAS_DO_EDITAL}
    return duplicar_perfil(origem or perfil_de_origem(), **{**padrao, **argumentos})


def _modalidade(perfil, codigo):
    return next(item for item in perfil["competitionModalities"] if item["code"] == codigo)


def _fato(perfil, codigo):
    return next(item for item in perfil["declaredFacts"] if item["code"] == codigo)


# --- FR-640: identidades novas ------------------------------------------------------------------


def _identidades(perfil):
    """Toda identidade que a cópia **possui**, posição a posição."""
    marcos = perfil["classificationMilestones"]
    return [
        perfil["id"],
        *(item["id"] for item in perfil["competitionModalities"]),
        *(
            item["normativeRule"]["id"]
            for item in perfil["competitionModalities"]
            if item.get("normativeRule")
        ),
        *(item["id"] for item in perfil["declaredFacts"]),
        *(item["id"] for item in perfil["vacancyTable"]),
        *(item["id"] for item in marcos),
        *(criterio["id"] for marco in marcos for criterio in marco["tiebreakers"]),
    ]


def test_tudo_o_que_a_copia_possui_tem_identidade_nova_e_distinta():
    copia = duplicar()

    identidades = _identidades(copia)
    assert len(identidades) == len(INTERNAS)
    assert len(set(identidades)) == len(identidades)
    assert set(identidades).isdisjoint(INTERNAS)
    assert all(identidade for identidade in identidades)


def test_a_linha_geral_tem_a_identidade_derivada_do_perfil_novo():
    """A mesma regra que a deriva para qualquer Perfil (027) — e é ela que torna a gravação
    idempotente. Uma identidade sorteada daria à linha geral duas identidades em duas gravações."""
    copia = duplicar()

    geral = next(linha for linha in copia["vacancyTable"] if linha["modalityId"] is None)
    assert geral["id"] == str(identidade_da_linha_geral(copia["id"]))


def test_duas_copias_da_mesma_origem_nao_partilham_identidade():
    primeira = duplicar(codigo="LP02")
    segunda = duplicar(codigo="LP03")

    assert set(_identidades(primeira)).isdisjoint(_identidades(segunda))


def test_nenhuma_identidade_interna_da_origem_sobrevive_em_posicao_alguma():
    """A asserção negativa, e é ela que pega a posição esquecida (023, T-005)."""
    serializada = json.dumps(duplicar())

    for identidade in INTERNAS:
        assert identidade not in serializada


# --- FR-641: referências para dentro ------------------------------------------------------------


def test_a_ampla_concorrencia_declarada_aponta_a_modalidade_da_copia():
    copia = duplicar()

    assert copia["generalCompetitionModalityId"] == _modalidade(copia, "AC")["id"]


def test_cada_linha_reservada_aponta_a_modalidade_da_copia_de_mesmo_codigo():
    origem = perfil_de_origem()
    copia = duplicar(origem)

    for na_origem, na_copia in zip(origem["vacancyTable"], copia["vacancyTable"], strict=True):
        if na_origem["modalityId"] is None:
            assert na_copia["modalityId"] is None
            continue
        assert _codigo_da_modalidade(copia, na_copia["modalityId"]) == _codigo_da_modalidade(
            origem, na_origem["modalityId"]
        )
        assert na_copia["immediateVacancies"] == na_origem["immediateVacancies"]


def _codigo_da_modalidade(perfil, identidade):
    modalidades = perfil["competitionModalities"]
    return next(item["code"] for item in modalidades if item["id"] == identidade)


def test_o_criterio_que_compara_fato_cita_o_fato_da_copia():
    copia = duplicar()

    criterio = copia["classificationMilestones"][0]["tiebreakers"][1]
    assert criterio["parameters"]["factId"] == _fato(copia, "EXP")["id"]


def test_perfil_sem_ampla_declarada_continua_sem_declarar():
    origem = perfil_de_origem()
    origem["generalCompetitionModalityId"] = None

    assert duplicar(origem)["generalCompetitionModalityId"] is None


# --- FR-642: referências para fora --------------------------------------------------------------


def test_as_etapas_do_edital_continuam_as_mesmas():
    marco = duplicar()["classificationMilestones"][0]

    assert marco["stages"] == [ETAPA_TITULOS]
    assert marco["drawMethod"]["qualifyingStageId"] == ETAPA_TITULOS
    assert marco["tiebreakers"][0]["parameters"]["stageId"] == ETAPA_TITULOS
    # `remapear` troca a Etapa governada (#169), e a do Edital mapeia para si mesma.
    assert marco["cutRule"]["governedStage"] == ETAPA_DOCUMENTAL


def test_etapa_governada_que_nao_e_do_edital_estoura():
    origem = perfil_de_origem()
    alheia = "00000000-0000-4000-8000-0000000430fe"
    origem["classificationMilestones"][0]["cutRule"]["governedStage"] = alheia

    with pytest.raises(ReferenciaNaoMapeada):
        duplicar(origem)


def test_corte_que_nao_governa_etapa_atravessa_intocado():
    origem = perfil_de_origem()
    origem["classificationMilestones"][0]["cutRule"]["governedStage"] = "NONE"

    assert duplicar(origem)["classificationMilestones"][0]["cutRule"]["governedStage"] == "NONE"


def test_etapa_que_nao_e_do_edital_estoura_em_vez_de_atravessar():
    """O mapa estende a identidade **às Etapas do Edital**, e não a qualquer Etapa citada: uma
    referência a Etapa de outro Edital continua sem mapa, e continua falhando alto (R-001)."""
    origem = perfil_de_origem()
    alheia = "00000000-0000-4000-8000-0000000430ff"
    origem["classificationMilestones"][0]["stages"] = [alheia]

    with pytest.raises(ReferenciaNaoMapeada) as recusa:
        duplicar(origem)

    assert alheia in str(recusa.value)


# --- FR-641: referência interna sem contraparte -------------------------------------------------


def test_criterio_que_cita_fato_que_o_perfil_nao_declara_estoura():
    origem = perfil_de_origem()
    origem["declaredFacts"] = [_fato(origem, "NASC")]

    with pytest.raises(ReferenciaNaoMapeada):
        duplicar(origem)


def test_linha_que_aponta_modalidade_de_outro_perfil_estoura():
    origem = perfil_de_origem()
    origem["vacancyTable"][1]["modalityId"] = "00000000-0000-4000-8000-0000000430ee"

    with pytest.raises(ReferenciaNaoMapeada):
        duplicar(origem)


# --- FR-635, FR-643, SC-233: o que muda e o que não muda -----------------------------------------


def test_codigo_e_localidade_sao_os_informados():
    copia = duplicar(codigo="LP07", localidade="Cariacica")

    assert copia["code"] == "LP07"
    assert copia["locality"] == "Cariacica"


def test_localidade_vazia_e_vazia_na_copia_e_nunca_a_da_origem():
    assert duplicar(localidade="")["locality"] == ""


def test_os_campos_sem_tela_nao_sao_copiados():
    copia = duplicar()

    assert "classificationInformation" not in copia
    assert "callInformation" not in copia


def _sem_identidades(valor, identidades):
    """O conteúdo com cada identidade trocada por um marcador — para comparar só o resto."""
    texto = json.dumps(valor, sort_keys=True)
    for identidade in identidades:
        texto = texto.replace(identidade, "<id>")
    return json.loads(texto)


def test_fora_identidades_codigo_localidade_e_marco_derivado_tudo_e_igual():
    """`SC-233`, no nível da transformação: a cópia difere da origem **só** no que a spec diz."""
    origem = perfil_de_origem()
    copia = duplicar(origem)

    esperado = {
        chave: valor
        for chave, valor in origem.items()
        if chave not in ("classificationInformation", "callInformation")
    }
    esperado = {**esperado, "code": "LP02", "locality": "Serra"}
    esperado["classificationMilestones"] = [
        {**esperado["classificationMilestones"][0], "code": "LP02"}
    ]
    assert _sem_identidades(copia, _identidades(copia)) == _sem_identidades(esperado, INTERNAS)


# --- FR-644: identidade do marco -----------------------------------------------------------------


def _com_marcos(*pares):
    origem = perfil_de_origem()
    modelo = origem["classificationMilestones"][0]
    origem["classificationMilestones"] = [
        {**copy.deepcopy(modelo), "id": str(uuid.uuid4()), "code": codigo, "name": nome}
        for codigo, nome in pares
    ]
    # Sem critério que cite fato: cada marco teria a mesma identidade de critério.
    for marco in origem["classificationMilestones"]:
        marco["tiebreakers"] = []
    return origem


DERIVADO = "Classificação final — Tutor a distância — Letras"


def test_marco_derivado_da_origem_e_derivado_de_novo_da_copia():
    copia = duplicar(_com_marcos(("LP01", DERIVADO), ("LP01-2", DERIVADO)))

    assert [marco["code"] for marco in copia["classificationMilestones"]] == ["LP02", "LP02-2"]
    assert {marco["name"] for marco in copia["classificationMilestones"]} == {DERIVADO}


def test_marco_escrito_a_mao_e_copiado_como_esta():
    copia = duplicar(_com_marcos(("SORT", "Sorteio público")))

    marco = copia["classificationMilestones"][0]
    assert (marco["code"], marco["name"]) == ("SORT", "Sorteio público")


def test_codigo_com_sufixo_que_o_desempate_nao_produz_e_escrito_a_mao():
    """`LP01-2025` começa pelo Código do Perfil, mas nenhum desempate o produziria: é decisão de
    quem compõe, e a cópia o leva como está (FR-421)."""
    copia = duplicar(_com_marcos(("LP01-2025", "Classificação de 2025")))

    assert copia["classificationMilestones"][0]["code"] == "LP01-2025"


def test_codigo_derivado_nao_colide_com_o_escrito_a_mao_da_propria_copia():
    copia = duplicar(_com_marcos(("LP01", DERIVADO), ("LP02", "Escrito à mão")))

    assert sorted(marco["code"] for marco in copia["classificationMilestones"]) == [
        "LP02",
        "LP02-2",
    ]


def test_codigo_da_origem_mudado_na_tela_nao_torna_o_marco_gravado_escrito_a_mao():
    """Quem muda o Código do LP01 na tela sem gravar não pode fazer o marco `LP01`, derivado do
    Código **gravado**, parecer escrito à mão (R-005)."""
    origem = _com_marcos(("LP01", DERIVADO))
    origem["code"] = "LP1"

    copia = duplicar(origem, codigo_gravado="LP01")

    assert copia["classificationMilestones"][0]["code"] == "LP02"


def test_denominacao_derivada_segue_a_denominacao_da_copia():
    origem = _com_marcos(("LP01", "Classificação final — Tutor"))
    origem["name"] = "Tutor a distância — Letras"

    copia = duplicar(origem, nome_gravado="Tutor")

    assert copia["classificationMilestones"][0]["name"] == DERIVADO


# --- R-002 e FR-646 -------------------------------------------------------------------------------


def test_regras_sem_identidade_saem_com_identidades_distintas():
    """`ler_perfis` devolve `""` para campo ausente, e o mapa registra por valor: sem a guarda,
    duas Regras vazias virariam **uma** Regra partilhada por duas Modalidades (R-002)."""
    origem = perfil_de_origem()
    for modalidade in origem["competitionModalities"]:
        if modalidade.get("normativeRule"):
            modalidade["normativeRule"]["id"] = ""

    copia = duplicar(origem)

    regras = [
        modalidade["normativeRule"]["id"]
        for modalidade in copia["competitionModalities"]
        if modalidade.get("normativeRule")
    ]
    assert len(regras) == 3
    assert all(regras)
    assert len(set(regras)) == 3


def test_a_origem_nao_muda():
    origem = perfil_de_origem()
    antes = copy.deepcopy(origem)

    duplicar(origem)

    assert origem == antes


def test_perfil_sem_modalidade_sem_marco_e_sem_fato_duplica_so_com_a_linha_geral():
    """Caso-limite da spec: a cópia não tem o que a origem não tinha."""
    origem = {
        "id": PERFIL,
        "code": "LP01",
        "name": "Tutor",
        "immediateVacancies": 2,
        "competitionModalities": [],
        "declaredFacts": [],
        "classificationMilestones": [],
        "vacancyTable": [{"id": LINHA_GERAL, "modalityId": None, "immediateVacancies": 2}],
    }

    copia = duplicar(origem)

    assert copia["competitionModalities"] == copia["declaredFacts"] == []
    assert copia["classificationMilestones"] == []
    assert copia["vacancyTable"] == [
        {
            "id": str(identidade_da_linha_geral(copia["id"])),
            "modalityId": None,
            "immediateVacancies": 2,
        }
    ]
