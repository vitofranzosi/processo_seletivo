"""O Perfil sem a ampla ganha a ampla, e quem não é cotista passa a se inscrever (048, `SC-288`).

É o caso da `D-G5`, que a auditoria chamou de *"o único Edital publicado sem correção possível"*:
um Perfil com duas cotas e nenhuma ampla concorrência exige escolher uma cota, e o não-cotista não
se inscreve. A Retificação acrescenta a Modalidade e a declara ampla, e o que este arquivo prova é
o que ela **não** faz — mexer em quem já se inscreveu — ao lado do que ela passa a permitir.
"""

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.inscricoes.application.rascunho import (
    abrir_inscricao,
    anexar_documento,
    gravar_dados,
)
from processo_seletivo.inscricoes.application.submissao import (
    enviar_inscricao,
    reconhecer_versao,
)
from processo_seletivo.inscricoes.models import Inscricao, ItemDaListaExigida
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.candidato import JOAO, MARIA, MODALIDADE_PPP, PERFIL_DOCENTE, pdf
from tests.fixtures.edital import identificador
from tests.fixtures.publicacao import retify
from tests.fixtures.selecao import (
    DOCUMENTO_DA_MODALIDADE,
    DOCUMENTO_DE_TODOS,
    DOCUMENTO_DO_PERFIL,
    publicar_selecao,
    rascunho_aberto_com_documentos,
)

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

MODALIDADE_PCD = identificador(470, 0)
AMPLA_NOVA = "00000000-0000-4000-8000-000000048301"
DECLARACOES = {"veracidade": True, "ciencia": True}


def _sem_a_ampla(rascunho):
    """O Perfil docente com PPP e PcD, e nenhuma ampla: a forma do achado da `034`."""
    docente = rascunho["profiles"][0]
    docente["competitionModalities"] = [
        modalidade for modalidade in docente["competitionModalities"] if modalidade["code"] != "AC"
    ] + [{"id": MODALIDADE_PCD, "code": "PCD", "name": "Pessoas com deficiência"}]
    docente["generalCompetitionModalityId"] = None
    docente["vacancyTable"] = [
        {"id": identificador(408, 0), "modalityId": None, "immediateVacancies": 0},
        {"id": identificador(409, 0), "modalityId": MODALIDADE_PPP, "immediateVacancies": 1},
        {"id": identificador(471, 0), "modalityId": MODALIDADE_PCD, "immediateVacancies": 1},
    ]
    return rascunho


@pytest.fixture
def edital(raiz_de_arquivos, candidatos_registrados, api_client, manager_headers, process_payload):
    agora = timezone.now() - timedelta(seconds=1)
    return publicar_selecao(
        api_client,
        manager_headers,
        process_payload,
        rascunho=_sem_a_ampla(rascunho_aberto_com_documentos(agora)),
    )


def _preencher(identidade, inscricao, modalidade, documentos):
    inscricao = gravar_dados(
        identidade=identidade,
        inscricao=inscricao,
        dados={
            "nome": identidade.nome,
            "cpf": identidade.cpf,
            "email": identidade.email,
            "modality_id": modalidade,
        },
    )
    for requisito in documentos:
        anexar_documento(
            identidade=identidade, inscricao=inscricao, requirement_id=requisito, arquivo=pdf()
        )
    inscricao.refresh_from_db()
    return inscricao


def _enviar(identidade, inscricao, chave):
    return enviar_inscricao(
        identidade=identidade, inscricao=inscricao, declaracoes=DECLARACOES, idempotency_key=chave
    )


def _acrescentar_a_ampla(api_client, edital):
    return retify(
        api_client,
        edital,
        [
            {
                "targetPath": f"/profiles/id={PERFIL_DOCENTE}/competitionModalities/-",
                "operation": "ADD",
                "newValue": {
                    "id": AMPLA_NOVA,
                    "code": "AC",
                    "name": "Ampla concorrência",
                    "description": "",
                    "normativeRule": None,
                },
            },
            {
                "targetPath": f"/profiles/id={PERFIL_DOCENTE}/generalCompetitionModalityId",
                "operation": "REPLACE",
                "newValue": AMPLA_NOVA,
            },
        ],
        suffix="ampla-048",
    )


def test_a_contraprova_sem_a_ampla_o_nao_cotista_nao_tem_o_que_escolher(edital):
    rascunho = abrir_inscricao(identidade=JOAO, edital_id=edital.id, profile_id=PERFIL_DOCENTE)

    with pytest.raises(DomainError):
        gravar_dados(
            identidade=JOAO,
            inscricao=rascunho,
            dados={"nome": JOAO.nome, "cpf": JOAO.cpf, "email": JOAO.email, "modality_id": ""},
        )


def test_a_ampla_acrescentada_recebe_o_nao_cotista_e_nao_mexe_em_quem_ja_enviou(
    client, edital, api_client
):
    maria = abrir_inscricao(identidade=MARIA, edital_id=edital.id, profile_id=PERFIL_DOCENTE)
    enviada = _enviar(
        MARIA,
        _preencher(
            MARIA,
            maria,
            MODALIDADE_PPP,
            (DOCUMENTO_DE_TODOS, DOCUMENTO_DO_PERFIL, DOCUMENTO_DA_MODALIDADE),
        ),
        "envio-maria-048",
    )
    lista_antes = sorted(
        ItemDaListaExigida.objects.filter(inscricao=enviada).values_list(
            "requisito_id", "modalidade_id"
        )
    )
    original = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")

    _acrescentar_a_ampla(api_client, edital)

    # FR-781: a inscrição enviada continua com a Modalidade e a lista exigida que tinha.
    enviada.refresh_from_db()
    assert str(enviada.modality_id) == MODALIDADE_PPP
    assert (
        sorted(
            ItemDaListaExigida.objects.filter(inscricao=enviada).values_list(
                "requisito_id", "modalidade_id"
            )
        )
        == lista_antes
    )

    # SC-288: o não-cotista se inscreve pela ampla, que a versão nova oferece.
    joao = abrir_inscricao(identidade=JOAO, edital_id=edital.id, profile_id=PERFIL_DOCENTE)
    enviada_pela_ampla = _enviar(
        JOAO,
        _preencher(JOAO, joao, AMPLA_NOVA, (DOCUMENTO_DE_TODOS, DOCUMENTO_DO_PERFIL)),
        "envio-joao-048",
    )
    assert enviada_pela_ampla.status == Inscricao.Status.SUBMETIDA
    assert str(enviada_pela_ampla.modality_id) == AMPLA_NOVA

    # FR-797: a página pública da seleção lê a versão vigente.
    pagina = client.get(reverse("portal:selecao", args=[edital.id])).content.decode()
    assert "Ampla concorrência" in pagina

    # FR-796: a publicação anterior continua consultável, com o conteúdo que tinha.
    anterior = client.get(f"/api/v1/public/versoes/{original.id}")
    assert anterior.status_code == 200
    docente = next(
        perfil
        for perfil in anterior.json()["content"]["profiles"]
        if perfil["id"] == PERFIL_DOCENTE
    )
    assert AMPLA_NOVA not in {m["id"] for m in docente["competitionModalities"]}


def test_o_rascunho_de_modalidade_unica_nao_envia_em_silencio(
    raiz_de_arquivos, candidatos_registrados, api_client, manager_headers, process_payload
):
    """Caso-limite *"Rascunho de inscrição aberto"*: o Perfil que passa de uma Modalidade para duas.

    Com uma só, a inscrição a assume sem perguntar, e **grava**. Depois da Retificação, o envio é
    recusado até a pessoa reconhecer a versão nova (009, FR-058); reconhecida, a Modalidade gravada
    continua sendo a escolha — trocá-la pela ampla é da pessoa. A primeira redação da spec dizia
    que a escolha passaria a ser exigida, e este caso mostrou que não: assumir sem perguntar é o
    achado A-1 da `048`.
    """
    rascunho = rascunho_aberto_com_documentos(timezone.now() - timedelta(seconds=1))
    docente = rascunho["profiles"][0]
    docente["competitionModalities"] = [
        modalidade for modalidade in docente["competitionModalities"] if modalidade["code"] == "PPP"
    ]
    docente["generalCompetitionModalityId"] = None
    docente["vacancyTable"] = [
        {"id": identificador(408, 0), "modalityId": None, "immediateVacancies": 1},
        {"id": identificador(409, 0), "modalityId": MODALIDADE_PPP, "immediateVacancies": 1},
    ]
    edital = publicar_selecao(api_client, manager_headers, process_payload, rascunho=rascunho)
    joao = abrir_inscricao(identidade=JOAO, edital_id=edital.id, profile_id=PERFIL_DOCENTE)
    joao = _preencher(
        JOAO, joao, "", (DOCUMENTO_DE_TODOS, DOCUMENTO_DO_PERFIL, DOCUMENTO_DA_MODALIDADE)
    )
    assert str(joao.modality_id) == MODALIDADE_PPP, "a contraprova: com uma só, ela é assumida"

    _acrescentar_a_ampla(api_client, edital)

    with pytest.raises(DomainError) as recusa:
        _enviar(JOAO, joao, "envio-joao-048-unica")
    assert recusa.value.code == "edital_updated", "não envia em silêncio"

    reconhecer_versao(
        identidade=JOAO,
        inscricao=joao,
        versao=VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at"),
    )
    joao.refresh_from_db()
    # Trocar pela ampla descarta a autodeclaração, que deixa de ser exigida — e o descarte é
    # confirmado, como em toda troca de Modalidade (FR-031 da 009).
    trocada = gravar_dados(
        identidade=JOAO,
        inscricao=joao,
        dados={"nome": JOAO.nome, "cpf": JOAO.cpf, "email": JOAO.email, "modality_id": AMPLA_NOVA},
        descartes_confirmados=[DOCUMENTO_DA_MODALIDADE],
    )
    enviada = _enviar(JOAO, trocada, "envio-joao-048-trocada")

    assert str(enviada.modality_id) == AMPLA_NOVA, "a pessoa pôde trocar pela ampla"
