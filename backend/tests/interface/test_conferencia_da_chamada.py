"""Conferir antes de chamar uma pessoa (152, história 3, SC-1902, SC-1903, SC-1907, SC-1909).

A ordem e o lote dos titulares tinham "Confira antes"; a chamada individual da fila e a chamada
para regularizar eram praticadas no primeiro clique, e a mensagem saía junto (achado 08 do estudo de
11/11/2026). Agora as duas passam pela conferência do lote, com uma pessoa (D-004): o que estes
casos prendem é a prévia sem efeito, a confirmação uma vez só, a recusa antes do botão, e a
autorização de sempre.
"""

from datetime import timedelta

import pytest
from django.core import mail
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from processo_seletivo.auditoria.models import IdempotencyRecord, RegistroAuditoria
from processo_seletivo.convocacao.application import fluxo, selectors
from processo_seletivo.convocacao.application.comunicar import LINK_NA_CONFERENCIA
from processo_seletivo.convocacao.domain import nomes
from processo_seletivo.convocacao.models import ComunicacaoEmitida, Convocacao
from processo_seletivo.publicacoes.domain.vocabulario_da_regra import FORMA_POR_PUBLICACAO
from tests.fixtures.convocacao import convocar, montar_cenario_da_convocacao
from tests.fixtures.corte import MARCO, regra
from tests.fixtures.edital import PROFILE_ID
from tests.interface.conftest import identificar
from tests.interface.test_convocacao_em_fluxo import VENCIMENTO, campos_da_conferencia

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

CONFERENCIA = "Confira antes de convocar"


def _cenario(gestor, api_client, manager_headers, process_payload, **extra):
    """Duas vagas, dois titulares e uma suplente — o recorte do 77/2026."""
    return montar_cenario_da_convocacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="interface-152",
        geral=2,
        cut=regra(surplusCount=1),
        **extra,
    )


@pytest.fixture
def cenario_da_tela(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    return _cenario(gestor, api_client, manager_headers, process_payload)


def _url(edital):
    return reverse("interface:convocar", args=[edital.id, MARCO])


def _fila(edital):
    contexto = selectors.contexto_do_recorte(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )
    identidades = selectors.identidades_de(set(contexto["fila"]))
    return [identidades[i] for i in contexto["fila"]]


def _pedir(client, edital, inscricao, **extra):
    dados = {
        "inscricao": str(inscricao),
        "vencimento": VENCIMENTO,
        "chave": "chamada-152",
        **extra,
    }
    return client.post(_url(edital), dados)


def _confirmar(client, edital, conferencia, **mudado):
    return client.post(
        _url(edital), {**campos_da_conferencia(conferencia), **mudado, "etapa": "confirmar"}
    )


def _fotografia(client):
    """Tudo o que a conferência não pode tocar (FR-5815)."""
    return {
        "convocacoes": Convocacao.objects.count(),
        "comunicacoes": ComunicacaoEmitida.objects.count(),
        "mensagens": len(mail.outbox),
        "trilha": RegistroAuditoria.objects.count(),
        "chaves": IdempotencyRecord.objects.count(),
        "sessao": dict(client.session.items()),
    }


def test_a_conferencia_nao_convoca_nao_envia_e_nao_grava_nada(
    client, seletor_ligado, cenario_da_tela
):
    """FR-5810, FR-5815, SC-1902: com e sem complemento, com e sem a etapa de conferir."""
    edital, _, _ = cenario_da_tela
    identificar(client, "carlos", ["gestor"])
    proxima = _fila(edital)[0]
    antes = _fotografia(client)

    sem = _pedir(client, edital, proxima["id"])
    com = _pedir(client, edital, proxima["id"], complemento="Item 8.2.", etapa="conferir")
    # O formulário antigo que diz "confirmar" sem o resumo também só confere.
    forjado = _pedir(client, edital, proxima["id"], etapa="confirmar")

    for resposta in (sem, com, forjado):
        assert resposta.status_code == 200
        assert CONFERENCIA in resposta.content.decode()
    assert _fotografia(client) == antes
    assert antes["convocacoes"] == 0


def test_a_conferencia_diz_a_pessoa_a_especie_o_texto_e_o_prazo(
    client, seletor_ligado, cenario_da_tela
):
    """FR-5811, FR-5813, FR-5814, UX-530: história 3, cenário 1."""
    edital, _, _ = cenario_da_tela
    identificar(client, "carlos", ["gestor"])
    proxima = _fila(edital)[0]

    pagina = _pedir(client, edital, proxima["id"]).content.decode()

    assert "Será convocada, para vaga inicial" in pagina
    assert f"{proxima['protocolo']} — {proxima['nome']} · 1ª na fila" in pagina
    assert "a pessoa está entre as vagas da apuração vigente" in pagina
    assert "Convocação para vaga inicial" in pagina
    assert "Assunto:" in pagina
    assert LINK_NA_CONFERENCIA in pagina
    assert "informado neste ato" in pagina
    # Desde a `159`, o botão diz também a publicação da relação (FR-6803).
    assert f"Convocar {proxima['nome']}, enviar 1 mensagem e publicar a relação</button>" in pagina
    assert "Cancelar e voltar" in pagina
    assert "Passa à frente de" not in pagina


def test_confirmada_a_chamada_acontece_uma_vez(client, seletor_ligado, cenario_da_tela):
    """FR-5816, FR-5818, SC-1903: uma convocação e uma mensagem, mesmo com o duplo clique."""
    edital, _, _ = cenario_da_tela
    identificar(client, "carlos", ["gestor"])
    conferencia = _pedir(client, edital, _fila(edital)[0]["id"])

    primeira = _confirmar(client, edital, conferencia)
    segunda = _confirmar(client, edital, conferencia)

    assert primeira.status_code == segunda.status_code == 302
    assert Convocacao.objects.count() == 1
    assert len(mail.outbox) == 1
    pagina = client.get(primeira["Location"]).content.decode()
    assert "Convocação praticada" in pagina


def test_o_texto_que_mudou_volta_a_conferencia_sem_ato(client, seletor_ligado, cenario_da_tela):
    """FR-5816: o complemento editado depois da prévia não é o que foi conferido."""
    edital, _, _ = cenario_da_tela
    identificar(client, "carlos", ["gestor"])
    conferencia = _pedir(client, edital, _fila(edital)[0]["id"])

    resposta = _confirmar(client, edital, conferencia, complemento="Outro texto.")

    assert resposta.status_code == 200
    assert "Outro texto." in resposta.content.decode()
    assert Convocacao.objects.count() == 0
    assert mail.outbox == []


def test_a_mensagem_conferida_e_a_que_sai(client, seletor_ligado, cenario_da_tela):
    """SC-1907: frase a frase, a mensagem da conferência é a enviada, exceto o link."""
    edital, _, _ = cenario_da_tela
    identificar(client, "carlos", ["gestor"])
    proxima = _fila(edital)[0]
    conferencia = fluxo.conferencia_da_chamada(
        edital=edital,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        lista_id=None,
        inscricao_id=proxima["id"],
        vencimento=timezone.make_aware(parse_datetime(VENCIMENTO)),
    )

    _confirmar(client, edital, _pedir(client, edital, proxima["id"]))

    (mensagem,) = conferencia["mensagens"]
    (enviada,) = mail.outbox
    link = next(linha for linha in enviada.body.splitlines() if "/convocacao" in linha)
    assert enviada.subject == mensagem["assunto"]
    assert enviada.body.replace(link.strip(), LINK_NA_CONFERENCIA) == mensagem["corpo"]


def test_quem_passa_a_frente_e_dito_e_sem_a_marca_e_recusado(
    client, seletor_ligado, cenario_da_tela
):
    """FR-5812, FR-5817: história 3, cenários 3 e 4."""
    edital, _, _ = cenario_da_tela
    identificar(client, "carlos", ["gestor"])
    primeira, segunda = _fila(edital)[:2]

    sem_marca = _pedir(client, edital, segunda["id"]).content.decode()
    com_marca = _pedir(client, edital, segunda["id"], justifica_precedencia="1").content.decode()

    assert "Não é possível convocar agora" in sem_marca
    assert "antes desta na ordem de chamada" in sem_marca
    assert 'name="texto_conferido"' not in sem_marca
    assert "Passa à frente de (1)" in com_marca
    assert f"{primeira['protocolo']} — {primeira['nome']}" in com_marca
    assert "A exceção fica registrada na trilha" in com_marca
    assert 'name="justifica_precedencia" value="1"' in com_marca


def test_a_pessoa_convocada_no_intervalo_recusa_a_confirmacao(
    client, seletor_ligado, cenario_da_tela, gestor
):
    """História 3, cenário 5: outra pessoa convoca antes da confirmação; nada é praticado."""
    edital, _, _ = cenario_da_tela
    identificar(client, "carlos", ["gestor"])
    proxima = _fila(edital)[0]
    conferencia = _pedir(client, edital, proxima["id"])
    convocar(edital, gestor, proxima["id"], idempotency_key="no-intervalo")

    resposta = _confirmar(client, edital, conferencia)

    pagina = resposta.content.decode()
    assert resposta.status_code == 200
    assert "Não é possível convocar agora" in pagina
    assert "aguardando desfecho" in pagina
    assert Convocacao.objects.count() == 1
    assert mail.outbox == []


def test_vencimento_no_passado_recusa_antes_do_botao(client, seletor_ligado, cenario_da_tela):
    """FR-5817: a recusa do vencimento, com a frase do comando."""
    edital, _, _ = cenario_da_tela
    identificar(client, "carlos", ["gestor"])
    ontem = (timezone.localtime() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M")

    pagina = _pedir(client, edital, _fila(edital)[0]["id"], vencimento=ontem).content.decode()

    assert "O vencimento informado já passou" in pagina
    assert 'name="texto_conferido"' not in pagina


def test_por_publicacao_a_conferencia_nao_promete_envio(
    client, seletor_ligado, db, gestor, api_client, manager_headers, process_payload,
    raiz_de_arquivos,
):  # fmt: skip
    """FR-5813: nenhuma mensagem sai, e o botão não fala em enviar."""
    edital, _, _ = _cenario(
        gestor, api_client, manager_headers, process_payload, forma=FORMA_POR_PUBLICACAO
    )
    identificar(client, "carlos", ["gestor"])
    proxima = _fila(edital)[0]

    pagina = _pedir(client, edital, proxima["id"]).content.decode()

    assert "Nenhuma mensagem sai neste ato" in pagina
    assert "Assunto:" not in pagina
    # Desde a `159`, um botão por veículo, e nenhum presumido (D-006).
    assert f"Convocar {proxima['nome']} e publicar no GPS</button>" in pagina
    assert f"Convocar {proxima['nome']} (a publicação será registrada depois)</button>" in pagina


@pytest.mark.parametrize(("subject", "papeis"), [("auditora", ["auditor"]), ("x", ["elaborador"])])
def test_quem_nao_pode_convocar_continua_recusado(
    client, seletor_ligado, cenario_da_tela, subject, papeis
):
    """FR-5819, SC-1909: a mesma porta do gesto, na conferência e na confirmação."""
    edital, _, _ = cenario_da_tela
    identificar(client, subject, papeis)
    proxima = _fila(edital)[0]

    conferencia = _pedir(client, edital, proxima["id"])
    confirmacao = _pedir(
        client, edital, proxima["id"], etapa="confirmar", texto_conferido="qualquer"
    )

    assert conferencia.status_code == confirmacao.status_code == 403
    assert CONFERENCIA not in conferencia.content.decode()
    assert Convocacao.objects.count() == 0


def test_o_botao_da_tela_leva_a_conferencia(client, seletor_ligado, cenario_da_tela):
    """FR-5822, UX-530: o botão e a ajuda dizem que nada é praticado antes da conferência."""
    edital, _, _ = cenario_da_tela
    identificar(client, "carlos", ["gestor"])

    pagina = client.get(reverse("interface:convocacao", args=[edital.id, MARCO])).content.decode()
    chamada = pagina.split("<summary>Chamar uma pessoa da fila</summary>", 1)[1].split("</form>")[0]

    assert '<button type="submit" class="botao">Conferir antes de convocar</button>' in chamada
    assert "Nada é praticado nem enviado antes de você confirmar nela." in chamada


@pytest.fixture
def com_indeferidos(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    """Dois indeferidos na faixa e três vagas: o recorte do item 8.2 do 77/2026."""
    return montar_cenario_da_convocacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="regularizar-152",
        indeferidas=(0, 1),
    )


def test_a_chamada_para_regularizar_passa_pela_mesma_conferencia(
    client, seletor_ligado, com_indeferidos
):
    """FR-5810, FR-5811: história 3, cenário 6 — a espécie e o Resultado que ela regulariza."""
    edital, _, _ = com_indeferidos
    identificar(client, "carlos", ["gestor"])
    primeiro = selectors.contexto_do_recorte(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )["regularizaveis"][0]
    pagina_da_tela = client.get(
        reverse("interface:convocacao", args=[edital.id, MARCO])
    ).content.decode()
    assert "Chamar para regularizar" in pagina_da_tela

    conferencia = _pedir(client, edital, primeiro, especie=nomes.PARA_REGULARIZAR)
    pagina = conferencia.content.decode()

    assert "Será convocada, para regularizar o indeferimento" in pagina
    assert "1ª na ordem dos indeferidos" in pagina
    assert "Regulariza o Resultado indeferido em" in pagina
    assert Convocacao.objects.count() == 0

    _confirmar(client, edital, conferencia)

    assert Convocacao.objects.get().especie == nomes.PARA_REGULARIZAR


def test_sem_forma_de_comunicar_declarada_a_conferencia_recusa_antes_do_botao(
    client, seletor_ligado, db, gestor, api_client, manager_headers, process_payload,
    raiz_de_arquivos,
):  # fmt: skip
    """FR-5817 (revisão do #502): antes, a confirmação gravava a convocação e o envio a recusava."""
    from processo_seletivo.convocacao.application.comunicar import SEM_FORMA_DECLARADA
    from tests.fixtures.legado import sem_as_regras_da_046

    # O Edital publicado antes da `051`, que cortava sem declarar a forma: hoje ele não publica.
    with sem_as_regras_da_046():
        edital, _, _ = _cenario(gestor, api_client, manager_headers, process_payload, forma="")
    identificar(client, "carlos", ["gestor"])
    proxima = _fila(edital)[0]

    pagina = _pedir(client, edital, proxima["id"]).content.decode()
    forjada = _pedir(client, edital, proxima["id"], etapa="confirmar", texto_conferido="x")

    assert "Não é possível convocar agora" in pagina
    assert SEM_FORMA_DECLARADA in pagina
    assert 'name="texto_conferido"' not in pagina
    assert forjada.status_code == 200
    assert Convocacao.objects.count() == 0
    assert mail.outbox == []


def test_a_especie_conferida_viaja_e_a_divergente_e_recusada(
    client, seletor_ligado, cenario_da_tela
):
    """Revisão do #502: a espécie da fila chegava vazia, e o comando derivava outra sem dizer.

    A virada de espécie entre a conferência e a confirmação não se monta com os dados de hoje — a
    desistência de uma titular deixa a suplente "para vaga que vagou" —, e por isso o caso é o do
    formulário que chega com a espécie de antes: a confirmação é recusada, e nada é praticado.
    """
    edital, _, _ = cenario_da_tela
    identificar(client, "carlos", ["gestor"])
    conferencia = _pedir(client, edital, _fila(edital)[0]["id"])

    assert campos_da_conferencia(conferencia)["especie"] == nomes.VAGA_INICIAL
    resposta = _confirmar(client, edital, conferencia, especie=nomes.SUPLENCIA)

    pagina = resposta.content.decode()
    assert resposta.status_code == 200
    assert "não é a que a posição desta pessoa determina" in pagina
    assert Convocacao.objects.count() == 0
    assert mail.outbox == []
