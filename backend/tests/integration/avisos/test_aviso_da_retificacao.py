"""O aviso sobre a publicação retificadora (066, US2, `D-002`, `FR-1248`, `FR-1255a`).

**Ninguém escolhe quem a retificação "afetou".** O aviso alcança quem a publicação retificadora
considerou, e diz que é retificação sem dizer que a situação de alguém mudou: a retificadora pode
ter mudado outra linha da lista, e afirmar mudança a todos seria afirmar o que o ato não diz.

**O aviso antigo não muda, e o link dele não quebra.** A publicação sucedida continua respondendo no
mesmo endereço e aponta a vigente — é por isso que congelar o link no aviso é seguro.
"""

import pytest
from django.urls import reverse

from processo_seletivo.avisos.application import destinatarios
from processo_seletivo.avisos.domain import nomes
from processo_seletivo.avisos.models import Aviso
from processo_seletivo.divulgacao.models import SituacaoDivulgada
from tests.fixtures.avisos import avisar_resultado
from tests.fixtures.divulgacao import emitir, montar_ato_publicavel, publicar_o_ato

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


@pytest.fixture
def retificado(gestor, api_client, manager_headers, process_payload):
    """Publicado, avisado, e então retificado por uma publicação sucessora."""
    cenario = montar_ato_publicavel(
        gestor, api_client, manager_headers, process_payload, pontuacoes=("90.0000", "70.0000")
    )
    cenario["primeira"] = publicar_o_ato(cenario)
    cenario["primeiro_aviso"] = avisar_resultado(
        cenario["edital"], cenario["primeira"].marco_id, chave="aviso-original"
    )
    sucessor = emitir(cenario, gestor, chave="emitir-066-retificacao", motivo="Correção da ordem.")
    cenario["retificadora"] = publicar_o_ato(
        cenario, ato=sucessor, chave="publicar-066-retificacao"
    )
    return cenario


def test_so_a_retificadora_e_nova_e_os_destinatarios_sao_os_dela(retificado):
    universo = destinatarios.universo_do_resultado(
        edital=retificado["edital"],
        marco_id=retificado["primeira"].marco_id,
        natureza=nomes.PRELIMINAR,
    )

    assert [p.id for p in universo.publicacoes] == [retificado["retificadora"].id]
    considerados = set(
        SituacaoDivulgada.objects.filter(publicacao=retificado["retificadora"]).values_list(
            "inscricao_id", flat=True
        )
    )
    assert {linha.inscricao.id for linha in universo.linhas} == considerados
    assert universo.retificadora


def test_a_linha_fixa_diz_que_retifica_e_nao_que_algo_mudou(retificado):
    declarado = avisar_resultado(
        retificado["edital"], retificado["primeira"].marco_id, chave="aviso-retificacao"
    )

    aviso = Aviso.objects.get(pk=declarado["aviso"])
    assert aviso.retificadora
    assert "Este aviso se refere a publicação que retifica a de" in aviso.corpo
    for frase in ("sua situação mudou", "você foi reclassificad", "sua posição mudou"):
        assert frase not in aviso.corpo.lower()


def test_o_primeiro_aviso_continua_como_foi(retificado):
    antes = Aviso.objects.get(pk=retificado["primeiro_aviso"]["aviso"])
    destinatarios_antes = list(antes.destinatarios.values_list("inscricao_id", "endereco"))
    corpo_antes = antes.corpo

    avisar_resultado(
        retificado["edital"], retificado["primeira"].marco_id, chave="aviso-retificacao"
    )

    depois = Aviso.objects.get(pk=antes.pk)
    assert depois.corpo == corpo_antes
    assert list(depois.destinatarios.values_list("inscricao_id", "endereco")) == (
        destinatarios_antes
    )
    assert not depois.retificadora


def test_retificar_sem_gesto_nao_avisa_ninguem(retificado):
    """`FR-1243`: a retificação publicada não dispara aviso nenhum."""
    assert Aviso.objects.count() == 1


def test_o_link_congelado_no_aviso_antigo_leva_a_vigente(retificado, client):
    """`FR-1255a`: o aviso que citou uma publicação traz o link dela, e o link continua valendo."""
    aviso = Aviso.objects.get(pk=retificado["primeiro_aviso"]["aviso"])
    caminho = reverse("portal:resultado", args=[retificado["primeira"].id])
    assert caminho in aviso.corpo

    resposta = client.get(caminho)

    assert resposta.status_code == 200
    corpo = resposta.content.decode()
    assert reverse("portal:resultado", args=[retificado["retificadora"].id]) in corpo
