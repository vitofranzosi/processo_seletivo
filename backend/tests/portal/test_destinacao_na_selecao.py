"""A destinação das vagas na página pública da seleção (155, T043, US7, FR-6337).

O certame é o das cotas da `016`, publicado com a reversão por esgotamento e com inscrições — para
que a ausência de nome e de protocolo seja prova, e não falta de candidato. Os atos entram direto no
banco, com a versão que citariam: o que se verifica aqui é a leitura pública, e o ato tem os seus
casos em `tests/integration/ocupacao/test_destinacao.py`.
"""

from datetime import timedelta

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.ocupacao.application.selectors import (
    DESFAZIMENTO_DA_DESTINACAO,
    DESTINACAO,
    NAO_PREENCHIDA,
    destinacoes_publicas,
)
from processo_seletivo.ocupacao.domain import nomes
from processo_seletivo.ocupacao.models import MovimentoDeVaga, VagaNaoPreenchida
from processo_seletivo.publicacoes.application.selectors import effective_version
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.ocupacao_sorteada import LISTA_PCD, LISTA_PPI, certame_sorteado_com_quadro
from tests.fixtures.sorteio import MARCO

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

FRASE_DO_EDITAL = "essas vagas passam para a ampla concorrência do mesmo código"
MOTIVO_DO_DESFAZIMENTO = "A desistência registrada foi anulada por decisão da comissão."
FUNDAMENTO_DA_DECLARACAO = (
    "A lista PCD não teve inscrito habilitado, e o Edital não declara reversão."
)


def destinar(edital, versao, quando, *, quantidade=1):
    return MovimentoDeVaga.objects.create(
        edital=edital,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        especie=nomes.MOVIMENTO_REVERSAO,
        origem_lista_id=LISTA_PPI,
        destino_lista_id=None,
        quantidade=quantidade,
        causa="Destinação à ampla concorrência por ato próprio: 1 de 1.",
        gatilho=nomes.REVERSAO_POR_ESGOTAMENTO,
        fundamento="frase gravada (versão do Edital vigente desde …)",
        versao=versao,
        registrado_por="maria",
        registrado_em=quando,
    )


def desfazer(movimento, quando):
    return MovimentoDeVaga.objects.create(
        edital=movimento.edital,
        perfil_id=movimento.perfil_id,
        marco_id=movimento.marco_id,
        especie=nomes.MOVIMENTO_DESFAZIMENTO,
        origem_lista_id=None,
        destino_lista_id=movimento.origem_lista_id,
        quantidade=movimento.quantidade,
        causa="Desfazimento da destinação.",
        gatilho=movimento.gatilho,
        fundamento=MOTIVO_DO_DESFAZIMENTO,
        versao=movimento.versao,
        desfaz=movimento,
        registrado_por="maria",
        registrado_em=quando,
    )


def declarar(edital, versao, quando):
    return VagaNaoPreenchida.objects.create(
        edital=edital,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        lista_id=LISTA_PCD,
        especie=nomes.NAO_PREENCHIDA_DECLARACAO,
        quantidade=1,
        fundamento=FUNDAMENTO_DA_DECLARACAO,
        versao=versao,
        registrado_por="maria",
        registrado_em=quando,
    )


@pytest.fixture
def certame(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    return certame_sorteado_com_quadro(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="pub-155",
        reversao=nomes.REVERSAO_POR_ESGOTAMENTO,
    )


@pytest.fixture
def com_atos(certame):
    edital = certame["edital"]
    versao = effective_version(edital_id=edital.id)
    agora = timezone.now()
    destinada = destinar(edital, versao, agora - timedelta(days=2))
    desfazer(destinada, agora - timedelta(days=1))
    declarar(edital, versao, agora)
    return certame


def pagina(client, certame):
    resposta = client.get(reverse("portal:selecao", args=[certame["edital"].id]))
    assert resposta.status_code == 200
    return resposta.content.decode()


def test_a_destinacao_a_nao_preenchida_e_o_desfazimento_aparecem_sem_login(client, com_atos):
    """US7, cenários 1 e 2: origem, destino, quantidade e fundamento; o desfazimento cita."""
    corpo = pagina(client, com_atos)

    assert "Destinação das vagas" in corpo
    assert (
        "1 vaga reservada à lista «Pretos, pardos e indígenas (PPI)» do Perfil «" in corpo
        and "foi destinada à ampla concorrência em" in corpo
    )
    assert FRASE_DO_EDITAL in corpo, "o fundamento é a frase que o Edital publicou"
    assert "A destinação de" in corpo and "foi desfeita em" in corpo
    assert MOTIVO_DO_DESFAZIMENTO in corpo
    assert "foi declarada não preenchida em" in corpo
    assert FUNDAMENTO_DA_DECLARACAO in corpo


def test_nenhum_nome_nem_protocolo_de_candidato(client, com_atos):
    """FR-6337: a vaga é dita, e não quem concorria a ela."""
    from processo_seletivo.inscricoes.models import Inscricao

    itens = destinacoes_publicas(com_atos["edital"])
    assert itens
    corpo = pagina(client, com_atos)
    secao = corpo[corpo.index('class="destinacao-das-vagas"') :]
    secao = secao[: secao.index("</section>")]
    for inscricao in Inscricao.objects.filter(edital=com_atos["edital"]):
        assert inscricao.nome not in secao
        assert inscricao.protocolo not in secao
    for item in itens:
        assert not {"nome", "protocolo", "inscricao", "inscricaoId"} & set(item)


def test_o_seletor_diz_cada_ato_e_o_que_o_desfazimento_desfaz(com_atos):
    destinacao, desfazimento, declaracao = destinacoes_publicas(com_atos["edital"])

    assert destinacao["especie"] == DESTINACAO
    assert (destinacao["origem"], destinacao["destino"]) == (
        "Pretos, pardos e indígenas (PPI)",
        "ampla concorrência",
    )
    assert destinacao["quantidade"] == 1
    assert FRASE_DO_EDITAL in destinacao["fundamento"]

    assert desfazimento["especie"] == DESFAZIMENTO_DA_DESTINACAO
    assert desfazimento["desfaz"] is destinacao
    assert desfazimento["fundamento"] == MOTIVO_DO_DESFAZIMENTO

    assert declaracao["especie"] == NAO_PREENCHIDA
    assert (declaracao["origem"], declaracao["destino"]) == (
        "Pessoas com deficiência (PCD)",
        "não preenchida",
    )


def test_o_custo_nao_cresce_com_os_atos(certame):
    """Custo fixo (FR-6337): duas consultas sem ato, três com qualquer número deles."""
    edital = certame["edital"]
    with CaptureQueriesContext(connection) as vazio:
        assert destinacoes_publicas(edital) == []
    assert len(vazio.captured_queries) == 2

    versao = effective_version(edital_id=edital.id)
    agora = timezone.now()
    for dias in range(4):
        destinar(edital, versao, agora - timedelta(days=dias))
        declarar(edital, versao, agora - timedelta(days=dias, hours=1))
    with CaptureQueriesContext(connection) as cheio:
        assert len(destinacoes_publicas(edital)) == 8
    assert len(cheio.captured_queries) == 3


def test_as_anteriores_ficam_recolhidas(client, certame):
    edital = certame["edital"]
    versao = effective_version(edital_id=edital.id)
    agora = timezone.now()
    for dias in range(4):
        declarar(edital, versao, agora - timedelta(days=dias))

    corpo = pagina(client, certame)
    assert "Registros anteriores (1)" in corpo


def test_sem_ato_a_secao_nao_aparece(client, certame):
    assert "Destinação das vagas" not in pagina(client, certame)
