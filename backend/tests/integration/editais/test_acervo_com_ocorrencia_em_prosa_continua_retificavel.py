"""O Edital publicado com a ocorrência em prosa **continua retificável** (035, FR-514, SC-179).

**É o irmão de `test_acervo_inexecutavel_continua_retificavel.py`, e existe pela mesma armadilha.**
`retificacoes.py` afere o conteúdo que o ato produziria com
`blocking_findings(validate_for_publication(content, ato=ATO_DE_RETIFICACAO))`. A sexta guarda do
método vive em `_validar_metodo_de_sorteio`, e essa função é atravessada **também** pela aferição —
escrita sem recorte por ato, ela tornaria irretificável todo Edital do acervo cuja ocorrência não
satisfaça a forma, inclusive por uma Retificação que só corrige uma data.

**E o que se perderia é justamente o que a feature existe para salvar.** O Edital cuja ocorrência
está em prosa é o destinatário da `US3`: a tela do sorteio dele passa a dizer qual campo corrigir, e
manda Retificar. Se a Retificação estivesse fechada, a feature teria trocado uma mensagem falsa por
um beco sem saída.

**A medição que autorizou este desenho está em `inventario-do-metodo.md`, `T004`:** zero Editais
nos bancos desta máquina têm ocorrência fora da forma. O zero diz que nada quebra hoje; a
`FR-514` diz que nada pode prender amanhã. São coisas diferentes, e este arquivo prende a
segunda — o acervo é **construído** com o defeito, de propósito, porque uma garantia sobre
conteúdo que não existe não é garantia nenhuma.

O acervo é simulado como ele realmente é — `Publicacao` inserida com o conteúdo que teria sido
publicado —, e não por `UPDATE` sobre linha publicada: publicação é append-only por trigger desde
a `002`. E a ocorrência em prosa é posta pelo `degradar`, e não pelo rascunho: a gravação **de
hoje** a recusa, que é precisamente o ponto da `US2`.
"""

import pytest

from processo_seletivo.editais.domain.validation import (
    ATO_DE_PUBLICACAO,
    ATO_DE_RETIFICACAO,
    blocking_findings,
    validate_for_publication,
)
from processo_seletivo.editais.models.perfis import MarcoClassificatorio
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from processo_seletivo.shared.canonical import SCHEMA_VERSION
from tests.fixtures.legado import publicar_sem_aferir
from tests.fixtures.publicacao import retify

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

QUE_SORTEIA = "aaaaaaaa-0000-4000-8000-0000000035c1"
MARCO_DE_SORTEIO = "aaaaaaaa-0000-4000-8000-0000000035d1"
LINHA_DO_SORTEIO = "aaaaaaaa-0000-4000-8000-0000000035f1"
EVENTO = "aaaaaaaa-0000-4000-8000-0000000035f2"
ETAPA = "aaaaaaaa-0000-4000-8000-0000000035f3"

#: A forma que uma pessoa escreve. O número está lá, e só não está onde a regra o procura.
EM_PROSA = "concurso 6100 da Loteria Federal"

#: O método inteiro e **derivável**, para que o rascunho atravesse a gravação de hoje. A ocorrência
#: é trocada no `degradar`, que é o único ponto em que o estado do acervo pode nascer.
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
    return {
        "profiles": [
            {
                "id": QUE_SORTEIA,
                "code": "SORTEIA",
                "name": "Perfil que sorteia",
                "immediateVacancies": 1,
                "reserveType": "NONE",
                "reserveLimit": None,
                "competitionModalities": [],
                "vacancyTable": [
                    {"id": LINHA_DO_SORTEIO, "modalityId": None, "immediateVacancies": 1}
                ],
                "classificationMilestones": [
                    {
                        "id": MARCO_DE_SORTEIO,
                        "code": "SORT-X",
                        "name": "Sorteio público",
                        "orderProduction": "POR_SORTEIO",
                        "stages": [],
                        # Exigidos pelo contrato do marco, e sem efeito num marco que sorteia: a
                        # ordem vem da chave, e o caminho computado simplesmente não é percorrido.
                        "operation": "SOMA_PONDERADA",
                        "normalization": "NENHUMA",
                        "tiebreakers": [],
                        "rounding": {"scale": 2, "mode": "MEIO_PARA_CIMA"},
                        "cutRule": {
                            "targetKind": "FIXED",
                            "targetCount": 1,
                            "surplusCount": 0,
                            "tieOutcome": "STRICT",
                            "governedStage": "NONE",
                            "continuation": "NONE",
                        },
                        "drawMethod": dict(METODO),
                    }
                ],
            }
        ],
        "stages": [
            {
                "id": ETAPA,
                "name": "Análise documental",
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


def _por_a_ocorrencia_em_prosa(edital):
    """O estado do acervo: um método completo cuja ocorrência a regra não sabe derivar.

    `update()` sobre a **elaboração**, que é editável; o que é append-only é a Publicação, e ela
    ainda não existe neste ponto. A gravação pela API não produz este estado — desde a `035` ela o
    recusa —, e é por isso que ele é montado aqui.
    """
    MarcoClassificatorio.objects.filter(pk=MARCO_DE_SORTEIO).update(
        metodo_de_sorteio={**METODO, "occurrence": EM_PROSA}
    )


@pytest.fixture
def do_acervo(api_client, manager_headers, process_payload):
    return publicar_sem_aferir(
        api_client,
        manager_headers,
        process_payload,
        draft=_rascunho_do_acervo(),
        degradar=_por_a_ocorrencia_em_prosa,
        versao=SCHEMA_VERSION,
    )


def vigente(edital):
    return VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")


def test_o_acervo_nasce_com_a_ocorrencia_em_prosa(do_acervo):
    """A premissa dos demais: sem ela, eles provariam outra coisa."""
    perfil = vigente(do_acervo).content["profiles"][0]
    marco = perfil["classificationMilestones"][0]

    assert marco["orderProduction"] == "POR_SORTEIO"
    assert marco["drawMethod"]["occurrence"] == EM_PROSA


def test_retificar_a_descricao_do_acervo_em_prosa_passa(api_client, do_acervo):
    """A armadilha inteira num teste: esta Retificação não tem nada com o sorteio.

    Ela corrige a descrição. Se a sexta guarda fosse impeditiva no ato de Retificação, este Edital
    — e todo o acervo com ele — ficaria preso, e a única saída que a `FR-517` aponta estaria
    fechada.
    """
    retify(
        api_client,
        do_acervo,
        [{"operation": "REPLACE", "targetPath": "/description", "newValue": "Descrição corrigida"}],
    )

    assert vigente(do_acervo).content["description"] == "Descrição corrigida"


def test_o_conteudo_do_acervo_nao_produz_impedimento_algum_ao_retificar(do_acervo):
    """O mesmo, dito sobre a aferição que `retificacoes.py` de fato executa."""
    conteudo = vigente(do_acervo).content

    achados = validate_for_publication(conteudo, ato=ATO_DE_RETIFICACAO)

    assert blocking_findings(achados) == []
    assert "draw_method_invalid" not in {item.code for item in achados}


def test_a_mesma_ocorrencia_continua_impedindo_a_publicacao(do_acervo):
    """A contraprova, e a que um recorte largo demais apagaria (`D-001`).

    O recorte por ato não é afrouxamento: o Edital que se publica **hoje** continua sendo impedido,
    e com a frase que diz o que corrigir. O que muda é que corrigir o de ontem continua possível.
    """
    conteudo = vigente(do_acervo).content

    impeditivos = blocking_findings(validate_for_publication(conteudo, ato=ATO_DE_PUBLICACAO))

    recusa = [item for item in impeditivos if item.code == "draw_method_invalid"]
    assert recusa, [item.code for item in impeditivos]
    assert "terminar no número" in recusa[0].message


def test_a_retificacao_que_corrige_a_ocorrencia_e_o_caminho_que_a_tela_aponta(
    api_client, do_acervo
):
    """E o caminho existe: trocar a ocorrência por uma derivável é uma Retificação comum.

    É o que a `FR-517` manda a tela do sorteio dizer, e ela só pode dizê-lo se funcionar.
    """
    caminho = (
        f"/profiles/id={QUE_SORTEIA}/classificationMilestones/id={MARCO_DE_SORTEIO}"
        "/drawMethod/occurrence"
    )

    retify(
        api_client,
        do_acervo,
        [{"operation": "REPLACE", "targetPath": caminho, "newValue": "6100"}],
    )

    marco = vigente(do_acervo).content["profiles"][0]["classificationMilestones"][0]
    assert marco["drawMethod"]["occurrence"] == "6100"
