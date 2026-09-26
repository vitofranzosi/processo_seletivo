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

from tests.fixtures.publicacao import encerrar_inscricoes
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
            # Aberto na publicação e encerrado logo abaixo por Retificação (`028`, FR-346,
            # FR-355): o Edital que este teste precisa é um Edital **encerrado**, e o caminho
            # que o produz é o ato que encerra, não a publicação de um prazo já vencido.
            "endAt": (agora + timedelta(days=1)).isoformat(),
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
    edital = encerrar_inscricoes(api_client, edital, agora - timedelta(days=30))

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


# ---------------------------------------------------------------------------
# 037 · as duas superfícies param de discordar sobre o mesmo Evento
# ---------------------------------------------------------------------------


def test_o_periodo_em_curso_e_acontecendo_agora_dos_dois_lados(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    """`FR-549a` e `SC-191`: **concordância de desfecho**, e não unificação de código.

    O defeito que este caso prende foi medido na reauditoria de 16/09/2026: o mesmo período de
    inscrições era *"acontecendo agora"* na página pública e **vencido** na gestão, no mesmo
    instante e sobre o mesmo dado. Não era erro de cálculo compartilhado — são **duas leituras
    independentes**, e cada uma lia certo pela régua que tinha.

    **Unificá-las não é escopo** (`FR-549a`): `portal/leitura.py` deriva a situação por conta
    própria e continua derivando. O que se exige é que as duas passem a dizer a mesma coisa — e é
    por isso que este caso afirma os **dois** lados na mesma requisição, e não a régua.
    """
    from django.urls import reverse

    from tests.interface.conftest import identificar

    agora = timezone.now()
    edital = publicar_selecao(
        api_client, manager_headers, process_payload, rascunho=rascunho_com_tres_eventos(agora)
    )

    # O lado do candidato: o período de inscrições começou há dois dias e termina em dez — é o
    # Evento em curso da página.
    publica = corpo_da_selecao(client, edital)

    assert 'class="marco em_curso"' in publica
    assert "Período de inscrições" in publica

    # E o lado da gestão, sobre o **mesmo** Edital e no mesmo instante. **A tela do Edital publicado
    # não é mais onde a conferência se lê** (046, `FR-755`): ela deixou de julgar o Edital publicado
    # como se ele ainda fosse publicar, e não acusa Evento nenhum — de modo que não pode divergir do
    # candidato. A concordância da `FR-549a` passa a ser afirmada onde a gestão ainda **diz** a
    # situação do Evento: a conferência do conteúdo publicado, e a fase que o pulso deriva (`045`).
    from processo_seletivo.editais.domain.validation import (
        ATO_DE_PUBLICACAO,
        validate_for_publication,
    )
    from processo_seletivo.interface.supervisao import fase_do_evento
    from processo_seletivo.publicacoes.application.selectors import effective_version

    conteudo = effective_version(edital_id=edital.id).content
    acusados = [
        item.message
        for item in validate_for_publication(conteudo, ato=ATO_DE_PUBLICACAO, agora=agora)
        if item.code == "schedule_event_in_past"
    ]

    # **A contraprova de que a conferência está sendo lida**, e não simplesmente vazia: a
    # Homologação do mesmo Cronograma começou há trinta dias e terminou há vinte, e continua
    # acusada. Sem esta linha, o caso passaria com a lista vazia.
    assert any("Homologação das inscrições" in frase for frase in acusados), (
        f"a conferência do Cronograma não leu o conteúdo publicado: {acusados}"
    )
    assert not any("Período de inscrições" in frase for frase in acusados), (
        "a gestão continua chamando de vencido o Evento que a página pública diz estar em curso"
    )
    periodo = next(e for e in conteudo["schedule"] if e.get("isRegistrationPeriod") is True)
    assert fase_do_evento(periodo, conteudo, agora) == "EM_ANDAMENTO", (
        "o pulso da gestão não diz em curso o período que o candidato vê em curso"
    )

    identificar(client, "ana.gestora", ["gestor"])
    gestao = client.get(reverse("interface:detalhe", args=[edital.id])).content.decode()
    assert "já passou" not in gestao, "a tela do Edital publicado voltou a julgá-lo (`RC-32`)"
