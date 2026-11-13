"""A marca da proposta, o caminho de volta e a versão-base na tela Retificar (123, M2 e M3).

Pelo cliente HTTP, sobre o Edital da auditoria de UX de 05/11/2026 (`edital_da_auditoria`). O que se
afirma é o que o **servidor** entrega: quais cartões saem «na proposta», a referência opaca de cada
linha do resumo, os sinais da barra no formulário e a frase da base em cada situação de vigência. O
que o script faz com isso — as duas frases da barra, a busca, o foco — é dos testes de JavaScript e
da jornada no navegador.
"""

import re
from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.interface import versao_base
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.edital_da_auditoria import (
    formulario,
    referencia_do_campo,
    retificacao_devolvida,
    retificacao_futura,
    versao_mais_recente,
)
from tests.fixtures.publicacao import create_retification, retify
from tests.fixtures.snapshot import DOCUMENTO, PERFIL
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


def _abrir(client, edital):
    identificar(client, "ana.elaboradora", ["elaborador"])
    return client.get(reverse("interface:retificar", args=[edital.id])).content.decode()


def _conferir(client, edital, dados):
    identificar(client, "ana.elaboradora", ["elaborador"])
    resposta = client.post(reverse("interface:retificar", args=[edital.id]), dados)
    assert resposta.status_code == 200, resposta.content[:500]
    return resposta.content.decode()


def _na_proposta(html):
    return set(re.findall(r'<fieldset[^>]*id="cartao-([\w-]+)"[^>]*data-na-proposta', html))


def _formulario_aberto(html):
    return re.search(r'<form method="post"[^>]*id="formulario-da-retificacao"[^>]*>', html).group(0)


def _resumo(html):
    inicio = html.index('id="resumo-titulo"')
    return html[inicio : html.index("</table>", inicio)]


def _tres_alteracoes(versao):
    """O cenário D da auditoria: três campos em três seções."""
    termino = referencia_do_campo(versao, "Evento 1", "Término")
    localidade = referencia_do_campo(versao, "Perfil P3", "Localidade")
    secao = referencia_do_campo(versao, "Seção Prazo de validade", "Texto da seção")
    dados = formulario(
        versao,
        **{termino: "2026-12-12T23:59", localidade: "Serra", secao: "Dois anos, prorrogáveis."},
    )
    return (
        dados,
        {termino.split("c")[0], localidade.split("c")[0], secao.split("c")[0]},
        (
            termino,
            localidade,
            secao,
        ),
    )


# ── M2: a proposta ─────────────────────────────────────────────────────────────────────────────


def test_a_conferencia_marca_os_cartoes_da_proposta(client, seletor_ligado, edital_da_auditoria):
    versao = versao_mais_recente(edital_da_auditoria)
    dados, cartoes, campos = _tres_alteracoes(versao)

    html = _conferir(client, edital_da_auditoria, dados)

    assert _na_proposta(html) == cartoes
    aberto = _formulario_aberto(html)
    assert 'data-proposta="conferida"' in aberto
    assert 'data-proposta-cartoes="3"' in aberto
    assert "data-enviado" in aberto
    assert "data-modo" not in aberto
    # Os atributos novos vêm depois do de sempre: há teste que afirma `action="…" data-conferido`.
    assert re.search(r'action="[^"]+" data-conferido data-enviado', aberto)
    resumo = _resumo(html)
    for campo in campos:
        assert f'href="#c-{campo}"' in resumo
    assert "Vigente hoje" not in html
    assert '<th scope="col">Na versão-base</th>' in resumo


def test_o_html_continua_sem_caminho_normativo(client, seletor_ligado, edital_da_auditoria):
    versao = versao_mais_recente(edital_da_auditoria)
    dados, _, _ = _tres_alteracoes(versao)
    html = _conferir(client, edital_da_auditoria, dados)
    assert "/profiles/id=" not in html
    assert "/schedule/id=" not in html


def test_antes_de_conferir_a_proposta_nao_foi_conferida(
    client, seletor_ligado, edital_da_auditoria
):
    html = _abrir(client, edital_da_auditoria)
    aberto = _formulario_aberto(html)
    assert 'data-proposta="nao-conferida"' in aberto
    assert "data-enviado" not in aberto
    assert _na_proposta(html) == set()


def test_a_remocao_marcada_entra_na_proposta_e_leva_ao_cartao(
    client, seletor_ligado, edital_da_auditoria
):
    versao = versao_mais_recente(edital_da_auditoria)
    documento = referencia_do_campo(versao, "Documento 3", "Nome").split("c")[0]
    html = _conferir(
        client, edital_da_auditoria, {**formulario(versao), f"remover:{documento}": "1"}
    )
    assert _na_proposta(html) == {documento}
    assert f'href="#cartao-{documento}"' in _resumo(html)


def test_a_linha_nova_entra_na_proposta_pelo_cartao_dela(
    client, seletor_ligado, edital_da_auditoria
):
    versao = versao_mais_recente(edital_da_auditoria)
    novo = {
        "novo-evento-0-type": "Resultado",
        "novo-evento-0-description": "Resultado final",
        "novo-evento-0-startAt": "2026-12-20T10:00",
    }
    html = _conferir(client, edital_da_auditoria, {**formulario(versao), **novo})
    assert re.search(r'<fieldset[^>]*id="cartao-novo-evento-0"[^>]*data-na-proposta', html)
    assert 'href="#cartao-novo-evento-0"' in _resumo(html)
    assert _na_proposta(html) == {"novo-evento-0"}


def test_a_linha_do_quadro_acrescentada_nao_marca_o_perfil(
    client, seletor_ligado, edital_da_auditoria
):
    versao = versao_mais_recente(edital_da_auditoria)
    novo = {
        "novo-linha-do-quadro-0-profileId": PERFIL["B"],
        "novo-linha-do-quadro-0-modalityId": "",
        "novo-linha-do-quadro-0-immediateVacancies": "1",
    }
    html = _conferir(client, edital_da_auditoria, {**formulario(versao), **novo})
    perfil = referencia_do_campo(versao, "Perfil P2", "Localidade").split("c")[0]
    assert perfil not in _na_proposta(html)


def test_a_conferencia_recusada_nao_marca_nada(client, seletor_ligado, edital_da_auditoria):
    versao = versao_mais_recente(edital_da_auditoria)
    vagas = referencia_do_campo(versao, "Perfil P1", "Vagas imediatas")
    html = _conferir(client, edital_da_auditoria, formulario(versao, **{vagas: "três"}))
    assert 'data-proposta="recusada"' in _formulario_aberto(html)
    assert _na_proposta(html) == set()


def test_a_edicao_abre_com_o_que_o_ato_ja_contem(
    client, seletor_ligado, edital_da_auditoria, api_client
):
    devolvida = retificacao_devolvida(
        api_client,
        edital_da_auditoria,
        [
            {
                "targetPath": f"/profiles/id={PERFIL['C']}/locality",
                "operation": "REPLACE",
                "newValue": "Serra",
            },
            {
                "targetPath": f"/profiles/id={PERFIL['B']}/workload",
                "operation": "REPLACE",
                "newValue": "40 horas semanais",
            },
            {"targetPath": f"/documentRequirements/id={DOCUMENTO['C']}", "operation": "REMOVE"},
        ],
    )
    identificar(client, "ana.elaboradora", ["elaborador"])
    html = client.get(reverse("interface:retificacao-editar", args=[devolvida.id])).content.decode()

    aberto = _formulario_aberto(html)
    assert 'data-modo="edicao"' in aberto
    assert 'data-proposta="conferida"' in aberto
    assert 'data-proposta-cartoes="2"' in aberto
    assert 'data-proposta-remocoes="1"' in aberto
    assert "data-enviado" not in aberto
    assert len(_na_proposta(html)) == 2
    assert html.count('name="desfazer-remocao"') == 1


# ── M3: a versão-base ──────────────────────────────────────────────────────────────────────────


def test_a_base_que_vigora_diz_desde_quando(client, seletor_ligado, edital_da_auditoria):
    html = _abrir(client, edital_da_auditoria)
    assert "A versão-base é a Publicação original de" in html
    assert "Ela vigora desde" in html
    assert "Abaixo está o conteúdo da versão-base do Edital." in html
    assert "conteúdo <em>vigente</em>" not in html


def test_a_base_de_vigencia_futura_nao_e_chamada_de_vigente(
    client, seletor_ligado, edital_da_auditoria, api_client
):
    retificacao_futura(api_client, edital_da_auditoria)
    versao = versao_mais_recente(edital_da_auditoria)
    html = _abrir(client, edital_da_auditoria)
    assert "A versão-base reúne a Publicação original de" in html
    assert "e a Retificação nº 2 (" in html
    assert "Ela ainda não vigora: passa a vigorar em" in html
    assert "Vigente hoje" not in html
    # A base da composição não mudou: a de maior início de vigência, mesmo futura (FR-3936).
    ultima = VersaoConsolidada.objects.filter(edital=edital_da_auditoria).order_by(
        "-valid_from", "-materialized_at"
    )[0]
    assert ultima.pk == versao.pk
    assert f'name="base" value="{ultima.id}"' in html


def test_as_telas_do_antes_dizem_a_base_da_retificacao(
    client, seletor_ligado, edital_da_auditoria, api_client
):
    retificacao_futura(api_client, edital_da_auditoria)
    perfil_c = f"/profiles/id={PERFIL['C']}/workload"
    item = create_retification(
        api_client,
        edital_da_auditoria,
        [{"targetPath": perfil_c, "operation": "REPLACE", "newValue": "30 horas semanais"}],
        suffix="sobre-a-futura",
    )
    identificar(client, "bruno.gestor", ["gestor"])
    telas = [
        client.get(reverse("interface:retificacao-detalhe", args=[item.id])),
        *(
            client.get(reverse("interface:retificacao-ato", args=[item.id, acao]))
            for acao in ("homologar", "devolver", "publicar")
        ),
    ]
    for tela in telas:
        corpo = tela.content.decode()
        assert "«Antes» é o conteúdo da versão-base desta Retificação." in corpo, tela
        assert "Ela ainda não vigora: passa a vigorar em" in corpo
        assert "Vigente hoje" not in corpo


def test_a_base_sucedida_diz_que_ja_nao_vigora(
    client, seletor_ligado, edital_da_auditoria, api_client
):
    rascunho = retificacao_devolvida(
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
    # Outra Retificação publica e passa a vigorar: a base do rascunho fica para trás.
    retify(
        api_client,
        edital_da_auditoria,
        [
            {
                "targetPath": f"/profiles/id={PERFIL['B']}/workload",
                "operation": "REPLACE",
                "newValue": "40 horas semanais",
            }
        ],
        suffix="sucessora",
    )
    identificar(client, "ana.elaboradora", ["elaborador"])
    destino = reverse("interface:retificacao-editar", args=[rascunho.id])
    html = client.get(destino).content.decode()
    assert "e já não é a versão em vigor" in html

    # A edição compara com o rascunho: a coluna do resumo diz «No rascunho».
    rascunho.refresh_from_db()
    localidade = re.search(r'name="campo:(g\d+c\d+)"[^>]*value="Serra"', html).group(1)
    dados = {
        "base": str(rascunho.base_snapshot_id),
        "revisao": str(rascunho.revision),
        "chave_idempotencia": "ui-teste-edicao",
        f"campo:{localidade}": "Cariacica",
    }
    conferido = client.post(destino, dados).content.decode()
    assert '<th scope="col">No rascunho</th>' in conferido
    assert "data-enviado" in _formulario_aberto(conferido)


def test_vigencia_exatamente_agora_vigora(edital_da_auditoria):
    versao = versao_mais_recente(edital_da_auditoria)
    assert versao_base.descrever_versao_base(versao, agora=versao.valid_from).situacao == (
        versao_base.VIGORA
    )
    antes = versao.valid_from - timedelta(seconds=1)
    assert versao_base.descrever_versao_base(versao, agora=antes).situacao == versao_base.FUTURA


def test_a_rematerializada_de_inicio_futuro_e_sucedida(edital_da_auditoria, api_client):
    """Uma publicação fora de ordem refaz as versões futuras: a antiga nunca vai vigorar."""
    retificacao_futura(api_client, edital_da_auditoria, dias=20, suffix="futura-1")
    antiga = versao_mais_recente(edital_da_auditoria)
    retify(
        api_client,
        edital_da_auditoria,
        [
            {
                "targetPath": f"/profiles/id={PERFIL['B']}/workload",
                "operation": "REPLACE",
                "newValue": "40 horas semanais",
            }
        ],
        suffix="imediata",
    )
    assert (
        VersaoConsolidada.objects.filter(
            edital=edital_da_auditoria, valid_from=antiga.valid_from
        ).count()
        == 2
    )
    agora = timezone.now()
    assert versao_base.descrever_versao_base(antiga, agora=agora).situacao == versao_base.SUCEDIDA


def test_o_somente_leitura_fala_da_versao_base(client, seletor_ligado, edital_da_auditoria):
    identificar(client, "bruno.homologador", ["homologador", "publicador"])
    html = client.get(
        reverse("interface:retificar", args=[edital_da_auditoria.id])
    ).content.decode()
    assert "Somente leitura" in html
    assert "Conteúdo da versão-base" in html
    assert "Abaixo está o conteúdo da versão-base do Edital, como" in html
    assert "A versão-base é a Publicação original de" in html
