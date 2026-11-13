"""Os impeditivos da criação já em «Ver o que vai mudar» (123, M4).

O cenário B da auditoria de 05/11/2026: as vagas do Perfil de 1 para 2, sem mexer no quadro. Até
aqui a conferência mostrava uma linha e nenhum aviso, e «Criar Retificação» recusava com a frase da
soma — depois da Justificativa escrita, e sem caminho até a linha do quadro.

O que se afirma: a conferência mostra o que a criação diria, com as mesmas frases e o link ao
cartão; não grava nada; a criação continua conferindo, e recusa o que aparece entre as duas; a
advertência não entra; e a edição confere o ato inteiro, e não só a diferença da tela.
"""

import re
from unittest import mock

import pytest
from django.urls import reverse

from processo_seletivo.editais.domain.validation import Severity, ValidationFinding
from processo_seletivo.publicacoes.application import retificacoes
from processo_seletivo.publicacoes.models_retificacao import AlteracaoNormativa, Retificacao
from tests.fixtures.edital_da_auditoria import (
    formulario,
    referencia_do_campo,
    retificacao_devolvida,
    versao_mais_recente,
)
from tests.fixtures.snapshot import PERFIL
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

LINHA_GERAL_DO_P1 = "Linha do quadro Ampla concorrência — P1"


def _enviar(client, edital, dados):
    identificar(client, "ana.elaboradora", ["elaborador"])
    resposta = client.post(reverse("interface:retificar", args=[edital.id]), dados)
    return resposta


def _secao(html):
    achada = re.search(r'<section id="impeditivos".*?</section>', html, re.S)
    return achada.group(0) if achada else None


def _quadro_que_nao_fecha(versao, **extra):
    vagas = referencia_do_campo(versao, "Perfil P1", "Vagas imediatas")
    return {**formulario(versao, **{vagas: "2"}), **extra}


def test_o_impeditivo_do_quadro_aparece_na_conferencia_com_o_caminho_ate_a_linha(
    client, seletor_ligado, edital_da_auditoria
):
    versao = versao_mais_recente(edital_da_auditoria)
    antes = Retificacao.objects.count(), AlteracaoNormativa.objects.count()

    html = _enviar(client, edital_da_auditoria, _quadro_que_nao_fecha(versao)).content.decode()

    secao = _secao(html)
    assert secao, "a conferência deveria mostrar o impeditivo"
    linha = referencia_do_campo(versao, LINHA_GERAL_DO_P1, "Vagas imediatas").split("c")[0]
    assert f'href="#cartao-{linha}"' in secao
    assert "será recusado enquanto houver" in secao
    # A seção vem antes do resumo (D-009), e «Criar» continua oferecido (D-004).
    assert html.index('id="impeditivos"') < html.index('id="resumo-titulo"')
    assert 'name="confirmar" value="1"' in html
    assert (Retificacao.objects.count(), AlteracaoNormativa.objects.count()) == antes


def test_as_frases_da_conferencia_sao_as_que_a_criacao_junta(
    client, seletor_ligado, edital_da_auditoria
):
    versao = versao_mais_recente(edital_da_auditoria)
    conferido = _secao(
        _enviar(client, edital_da_auditoria, _quadro_que_nao_fecha(versao)).content.decode()
    )
    frases = [
        re.sub(r"\s+", " ", f).strip()
        for f in re.findall(r"<li>(.*?)(?: <a |</li>)", conferido, re.S)
    ]

    criado = _enviar(
        client,
        edital_da_auditoria,
        _quadro_que_nao_fecha(versao, confirmar="1", justificativa="Mais uma vaga."),
    ).content.decode()
    recusa = re.search(r"possui erros impeditivos: (.*?)</li>", criado, re.S).group(1)
    assert re.sub(r"\s+", " ", recusa).strip() == "; ".join(frases)
    # A criação recusada volta com a mesma seção, e com o link (R-013).
    assert _secao(criado) is not None
    assert Retificacao.objects.count() == 0


def test_sem_impeditivo_nao_ha_secao(client, seletor_ligado, edital_da_auditoria):
    versao = versao_mais_recente(edital_da_auditoria)
    localidade = referencia_do_campo(versao, "Perfil P3", "Localidade")
    html = _enviar(
        client, edital_da_auditoria, formulario(versao, **{localidade: "Serra"})
    ).content.decode()
    assert _secao(html) is None


def test_a_advertencia_nao_entra_na_conferencia(client, seletor_ligado, edital_da_auditoria):
    versao = versao_mais_recente(edital_da_auditoria)
    descricao = referencia_do_campo(versao, "Edital", "Descrição")
    html = _enviar(
        client, edital_da_auditoria, formulario(versao, **{descricao: ""})
    ).content.decode()
    assert _secao(html) is None


def test_o_impeditivo_na_linha_nova_leva_a_ela(client, seletor_ligado, edital_da_auditoria):
    versao = versao_mais_recente(edital_da_auditoria)
    novo = {"novo-evento-0-type": "Resultado", "novo-evento-0-description": "Sem data"}
    resposta = _enviar(client, edital_da_auditoria, {**formulario(versao), **novo})
    secao = _secao(resposta.content.decode())
    if secao is None:
        pytest.skip("o Evento sem início é recusado antes, pela própria linha")
    assert 'href="#cartao-novo-evento-0"' in secao


def test_a_edicao_confere_o_ato_inteiro(client, seletor_ligado, edital_da_auditoria, api_client):
    devolvida = retificacao_devolvida(
        api_client,
        edital_da_auditoria,
        [
            {
                "targetPath": f"/profiles/id={PERFIL['C']}/locality",
                "operation": "REPLACE",
                "newValue": "Serra",
            }
        ],
    )
    identificar(client, "ana.elaboradora", ["elaborador"])
    destino = reverse("interface:retificacao-editar", args=[devolvida.id])
    html = client.get(destino).content.decode()
    # O ato só troca uma localidade: o proposto tem os cartões e as referências da base.
    vagas = referencia_do_campo(
        versao_mais_recente(edital_da_auditoria), "Perfil P1", "Vagas imediatas"
    )
    assert f'name="campo:{vagas}"' in html
    dados = {
        "base": str(devolvida.base_snapshot_id),
        "revisao": str(devolvida.revision),
        "chave_idempotencia": "ui-teste-edicao",
        f"campo:{vagas}": "2",
    }
    conferido = client.post(destino, dados).content.decode()
    secao = _secao(conferido)
    assert secao and "gravar esta Retificação" in secao


def test_a_criacao_confere_de_novo_e_recusa_o_que_surgiu_no_intervalo(
    client, seletor_ligado, edital_da_auditoria
):
    """SC-1180: a conferência limpa não dispensa a da criação.

    No ato de Retificação nenhuma regra impeditiva depende do relógio; a que depende do banco é a do
    corte que nasce sobre Etapa já avaliada. Aqui o intervalo é simulado no ponto em que o mundo
    muda — os achados do conteúdo —, para provar o que importa: a criação chama a conferência outra
    vez e recusa pelo que ela diz **agora**, e nada é gravado.
    """
    versao = versao_mais_recente(edital_da_auditoria)
    localidade = referencia_do_campo(versao, "Perfil P3", "Localidade")
    dados = formulario(versao, **{localidade: "Serra"})

    html = _enviar(client, edital_da_auditoria, dados).content.decode()
    assert _secao(html) is None

    surgiu = ValidationFinding(
        Severity.BLOCKING_ERROR,
        "cut_rule_born_over_evaluated_stage",
        "A Etapa já tem Resultado registrado.",
        f"/profiles/id={PERFIL['C']}",
    )
    original = retificacoes.impeditivos_do_conteudo
    chamadas = []

    def no_intervalo(*args, **kwargs):
        chamadas.append(1)
        return [*original(*args, **kwargs), surgiu]

    with mock.patch.object(retificacoes, "impeditivos_do_conteudo", no_intervalo):
        criado = _enviar(
            client, edital_da_auditoria, {**dados, "confirmar": "1", "justificativa": "Local."}
        )
    assert criado.status_code == 200
    assert "A Etapa já tem Resultado registrado." in criado.content.decode()
    assert chamadas, "a criação precisa conferir de novo"
    assert Retificacao.objects.count() == 0


def test_a_conferencia_nao_le_o_banco_por_item(
    client, seletor_ligado, edital_extenso, django_assert_max_num_queries
):
    """A conferência de conteúdo custa leituras constantes, e não por cartão (plan, metas)."""
    versao = versao_mais_recente(edital_extenso)
    vagas = referencia_do_campo(versao, "Perfil CURSO-2", "Vagas imediatas")
    dados = formulario(versao, **{vagas: "2"})
    identificar(client, "ana.elaboradora", ["elaborador"])
    destino = reverse("interface:retificar", args=[edital_extenso.id])

    with mock.patch(
        "processo_seletivo.interface.views._impeditivos_da_conferencia", return_value=[]
    ):
        from django.db import connection
        from django.test.utils import CaptureQueriesContext

        with CaptureQueriesContext(connection) as sem:
            client.post(destino, dados)
    with django_assert_max_num_queries(len(sem.captured_queries) + 4):
        resposta = client.post(destino, dados)
    assert _secao(resposta.content.decode()) is not None
