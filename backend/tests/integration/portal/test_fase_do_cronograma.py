"""O cronograma público diz a fase que a gestão diz (047, US2, `FR-765`, `FR-766`, `SC-283`).

Até a 047 o portal tinha régua própria: comparava o **dia**, em UTC, e não conhecia o Evento
cancelado. A gestão lia outra, a da `045`. Estes casos afirmam os dois lados sobre o **mesmo**
conteúdo publicado e no **mesmo** instante, porque é a concordância que a feature entrega — uma
régua que acerta a página e erra o pulso seria a terceira.
"""

import re
from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.editais.domain.fase_do_evento import fase_do_evento
from processo_seletivo.portal import leitura
from processo_seletivo.publicacoes.application.selectors import effective_version
from tests.fixtures.selecao import identificador, publicar_selecao, rascunho_de_selecao

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

CLASSE = {"PLANEJADO": "futuro", "EM_ANDAMENTO": "em_curso", "CONCLUIDO": "concluido"}


def rascunho_com_quatro_eventos(agora):
    """O período, um Evento com término em curso, um pontual já iniciado e um cancelado."""
    rascunho = rascunho_de_selecao()
    rascunho["schedule"] = [
        {
            "id": identificador(470, 0),
            "type": "Inscrições",
            "description": "Período de inscrições",
            "startAt": (agora - timedelta(days=2)).isoformat(),
            "endAt": (agora + timedelta(days=10)).isoformat(),
            "order": 0,
            "isRegistrationPeriod": True,
        },
        {
            "id": identificador(471, 0),
            "type": "Análise",
            "description": "Análise documental",
            "startAt": (agora - timedelta(days=1)).isoformat(),
            "endAt": (agora + timedelta(days=3)).isoformat(),
            "order": 1,
        },
        {
            # **O caso que a régua anterior errava**: sem término, iniciado há uma hora. O portal o
            # dizia *acontecendo agora* até a meia-noite em UTC; a régua da 045 o conclui no
            # instante do início (047, `D-004`).
            "id": identificador(472, 0),
            "type": "Reunião",
            "description": "Reunião de abertura dos envelopes",
            "startAt": (agora - timedelta(hours=1)).isoformat(),
            "order": 2,
        },
        {
            # Só a API do rascunho declara o cancelamento (045, fora de escopo pela tela).
            "id": identificador(473, 0),
            "type": "Prova",
            "description": "Prova presencial suprimida",
            "startAt": (agora + timedelta(days=20)).isoformat(),
            "endAt": (agora + timedelta(days=20, hours=4)).isoformat(),
            "order": 3,
            "status": "CANCELADO",
        },
    ]
    return rascunho


def linha(corpo, descricao):
    """O `<li>` do Evento, pela descrição publicada."""
    for trecho in re.findall(r'<li class="marco[^"]*".*?</li>', corpo, flags=re.S):
        if descricao in trecho:
            return trecho
    raise AssertionError(f"o Evento {descricao!r} não aparece no cronograma")


@pytest.fixture
def enviada(inscricao_de_maria):
    """A inscrição enviada de `test_acompanhamento.py`, declarada de novo de propósito: importar
    a fixture de outro módulo de teste a redefine aqui, que é o que o `F811` acusa
    (`tests/fixtures/corte.py`)."""
    from processo_seletivo.inscricoes.application.rascunho import anexar_documento, gravar_dados
    from processo_seletivo.inscricoes.application.submissao import enviar_inscricao
    from tests.fixtures.candidato import MARIA, MODALIDADE_AC, pdf
    from tests.fixtures.selecao import DOCUMENTO_DE_TODOS, DOCUMENTO_DO_PERFIL

    inscricao = gravar_dados(
        identidade=MARIA, inscricao=inscricao_de_maria, dados={"modality_id": MODALIDADE_AC}
    )
    for requisito, nome in ((DOCUMENTO_DE_TODOS, "rg.pdf"), (DOCUMENTO_DO_PERFIL, "d.pdf")):
        anexar_documento(
            identidade=MARIA, inscricao=inscricao, requirement_id=requisito, arquivo=pdf(nome)
        )
    inscricao.refresh_from_db()
    return enviar_inscricao(
        identidade=MARIA,
        inscricao=inscricao,
        declaracoes={"veracidade": True, "ciencia": True},
        idempotency_key="envio-fase-do-cronograma",
    )


@pytest.fixture
def publicado(api_client, manager_headers, process_payload):
    agora = timezone.now()
    edital = publicar_selecao(
        api_client, manager_headers, process_payload, rascunho=rascunho_com_quatro_eventos(agora)
    )
    return edital


def test_o_pontual_iniciado_ha_uma_hora_ja_e_concluido(client, publicado):
    corpo = client.get(reverse("portal:selecao", args=[publicado.id])).content.decode()

    trecho = linha(corpo, "Reunião de abertura dos envelopes")

    assert 'class="marco concluido"' in trecho
    assert "Acontecendo agora" not in trecho


def test_o_evento_com_termino_em_curso_e_acontecendo_agora(client, publicado):
    corpo = client.get(reverse("portal:selecao", args=[publicado.id])).content.decode()

    trecho = linha(corpo, "Análise documental")

    assert 'class="marco em_curso"' in trecho
    assert "Acontecendo agora" in trecho


def test_o_cancelado_e_dito_cancelado_e_nao_tem_fase(client, publicado):
    corpo = client.get(reverse("portal:selecao", args=[publicado.id])).content.decode()

    trecho = linha(corpo, "Prova presencial suprimida")

    assert 'class="marco cancelado"' in trecho
    assert "Cancelado" in trecho, "o cancelamento precisa existir em texto, e não só em traço"
    assert "Acontecendo agora" not in trecho


def test_portal_e_gestao_dizem_a_mesma_fase_para_cada_evento(client, publicado):
    """`SC-283`: a classe de cada linha é a fase que o pulso da gestão lê do mesmo conteúdo."""
    agora = timezone.now()
    conteudo = effective_version(edital_id=publicado.id).content
    corpo = client.get(reverse("portal:selecao", args=[publicado.id])).content.decode()

    for evento in conteudo["schedule"]:
        fase = fase_do_evento(evento, conteudo, agora)
        esperada = CLASSE[fase] if fase else "cancelado"
        trecho = linha(corpo, evento["description"])
        assert f'class="marco {esperada}"' in trecho, (evento["description"], fase, trecho)


def test_o_periodo_marcado_como_cancelado_segue_a_regua_do_periodo():
    """Caso-limite da 047: *"Período de inscrições marcado como cancelado"*.

    A régua do período ignora o `status`, e o sistema continua recebendo inscrição
    (`inscricoes/domain/periodo.py`). A página não pode dizer *cancelado* na linha e *aberta* na
    marca. A pergunta de fundo está registrada na spec da 047, em *Achados*.
    """
    agora = timezone.now()
    periodo = {
        "id": identificador(474, 0),
        "description": "Período de inscrições",
        "startAt": (agora - timedelta(days=1)).isoformat(),
        "endAt": (agora + timedelta(days=5)).isoformat(),
        "order": 0,
        "status": "CANCELADO",
        "isRegistrationPeriod": True,
    }
    conteudo = {"schedule": [periodo]}

    assert leitura.situacao_do_evento(periodo, conteudo, agora) == "em_curso"
    assert leitura.cronograma(conteudo, agora)[0]["situacao"] == "em_curso"


def test_o_acompanhamento_le_a_mesma_regua(client, enviada, selecao):
    """O acompanhamento e a página pública chamam `leitura.cronograma`, e por isso a régua é a
    mesma: cada linha do acompanhamento tem a classe que a régua do domínio dá ao Evento."""
    from tests.fixtures.candidato import MARIA, identificar

    agora = timezone.now()
    conteudo = effective_version(edital_id=selecao.id).content
    identificar(client, MARIA)
    corpo = client.get(reverse("portal:acompanhamento", args=[enviada.id])).content.decode()
    bloco = corpo[corpo.index("Cronograma do processo") :]

    for evento in conteudo["schedule"]:
        nome = evento.get("description") or evento.get("type")
        assert f'class="marco {leitura.situacao_do_evento(evento, conteudo, agora)}"' in linha(
            bloco, nome
        )
