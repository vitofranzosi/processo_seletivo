"""As funções puras que transformam conteúdo publicado em rascunho (023).

Aqui mora o risco da feature, e ele é de uma natureza específica: **a cópia preserva a coerência
interna do que copia**. Um identificador da origem que escape do remapeamento continua consistente
com os seus vizinhos, atravessa a validação da gravação e só falha na publicação — ou nunca. Os
testes deste arquivo são a guarda que o domínio não oferece (T-005).
"""

from datetime import datetime
from decimal import Decimal

import pytest

from processo_seletivo.editais.domain.reaproveitamento import (
    ReferenciaNaoMapeada,
    converter_valores,
    mapa_de_identidades,
    payload_do_conteudo,
    remapear,
)

PERFIL = "00000000-0000-0000-0000-0000000000a1"
MODALIDADE = "00000000-0000-0000-0000-0000000000a2"
REGRA = "00000000-0000-0000-0000-0000000000a3"
FATO = "00000000-0000-0000-0000-0000000000a4"
MARCO = "00000000-0000-0000-0000-0000000000a5"
CRITERIO = "00000000-0000-0000-0000-0000000000a6"
EVENTO = "00000000-0000-0000-0000-0000000000a7"
ETAPA = "00000000-0000-0000-0000-0000000000a8"
DOCUMENTO = "00000000-0000-0000-0000-0000000000a9"
ANEXO = "00000000-0000-0000-0000-0000000000b1"

IDENTIDADES = (
    PERFIL,
    MODALIDADE,
    REGRA,
    FATO,
    MARCO,
    CRITERIO,
    EVENTO,
    ETAPA,
    DOCUMENTO,
    ANEXO,
)


def conteudo_publicado():
    """Uma origem que **usa** todas as referências, que é a única que prova algo."""
    return {
        "schemaVersion": 11,
        "number": "173",
        "year": 2025,
        "title": "Designer Educacional",
        "description": "Seleção anterior",
        "maxInscricoesPorCandidato": 1,
        "processoCode": "PS-2025-1",
        "processoTitle": "Processo de 2025",
        "profiles": [
            {
                "id": PERFIL,
                "code": "P1",
                "name": "Designer",
                "description": "",
                "requirements": ["Graduação"],
                "immediateVacancies": 40,
                "reserveType": "NONE",
                "reserveLimit": None,
                "locality": "Vitória",
                "duties": "",
                "workload": "",
                "compensation": "",
                "classificationInformation": {"texto": "não tem tela"},
                "callInformation": {"texto": "também não"},
                "competitionModalities": [
                    {
                        "id": MODALIDADE,
                        "code": "AC",
                        "name": "Ampla concorrência",
                        "description": "",
                        "normativeRule": {
                            "id": REGRA,
                            "foundation": "Lei 12.990/2014",
                            "version": "2014-06-09",
                            "percentage": "20.0000",
                            "calculation": "PERCENTUAL",
                            "rounding": "UP",
                            "distribution": {},
                            "callRules": {},
                            "effectiveFrom": "2026-01-01T00:00:00-03:00",
                        },
                    }
                ],
                "declaredFacts": [
                    {"id": FATO, "code": "NASCIMENTO", "label": "Nascimento", "type": "DATA"}
                ],
                "classificationMilestones": [
                    {
                        "id": MARCO,
                        "code": "M1",
                        "name": "Classificação final",
                        "stages": [ETAPA],
                        "operation": "SOMA",
                        "normalization": None,
                        "rounding": "HALF_UP",
                        "appealWindow": {"admits": True, "amount": 5, "unit": "DIAS_CORRIDOS"},
                        "drawMethod": {"source": "LOTERIA", "qualifyingStageId": ETAPA},
                        "tiebreakers": [
                            {
                                "id": CRITERIO,
                                "order": 1,
                                "type": "MAIOR_PONTUACAO_NA_ETAPA",
                                "parameters": {"stageId": ETAPA, "factId": FATO},
                                "whenMissing": "IGNORA",
                            }
                        ],
                    }
                ],
            }
        ],
        "schedule": [
            {
                "id": EVENTO,
                "type": "INSCRICAO",
                "description": "Inscrições",
                "startAt": "2025-09-01T09:00:00-03:00",
                "endAt": "2025-09-10T23:59:00-03:00",
                "order": 1,
                "status": "CONCLUIDO",
                "isRegistrationPeriod": True,
                "location": "Campus Vitória",
            }
        ],
        "stages": [
            {
                "id": ETAPA,
                "name": "Prova de títulos",
                "order": 1,
                "weight": "1.5000",
                "eliminatory": False,
                "classificatory": True,
                "minimumScore": "10.0000",
                "evaluationsPerRegistration": 2,
                "maximumScore": "100.0000",
                "forma": "PONTUADA",
                "rotuloFavoravel": None,
                "rotuloDesfavoravel": None,
                "scheduleEventId": EVENTO,
            }
        ],
        "documentRequirements": [
            {
                "id": DOCUMENTO,
                "key": "identidade",
                "name": "Documento de identificação",
                "instructions": "frente e verso",
                "required": True,
                "order": 1,
                "profileId": PERFIL,
                "modalityId": MODALIDADE,
                "attachmentId": ANEXO,
            }
        ],
        "sections": [
            {
                "id": "ignorada",
                "key": "apresentacao",
                "title": "Apresentação",
                "order": 1,
                "type": "TEXT",
                "content": "Texto redigido",
            },
            {
                "id": "ignorada",
                "key": "anexos",
                "title": "Anexos",
                "order": 11,
                "type": "GENERATED",
                "source": "attachments",
            },
        ],
        "attachments": [
            {
                "id": ANEXO,
                "label": "ANEXO I",
                "order": 1,
                "artifactId": "qualquer",
                "artifactHash": "abc",
            }
        ],
    }


def test_o_mapa_cobre_as_dez_posicoes_de_identidade():
    mapa = mapa_de_identidades(conteudo_publicado())

    assert sorted(mapa) == sorted(IDENTIDADES)
    assert all(valor not in IDENTIDADES for valor in mapa.values())


def test_duas_copias_do_mesmo_conteudo_produzem_identidades_distintas():
    primeira = mapa_de_identidades(conteudo_publicado())
    segunda = mapa_de_identidades(conteudo_publicado())

    assert set(primeira.values()).isdisjoint(segunda.values())


def test_o_remapeamento_alcanca_as_oito_posicoes_de_referencia():
    conteudo = conteudo_publicado()
    mapa = mapa_de_identidades(conteudo)

    copia = remapear(conteudo, mapa)

    perfil = copia["profiles"][0]
    marco = perfil["classificationMilestones"][0]
    documento = copia["documentRequirements"][0]
    assert copia["stages"][0]["scheduleEventId"] == mapa[EVENTO]
    assert documento["profileId"] == mapa[PERFIL]
    assert documento["modalityId"] == mapa[MODALIDADE]
    assert documento["attachmentId"] == mapa[ANEXO]
    assert marco["stages"] == [mapa[ETAPA]]
    assert marco["tiebreakers"][0]["parameters"]["stageId"] == mapa[ETAPA]
    assert marco["tiebreakers"][0]["parameters"]["factId"] == mapa[FATO]
    assert marco["drawMethod"]["qualifyingStageId"] == mapa[ETAPA]


def test_nenhuma_identidade_da_origem_sobrevive_em_posicao_alguma():
    """A asserção negativa, e é ela que pega a posição esquecida."""
    conteudo = conteudo_publicado()
    mapa = mapa_de_identidades(conteudo)

    copia = remapear(conteudo, mapa)

    import json

    serializada = json.dumps(copia)
    for identidade in IDENTIDADES:
        assert identidade not in serializada


def test_referencia_fora_do_mapa_falha_alto():
    """Falhar alto é o requisito: identificador não mapeado é defeito determinável (FR-010a)."""
    conteudo = conteudo_publicado()
    mapa = mapa_de_identidades(conteudo)
    del mapa[ETAPA]

    with pytest.raises(ReferenciaNaoMapeada) as recusa:
        remapear(conteudo, mapa)

    assert ETAPA in str(recusa.value)


def test_a_secao_nao_entra_no_mapa_porque_a_identidade_dela_e_derivada():
    mapa = mapa_de_identidades(conteudo_publicado())

    assert "ignorada" not in mapa


def test_os_instantes_voltam_a_ser_instantes():
    convertido = converter_valores(conteudo_publicado())

    evento = convertido["schedule"][0]
    regra = convertido["profiles"][0]["competitionModalities"][0]["normativeRule"]
    assert isinstance(evento["startAt"], datetime) and evento["startAt"].tzinfo is not None
    assert isinstance(evento["endAt"], datetime)
    assert isinstance(regra["effectiveFrom"], datetime)


def test_os_decimais_da_etapa_voltam_a_ser_decimais():
    """Descoberto na implementação: `validate_stage` compara `peso <= 0`, e `str` estoura ali."""
    etapa = converter_valores(conteudo_publicado())["stages"][0]

    assert etapa["weight"] == Decimal("1.5")
    assert etapa["minimumScore"] == Decimal("10")
    assert etapa["maximumScore"] == Decimal("100")


def test_sem_a_conversao_a_validacao_estoura_em_vez_de_recusar():
    """A contraprova: não é recusa bem formada, é `TypeError` — daí a conversão ser condição."""
    from processo_seletivo.editais.domain.cronograma import validate_schedule
    from processo_seletivo.editais.domain.etapas import validate_stages

    conteudo = conteudo_publicado()
    with pytest.raises(AttributeError):
        validate_schedule(conteudo["schedule"])
    with pytest.raises(TypeError):
        validate_stages(conteudo["stages"], schedule=conteudo["schedule"])


def test_o_payload_traz_as_cinco_colecoes_e_nada_mais():
    payload = payload_do_conteudo(conteudo_publicado())

    assert sorted(payload) == [
        "documentRequirements",
        "profiles",
        "schedule",
        "sections",
        "stages",
    ]


def test_os_campos_sem_tela_nao_viajam():
    perfil = payload_do_conteudo(conteudo_publicado())["profiles"][0]

    assert "classificationInformation" not in perfil
    assert "callInformation" not in perfil


def test_a_identificacao_do_edital_nao_viaja():
    payload = payload_do_conteudo(conteudo_publicado())

    assert not {"number", "year", "title", "description", "maxInscricoesPorCandidato"} & set(
        payload
    )


def test_o_evento_copiado_nasce_planejado_e_preserva_a_designacao_do_periodo():
    evento = payload_do_conteudo(conteudo_publicado())["schedule"][0]

    assert evento["status"] == "PLANEJADO"
    assert evento["isRegistrationPeriod"] is True


def test_so_as_secoes_textuais_passam():
    secoes = payload_do_conteudo(conteudo_publicado())["sections"]

    assert [secao["key"] for secao in secoes] == ["apresentacao"]
    assert secoes[0]["content"] == "Texto redigido"
