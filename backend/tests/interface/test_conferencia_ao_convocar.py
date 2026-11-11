"""A conferência antes de convocar os titulares (140, FR-4800 a FR-4818, SC-1500 a SC-1505).

No C10 dos cenários de treinamento da `134`, "Convocar as 3" praticou as três convocações e enviou
as três mensagens no clique, e a ajuda ao lado prometia uma conferência que só existia com
complemento digitado. O que estes casos prendem é o que o usuário exigiu: a prévia sem efeito
nenhum, a confirmação uma vez só, a recusa do que mudou, e a autorização de sempre.
"""

from datetime import timedelta

import pytest
from django.core import mail
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from processo_seletivo.auditoria.models import IdempotencyRecord, RegistroAuditoria
from processo_seletivo.convocacao.application import fluxo
from processo_seletivo.convocacao.application.comunicar import LINK_NA_CONFERENCIA
from processo_seletivo.convocacao.models import ComunicacaoEmitida, Convocacao
from processo_seletivo.publicacoes.domain.vocabulario_da_regra import FORMA_POR_PUBLICACAO
from tests.fixtures.convocacao import convocar, montar_cenario_da_convocacao
from tests.fixtures.corte import MARCO, regra
from tests.fixtures.edital import PROFILE_ID
from tests.interface.conftest import identificar
from tests.interface.test_convocacao_em_fluxo import (
    VENCIMENTO,
    abrir,
    campos_da_conferencia,
    conferir_titulares,
    postar_titulares,
    previa,
)

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


def _cenario(gestor, api_client, manager_headers, process_payload, **extra):
    """Duas vagas, dois titulares e uma suplente — o recorte do 77/2026."""
    return montar_cenario_da_convocacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="interface-140",
        geral=2,
        cut=regra(surplusCount=1),
        **extra,
    )


@pytest.fixture
def cenario_da_tela(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    return _cenario(gestor, api_client, manager_headers, process_payload)


def _url(edital):
    return reverse("interface:convocar-titulares", args=[edital.id, MARCO])


def _confirmar(client, edital, conferencia, **mudado):
    return client.post(
        _url(edital), {**campos_da_conferencia(conferencia), **mudado, "etapa": "confirmar"}
    )


def _fotografia(client):
    """Tudo o que a prévia não pode tocar (FR-4807)."""
    return {
        "convocacoes": Convocacao.objects.count(),
        "comunicacoes": ComunicacaoEmitida.objects.count(),
        "mensagens": len(mail.outbox),
        "trilha": RegistroAuditoria.objects.count(),
        "chaves": IdempotencyRecord.objects.count(),
        "sessao": dict(client.session.items()),
    }


# --- US1 · conferir antes de convocar -------------------------------------------------------------


def test_a_conferencia_nao_envia_nao_convoca_e_nao_grava_nada(
    client, seletor_ligado, cenario_da_tela
):
    """FR-4800, FR-4807, SC-1500: sem complemento, com e sem a etapa, nada acontece."""
    edital, _, _ = cenario_da_tela
    identificar(client, "carlos", ["gestor"])
    abrir(client, edital)
    antes = _fotografia(client)

    primeira = conferir_titulares(client, edital, previa(edital)["assinatura"])
    # Recarregar a conferência é pedi-la de novo; a etapa "conferir" é o botão de conferir de novo.
    conferir_titulares(client, edital, previa(edital)["assinatura"], etapa="conferir")

    assert primeira.status_code == 200
    assert "Confira antes de convocar" in primeira.content.decode()
    assert _fotografia(client) == antes
    assert antes["convocacoes"] == 0
    assert mail.outbox == []


def test_a_conferencia_diz_quem_o_texto_o_prazo_e_quem_fica_de_fora(
    client, seletor_ligado, cenario_da_tela
):
    """FR-4801 a FR-4806, UX-330, UX-331: as quatro perguntas, numa página só."""
    edital, _, _ = cenario_da_tela
    identificar(client, "carlos", ["gestor"])
    p = previa(edital)

    pagina = conferir_titulares(client, edital, p["assinatura"]).content.decode()

    for pessoa in p["pessoas"]:
        assert f"{pessoa['protocolo']} — {pessoa['nome']} · para vaga inicial" in pagina
    assert "Serão convocadas (2), para vaga inicial" in pagina
    assert "A espécie vem da posição na fila" in pagina
    assert p["fundamento"] in pagina
    assert "Assunto:" in pagina
    assert LINK_NA_CONFERENCIA in pagina
    assert "Prazo para atender: até" in pagina
    assert "informado neste ato" in pagina
    assert "Fica de fora (1)" in pagina
    assert f"{p['parada']['protocolo']} — {p['parada']['nome']}" in pagina
    assert "é suplente" in pagina
    assert "Convocar as 2 e enviar 2 mensagens" in pagina
    assert "Cancelar e voltar" in pagina
    assert 'class="consequencias irreversivel"' in pagina


def test_sem_vencimento_a_conferencia_diz_a_falta_e_o_que_a_mensagem_dira(
    client, seletor_ligado, cenario_da_tela
):
    """FR-4805: a falta do prazo dita, e o caminho para informá-lo."""
    edital, _, _ = cenario_da_tela
    identificar(client, "carlos", ["gestor"])

    pagina = conferir_titulares(
        client, edital, previa(edital)["assinatura"], vencimento=""
    ).content.decode()

    assert "Nenhum vencimento informado." in pagina
    assert "o prazo para atender é o que o Edital publica" in pagina
    assert "cancele, volte e informe-o" in pagina


def test_confirmada_a_conferencia_o_ato_acontece_como_hoje(client, seletor_ligado, cenario_da_tela):
    """US1, cenário 2: duas convocações, duas mensagens, e a tela diz o que aconteceu."""
    edital, _, _ = cenario_da_tela
    identificar(client, "carlos", ["gestor"])

    resposta = postar_titulares(client, edital, previa(edital)["assinatura"])

    assert resposta.status_code == 302
    assert Convocacao.objects.count() == 2
    assert len(mail.outbox) == 2
    assert (
        "2 convocações praticadas num ato só" in client.get(resposta["Location"]).content.decode()
    )


def test_a_mensagem_conferida_e_a_que_sai(client, seletor_ligado, cenario_da_tela, gestor):
    """SC-1505, D-003: frase a frase, a mensagem da conferência é a enviada, exceto o link."""
    edital, _, _ = cenario_da_tela
    identificar(client, "carlos", ["gestor"])
    p = previa(edital)
    vencimento = timezone.make_aware(parse_datetime(VENCIMENTO))
    conferencia = fluxo.conferencia_dos_titulares(
        actor=None,
        edital=edital,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        lista_id=None,
        alcance_confirmado=p["assinatura"],
        vencimento=vencimento,
    )

    postar_titulares(client, edital, p["assinatura"])

    (mensagem,) = conferencia["mensagens"]
    assert sorted(mensagem["inscricoes"]) == sorted(str(pessoa["id"]) for pessoa in p["pessoas"])
    for enviada in mail.outbox:
        link = next(linha for linha in enviada.body.splitlines() if "/convocacao" in linha)
        assert enviada.subject == mensagem["assunto"]
        assert enviada.body.replace(link.strip(), LINK_NA_CONFERENCIA) == mensagem["corpo"]


def test_cancelar_volta_a_tela_do_mesmo_recorte(client, seletor_ligado, cenario_da_tela):
    """FR-4815, US1 cenário 3."""
    edital, _, _ = cenario_da_tela
    identificar(client, "carlos", ["gestor"])

    pagina = conferir_titulares(client, edital, previa(edital)["assinatura"]).content.decode()

    volta = reverse("interface:convocacao", args=[edital.id, MARCO])
    assert f'<a href="{volta}" class="acao">Cancelar e voltar</a>' in pagina


def test_por_publicacao_a_conferencia_nao_promete_envio(
    client, seletor_ligado, db, gestor, api_client, manager_headers, process_payload,
    raiz_de_arquivos,
):  # fmt: skip
    """FR-4804, US1 cenário 4: nenhuma mensagem, e o botão não fala em enviar."""
    edital, _, _ = _cenario(
        gestor, api_client, manager_headers, process_payload, forma=FORMA_POR_PUBLICACAO
    )
    identificar(client, "carlos", ["gestor"])

    pagina = conferir_titulares(client, edital, previa(edital)["assinatura"]).content.decode()

    assert "Nenhuma mensagem sai neste ato" in pagina
    assert "Assunto:" not in pagina
    assert "Convocar as 2</button>" in pagina
    assert "enviar 2 mensagens" not in pagina


# --- US2 · uma vez só, e só sobre o que foi conferido -----------------------------------------


def test_a_confirmacao_repetida_nao_duplica_nada(client, seletor_ligado, cenario_da_tela):
    """FR-4808, FR-4812, SC-1502, D-005: o duplo clique repete o resultado, e não o ato."""
    edital, _, _ = cenario_da_tela
    identificar(client, "carlos", ["gestor"])
    conferencia = conferir_titulares(client, edital, previa(edital)["assinatura"])

    primeira = _confirmar(client, edital, conferencia)
    segunda = _confirmar(client, edital, conferencia)

    assert primeira.status_code == segunda.status_code == 302
    assert Convocacao.objects.count() == 2
    assert ComunicacaoEmitida.objects.count() == 2
    assert len(mail.outbox) == 2
    # O que a segunda resposta diz é o desfecho do primeiro clique, e não uma recusa.
    assert "2 convocações praticadas num ato só" in client.get(segunda["Location"]).content.decode()


def test_a_confirmacao_carrega_a_chave_e_o_alcance_da_tela(client, seletor_ligado, cenario_da_tela):
    """FR-4808: a conferência devolve, intactos, a chave e a assinatura que a tela emitiu."""
    edital, _, _ = cenario_da_tela
    identificar(client, "carlos", ["gestor"])
    p = previa(edital)

    campos = campos_da_conferencia(conferir_titulares(client, edital, p["assinatura"]))

    assert campos["chave"] == "tela-titulares"
    assert campos["alcance"] == p["assinatura"]
    assert campos["texto_conferido"]


def test_o_alcance_que_mudou_depois_da_conferencia_recusa_com_a_razao(
    client, seletor_ligado, cenario_da_tela, gestor
):
    """FR-4810, SC-1503, US2 cenário 2: nada praticado sobre o estado novo."""
    edital, _, _ = cenario_da_tela
    identificar(client, "carlos", ["gestor"])
    conferencia = conferir_titulares(client, edital, previa(edital)["assinatura"])
    convocar(edital, gestor, previa(edital)["pessoas"][0]["id"], idempotency_key="no-meio")
    convocacoes, mensagens = Convocacao.objects.count(), len(mail.outbox)

    resposta = _confirmar(client, edital, conferencia)
    pagina = resposta.content.decode()

    assert resposta.status_code == 200
    assert "Não é possível convocar agora" in pagina
    assert "mudou desde que a tela foi aberta" in pagina
    assert 'name="texto_conferido"' not in pagina
    assert "Voltar à convocação" in pagina
    assert (Convocacao.objects.count(), len(mail.outbox)) == (convocacoes, mensagens)


def test_o_texto_que_mudou_volta_a_conferencia_sem_ato(client, seletor_ligado, cenario_da_tela):
    """FR-4809, FR-4814, US2 cenário 3: o resumo não confere, e a conferência volta com o novo."""
    edital, _, _ = cenario_da_tela
    identificar(client, "carlos", ["gestor"])
    conferencia = conferir_titulares(client, edital, previa(edital)["assinatura"])

    pagina = _confirmar(client, edital, conferencia, complemento="Item 8.2.").content.decode()

    assert Convocacao.objects.count() == 0
    assert mail.outbox == []
    assert "O texto mudou desde a prévia" in pagina
    assert "Complemento: Item 8.2." in pagina


def test_confirmar_sem_o_resumo_abre_a_conferencia(client, seletor_ligado, cenario_da_tela):
    """FR-4800: o formulário antigo, ou forjado, com "confirmar" e sem resumo, nunca pratica."""
    edital, _, _ = cenario_da_tela
    identificar(client, "carlos", ["gestor"])

    resposta = conferir_titulares(client, edital, previa(edital)["assinatura"], etapa="confirmar")

    assert resposta.status_code == 200
    assert "Confira antes de convocar" in resposta.content.decode()
    assert Convocacao.objects.count() == 0
    assert mail.outbox == []


def test_vencimento_no_passado_recusa_antes_do_botao(client, seletor_ligado, cenario_da_tela):
    """FR-4811: a recusa do comando, dita na conferência, e nenhum botão de confirmar."""
    edital, _, _ = cenario_da_tela
    identificar(client, "carlos", ["gestor"])
    passado = (timezone.localtime() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M")

    pagina = conferir_titulares(
        client, edital, previa(edital)["assinatura"], vencimento=passado
    ).content.decode()

    assert "O vencimento informado já passou" in pagina
    assert 'name="texto_conferido"' not in pagina
    assert Convocacao.objects.count() == 0


def test_sem_titular_a_chamar_a_conferencia_recusa(client, seletor_ligado, cenario_da_tela, gestor):
    """FR-4811, UX-332: depois do gesto, a conferência de novo diz por que não há o que fazer."""
    edital, _, _ = cenario_da_tela
    identificar(client, "carlos", ["gestor"])
    postar_titulares(client, edital, previa(edital)["assinatura"])

    pagina = conferir_titulares(client, edital, previa(edital)["assinatura"]).content.decode()

    assert "Não há titular ainda não chamado neste recorte." in pagina
    assert "Voltar à convocação" in pagina
    assert 'name="texto_conferido"' not in pagina


@pytest.mark.parametrize(("subject", "papeis"), [("auditora", ["auditor"]), ("x", ["elaborador"])])
def test_quem_nao_pode_convocar_continua_recusado(
    client, seletor_ligado, cenario_da_tela, subject, papeis
):
    """FR-4813, SC-1504: a mesma porta do gesto, na conferência e na confirmação."""
    edital, _, _ = cenario_da_tela
    identificar(client, subject, papeis)
    p = previa(edital)

    conferencia = conferir_titulares(client, edital, p["assinatura"])
    confirmacao = conferir_titulares(
        client, edital, p["assinatura"], etapa="confirmar", texto_conferido="qualquer"
    )

    assert conferencia.status_code == confirmacao.status_code == 403
    assert "Confira antes de convocar" not in conferencia.content.decode()
    assert Convocacao.objects.count() == 0
    assert mail.outbox == []


# --- US3 · a ajuda diz o que acontece -------------------------------------------------------------


def test_o_botao_da_tela_leva_a_conferencia_e_a_ajuda_nao_promete_o_que_nao_ha(
    client, seletor_ligado, cenario_da_tela
):
    """FR-4816: o botão diz que confere, e a ajuda antiga, condicional, saiu."""
    edital, _, _ = cenario_da_tela
    identificar(client, "carlos", ["gestor"])

    pagina = abrir(client, edital)

    assert "Conferir antes de convocar as 2" in pagina
    assert "Nada é praticado nem enviado antes de você confirmar nela." in pagina
    assert "antes de confirmar, você o verá como o candidato" not in pagina
