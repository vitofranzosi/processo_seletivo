"""Cenário mínimo do sorteio: um Edital publicado com método declarado, e relações sobre ele."""

from django.db import transaction
from django.utils import timezone

from processo_seletivo.shared.canonical import canonical_sha256
from processo_seletivo.sorteios.models import ParticipanteHabilitado, RelacaoDeHabilitados

MARCO = "00000000-0000-4000-8000-000000000821"
LISTA_PPI = "00000000-0000-4000-8000-000000000831"
LISTA_PCD = "00000000-0000-4000-8000-000000000832"

# **`occurrence` é a ocorrência concreta**, e `derivation` é a prosa que explica como ela foi
# escolhida a partir da data programada. Se `occurrence` fosse a regra em prosa, a escolha de qual
# extração observar voltaria para a mesa no dia do sorteio — que é exatamente o que a FR-015 e a
# FR-017 proíbem. O Edital nomeia o concurso **antes** do congelamento.
METODO = {
    "algorithm": "IFES-SORTEIO-SHA256-v1",
    # Nome do vocabulário fechado de fontes: é ele que determina qual adaptador consulta a semente.
    "source": "Fonte de demonstração",
    "occurrence": "5900",
    # O instante publicado da ocorrência, **no passado** para que os cenários possam observá-la.
    # É ele que separa "a fonte ainda não publicou" de "a fonte não publicará" (FR-077).
    "occurrenceAt": "2020-01-01T20:00:00-03:00",
    "derivation": "concurso 5900: a extração de sábado imediatamente anterior à data publicada",
    "normalization": {
        "rule": "DIGITOS_EM_SEQUENCIA",
        "text": "os cinco números sorteados, na ordem dos prêmios, separados por espaço",
    },
    "substitutionRule": {
        "rule": "OCORRENCIA_SEGUINTE_DA_MESMA_FONTE",
        "text": "não havendo extração na data, vale a extração seguinte da mesma fonte",
    },
}


def marco_com_metodo(rascunho, *, perfil_id, etapa_id, metodo=None, marco_id=MARCO):
    """Declara, no rascunho, um marco de classificação que publica o método do sorteio.

    **O peso da Etapa entra porque a validação da `015` o exige** — "quem enumera declara o peso" —,
    e não porque o sorteio o use: a ordem vem da chave, e o caminho computado do marco simplesmente
    não é percorrido num ato de origem `SORTEIO`. Enumerar a Etapa é o que liga o marco ao ponto do
    certame em que a ordem é produzida; o peso é exigência do outro caminho, que existe para os
    marcos que ordenam por pontuação.
    """
    for etapa in rascunho.get("stages") or []:
        if str(etapa["id"]) == str(etapa_id):
            etapa.setdefault("weight", "1.0000")
    for perfil in rascunho["profiles"]:
        if str(perfil["id"]) != str(perfil_id):
            continue
        perfil["classificationMilestones"] = [
            {
                "id": marco_id,
                "code": "SORTEIO",
                "name": "Sorteio público",
                "stages": [etapa_id],
                "operation": "SOMA_PONDERADA",
                "normalization": "NENHUMA",
                "rounding": {"scale": 2, "mode": "MEIO_PARA_CIMA"},
                "tiebreakers": [],
                # **A janela recursal declarada**, como o `seed_demo` já a declara: um marco de
                # sorteio admite recurso, e é o prazo dele que a definitiva precisa esperar. Sem
                # ela, o cenário do prazo por lista não se coloca — e foi o que escondeu, por um
                # tempo, o eixo perdido em `_janela_aberta` (018, FR-030; 021, FR-068).
                "appealWindow": {"admits": True, "durationDays": 5, "unit": "DIAS_CORRIDOS"},
                "drawMethod": METODO if metodo is None else metodo,
            }
        ]
    return rascunho


def certame_de_sorteio(gestor, api_client, manager_headers, process_payload, *, quantos=3):
    """Um Edital publicado com marco de sorteio, comissão presidida e inscrições submetidas.

    É o ponto de partida de quase todo teste da feature. A presidência entra porque os comandos do
    sorteio passam por `comando_de_comissao`, e a base suficiente é a presidência deste Processo.
    """
    from processo_seletivo.comissoes.domain.funcoes import Funcao
    from tests.fixtures.comissao import constituir, inscrever, rascunho_com_etapas
    from tests.fixtures.edital import PROFILE_ID
    from tests.fixtures.publicacao import publish_original

    rascunho = rascunho_com_etapas()
    marco_com_metodo(rascunho, perfil_id=PROFILE_ID, etapa_id=rascunho["stages"][1]["id"])
    edital = publish_original(api_client, manager_headers, process_payload, draft=rascunho)
    membros = constituir(
        gestor,
        edital.processo,
        [("maria", Funcao.PRESIDENTE)],
        prefixo="sorteio-021",
    )
    return {
        "edital": edital,
        "processo": edital.processo,
        "membros": membros,
        "perfil": PROFILE_ID,
        "marco": MARCO,
        "inscricoes": inscrever(edital, quantos, primeiro=901),
    }


def certame_com_cotas(gestor, api_client, manager_headers, process_payload, *, quantos=6):
    """O 57 e o 28: ampla concorrência, PPI e PcD sobre o mesmo marco.

    O cotista aparece em **duas** listas — a de ampla concorrência alcança todos, a de reserva
    alcança quem declarou aquela modalidade —, e é isso que a US4 precisa exercitar.
    """
    from processo_seletivo.comissoes.domain.funcoes import Funcao
    from tests.fixtures.comissao import constituir, inscrever, rascunho_com_etapas
    from tests.fixtures.edital import PROFILE_ID
    from tests.fixtures.publicacao import publish_original

    rascunho = rascunho_com_etapas()
    marco_com_metodo(rascunho, perfil_id=PROFILE_ID, etapa_id=rascunho["stages"][1]["id"])
    for perfil in rascunho["profiles"]:
        if str(perfil["id"]) == PROFILE_ID:
            perfil["competitionModalities"] = [
                {
                    "id": LISTA_PPI,
                    "code": "PPI",
                    "name": "Pretos, pardos e indígenas",
                    "reservedVacancies": 1,
                },
                {
                    "id": LISTA_PCD,
                    "code": "PCD",
                    "name": "Pessoas com deficiência",
                    "reservedVacancies": 1,
                },
            ]
    edital = publish_original(api_client, manager_headers, process_payload, draft=rascunho)
    constituir(gestor, edital.processo, [("maria", Funcao.PRESIDENTE)], prefixo="cotas-021")
    inscricoes = inscrever(edital, quantos, primeiro=701)
    # Os dois primeiros declaram cota: eles figuram na ampla concorrência **e** na reserva deles,
    # com numeração própria em cada (FR-004).
    from processo_seletivo.inscricoes.models import Inscricao

    Inscricao.objects.filter(pk=inscricoes[0].pk).update(modality_id=LISTA_PPI)
    Inscricao.objects.filter(pk=inscricoes[1].pk).update(modality_id=LISTA_PCD)
    for inscricao in inscricoes:
        inscricao.refresh_from_db()
    return {
        "edital": edital,
        "processo": edital.processo,
        "perfil": PROFILE_ID,
        "marco": MARCO,
        "inscricoes": inscricoes,
        "cotista_ppi": inscricoes[0],
        "cotista_pcd": inscricoes[1],
    }


def presidente(subject="maria"):
    from tests.conftest import ator_institucional

    return ator_institucional(subject)


def universo_de_sorteio(
    edital, *, versao, perfil_id, marco_id=MARCO, relacao=None, sorteio_id=None
):
    """O `universo` que um ato de sorteio grava — inclusive o que a trigger exige (021, FR-069).

    As quatro identidades e `stageResults` não são adorno: `check_ordering_act_provenance` recusa a
    gravação sem elas. `[]` é a resposta verdadeira para um sorteio, que nenhuma Etapa produziu.
    """
    return {
        "editalId": str(edital.id),
        "profileId": str(perfil_id),
        "milestoneId": str(marco_id),
        "versionId": str(versao.id),
        "stageResults": [],
        "origem": "SORTEIO",
        "sorteioId": str(sorteio_id) if sorteio_id else None,
        "relacaoId": str(relacao.id) if relacao is not None else None,
        "relationHash": relacao.resumo if relacao is not None else None,
        "quantidade": relacao.quantidade if relacao is not None else 0,
    }


def relacao(
    edital,
    *,
    versao,
    perfil_id,
    marco_id=MARCO,
    lista_id=None,
    inscricoes=(),
    anterior=None,
    motivo="",
    metodo_hash=None,
):
    """Uma relação publicada, direto no agregado — para exercitar constraint, e não comando."""
    participantes = list(inscricoes)
    conteudo = {
        "relationId": None,
        "participants": [
            {"publicNumber": i, "name": ins.nome, "protocol": ins.protocolo}
            for i, ins in enumerate(participantes, start=1)
        ],
    }
    with transaction.atomic():
        criada = RelacaoDeHabilitados.objects.create(
            edital=edital,
            perfil_id=perfil_id,
            marco_id=marco_id,
            lista_id=lista_id,
            versao=versao,
            metodo_hash=metodo_hash or canonical_sha256(METODO),
            criterio_de_projecao="Inscrições submetidas do recorte.",
            quantidade=max(len(participantes), 1),
            resumo=canonical_sha256(conteudo),
            publicada_em=timezone.now(),
            publicada_por="cpf:presidente",
            relacao_anterior=anterior,
            motivo_da_sucessao=motivo,
        )
        ParticipanteHabilitado.objects.bulk_create(
            [
                ParticipanteHabilitado(relacao=criada, inscricao=ins, numero_publico=numero)
                for numero, ins in enumerate(participantes, start=1)
            ]
        )
    return criada
