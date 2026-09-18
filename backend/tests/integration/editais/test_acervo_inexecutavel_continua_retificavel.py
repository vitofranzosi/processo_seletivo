"""O Edital do acervo que não funciona continua retificável (032, FR-460, SC-161).

**Este arquivo é o irmão de `test_acervo_sem_quadro_continua_retificavel.py`, e existe pela mesma
armadilha.** `retificacoes.py` afere o conteúdo que o ato produziria com
`blocking_findings(validate_for_publication(content))`. Uma regra da família de executabilidade
escrita **sem** o recorte por ato bloquearia toda Retificação de todo Edital do acervo que tenha
qualquer uma das três ausências — inclusive as Retificações que corrigem uma data e nada têm com
classificação. O defeito não apareceria em teste de composição nenhum: apareceria no dia em que
alguém tentasse corrigir um Edital antigo.

**E o que se perderia é justamente o que a feature existe para salvar.** O Edital publicado sem
marco, sem método de sorteio ou com reserva que ninguém apura **existe** — é o que a auditoria de
16/09/2026 publicou, e é a razão de a `032` ter sido escrita. Tornar irretificável exatamente esse
Edital trocaria um problema por outro pior: a Retificação é a única saída que ele tem.

O acervo é simulado como ele realmente é — `Publicacao` inserida com o conteúdo que teria sido
publicado —, e não por `UPDATE` sobre linha publicada: publicação é append-only por trigger desde a
`002`.

**E a publicação passa por `publicar_sem_aferir`, e não por `publicar_na_versao_anterior`.** Aquela
submete pela API, e a submissão afere publicabilidade — ela recusa o marco que não declara a forma
da ordem, e recusa os três estados que este arquivo precisa ter publicados. Uma fixture que
atravesse a aferição não consegue, por construção, produzir o Edital que a aferição rejeita; e é
exatamente esse Edital que existe no acervo e precisa continuar retificável. O rascunho é gravado
como a composição de então o gravava — completo —, e os marcos são devolvidos ao estado do acervo
**antes** do congelamento do snapshot, que é o mesmo recurso que `test_forma_da_ordem.py` usa.
"""

import pytest

from processo_seletivo.editais.domain.validation import (
    ATO_DE_RETIFICACAO,
    blocking_findings,
    validate_for_publication,
)
from processo_seletivo.editais.models.perfis import MarcoClassificatorio
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.legado import publicar_sem_aferir
from tests.fixtures.publicacao import retify

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

SEM_MARCO = "aaaaaaaa-0000-4000-8000-0000000032c1"
COM_RESERVA = "aaaaaaaa-0000-4000-8000-0000000032c2"
QUE_SORTEIA = "aaaaaaaa-0000-4000-8000-0000000032c3"
MARCO_COMPUTADO = "aaaaaaaa-0000-4000-8000-0000000032d1"
MARCO_DE_SORTEIO = "aaaaaaaa-0000-4000-8000-0000000032d2"
PCD = "aaaaaaaa-0000-4000-8000-0000000032e1"
NEGROS = "aaaaaaaa-0000-4000-8000-0000000032e2"
LINHA_GERAL = "aaaaaaaa-0000-4000-8000-0000000032f1"
LINHA_PCD = "aaaaaaaa-0000-4000-8000-0000000032f2"
LINHA_NEGROS = "aaaaaaaa-0000-4000-8000-0000000032f3"
LINHA_DO_SORTEIO = "aaaaaaaa-0000-4000-8000-0000000032f4"
LINHA_SEM_MARCO = "aaaaaaaa-0000-4000-8000-0000000032f5"
EVENTO = "aaaaaaaa-0000-4000-8000-0000000032f6"
ETAPA = "aaaaaaaa-0000-4000-8000-0000000032f7"
MARCO_A_REMOVER = "aaaaaaaa-0000-4000-8000-0000000032d3"

#: A versão canônica imediatamente anterior ao Requerimento de Matrícula. Rebaixar até ela mantém
#: marcos e quadro de vagas — que é o que estes cenários precisam ter — e não é o ponto do teste;
#: o ponto é a `Publicacao` inserida sem passar pela aferição de publicabilidade.
VERSAO_DO_ACERVO = 15


def _marco(identidade, codigo, **alteracoes):
    """Um marco como a composição o gravava: completo, e por isso aceito pela gravação de então."""
    base = {
        "id": identidade,
        "code": codigo,
        "name": f"Marco {codigo}",
        "stages": [],
        "operation": "SOMA_PONDERADA",
        "normalization": "NENHUMA",
        "rounding": {"scale": 2, "mode": "MEIO_PARA_CIMA"},
        "tiebreakers": [],
        "cutRule": {
            "targetKind": "FIXED",
            "targetCount": 2,
            "surplusCount": 0,
            "tieOutcome": "STRICT",
            "governedStage": "NONE",
            "continuation": "NONE",
        },
    }
    base.update(alteracoes)
    return base


#: O método inteiro, para que o marco de sorteio atravesse a gravação. Ele é retirado no
#: congelamento, que é onde o estado do acervo nasce.
METODO = {
    "algorithm": "IFES-SORTEIO-SHA256-v1",
    "source": "Fonte de demonstração",
    "occurrence": "5900",
    "occurrenceAt": "2020-01-01T20:00:00-03:00",
    "derivation": "a extração de sábado imediatamente anterior à data publicada",
    "normalization": {"rule": "DIGITOS_EM_SEQUENCIA", "text": "os cinco números sorteados"},
    "substitutionRule": {
        "rule": "OCORRENCIA_SEGUINTE_DA_MESMA_FONTE",
        "text": "não havendo extração na data, vale a seguinte da mesma fonte",
    },
}


def _rascunho_do_acervo():
    """Os três estados que a `032` passa a apontar, num Edital só.

    Um Perfil que **não classifica ninguém** (`FR-457`), um Perfil cujo marco ordena por sorteio e
    **não publica método** (`FR-467`) e um Perfil que **reparte vagas em recortes que o marco dele
    não emite** (`FR-470`). Os três no mesmo Edital de propósito: é a forma do achado "mais de um
    achado no mesmo Edital", e é o pior caso para uma recusa escrita sem recorte por ato.
    """
    return {
        "profiles": [
            {
                "id": SEM_MARCO,
                "code": "SEM-MARCO",
                "name": "Perfil que não classifica",
                "immediateVacancies": 1,
                "reserveType": "NONE",
                "reserveLimit": None,
                "competitionModalities": [],
                "vacancyTable": [
                    {"id": LINHA_SEM_MARCO, "modalityId": None, "immediateVacancies": 1}
                ],
                # Nasce com marco para atravessar a gravação; ele é removido no congelamento.
                "classificationMilestones": [
                    _marco(MARCO_A_REMOVER, "TEMP", stages=[ETAPA], orderProduction="POR_PONTUACAO")
                ],
            },
            {
                "id": COM_RESERVA,
                "code": "COM-RESERVA",
                "name": "Perfil com reserva sem apuração",
                "immediateVacancies": 10,
                "reserveType": "NONE",
                "reserveLimit": None,
                "competitionModalities": [
                    {"id": PCD, "code": "PCD", "name": "Pessoas com deficiência"},
                    {"id": NEGROS, "code": "PPI", "name": "Negros"},
                ],
                # O quadro 7/1/2 da auditoria, num marco que **não** sorteia: a ordem sai em lista
                # única, e os dois recortes reservados nunca terão ordem emitida.
                "vacancyTable": [
                    {"id": LINHA_GERAL, "modalityId": None, "immediateVacancies": 7},
                    {"id": LINHA_PCD, "modalityId": PCD, "immediateVacancies": 1},
                    {"id": LINHA_NEGROS, "modalityId": NEGROS, "immediateVacancies": 2},
                ],
                "classificationMilestones": [
                    _marco(
                        MARCO_COMPUTADO,
                        "CLASS-TUT",
                        stages=[ETAPA],
                        orderProduction="POR_PONTUACAO",
                    )
                ],
            },
            {
                "id": QUE_SORTEIA,
                "code": "SORTEIA",
                "name": "Perfil que sorteia sem método",
                "immediateVacancies": 1,
                "reserveType": "NONE",
                "reserveLimit": None,
                "competitionModalities": [],
                "vacancyTable": [
                    {"id": LINHA_DO_SORTEIO, "modalityId": None, "immediateVacancies": 1}
                ],
                "classificationMilestones": [
                    _marco(
                        MARCO_DE_SORTEIO,
                        "SORT-X",
                        orderProduction="POR_SORTEIO",
                        drawMethod=dict(METODO),
                    )
                ],
            },
        ],
        "stages": [
            {
                "id": ETAPA,
                "name": "Análise curricular",
                "order": 1,
                "weight": "1.0000",
                "eliminatory": False,
                "classificatory": True,
                "minimumScore": None,
                "scheduleEventId": None,
            }
        ],
        "schedule": [
            {
                "id": EVENTO,
                "type": "INSCRICAO",
                "description": "Inscrições",
                "startAt": "2026-09-01T09:00:00-03:00",
                "order": 1,
            }
        ],
    }


def _devolver_ao_estado_do_acervo(edital):
    """O que a migration deixou, e o que os degraus 10 e 13 escrevem no marco publicado antes deles.

    Três movimentos, e cada um corresponde a um Edital real que a auditoria encontrou publicado:
    o Perfil perde o marco, o marco computado perde a regra de corte, e o marco de sorteio perde o
    método. É `update()` sobre a **elaboração**, que é editável; o que é append-only é a Publicação,
    e ela ainda não existe neste ponto.
    """
    MarcoClassificatorio.objects.filter(pk=MARCO_A_REMOVER).delete()
    MarcoClassificatorio.objects.filter(pk=MARCO_COMPUTADO).update(regra_de_corte={})
    MarcoClassificatorio.objects.filter(pk=MARCO_DE_SORTEIO).update(metodo_de_sorteio={})


@pytest.fixture
def do_acervo(api_client, manager_headers, process_payload):
    return publicar_sem_aferir(
        api_client,
        manager_headers,
        process_payload,
        draft=_rascunho_do_acervo(),
        degradar=_devolver_ao_estado_do_acervo,
        versao=VERSAO_DO_ACERVO,
    )


def vigente(edital):
    return VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")


def test_o_acervo_nasce_com_as_tres_ausencias(do_acervo):
    """A premissa dos demais: sem ela, eles provariam outra coisa."""
    perfis = {perfil["code"]: perfil for perfil in vigente(do_acervo).content["profiles"]}

    assert perfis["SEM-MARCO"]["classificationMilestones"] == []
    sorteio = perfis["SORTEIA"]["classificationMilestones"][0]
    assert sorteio["orderProduction"] == "POR_SORTEIO"
    assert not sorteio.get("drawMethod"), "sorteia e não publica método — nem próprio, nem comum"
    computado = perfis["COM-RESERVA"]["classificationMilestones"][0]
    assert not computado.get("cutRule")
    assert [linha["immediateVacancies"] for linha in perfis["COM-RESERVA"]["vacancyTable"]] == [
        7,
        1,
        2,
    ]


def test_retificar_a_descricao_do_acervo_inexecutavel_passa(api_client, do_acervo):
    """A armadilha inteira num teste: esta Retificação não tem nada com classificação.

    Ela corrige a descrição. Se qualquer regra da família nova fosse impeditiva no ato de
    Retificação, este Edital — e todo o acervo com ele — ficaria preso.
    """
    retify(
        api_client,
        do_acervo,
        [{"operation": "REPLACE", "targetPath": "/description", "newValue": "Descrição corrigida"}],
    )

    assert vigente(do_acervo).content["description"] == "Descrição corrigida"


def test_o_conteudo_do_acervo_nao_produz_impedimento_algum_ao_retificar(do_acervo):
    """O mesmo, dito sobre a aferição que `retificacoes.py` de fato executa.

    O teste acima prova o caminho; este prova a **razão**, e nomeia os achados: nenhum dos quatro
    da família alcança o ato de Retificação, seja ele impeditivo ou aviso.
    """
    conteudo = vigente(do_acervo).content

    achados = validate_for_publication(conteudo, ato=ATO_DE_RETIFICACAO)
    codigos = {item.code for item in achados}

    assert blocking_findings(achados) == []
    assert codigos.isdisjoint(
        {
            "profile_without_milestone",
            "milestone_without_cut_rule",
            "drawn_milestone_without_method",
            "reserved_row_without_ordering",
        }
    ), sorted(codigos)
