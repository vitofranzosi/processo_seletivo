"""O teto de Inscrições por candidato, sob concorrência real (015, D-3).

**Este teste precisa de duas conexões PostgreSQL de verdade.** A corrida que ele exercita não é
observável em processo único: duas submissões de Perfis diferentes travam linhas diferentes, e nas
duas primeiras não existe linha submetida para travar — a contagem de ambas dá zero e as duas
passam. É por isso que a serialização é um advisory lock sobre o **par** candidato–Edital, e não
`select_for_update` sobre linhas que ainda não existem.

A barreira é o que faz as duas chegarem juntas à região crítica. Sem ela o teste passaria por
acidente, na ordem em que o agendador quisesse.
"""

import threading

import pytest
from django.db import connection, connections

from processo_seletivo.inscricoes.application.rascunho import (
    abrir_inscricao,
    anexar_documento,
    gravar_dados,
)
from processo_seletivo.inscricoes.application.submissao import enviar_inscricao
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.candidato import (
    MARIA,
    MODALIDADE_AC,
    PERFIL_DOCENTE,
    PERFIL_TECNICO,
    pdf,
)
from tests.fixtures.publicacao import retify
from tests.fixtures.selecao import DOCUMENTO_DE_TODOS, DOCUMENTO_DO_PERFIL

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

SOMENTE_POSTGRES = pytest.mark.skipif(
    connection.vendor != "postgresql",
    reason="A corrida é entre conexões; em sqlite a escrita já é serializada e ela não existe.",
)

DECLARACOES = {"veracidade": True, "ciencia": True}


def _pronta(edital, perfil):
    inscricao = abrir_inscricao(identidade=MARIA, edital_id=edital.id, profile_id=perfil)
    inscricao = gravar_dados(
        identidade=MARIA, inscricao=inscricao, dados={"modality_id": MODALIDADE_AC}
    )
    # O documento do Perfil só se aplica ao docente; anexar o inaplicável é 404, e o teste não
    # está aqui para exercitar aplicabilidade.
    exigidos = [(DOCUMENTO_DE_TODOS, "rg.pdf")]
    if perfil == PERFIL_DOCENTE:
        exigidos.append((DOCUMENTO_DO_PERFIL, "dip.pdf"))
    for requisito, nome in exigidos:
        anexar_documento(
            identidade=MARIA, inscricao=inscricao, requirement_id=requisito, arquivo=pdf(nome)
        )
    inscricao.refresh_from_db()
    return inscricao


@pytest.fixture
def com_teto_de_uma(api_client, selecao):
    """O teto entra por Retificação, que é o caminho real — o conteúdo publicado não se reescreve.

    A primeira redação deste teste alterava a `VersaoConsolidada` direto, e a trigger append-only
    recusou. Ela estava certa: publicar é ato, e um teste que finge o conteúdo publicado prova
    menos do que parece.
    """
    retify(
        api_client,
        selecao,
        [{"targetPath": "/maxInscricoesPorCandidato", "operation": "REPLACE", "newValue": 1}],
        suffix="teto",
    )
    Edital.objects.filter(pk=selecao.pk).update(max_inscricoes_por_candidato=1)
    selecao.refresh_from_db()
    return selecao


@SOMENTE_POSTGRES
def test_duas_submissoes_concorrentes_respeitam_o_teto(com_teto_de_uma, candidatos_registrados):
    """Uma submetida e uma recusa — nunca duas, e nunca zero."""
    primeira = _pronta(com_teto_de_uma, PERFIL_DOCENTE)
    segunda = _pronta(com_teto_de_uma, PERFIL_TECNICO)
    barreira = threading.Barrier(2, timeout=10)
    desfechos = {}

    def enviar(nome, inscricao):
        try:
            barreira.wait()
            enviar_inscricao(
                identidade=MARIA,
                inscricao=inscricao,
                declaracoes=DECLARACOES,
                idempotency_key=f"corrida-{nome}",
            )
            desfechos[nome] = "enviada"
        except DomainError as exc:
            desfechos[nome] = exc.code
        finally:
            connections.close_all()

    fios = [
        threading.Thread(target=enviar, args=("a", primeira)),
        threading.Thread(target=enviar, args=("b", segunda)),
    ]
    for fio in fios:
        fio.start()
    for fio in fios:
        fio.join(timeout=20)

    submetidas = Inscricao.objects.filter(
        identity_subject=MARIA.subject,
        edital=com_teto_de_uma,
        status=Inscricao.Status.SUBMETIDA,
    ).count()
    assert submetidas == 1, desfechos
    assert sorted(desfechos.values()) == ["enviada", "registration_limit_reached"], desfechos


@SOMENTE_POSTGRES
def test_a_submissao_e_a_retificacao_nao_se_atropelam(api_client, selecao, candidatos_registrados):
    """A prova do `FOR SHARE`, que o teste do teto não cobre.

    O advisory lock serializa **o mesmo candidato**; ele nada diz sobre uma Retificação publicada
    no meio do ato. Quem responde por isso é o `FOR SHARE` no Edital, conflitante com o
    `FOR UPDATE` que a publicação toma sobre a mesma linha.

    Os dois desfechos são legítimos, e é a **combinação proibida** que este teste exclui: submeter
    sob a versão antiga **depois** de a Retificação concorrente já ter vencido. Ou a submissão
    chega primeiro e conclui sob a versão que leu — e a Retificação espera —, ou a Retificação
    chega primeiro e a submissão, ao ler a versão nova, recusa com `edital_updated`, porque a
    pessoa não reconheceu aquela norma.
    """
    inscricao = _pronta(selecao, PERFIL_DOCENTE)
    antes = VersaoConsolidada.objects.filter(edital=selecao).latest("materialized_at")

    barreira = threading.Barrier(2, timeout=10)
    desfechos = {}

    def submeter():
        try:
            barreira.wait()
            enviada = enviar_inscricao(
                identidade=MARIA,
                inscricao=inscricao,
                declaracoes=DECLARACOES,
                idempotency_key="corrida-versao",
            )
            desfechos["submissao"] = ("enviada", enviada.versao_aceita_id)
        except DomainError as exc:
            desfechos["submissao"] = (exc.code, None)
        finally:
            connections.close_all()

    def retificar():
        try:
            barreira.wait()
            retify(
                api_client,
                selecao,
                [{"targetPath": "/title", "operation": "REPLACE", "newValue": "Retificado"}],
                suffix="corrida",
            )
            desfechos["retificacao"] = "publicada"
        finally:
            connections.close_all()

    fios = [threading.Thread(target=submeter), threading.Thread(target=retificar)]
    for fio in fios:
        fio.start()
    for fio in fios:
        fio.join(timeout=30)

    codigo, versao_aceita = desfechos["submissao"]
    depois = VersaoConsolidada.objects.filter(edital=selecao).latest("materialized_at")
    if codigo == "enviada":
        # Chegou primeiro: concluiu sob a versão que leu, e a Retificação esperou.
        assert versao_aceita == antes.pk, desfechos
    else:
        # A Retificação venceu: a submissão leu a versão nova e recusou, porque ninguém a
        # reconheceu ainda. O que **não** pode acontecer é ela ter passado sob a antiga.
        assert codigo == "edital_updated", desfechos
        assert depois.pk != antes.pk, "a Retificação precisa ter sido publicada neste ramo"
    assert (
        Inscricao.objects.filter(
            pk=inscricao.pk, status=Inscricao.Status.SUBMETIDA, versao_aceita=antes
        ).exists()
        or codigo != "enviada"
    ), "submeter sob a versão antiga depois de a Retificação vencer é a combinação proibida"
