"""O Cronograma publicado, legível **antes** de qualquer identificação (024, FR-125 a FR-128).

**Por que existe.** O calendário do Edital já estava no conteúdo publicado e já era renderizado —
só que no acompanhamento, isto é, depois de a pessoa se inscrever. Quem já se inscreveu via quando
era a prova; quem estava decidindo se valia a pena, não. Era exatamente o inverso de quem precisa
da informação, e não havia dado novo a produzir: só faltava mostrar.
"""

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from tests.fixtures.selecao import identificador, publicar_selecao, rascunho_de_selecao

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

LOCAL = "Auditório do Campus Serra"


def rascunho_com_tres_eventos(agora):
    """Um evento concluído, um em curso e um por vir — as três situações numa página só."""
    rascunho = rascunho_de_selecao()
    rascunho["schedule"] = [
        {
            "id": identificador(402, 0),
            "type": "Inscrições",
            "description": "Período de inscrições",
            "startAt": (agora - timedelta(days=2)).isoformat(),
            "endAt": (agora + timedelta(days=10)).isoformat(),
            "order": 1,
            "isRegistrationPeriod": True,
        },
        {
            "id": identificador(403, 0),
            "type": "Homologação",
            "description": "Homologação das inscrições",
            "startAt": (agora - timedelta(days=30)).isoformat(),
            "endAt": (agora - timedelta(days=20)).isoformat(),
            "order": 0,
        },
        {
            "id": identificador(404, 0),
            "type": "Prova",
            "description": "Prova de desempenho didático",
            "startAt": (agora + timedelta(days=20)).isoformat(),
            "endAt": (agora + timedelta(days=21)).isoformat(),
            "order": 2,
            "location": LOCAL,
        },
    ]
    return rascunho


def corpo_da_selecao(client, edital):
    return client.get(reverse("portal:selecao", args=[edital.id])).content.decode()


def test_o_cronograma_publicado_aparece_sem_identificacao(
    client, api_client, manager_headers, process_payload
):
    """FR-125, FR-126, FR-150 — sem sessão, e com a situação de cada Evento.

    O cliente deste teste nunca se identifica. É a condição que a `FR-150` cobra e a que separa
    esta feature de tudo o que já existia: o mesmo dado, do lado de fora da porta.
    """
    agora = timezone.now()
    edital = publicar_selecao(
        api_client, manager_headers, process_payload, rascunho=rascunho_com_tres_eventos(agora)
    )

    corpo = corpo_da_selecao(client, edital)

    assert "Cronograma" in corpo
    for nome in (
        "Homologação das inscrições",
        "Período de inscrições",
        "Prova de desempenho didático",
    ):
        assert nome in corpo, f"o Evento {nome!r} não chegou à página pública"
    # A situação **do Evento**: concluído o que terminou, em curso o que corre, por vir o que não
    # começou. Afirmar sobre a classe, e não sobre a aparência, é o que sobrevive ao próximo ajuste
    # de folha de estilo.
    assert 'class="marco concluido"' in corpo
    assert 'class="marco em_curso"' in corpo
    assert 'class="marco futuro"' in corpo


def test_a_ordem_e_a_publicada_e_nao_a_cronologica(
    client, api_client, manager_headers, process_payload
):
    """FR-125 — quem elabora decidiu a ordem, e a página não a reinventa.

    Os três eventos da fixture têm `order` 1, 0 e 2 e datas que **não** seguem essa ordem. Se a
    página ordenasse por data, a homologação viria antes das inscrições na tela — o que é verdade
    no calendário deste teste e mentira sobre o que o Edital publicou.
    """
    agora = timezone.now()
    edital = publicar_selecao(
        api_client, manager_headers, process_payload, rascunho=rascunho_com_tres_eventos(agora)
    )

    corpo = corpo_da_selecao(client, edital)

    posicoes = [
        corpo.index("Homologação das inscrições"),
        corpo.index("Período de inscrições"),
        corpo.index("Prova de desempenho didático"),
    ]
    assert posicoes == sorted(posicoes), "a página reordenou o que o Edital publicou"


def test_o_local_aparece_quando_declarado_e_some_quando_nao(
    client, api_client, manager_headers, process_payload
):
    """FR-127 — e a ausência não vira "local não informado".

    Dizer que o local não foi informado afirma uma omissão do Edital. Ele pode nunca ter tido o que
    declarar ali: uma homologação não acontece em lugar nenhum.
    """
    agora = timezone.now()
    edital = publicar_selecao(
        api_client, manager_headers, process_payload, rascunho=rascunho_com_tres_eventos(agora)
    )

    corpo = corpo_da_selecao(client, edital)

    assert LOCAL in corpo
    assert corpo.count('class="onde"') == 1, "só um dos três Eventos declarou local"
    assert "não informado" not in corpo


def test_sem_evento_publicado_a_secao_some_inteira(
    client, api_client, manager_headers, process_payload
):
    """FR-128, D-009 — a seção some, e nenhuma frase de ausência é escrita.

    **Por que este teste renderiza o template em vez de publicar um Edital sem Evento.** Não dá
    para publicá-lo: `schedule_required` é achado **impeditivo**, e a submissão é recusada antes de
    chegar à homologação. O estado existe assim mesmo — conteúdo publicado antes de a regra
    existir continua legível, e é a ele que o guarda atende. Publicar pelo canal para provar isto
    seria pedir ao domínio que aceitasse o que ele recusa.

    Então o teste afirma sobre o que de fato se quer garantir: dado um contexto sem Evento, a
    página não desenha a seção. O contexto é o **real** — o mesmo que a view monta —, com a lista
    de Eventos esvaziada.

    É a diferença entre esta tela e o acompanhamento, e ela é deliberada: lá o assunto é a
    inscrição da pessoa, e um bloco vazio seria um buraco sem explicação; aqui o assunto é o
    Edital, e a frase afirmaria uma omissão que ele pode nunca ter tido o que declarar.
    """
    from django.template.loader import render_to_string

    edital = publicar_selecao(api_client, manager_headers, process_payload)
    resposta = client.get(reverse("portal:selecao", args=[edital.id]))
    contexto = {**resposta.context[-1].flatten(), "cronograma": []}

    corpo = render_to_string("portal/selecao.html", contexto)
    # A folha de estilo é embutida em toda página do portal, e ela **menciona**
    # `.linha-do-tempo`. Afirmar sobre o documento inteiro acusaria a regra de CSS como se fosse
    # marcação: é o mesmo tropeço que a `021` já registrou com a prosa de um comentário.
    marcacao = corpo[corpo.index("</style>") :]

    assert "linha-do-tempo" not in marcacao
    assert "cronograma-titulo" not in marcacao
    assert "O Edital não publicou cronograma" not in marcacao
    assert "não divulgado" not in marcacao


def test_a_situacao_descreve_o_evento_e_nunca_quem_le(
    client, api_client, manager_headers, process_payload
):
    """FR-126 — a mesma distinção que a FR-077 da `010` nomeia, aqui em vocabulário.

    Um cronograma que diz "sua análise foi concluída" porque a data passou é uma afirmação sobre a
    pessoa que ninguém fez. A seção fala de Eventos, e o teste afirma sobre o vocabulário: nenhuma
    forma de segunda pessoa, nenhum possessivo, dentro do bloco do cronograma.
    """
    agora = timezone.now()
    edital = publicar_selecao(
        api_client, manager_headers, process_payload, rascunho=rascunho_com_tres_eventos(agora)
    )

    corpo = corpo_da_selecao(client, edital)
    bloco = corpo[corpo.index('id="cronograma-titulo"') :]
    bloco = bloco[: bloco.index("</aside>")]

    for pessoal in (" sua ", " seu ", " você ", "Sua ", "Seu ", "Você "):
        assert pessoal not in bloco, f"o cronograma fala da pessoa: {pessoal!r}"


def test_evento_sem_termino_nao_acontece_para_sempre(
    client, api_client, manager_headers, process_payload
):
    """A prova de um dia não pode dizer "acontecendo agora" um mês depois.

    **O defeito que este teste prende.** A regra herdada mandava tudo o que não era futuro nem
    concluído para "em curso", e Evento sem `endAt` nunca satisfazia "concluído". Num Edital
    encerrado em agosto, a página anunciava a prova de 16/08 e o resultado de 10/09 como se
    estivessem acontecendo — em setembro, com as inscrições fechadas.

    Passou despercebido enquanto a situação era só peso de fonte. A etiqueta da `024` a pôs em
    palavras.
    """
    agora = timezone.now()
    rascunho = rascunho_de_selecao()
    rascunho["schedule"] = [
        {
            "id": identificador(402, 0),
            "type": "Inscrições",
            "description": "Período de inscrições",
            "startAt": (agora - timedelta(days=60)).isoformat(),
            "endAt": (agora - timedelta(days=30)).isoformat(),
            "order": 0,
            "isRegistrationPeriod": True,
        },
        {
            "id": identificador(403, 0),
            "type": "Prova",
            "description": "Aplicação da prova",
            "startAt": (agora - timedelta(days=20)).isoformat(),
            "order": 1,
        },
        {
            "id": identificador(404, 0),
            "type": "Resultado",
            "description": "Resultado final",
            "startAt": (agora + timedelta(days=5)).isoformat(),
            "order": 2,
        },
    ]
    edital = publicar_selecao(api_client, manager_headers, process_payload, rascunho=rascunho)

    corpo = corpo_da_selecao(client, edital)
    marcacao = corpo[corpo.index("</style>") :]

    assert "Acontecendo agora" not in marcacao, "um Evento passado ainda se anuncia como corrente"
    assert marcacao.count('class="marco concluido"') == 2, "a prova sem término não foi concluída"
    assert 'class="marco futuro"' in marcacao


def test_o_periodo_de_inscricoes_sem_termino_continua_em_curso(
    client, api_client, manager_headers, process_payload
):
    """A exceção, e por que ela não é arbitrária.

    `periodo_de_inscricoes` decide que período sem término declarado **segue aberto**, porque
    inventar um fechamento seria o sistema criando prazo que o Edital não fixou. Se o cronograma
    dissesse "concluído" ali, a mesma página afirmaria duas coisas contrárias sobre a mesma data:
    a tarja anunciando inscrições abertas e a linha abaixo dizendo que acabaram.
    """
    agora = timezone.now()
    rascunho = rascunho_de_selecao()
    rascunho["schedule"] = [
        {
            "id": identificador(402, 0),
            "type": "Inscrições",
            "description": "Período de inscrições",
            "startAt": (agora - timedelta(days=10)).isoformat(),
            "order": 0,
            "isRegistrationPeriod": True,
        }
    ]
    edital = publicar_selecao(api_client, manager_headers, process_payload, rascunho=rascunho)

    corpo = corpo_da_selecao(client, edital)

    assert "Inscrições abertas" in corpo
    assert 'class="marco em_curso"' in corpo
