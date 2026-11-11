"""Edital publicado antes do degrau 21 continua vivo — e a ausência do barema é a lista vazia (146).

Todo Edital publicado antes deste degrau somava a ficha fora do sistema: a Etapa não publicava
critério nenhum. A lista vazia é a verdade sobre o acervo, e não um padrão escolhido — conversão sem
invenção, no molde do degrau 7, que trouxe as coleções do Perfil (D-001, FR-5208).
"""

import pytest

from processo_seletivo.editais.domain.mutabilidade import CONTRATO, Natureza
from processo_seletivo.editais.domain.validation import blocking_findings, validate_for_publication
from processo_seletivo.publicacoes.domain import colecoes
from processo_seletivo.publicacoes.domain.changes import apply_changes
from processo_seletivo.publicacoes.domain.elevacao import (
    DEGRAUS,
    diz_o_mesmo_que_a_ausencia,
    elevar,
    elevar_etapa,
    elevar_valor,
)
from processo_seletivo.shared.canonical import SCHEMA_VERSION

pytestmark = [pytest.mark.contract]

ETAPA = "66666666-6666-6666-6666-666666666666"
CRITERIO = "77777777-7777-7777-7777-777777777777"


def conteudo_na_versao(versao):
    return {
        "schemaVersion": versao,
        "profiles": [],
        "schedule": [],
        "attachments": [],
        "documentRequirements": [],
        "maxInscricoesPorCandidato": None,
        "stages": [
            {
                "id": ETAPA,
                "name": "Prova de Títulos",
                "order": 1,
                "weight": None,
                "eliminatory": False,
                "classificatory": True,
                "minimumScore": None,
                "evaluationsPerRegistration": 1,
                "maximumScore": "100.0000",
                "forma": "PONTUADA",
                "rotuloFavoravel": None,
                "rotuloDesfavoravel": None,
                "scheduleEventId": None,
            }
        ],
    }


def criterio(**campos):
    return {
        "id": CRITERIO,
        "name": "Diploma de Doutorado",
        "description": "",
        "maximumScore": "20.0000",
        "pointsPerUnit": "20.0000",
        "unitLabel": "diploma",
        "documentRequirementId": None,
        **campos,
    }


def test_o_degrau_21_existe_no_nivel_da_etapa_e_grafa_a_ausencia_como_lista_vazia():
    assert DEGRAUS[21] == {"criteria": []}
    assert SCHEMA_VERSION >= 21


def test_o_edital_anterior_eleva_com_toda_etapa_sem_barema():
    elevado = elevar(conteudo_na_versao(20))

    etapa = elevado["stages"][0]
    assert elevado["schemaVersion"] == SCHEMA_VERSION
    assert etapa["criteria"] == []
    assert etapa["maximumScore"] == "100.0000", "nada mais da Etapa é tocado"


def test_o_edital_de_antes_da_forma_recebe_os_degraus_da_etapa_em_cadeia():
    """Do 5 ao 21: a forma pontuada e o barema vazio, cada um pelo seu degrau."""
    anterior = conteudo_na_versao(5)
    for chave in ("forma", "rotuloFavoravel", "rotuloDesfavoravel"):
        del anterior["stages"][0][chave]

    etapa = elevar(anterior)["stages"][0]

    assert etapa["forma"] == "PONTUADA"
    assert etapa["criteria"] == []


def test_cada_etapa_recebe_a_propria_lista():
    """A `[]` do degrau não é compartilhada: acrescentar a uma não acrescenta às outras."""
    conteudo = conteudo_na_versao(20)
    conteudo["stages"].append({**conteudo["stages"][0], "id": CRITERIO, "order": 2})

    elevado = elevar(conteudo)
    elevado["stages"][0]["criteria"].append(criterio())

    assert elevado["stages"][1]["criteria"] == []
    assert DEGRAUS[21] == {"criteria": []}


def test_a_etapa_com_barema_nao_e_reescrita():
    etapa = elevar_etapa({"id": ETAPA, "criteria": [criterio()]}, de=20)

    assert etapa["criteria"] == [criterio()]


def test_a_elevacao_e_idempotente():
    ja_elevado = elevar(conteudo_na_versao(20))

    assert elevar(ja_elevado) is ja_elevado


def test_a_etapa_acrescentada_por_ato_antigo_chega_sem_barema():
    """O `newValue` de um ato anterior ao degrau, que acrescentou a Etapa inteira, é elevado."""
    valor = {**conteudo_na_versao(20)["stages"][0]}

    assert elevar_valor("/stages/-", valor)["criteria"] == []


def test_lista_vazia_e_ausencia_dizem_o_mesmo():
    base = {"evaluationsPerRegistration": 1, "forma": "PONTUADA"}

    assert diz_o_mesmo_que_a_ausencia(base) is True
    assert diz_o_mesmo_que_a_ausencia({**base, "criteria": []}) is True
    assert diz_o_mesmo_que_a_ausencia({**base, "criteria": [criterio()]}) is False


def test_o_conteudo_elevado_passa_pela_forma_publicada():
    """O acervo elevado não ganha recusa nova: a lista vazia é a forma que a 146 declara."""
    elevado = elevar(conteudo_na_versao(20))
    achados = [
        achado
        for achado in blocking_findings(validate_for_publication(elevado))
        if "/criteria" in achado.path
    ]

    assert achados == []


def test_o_barema_e_colecao_com_chave():
    """FR-5210: endereçado por identidade, e não por posição, desde o primeiro Edital com barema."""
    assert colecoes.tem_chave("/stages/*/criteria")
    assert colecoes.FORMA_DA_COLECAO["criteria"] == "/stages/*/criteria/*"


@pytest.mark.parametrize(
    "campo",
    ["name", "description", "maximumScore", "pointsPerUnit", "unitLabel", "documentRequirementId"],
)
def test_todo_campo_do_criterio_e_retificavel(campo):
    assert CONTRATO[("criteria", campo)].natureza is Natureza.RETIFICAVEL
    assert CONTRATO[("criteria", "id")].natureza is Natureza.ESTRUTURAL


def test_acrescentar_criterio_ao_acervo_elevado_pela_gramatica_que_ja_existe():
    """Edital anterior ao degrau ganha barema por Retificação, com o critério e a máxima juntos."""
    conteudo = elevar(conteudo_na_versao(20))
    conteudo["stages"][0]["maximumScore"] = "100.0000"

    resultado, _registro = apply_changes(
        conteudo,
        [
            {
                "targetPath": f"/stages/id={ETAPA}/criteria/-",
                "operation": "ADD",
                "newValue": criterio(maximumScore="100.0000", pointsPerUnit="25.0000"),
            },
            {
                "targetPath": f"/stages/id={ETAPA}/criteria/id={CRITERIO}/unitLabel",
                "operation": "REPLACE",
                "newValue": "título",
            },
        ],
        publication_id="88888888-8888-8888-8888-888888888888",
    )

    barema = resultado["stages"][0]["criteria"]
    assert [c["id"] for c in barema] == [CRITERIO]
    assert barema[0]["unitLabel"] == "título"
