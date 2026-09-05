"""A ocorrência alcançada pela presidência na interface administrativa (D-1).

Capacidade que o domínio sustenta e nenhuma interface alcança não está entregue (Princípio VI), e
o comando interno sozinho seria exatamente isso. O que este arquivo prova é o caminho inteiro: a
tela é alcançável a partir da Etapa, ela lista quem ainda não tem Resultado, ela **não grava sem
confirmação**, e o Resultado aparece na consulta com a origem dita.
"""

import pytest
from django.urls import reverse

from processo_seletivo.resultados.models import ResultadoEtapa
from tests.fixtures.comissao import inscrever
from tests.fixtures.resultado import montar_etapa_de_leitura_unica
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db]

FALTOU = "não compareceu à Entrevista (item 6.3 do Edital)"


@pytest.fixture
def cenario(gestor, api_client, manager_headers):
    montado = montar_etapa_de_leitura_unica(
        gestor, api_client, manager_headers, seed=1700, codigo="1700"
    )
    montado["inscricoes"] = inscrever(montado["edital"], 2, primeiro=1)
    return montado


def pagina(cenario):
    return reverse(
        "interface:registrar-ocorrencia", args=[cenario["edital"].id, cenario["primeira"]]
    )


def test_a_distribuicao_leva_ate_a_ocorrencia(client, seletor_ligado, cenario):
    """O caminho existe **a partir de onde a presidência já está**, e não por URL decorada."""
    identificar(client, "maria", ["gestor"])
    resposta = client.get(
        reverse("interface:distribuicao", args=[cenario["edital"].id, cenario["primeira"]])
    )
    assert pagina(cenario) in resposta.content.decode()


def test_a_tela_lista_quem_ainda_nao_tem_resultado(client, seletor_ligado, cenario):
    """A oferta é mais larga que a da consolidação, de propósito.

    Ninguém aqui tem avaliação concluída — e é justamente quem falta à Etapa que esta tela existe
    para resolver.
    """
    identificar(client, "maria", ["gestor"])
    corpo = client.get(pagina(cenario)).content.decode()
    for inscricao in cenario["inscricoes"]:
        assert str(inscricao.id) in corpo


def test_o_primeiro_envio_revisa_e_nao_grava(client, seletor_ligado, cenario):
    """A confirmação declara o alcance antes do ato. Tirar alguém do Processo não é um clique."""
    identificar(client, "maria", ["gestor"])
    resposta = client.post(
        pagina(cenario),
        {"inscricao_id": [str(cenario["inscricoes"][0].id)], "motivo": FALTOU},
    )
    corpo = resposta.content.decode()
    assert "Confirme antes de registrar" in corpo
    assert FALTOU in corpo
    assert ResultadoEtapa.objects.count() == 0


def test_a_confirmacao_grava_e_o_resultado_aparece_na_consulta(client, seletor_ligado, cenario):
    identificar(client, "maria", ["gestor"])
    faltante = cenario["inscricoes"][0]
    resposta = client.post(
        pagina(cenario),
        {
            "confirmar": "1",
            "inscricao_id": [str(faltante.id)],
            "motivo": FALTOU,
            "chave_idempotencia": "tela-1700",
        },
    )
    assert resposta.status_code == 302

    resultado = ResultadoEtapa.objects.get(inscricao=faltante)
    assert resultado.origem == ResultadoEtapa.Origem.OCORRENCIA
    assert resultado.consequencia == ResultadoEtapa.Consequencia.ELIMINADA

    corpo = client.get(
        reverse("interface:resultados-da-etapa", args=[cenario["edital"].id, cenario["primeira"]])
    ).content.decode()
    # A origem na tabela, e a ausência de quem avaliou dita por extenso: a coluna vazia faria
    # parecer dado que faltou, e ela é dado que não existe.
    assert "Ocorrência" in corpo
    assert "ninguém: não houve avaliação" in corpo
    assert FALTOU in corpo


def test_sem_motivo_a_tela_recusa_antes_de_confirmar(client, seletor_ligado, cenario):
    identificar(client, "maria", ["gestor"])
    resposta = client.post(
        pagina(cenario), {"inscricao_id": [str(cenario["inscricoes"][0].id)], "motivo": "   "}
    )
    assert "Descreva a ocorrência" in resposta.content.decode()
    assert ResultadoEtapa.objects.count() == 0


def test_sem_selecao_a_tela_recusa_antes_de_confirmar(client, seletor_ligado, cenario):
    identificar(client, "maria", ["gestor"])
    resposta = client.post(pagina(cenario), {"motivo": FALTOU})
    assert "Selecione ao menos uma inscrição" in resposta.content.decode()
    assert ResultadoEtapa.objects.count() == 0
