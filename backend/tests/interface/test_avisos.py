"""As telas dos avisos: o que se oferece, a quem, e o que a tela diz antes do clique (066).

**O botão é a última porta antes da caixa de entrada de centenas de pessoas.** Os casos prendem o
que a spec pôs ali para prevenir o engano: o número no rótulo (`UX-173`), a orientação do assunto
(`FR-1258`), o rodapé visível e fixo (`UX-176`), o aviso de que o envio não se desfaz, e nenhum
botão para publicação sucedida (`UX-174`).
"""

import pytest
from django.urls import reverse

from processo_seletivo.avisos.application.modelos import criar, garantir_modelos_iniciais
from processo_seletivo.avisos.domain import nomes
from processo_seletivo.avisos.models import Aviso
from tests.fixtures.avisos import PUBLICADORA, avisar_resultado
from tests.fixtures.divulgacao import montar_ato_publicavel, publicar_o_ato
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


@pytest.fixture(autouse=True)
def _seletor(seletor_ligado):
    """Sem o seletor de identidade, `/gestao/` devolve 503 antes de qualquer autorização."""


@pytest.fixture
def publicado(gestor, api_client, manager_headers, process_payload):
    cenario = montar_ato_publicavel(
        gestor, api_client, manager_headers, process_payload, pontuacoes=("90.0000", "70.0000")
    )
    cenario["publicacao"] = publicar_o_ato(cenario)
    return cenario


def _url_da_previa(cenario, natureza=nomes.PRELIMINAR):
    return (
        reverse(
            "interface:aviso-do-resultado",
            args=[cenario["edital"].id, cenario["publicacao"].marco_id],
        )
        + f"?natureza={natureza}"
    )


def test_o_historico_do_marco_oferece_avisar_a_quem_publica(client, publicado):
    identificar(client, "publicadora", ["publicador"])

    corpo = client.get(
        reverse(
            "interface:publicacoes-do-marco",
            args=[publicado["edital"].id, publicado["publicacao"].marco_id],
        )
    ).content.decode()

    assert "Avisar candidatos — resultado preliminar" in corpo
    assert "Nenhum aviso enviado sobre este marco." in corpo


def test_quem_so_audita_nao_ve_o_botao(client, publicado):
    identificar(client, "auditora", ["auditor"])

    corpo = client.get(
        reverse(
            "interface:publicacoes-do-marco",
            args=[publicado["edital"].id, publicado["publicacao"].marco_id],
        )
    ).content.decode()

    assert "Avisar candidatos — resultado" not in corpo


def test_a_previa_diz_o_numero_a_orientacao_o_rodape_e_a_irreversibilidade(client, publicado):
    garantir_modelos_iniciais()
    identificar(client, "publicadora", ["publicador"])

    resposta = client.get(_url_da_previa(publicado))
    corpo = resposta.content.decode()

    assert resposta.status_code == 200
    assert "Enviar a 2 pessoas" in corpo
    assert "não nomeie modalidade, lista ou procedimento de reserva de vagas" in corpo
    assert "Rodapé fixo" in corpo and "Este aviso não substitui a publicação." in corpo
    assert "O envio não se desfaz." in corpo
    assert "A mensagem, como sai para" in corpo, "a prévia com uma pessoa real da lista"
    assert (
        resposta["Cache-Control"].startswith("no-store") or "no-store" in resposta["Cache-Control"]
    )


def test_confirmar_pela_tela_leva_ao_historico(client, publicado):
    garantir_modelos_iniciais()
    identificar(client, "publicadora", ["publicador"])
    corpo = client.get(_url_da_previa(publicado)).content.decode()
    import re

    assinatura = re.search(r'name="assinatura" value="([^"]+)"', corpo).group(1)
    chave = re.search(r'name="chave" value="([^"]+)"', corpo).group(1)

    resposta = client.post(
        _url_da_previa(publicado),
        {
            "acao": "confirmar",
            "natureza": nomes.PRELIMINAR,
            "assinatura": assinatura,
            "chave": chave,
            "assunto": "Processo Seletivo Ifes — Nova publicação disponível",
            "corpo": "Olá, {nome_do_candidato}. Saiu o resultado: {area_do_candidato}",
        },
    )

    aviso = Aviso.objects.get()
    assert resposta.status_code == 302
    assert resposta["Location"] == reverse("interface:aviso", args=[aviso.id])
    historico = client.get(resposta["Location"]).content.decode()
    assert "Aviso confirmado para 2 pessoas" in historico
    assert "pendente" in historico
    visivel = re.sub(r"<style.*?</style>", " ", historico, flags=re.S).lower()
    for proibido in (r"\bentregue\b", r"\brecebida\b", r"\blida\b", "notificação oficial"):
        assert not re.search(proibido, visivel), proibido


def test_a_chave_desligada_explica_e_nao_oferece_formulario(client, publicado, settings):
    settings.AVISOS_AOS_CANDIDATOS = False
    identificar(client, "publicadora", ["publicador"])

    corpo = client.get(_url_da_previa(publicado)).content.decode()

    assert "O envio de avisos está desabilitado nesta instalação." in corpo
    assert 'value="confirmar"' not in corpo


def test_outra_unidade_e_inexistente(client, publicado):
    identificar(client, "de-fora", ["publicador"], escopo="campus")

    assert client.get(_url_da_previa(publicado)).status_code == 404


def test_o_historico_do_aviso_responde_e_isola_o_escopo(client, publicado):
    declarado = avisar_resultado(publicado["edital"], publicado["publicacao"].marco_id)
    url = reverse("interface:aviso", args=[declarado["aviso"]])

    identificar(client, "publicadora", ["publicador"])
    assert client.get(url).status_code == 200
    identificar(client, "de-fora", ["publicador"], escopo="campus")
    assert client.get(url).status_code == 404


def test_interromper_diz_que_o_aceito_nao_volta(client, publicado):
    declarado = avisar_resultado(publicado["edital"], publicado["publicacao"].marco_id)
    identificar(client, "publicadora", ["publicador"])

    corpo = client.get(
        reverse("interface:aviso-interromper", args=[declarado["aviso"]])
    ).content.decode()

    assert "não pode" in corpo and "ser recuperada" in corpo
    assert "A interrupção não recolhe nada." in corpo


def test_os_modelos_iniciais_aparecem_e_a_presidencia_nao_os_administra(client, publicado):
    garantir_modelos_iniciais()

    identificar(client, "publicadora", ["publicador"])
    corpo = client.get(reverse("interface:modelos-de-aviso")).content.decode()
    for nome in ("Divulgação de resultado", "Publicação retificadora", "Nova chamada publicada"):
        assert nome in corpo

    identificar(client, "elaboradora", ["elaborador"])
    assert client.get(reverse("interface:modelos-de-aviso")).status_code == 404


def test_o_modelo_com_variavel_sensivel_e_recusado_na_tela(client):
    identificar(client, "publicadora", ["publicador"])

    resposta = client.post(
        reverse("interface:modelo-de-aviso-novo"),
        {"nome": "Ruim", "assunto": "Assunto", "corpo": "Sua posição é {posicao}."},
    )

    assert resposta.status_code == 422
    assert "{posicao}" in resposta.content.decode()


def test_criar_e_inativar_pela_tela(client):
    identificar(client, "publicadora", ["publicador"])
    modelo = criar(actor=PUBLICADORA, nome="Meu modelo", assunto="Assunto", corpo="Texto.")

    resposta = client.post(
        reverse("interface:modelo-de-aviso-situacao", args=[modelo.id]), {"ativo": "0"}
    )

    assert resposta.status_code == 302
    modelo.refresh_from_db()
    assert not modelo.ativo


def test_o_historico_mostra_o_indeterminado_e_o_caminho_do_reenvio(client, publicado, settings):
    from processo_seletivo.avisos.application.despacho import despachar
    from tests.fixtures import correio

    declarado = avisar_resultado(publicado["edital"], publicado["publicacao"].marco_id)
    correio.usar(settings, correio.aceita_e_derruba())
    despachar()
    identificar(client, "publicadora", ["publicador"])

    corpo = client.get(reverse("interface:aviso", args=[declarado["aviso"]])).content.decode()

    assert "resultado indeterminado" in corpo
    assert "O sistema nunca a reenvia sozinho." in corpo
    assert "Reenviar, com justificativa" in corpo


def test_o_alerta_de_despacho_parado_aparece_depois_do_limite(
    client, publicado, settings, monkeypatch
):
    from datetime import timedelta

    from django.utils import timezone

    declarado = avisar_resultado(publicado["edital"], publicado["publicacao"].marco_id)
    identificar(client, "publicadora", ["publicador"])
    url = reverse("interface:aviso", args=[declarado["aviso"]])

    assert "O despacho pode não estar processando." not in client.get(url).content.decode()

    real = timezone.now
    monkeypatch.setattr(
        timezone,
        "now",
        lambda: real() + timedelta(minutes=settings.AVISOS_ALERTA_DE_PENDENTE_MIN + 1),
    )
    assert "O despacho pode não estar processando." in client.get(url).content.decode()


def test_o_reenvio_de_falhas_mostra_o_texto_do_anterior_sem_edicao(client, publicado, settings):
    from processo_seletivo.avisos.application.despacho import despachar
    from tests.fixtures import correio

    declarado = avisar_resultado(publicado["edital"], publicado["publicacao"].marco_id)
    correio.usar(settings, correio.recusa(550), correio.recusa(550))
    despachar()
    identificar(client, "publicadora", ["publicador"])

    corpo = client.get(
        reverse("interface:aviso-reenviar", args=[declarado["aviso"]])
        + f"?motivo={nomes.REENVIO_DE_FALHAS}"
    ).content.decode()

    assert "O texto, o mesmo do aviso anterior" in corpo
    assert 'name="corpo"' not in corpo
    assert "Enviar a 2 pessoas" in corpo
