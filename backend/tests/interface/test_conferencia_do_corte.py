"""Conferir antes de emitir o corte, a sucessão e a faixa seguinte (152, história 4).

Cobre SC-1903 e SC-1904.

O corte era o único ato da cadeia ordem → corte → convocação gravado no primeiro clique (achado 08
do estudo de 11/11/2026). Agora "Conferir antes de emitir" abre "Confira antes de emitir o corte", e
só o botão dela emite. O que estes casos prendem é a conferência sem efeito, a emissão uma vez só,
a recusa do cálculo que mudou, e a autorização de sempre.
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.auditoria.models import IdempotencyRecord, RegistroAuditoria
from processo_seletivo.classificacao.models import Corte
from tests.interface.conftest import identificar
from tests.interface.test_corte import cliente_no_corte  # noqa: F401

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

CONFERENCIA = "Confira antes de emitir o corte"


def _campo(pagina, nome):
    return re.search(rf'name="{nome}" value="([^"]*)"', pagina).group(1)


def _tela(client, edital, marco):
    return client.get(reverse("interface:corte", args=[edital.id, marco])).content.decode()


def _conferir_o_corte(client, edital, marco, **extra):
    tela = _tela(client, edital, marco)
    dados = {
        "chave_idempotencia": _campo(tela, "chave_idempotencia"),
        "confirmacao_do_calculo": _campo(tela, "confirmacao_do_calculo"),
        **extra,
    }
    return client.post(reverse("interface:emitir-corte", args=[edital.id, marco]), dados)


def _confirmar(client, url, conferencia, **mudado):
    pagina = conferencia.content.decode()
    formulario = pagina.split('class="confirmar">', 1)[1].split("</form>", 1)[0]
    campos = dict(re.findall(r'<input type="hidden" name="([^"]+)" value="([^"]*)"', formulario))
    motivo = re.search(r'<textarea[^>]*name="motivo"[^>]*>(.*?)</textarea>', formulario, re.S)
    if motivo:
        campos["motivo"] = motivo.group(1)
    return client.post(url, {**campos, **mudado})


def _fotografia(client):
    """Tudo o que a conferência não pode tocar (FR-5830)."""
    return {
        "cortes": Corte.objects.count(),
        "trilha": RegistroAuditoria.objects.count(),
        "chaves": IdempotencyRecord.objects.count(),
        "sessao": dict(client.session.items()),
    }


def _emitir(client, edital, marco):
    conferencia = _conferir_o_corte(client, edital, marco)
    url = reverse("interface:emitir-corte", args=[edital.id, marco])
    return _confirmar(client, url, conferencia)


def test_a_conferencia_do_corte_nao_grava_nada(cliente_no_corte):  # noqa: F811
    """FR-5825, FR-5830, SC-1904: com a assinatura da tela, e sem `confirmar`, nada é emitido."""
    client, edital, marco = cliente_no_corte
    _tela(client, edital, marco)
    antes = _fotografia(client)

    resposta = _conferir_o_corte(client, edital, marco)

    assert resposta.status_code == 200
    assert CONFERENCIA in resposta.content.decode()
    assert _fotografia(client) == antes
    assert antes["cortes"] == 0


def test_a_conferencia_mostra_a_faixa_e_o_que_acontece_depois(cliente_no_corte):  # noqa: F811
    """FR-5826, FR-5827, UX-531: história 4, cenário 1."""
    client, edital, marco = cliente_no_corte

    pagina = _conferir_o_corte(client, edital, marco).content.decode()

    assert "Primeiro corte deste recorte." in pagina
    for rotulo in ("Alvo declarado", "Alvo apurado", "Suplentes", "Progridem", "Ficam fora"):
        assert rotulo in pagina
    assert re.search(r"<li>1º — ", pagina), "quem progride, com a posição"
    assert "O que acontece depois" in pagina
    assert "segue para a Etapa seguinte que o marco declara" in pagina
    assert '<button type="submit" class="botao perigoso">Emitir o corte</button>' in pagina
    assert "Cancelar e voltar" in pagina


def test_confirmada_a_emissao_acontece_uma_vez(cliente_no_corte):  # noqa: F811
    """FR-5831, FR-5832, SC-1903: história 4, cenário 2 — e o duplo clique não emite duas."""
    client, edital, marco = cliente_no_corte
    url = reverse("interface:emitir-corte", args=[edital.id, marco])
    conferencia = _conferir_o_corte(client, edital, marco)

    primeira = _confirmar(client, url, conferencia)
    segunda = _confirmar(client, url, conferencia)

    assert primeira.status_code == segunda.status_code == 302
    assert Corte.objects.count() == 1
    assert "Corte emitido" in client.get(primeira["Location"]).content.decode()


def test_o_corte_emitido_no_intervalo_recusa_a_confirmacao(cliente_no_corte, gestor):  # noqa: F811
    """FR-5831: história 4, cenário 3 — o cálculo mudou de verdade entre a conferência e o clique.

    Outra pessoa emite o corte com a conferência aberta: a geração vista não é mais a de agora, e
    o comando recusa a confirmação sem emitir.
    """
    from tests.fixtures.corte import emitir

    client, edital, marco = cliente_no_corte
    url = reverse("interface:emitir-corte", args=[edital.id, marco])
    conferencia = _conferir_o_corte(client, edital, marco)
    emitir(edital, gestor, chave="outra-pessoa-152")

    resposta = _confirmar(client, url, conferencia)

    assert resposta.status_code == 302
    assert Corte.objects.count() == 1, "só o da outra pessoa"
    pagina = client.get(resposta["Location"]).content.decode()
    assert "Outro corte foi emitido depois da sua leitura" in pagina


def test_a_tela_sem_geracao_aberta_depois_do_outro_corte_e_dita(
    cliente_no_corte,
    gestor,  # noqa: F811
):
    """Revisão do #502: a conferência pedida da tela de antes do primeiro corte não vira sucessão
    em silêncio — ela diz que outro corte foi emitido, com a frase do comando."""
    from tests.fixtures.corte import emitir

    client, edital, marco = cliente_no_corte
    tela = _tela(client, edital, marco)
    emitir(edital, gestor, chave="outra-pessoa-152b")

    pagina = client.post(
        reverse("interface:emitir-corte", args=[edital.id, marco]),
        {
            "chave_idempotencia": _campo(tela, "chave_idempotencia"),
            "confirmacao_do_calculo": _campo(tela, "confirmacao_do_calculo"),
        },
    ).content.decode()

    assert "Outro corte foi emitido depois da sua leitura" in pagina
    assert "O cálculo mudou desde que você abriu o corte." not in pagina
    assert "Sucessão da geração vigente." in pagina


def test_a_tela_antiga_e_dita_na_conferencia(cliente_no_corte):  # noqa: F811
    """A assinatura recomposta não esconde a mudança: a conferência diz que o cálculo mudou."""
    client, edital, marco = cliente_no_corte

    pagina = _conferir_o_corte(
        client, edital, marco, confirmacao_do_calculo="de-uma-tela-antiga"
    ).content.decode()

    assert "O cálculo mudou desde que você abriu o corte." in pagina


def test_a_sucessao_passa_pela_conferencia(cliente_no_corte):  # noqa: F811
    """FR-5825, FR-5826: na sucessão, o motivo e que a geração vigente continua legível; e só a
    confirmação nela emite a sucessora."""
    client, edital, marco = cliente_no_corte
    _emitir(client, edital, marco)
    url = reverse("interface:emitir-corte", args=[edital.id, marco])

    conferencia = _conferir_o_corte(client, edital, marco, motivo="Recurso deferido.")

    pagina = conferencia.content.decode()
    assert "Sucessão da geração vigente." in pagina
    assert "A geração vigente continua legível" in pagina
    assert re.search(r'name="motivo"[^>]*required[^>]*>Recurso deferido\.</textarea>', pagina)
    assert Corte.objects.count() == 1

    _confirmar(client, url, conferencia)

    sucessora = Corte.objects.exclude(corte_anterior=None).get()
    assert sucessora.motivo == "Recurso deferido."


def _conferir_a_faixa_seguinte(client, edital, marco, **dados):
    tela = _tela(client, edital, marco)
    url = reverse("interface:continuar-corte", args=[edital.id, marco])
    formulario = tela[tela.index("/corte/continuar") :]
    chave = _campo(formulario, "chave_idempotencia")
    return url, client.post(url, {"chave_idempotencia": chave, **dados})


def test_a_faixa_seguinte_passa_pela_conferencia(cliente_no_corte):  # noqa: F811
    """FR-5829, SC-1903, SC-1904: história 4, cenário 4."""
    client, edital, marco = cliente_no_corte
    _emitir(client, edital, marco)
    _tela(client, edital, marco)  # consome o resultado da emissão, que a sessão levava
    antes = _fotografia(client)

    url, conferencia = _conferir_a_faixa_seguinte(
        client, edital, marco, quantidade="1", motivo="Um indeferimento."
    )

    pagina = conferencia.content.decode()
    assert conferencia.status_code == 200
    assert "Faixa seguinte da geração vigente." in pagina
    assert "A faixa seguinte alcança 1 pessoa" in pagina
    assert "não revoga a faixa anterior" in pagina
    assert "Um indeferimento." in pagina
    assert '<button type="submit" class="botao perigoso">Emitir a faixa seguinte</button>' in pagina
    assert _fotografia(client) == antes

    _confirmar(client, url, conferencia)
    _confirmar(client, url, conferencia)

    assert Corte.objects.count() == 2


def test_a_faixa_seguinte_alem_do_resto_e_mostrada_sem_recusa(cliente_no_corte):  # noqa: F811
    """Caso-limite e T027: o comando aceita e alcança só quem resta (FR-5846); a conferência mostra
    a quantidade pedida ao lado de quantas a faixa alcança, antes do botão."""
    client, edital, marco = cliente_no_corte
    _emitir(client, edital, marco)

    _, conferencia = _conferir_a_faixa_seguinte(
        client, edital, marco, quantidade="99", motivo="Muitas desistências."
    )

    pagina = conferencia.content.decode()
    assert "Não é possível emitir agora" not in pagina
    assert "Pedida: 99." in pagina
    assert re.search(r"A faixa seguinte alcança \d+ (pessoa|pessoas)", pagina)
    assert "Emitir a faixa seguinte</button>" in pagina


def test_a_faixa_seguinte_sem_a_assinatura_nao_emite(cliente_no_corte):  # noqa: F811
    """FR-5831: a confirmação forjada, sem a conferência, é recusada como cálculo divergente."""
    client, edital, marco = cliente_no_corte
    _emitir(client, edital, marco)
    url, _ = _conferir_a_faixa_seguinte(client, edital, marco, quantidade="1", motivo="x")

    tela = _tela(client, edital, marco)
    chave = _campo(tela[tela.index("/corte/continuar") :], "chave_idempotencia")
    resposta = client.post(
        url, {"chave_idempotencia": chave, "quantidade": "1", "motivo": "x", "confirmar": "1"}
    )

    assert resposta.status_code == 302
    assert Corte.objects.count() == 1
    assert "A faixa mudou desde a sua leitura" in client.get(resposta["Location"]).content.decode()


def test_a_faixa_seguinte_que_o_comando_recusaria_e_recusada_antes_do_botao(
    cliente_no_corte,  # noqa: F811
):
    """FR-5829: sem motivo, a razão do comando, e nenhum botão de emitir."""
    client, edital, marco = cliente_no_corte
    _emitir(client, edital, marco)

    _, conferencia = _conferir_a_faixa_seguinte(client, edital, marco, quantidade="1")

    pagina = conferencia.content.decode()
    assert "Não é possível emitir agora" in pagina
    assert "Declare por que a faixa seguinte é necessária" in pagina
    assert "Emitir a faixa seguinte</button>" not in pagina


@pytest.mark.parametrize(("subject", "papeis"), [("auditora", ["auditor"]), ("x", ["elaborador"])])
def test_quem_nao_pode_emitir_continua_recusado(cliente_no_corte, subject, papeis):  # noqa: F811
    """FR-5833: a mesma porta de hoje, na conferência e na confirmação."""
    client, edital, marco = cliente_no_corte
    tela = _tela(client, edital, marco)
    identificar(client, subject, papeis)
    url = reverse("interface:emitir-corte", args=[edital.id, marco])
    dados = {
        "chave_idempotencia": _campo(tela, "chave_idempotencia"),
        "confirmacao_do_calculo": _campo(tela, "confirmacao_do_calculo"),
    }

    conferencia = client.post(url, dados)
    confirmacao = client.post(url, {**dados, "confirmar": "1"})

    assert conferencia.status_code == confirmacao.status_code == 403
    assert Corte.objects.count() == 0


def test_o_botao_da_tela_diz_que_leva_a_conferencia(cliente_no_corte):  # noqa: F811
    """UX-531: "Conferir antes de emitir", e a ajuda diz que nada é gravado antes."""
    client, edital, marco = cliente_no_corte

    tela = _tela(client, edital, marco)

    assert '<button type="submit" class="botao">Conferir antes de emitir</button>' in tela
    assert "Nada é gravado antes de você confirmar nela." in tela
