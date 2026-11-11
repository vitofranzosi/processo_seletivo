"""A ficha do barema na Mesa, pelo canal HTTP real (146, T019, T020).

O que se prende é a tela: a ficha no lugar do campo único, uma linha por critério com a frase, a
máxima e a comprovação; o envio do formulário real até a conclusão; a recusa que nomeia o pendente
e devolve o digitado; a leitura da concluída; e as conclusões preservadas, cada uma com o barema da
versão que cita.
"""

import re
from decimal import Decimal

import pytest
from django.urls import reverse

from processo_seletivo.avaliacoes.application.avaliacao import reabrir
from processo_seletivo.avaliacoes.models import Avaliacao
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.barema import (
    concluir_com_ficha,
    criterio_de,
    ficha,
    montar_mesa_com_barema,
)
from tests.fixtures.comissao import inscrever
from tests.fixtures.mesa import distribuir_para
from tests.fixtures.publicacao import retify
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("raiz_de_arquivos")]

SEED = 147


@pytest.fixture
def cenario(gestor, api_client, manager_headers):
    return montar_mesa_com_barema(gestor, api_client, manager_headers, seed=SEED, codigo="M147")


@pytest.fixture
def inscricao(cenario, gestor):
    # Só os títulos: a declaração de docência não foi apresentada.
    inscrita = inscrever(cenario["edital"], 1, primeiro=4701, documentos=[cenario["titulos"]])[0]
    distribuir_para(cenario, gestor, ["joao"], [inscrita], chave="mesa-147")
    return inscrita


def pagina(cenario, inscricao):
    return reverse(
        "interface:mesa-inscricao", args=[cenario["edital"].id, cenario["etapa"], inscricao.id]
    )


def enviar(client, cenario, inscricao, valores, *, rota="concluir", revisao=1, parecer="Ok."):
    versao = VersaoConsolidada.objects.filter(edital=cenario["edital"]).latest("materialized_at")
    dados = {
        "expected_revision": revisao,
        "versao_reconhecida": versao.id,
        "parecer": parecer,
    }
    for indice, valor in enumerate(valores):
        dados[f"ficha-{criterio_de(indice, SEED)}-quantidade"] = "" if valor is None else valor
        dados[f"ficha-{criterio_de(indice, SEED)}-justificativa"] = ""
    return client.post(
        reverse(
            f"interface:mesa-avaliacao-{rota}",
            args=[cenario["edital"].id, cenario["etapa"], inscricao.id],
        ),
        dados,
    )


def test_a_ficha_substitui_o_campo_unico(client, seletor_ligado, cenario, inscricao):
    identificar(client, "joao", [])
    corpo = client.get(pagina(cenario, inscricao)).content.decode()

    assert 'id="pontuacao"' not in corpo
    assert "Barema" in corpo
    assert "Diploma de Doutorado" in corpo
    assert "5 pontos por certificado, até 10" in corpo
    assert "Lato sensu, na área da Educação." in corpo
    assert f'name="ficha-{criterio_de(0, SEED)}-quantidade"' in corpo
    assert f'name="ficha-{criterio_de(0, SEED)}-justificativa"' in corpo
    # A comprovação: o documento apresentado abre no painel; o não apresentado é dito.
    assert "Comprovação: Títulos acadêmicos" in corpo
    assert "Comprovação: Declaração de exercício de docência" in corpo
    assert "não apresentado" in corpo
    assert 'data-documento="Títulos acadêmicos"' in corpo
    assert "interface/mesa_barema.js" in corpo
    assert "interface/grupos/ficha-do-barema.css" in corpo
    # Nada respondido ainda: o total é o traço e os cinco são pendentes.
    assert corpo.count(">pendente<") == 5


def test_concluir_pelo_formulario(client, seletor_ligado, cenario, inscricao):
    identificar(client, "joao", [])

    resposta = enviar(client, cenario, inscricao, [1, 0, 3, 0, 52])

    assert resposta.status_code == 302
    avaliacao = Avaliacao.objects.get(inscricao_id=inscricao.id)
    assert avaliacao.estado == Avaliacao.Estado.CONCLUIDA
    assert avaliacao.pontuacao == Decimal("70.0000")

    corpo = client.get(pagina(cenario, inscricao)).content.decode()
    # A leitura da concluída: as parcelas, o limite em texto e o total.
    assert "limitada ao máximo" in corpo
    assert re.search(r"<strong>70</strong>\s*de 100", corpo)
    # Concluída é leitura: nenhum campo da ficha sobra na página.
    assert 'name="ficha-' not in corpo
    assert "interface/mesa_barema.js" not in corpo


def test_salvar_sem_concluir_aceita_o_pendente(client, seletor_ligado, cenario, inscricao):
    identificar(client, "joao", [])

    enviar(client, cenario, inscricao, [1, None, 3], rota="gravar")

    avaliacao = Avaliacao.objects.get(inscricao_id=inscricao.id)
    assert avaliacao.estado == Avaliacao.Estado.RASCUNHO
    assert avaliacao.pontuacao == Decimal("30.0000")
    corpo = client.get(pagina(cenario, inscricao)).content.decode()
    assert "Rascunho salvo." in corpo
    assert f'name="ficha-{criterio_de(0, SEED)}-quantidade" value="1"' in corpo
    assert "Pendentes: Diploma de Mestrado; Curso de formação de orientadores;" in corpo


def test_a_recusa_nomeia_o_pendente_e_devolve_o_digitado(
    client, seletor_ligado, cenario, inscricao
):
    identificar(client, "joao", [])

    enviar(client, cenario, inscricao, [1, None, 3, 0, 52])
    corpo = client.get(pagina(cenario, inscricao)).content.decode()

    assert "Pendentes: Diploma de Mestrado." in corpo
    assert 'role="alert"' in corpo
    # O digitado volta: a avaliadora não perde as outras linhas.
    assert f'name="ficha-{criterio_de(4, SEED)}-quantidade" value="52"' in corpo
    assert not Avaliacao.objects.filter(estado=Avaliacao.Estado.CONCLUIDA).exists()


def test_o_parecer_existente_e_preservado(client, seletor_ligado, cenario, inscricao):
    identificar(client, "joao", [])

    enviar(client, cenario, inscricao, [1, 0, 3, 0, 52], parecer="Títulos conferidos um a um.")

    assert Avaliacao.objects.get(inscricao_id=inscricao.id).parecer == (
        "Títulos conferidos um a um."
    )


def test_as_conclusoes_preservadas_leem_o_barema_de_cada_versao(
    client, seletor_ligado, api_client, cenario, inscricao, gestor
):
    """SC-1633: a Retificação renomeia um critério entre duas conclusões preservadas."""
    primeira = concluir_com_ficha(cenario, "joao", inscricao, ficha(SEED, 1, 0, 3, 0, 52))
    retify(
        api_client,
        cenario["edital"],
        [
            {
                "targetPath": (
                    f"/stages/id={cenario['etapa']}/criteria/id={criterio_de(0, SEED)}/name"
                ),
                "operation": "REPLACE",
                "newValue": "Título de Doutor",
            }
        ],
        suffix="n",
    )
    reaberta = reabrir(
        actor=gestor,
        processo_id=cenario["processo"].id,
        avaliacao_id=primeira.id,
        motivo="Retificado o nome do critério.",
        expected_revision=primeira.revision,
        idempotency_key="mesa-147-reabrir",
        correlation_id="teste",
    )
    concluir_com_ficha(
        cenario, "joao", inscricao, ficha(SEED, 1, 0, 2, 0, 52), revisao=reaberta.revision
    )

    identificar(client, "maria", [])
    corpo = client.get(
        reverse("interface:conclusoes-preservadas", args=[cenario["edital"].id, cenario["etapa"]])
    ).content.decode()

    assert "Diploma de Doutorado: 20 de 20" in corpo
    assert "Título de Doutor: 20 de 20" in corpo
    assert "Especialização: 10 de 10 (limitada ao máximo)" in corpo
    assert "interface/grupos/ficha-do-barema.css" in corpo


def test_a_mesa_sem_barema_continua_com_o_campo_unico(
    client, seletor_ligado, gestor, api_client, manager_headers
):
    """SC-1624: a Etapa sem barema mostra o campo de sempre, e nada da ficha."""
    from tests.fixtures.mesa import montar_cenario_da_presidencia

    sem = montar_cenario_da_presidencia(gestor, api_client, manager_headers, seed=148)
    identificar(client, "joao", [])

    corpo = client.get(
        reverse(
            "interface:mesa-inscricao",
            args=[sem["edital"].id, sem["etapa"], sem["inscricao"].id],
        )
    ).content.decode()

    assert 'id="pontuacao"' in corpo
    assert "data-ficha-do-barema" not in corpo
    assert 'class="tabela-da-ficha"' not in corpo
    assert "mesa_barema.js" not in corpo
