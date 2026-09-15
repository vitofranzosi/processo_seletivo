"""Os três achados do cronograma vencido, contra o instante do ato (028).

**Todo instante é fixado.** A feature julga contra o instante em que o ato é conferido, e um teste
que dependesse do dia em que a suíte rodasse passaria hoje e reprovaria em janeiro — o defeito que a
`SC-118` existe para impedir.

**O cenário de referência é o da auditoria de 13/09/2026**: o Edital 12/2027 criado a partir do
90/2026, com o período de inscrição de 13/09/2026 08:00 a 09:00 — uma janela de uma hora, do ano
anterior, já encerrada. Ele mora em `test_o_cenario_do_12_2027_produz_exatamente_tres_achados`.
"""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from processo_seletivo.editais.domain.validation import (
    ATO_DE_PUBLICACAO,
    ATO_DE_RETIFICACAO,
    Severity,
    blocking_findings,
    validate_for_publication,
)
from processo_seletivo.interface.views import _destino

VITORIA = ZoneInfo("America/Sao_Paulo")
AGORA = datetime(2026, 9, 15, 12, 0, tzinfo=VITORIA)

EVENTO = "22222222-2222-2222-2222-222222222222"
OUTRO = "33333333-3333-3333-3333-333333333333"

CODIGOS = ("schedule_event_in_past", "schedule_event_year_mismatch", "registration_period_closed")


def em(**delta):
    return (AGORA + timedelta(**delta)).isoformat()


def evento(*, identidade=EVENTO, inicio, fim=None, periodo=False, descricao="Prova objetiva"):
    return {
        "id": identidade,
        "type": "Etapa",
        "description": descricao,
        "startAt": inicio,
        "endAt": fim,
        "order": 1,
        "status": "PLANEJADO",
        "location": "",
        "isRegistrationPeriod": periodo,
    }


def conteudo(*eventos, ano=2026):
    return {
        "title": "Edital de teste",
        "description": "Conteúdo mínimo para conferir o cronograma.",
        "number": "12",
        "year": ano,
        "profiles": [{"id": "11111111-1111-1111-1111-111111111111"}],
        "schedule": list(eventos),
    }


def achados(snapshot, *, ato=ATO_DE_PUBLICACAO, agora=AGORA):
    """Só os achados desta feature: os demais têm teste próprio e não são assunto daqui."""
    return [
        item
        for item in validate_for_publication(snapshot, ato=ato, agora=agora)
        if item.code in CODIGOS
    ]


def codigos(snapshot, **kwargs):
    return [item.code for item in achados(snapshot, **kwargs)]


# --- T008 · um instante por ato (FR-341) --------------------------------------------------------


def test_a_conferencia_usa_um_instante_para_o_cronograma_inteiro():
    """Dois Eventos em torno do instante do ato, separados por microssegundos.

    Este é o único teste que distingue "o instante é resolvido uma vez" de "o relógio é lido a cada
    Evento": nos demais casos as duas implementações concordam. Com a leitura repetida, o Evento
    que está a um microssegundo do futuro pode virar passado entre uma verificação e a outra, e o
    relatório passaria a descrever um estado que nunca existiu.
    """
    quase = (AGORA + timedelta(microseconds=1)).isoformat()
    snapshot = conteudo(
        evento(inicio=(AGORA - timedelta(microseconds=1)).isoformat()),
        evento(identidade=OUTRO, inicio=quase),
    )

    primeira = codigos(snapshot)
    segunda = codigos(snapshot)

    assert primeira == segunda == ["schedule_event_in_past"]


def test_o_instante_passado_governa_e_nao_o_relogio_da_maquina():
    """Passar `agora` torna o resultado independente do dia em que a suíte roda.

    O Edital é declarado de 2020 junto com o Evento: sem isso a divergência de ano entraria no
    meio da medição e o teste passaria a falar de duas coisas ao mesmo tempo.
    """
    snapshot = conteudo(evento(inicio="2020-01-01T09:00:00-03:00"), ano=2020)

    no_futuro = datetime(2019, 1, 1, tzinfo=VITORIA)

    assert codigos(snapshot, agora=no_futuro) == []
    assert "schedule_event_in_past" in codigos(snapshot)


# --- T010 · o ato, e a precedência do instante nomeado (FR-343a, FR-354) ------------------------


def test_o_achado_existe_na_publicacao_e_nao_existe_na_retificacao():
    """No acervo, Evento vencido é a condição normal: produzir advertência ali faria toda
    Retificação de vírgula carregar uma por Evento, e o que se repete deixa de ser lido."""
    snapshot = conteudo(evento(inicio=em(days=-9), fim=em(days=-1)))

    assert codigos(snapshot, ato=ATO_DE_PUBLICACAO) == ["schedule_event_in_past"]
    assert codigos(snapshot, ato=ATO_DE_RETIFICACAO) == []


def test_com_inicio_e_termino_vencidos_a_mensagem_nomeia_o_termino():
    """FR-343a. O término é o instante mais tardio, e é o que diz que o Evento inteiro acabou."""
    snapshot = conteudo(evento(inicio=em(days=-9), fim=em(days=-1)))

    (item,) = achados(snapshot)

    assert item.path == f"/schedule/id={EVENTO}/endAt"
    assert "14/09/2026" in item.message, item.message


def test_sem_termino_declarado_a_mensagem_nomeia_o_inicio():
    snapshot = conteudo(evento(inicio=em(days=-9), fim=None))

    (item,) = achados(snapshot)

    assert item.path == f"/schedule/id={EVENTO}/startAt"
    assert "06/09/2026" in item.message, item.message


def test_evento_em_curso_nomeia_o_inicio_e_nao_o_termino_futuro():
    snapshot = conteudo(evento(inicio=em(days=-1), fim=em(days=2)))

    (item,) = achados(snapshot)

    assert item.path == f"/schedule/id={EVENTO}/startAt"


def test_um_achado_por_evento_e_nao_um_por_instante():
    snapshot = conteudo(evento(inicio=em(days=-9), fim=em(days=-1)))

    assert codigos(snapshot) == ["schedule_event_in_past"]


def test_cronograma_inteiro_no_futuro_nao_produz_achado():
    snapshot = conteudo(evento(inicio=em(days=1), fim=em(days=2)))

    assert codigos(snapshot) == []


def test_instante_malformado_nao_produz_achado_desta_feature():
    """Quem acusa texto que não é instante é a conferência de forma; empilhar duas acusações sobre
    a mesma causa esconde a que resolve."""
    snapshot = conteudo(evento(inicio="ontem de manhã"))

    assert codigos(snapshot) == []


# --- T014 · o destino da pendência é a etapa Cronograma (FR-349) --------------------------------


def test_os_tres_achados_levam_a_etapa_do_cronograma_e_nao_a_da_inscricao():
    """**A armadilha do caminho `/schedule`.** O roteamento tem entrada exata para `/schedule` que
    manda para a etapa Inscrição — correta para a *designação* do período, e sem campo de data
    nenhum. A data se corrige na etapa Cronograma, e é por isso que todo achado desta feature
    endereça o Evento, e não a coleção.
    """
    snapshot = conteudo(
        evento(inicio=em(days=-9), fim=em(days=-1), periodo=True, descricao="Inscrições"),
        ano=2027,
    )

    destinos = {item.code: _destino(item.path, item.code)[0] for item in achados(snapshot)}

    assert destinos == {
        "schedule_event_in_past": "cronograma",
        "schedule_event_year_mismatch": "cronograma",
        "registration_period_closed": "cronograma",
    }


def test_o_destino_da_designacao_ausente_continua_sendo_a_etapa_de_inscricao():
    """O achado que já existia não muda de casa: ele fala da marca, e a marca se declara lá."""
    assert _destino("/schedule", "registration_period_missing")[0] == "inscricao"


# --- T016 · as bordas do impedimento (FR-346, FR-347, FR-350, FR-354) --------------------------


def periodo(*, inicio, fim, ano=2026):
    return conteudo(evento(inicio=inicio, fim=fim, periodo=True, descricao="Inscrições"), ano=ano)


def test_periodo_encerrado_impede_a_publicacao():
    snapshot = periodo(inicio=em(days=-9), fim=em(days=-1))

    impeditivos = [item.code for item in blocking_findings(achados(snapshot))]

    assert impeditivos == ["registration_period_closed"]


def test_termino_igual_ao_instante_do_ato_nao_encerra():
    """FR-347. O prazo que termina agora ainda é prazo — e é a mesma régua estrita que
    `periodo_de_inscricoes` aplica, para que o selo e o impedimento não discordem por um segundo."""
    snapshot = periodo(inicio=em(days=-9), fim=AGORA.isoformat())

    assert "registration_period_closed" not in codigos(snapshot)


def test_periodo_sem_termino_declarado_nao_encerra():
    """Inventar um fim seria o sistema criando prazo que o Edital não fixou."""
    snapshot = periodo(inicio=em(days=-9), fim=None)

    assert "registration_period_closed" not in codigos(snapshot)


def test_periodo_em_curso_adverte_mas_nao_impede():
    """O Edital que abre inscrições e é publicado no mesmo dia é legítimo."""
    snapshot = periodo(inicio=em(days=-1), fim=em(days=9))

    assert codigos(snapshot) == ["schedule_event_in_past"]
    assert blocking_findings(achados(snapshot)) == []


def test_periodo_futuro_nao_produz_achado_nenhum():
    snapshot = periodo(inicio=em(days=1), fim=em(days=9))

    assert codigos(snapshot) == []


def test_o_impedimento_nao_existe_no_ato_de_retificacao():
    """FR-354 para este código. Antecipar ou encerrar prazo é ato de quem assina o Edital."""
    snapshot = periodo(inicio=em(days=-9), fim=em(days=-1))

    assert codigos(snapshot, ato=ATO_DE_RETIFICACAO) == []


def test_os_achados_que_ja_existiam_sobre_o_periodo_nao_mudam():
    """FR-350: marca ausente continua advertindo, marca ambígua continua impedindo, e esta feature
    não empilha um segundo relato sobre nenhuma das duas causas."""
    sem_marca = conteudo(evento(inicio=em(days=1), fim=em(days=9)))
    ambiguo = conteudo(
        evento(inicio=em(days=1), fim=em(days=9), periodo=True),
        evento(identidade=OUTRO, inicio=em(days=1), fim=em(days=9), periodo=True),
    )

    todos = {item.code for item in validate_for_publication(sem_marca, agora=AGORA)}
    assert "registration_period_missing" in todos
    assert codigos(sem_marca) == []

    impeditivos = {
        item.code for item in blocking_findings(validate_for_publication(ambiguo, agora=AGORA))
    }
    assert "registration_period_ambiguous" in impeditivos
    assert "registration_period_closed" not in impeditivos


# --- T017 · a forma da mensagem (UX-047, UX-048) ------------------------------------------------


def test_a_mensagem_do_impedimento_diz_quando_encerrou_e_o_que_acontece():
    snapshot = periodo(inicio=em(days=-9), fim=em(days=-1))

    (item,) = [i for i in achados(snapshot) if i.code == "registration_period_closed"]

    assert "14/09/2026 às 12:00" in item.message, item.message
    assert "não receberá inscrição alguma" in item.message
    assert "Cronograma" in item.message


def test_nenhuma_mensagem_desta_feature_traz_iso_cru_json_pointer_ou_utc():
    """A régua vem do achado P1 da auditoria — "JSON Pointer e UTC na conferência da Retificação".
    O caminho continua sendo JSON Pointer, porque é endereço; a **mensagem** não o exibe."""
    snapshot = periodo(inicio=em(days=-9), fim=em(days=-1), ano=2027)

    for item in achados(snapshot):
        assert "T" not in item.message.replace("Término", "").replace("Tarde", ""), item.message
        assert "+00:00" not in item.message
        assert "-03:00" not in item.message
        assert "/schedule" not in item.message


# --- T022 · o ano (FR-344, FR-345, SC-118) ------------------------------------------------------


def test_o_edital_de_dezembro_com_eventos_do_ano_seguinte_adverte_e_nao_impede():
    """O caso que a `D-006` decidiu não recusar: o Edital **de 2026**, publicado em dezembro, cuja
    prova acontece em março de 2027. O ano do Evento diverge do ano do Edital, e está certo.

    É também a razão de ser advertência e não impedimento pelo lado do contrato: o `year` é **não
    retificável** pela `026`, de modo que uma recusa apontaria para um campo que ninguém pode mexer.
    """
    dezembro = datetime(2026, 12, 10, 9, 0, tzinfo=VITORIA)
    snapshot = conteudo(evento(inicio="2027-03-02T09:00:00-03:00"), ano=2026)

    resultado = achados(snapshot, agora=dezembro)

    assert [item.code for item in resultado] == ["schedule_event_year_mismatch"]
    assert blocking_findings(resultado) == []
    assert all(item.severity == Severity.WARNING for item in resultado)


def test_o_edital_do_ano_seguinte_com_eventos_do_ano_seguinte_nao_adverte():
    """A outra metade, e a que mede o silêncio: Edital 12/2027 com eventos de 2027, composto em
    dezembro de 2026. Não há divergência, e não há o que dizer — o ruído aqui seria o defeito."""
    dezembro = datetime(2026, 12, 10, 9, 0, tzinfo=VITORIA)
    snapshot = conteudo(evento(inicio="2027-03-02T09:00:00-03:00"), ano=2027)

    assert codigos(snapshot, agora=dezembro) == []


def test_o_ultimo_horario_do_ano_em_vitoria_nao_diverge():
    """SC-118. Em UTC este instante é 2027-01-01T02:30Z, e o Edital de 2026 seria acusado de
    divergir de si mesmo — só nos últimos horários do ano, quando ninguém está olhando."""
    virada = datetime(2026, 12, 20, tzinfo=VITORIA)
    snapshot = conteudo(evento(inicio="2026-12-31T23:30:00-03:00"), ano=2026)

    assert codigos(snapshot, agora=virada) == []


def test_o_ano_e_o_do_inicio_e_nao_o_do_termino():
    """Evento que atravessa o ano é normal; conferir os dois acusaria todo Edital de fim de ano."""
    dezembro = datetime(2026, 12, 10, tzinfo=VITORIA)
    snapshot = conteudo(
        evento(inicio="2026-12-28T09:00:00-03:00", fim="2027-01-05T18:00:00-03:00"), ano=2026
    )

    assert codigos(snapshot, agora=dezembro) == []


def test_evento_no_passado_e_com_ano_divergente_produz_as_duas_advertencias():
    """FR-345: duas espécies, cada uma uma vez, cada uma nomeando o instante de que fala."""
    snapshot = conteudo(evento(inicio=em(days=-9), fim=em(days=-1)), ano=2027)

    resultado = achados(snapshot)

    assert sorted(item.code for item in resultado) == [
        "schedule_event_in_past",
        "schedule_event_year_mismatch",
    ]
    do_passado = next(i for i in resultado if i.code == "schedule_event_in_past")
    do_ano = next(i for i in resultado if i.code == "schedule_event_year_mismatch")
    assert do_passado.path.endswith("/endAt")
    assert do_ano.path.endswith("/startAt")


def test_a_advertencia_de_ano_nao_existe_no_ato_de_retificacao():
    """FR-354 para este código."""
    snapshot = conteudo(evento(inicio=em(days=1)), ano=2027)

    assert codigos(snapshot, ato=ATO_DE_PUBLICACAO) == ["schedule_event_year_mismatch"]
    assert codigos(snapshot, ato=ATO_DE_RETIFICACAO) == []


# --- T023 · o cenário medido pela auditoria (SC-114) --------------------------------------------


def test_o_cenario_do_12_2027_produz_exatamente_tres_achados():
    """O Edital 12/2027 criado a partir do 90/2026, como a auditoria de 13/09/2026 o mediu.

    Cronograma: "Período de inscrição — Início: 13/09/2026 08:00 · Término: 13/09/2026 09:00".
    Uma janela de uma hora, do ano anterior, já encerrada — e o Edital seguia para a publicação com
    a etapa 9 dizendo uma única linha, sobre a descrição ausente.

    **E nada é dito sobre a duração de uma hora**, que é a última cláusula da D-005: duração é
    decisão normativa, e uma hora é janela legítima para um sorteio ou uma sessão de prova. A janela
    é acusada por estar encerrada, e por mais nada.
    """
    depois = datetime(2026, 9, 13, 18, 0, tzinfo=VITORIA)
    snapshot = conteudo(
        evento(
            inicio="2026-09-13T08:00:00-03:00",
            fim="2026-09-13T09:00:00-03:00",
            periodo=True,
            descricao="Período de inscrição",
        ),
        ano=2027,
    )

    resultado = achados(snapshot, agora=depois)

    assert sorted(item.code for item in resultado) == [
        "registration_period_closed",
        "schedule_event_in_past",
        "schedule_event_year_mismatch",
    ]
    assert [item.code for item in blocking_findings(resultado)] == ["registration_period_closed"]
    for item in resultado:
        assert "hora" not in item.message, "duração não é assunto desta feature (D-005)"


def test_o_mesmo_cenario_nao_produz_achado_algum_num_ato_de_retificacao():
    depois = datetime(2026, 9, 13, 18, 0, tzinfo=VITORIA)
    snapshot = conteudo(
        evento(
            inicio="2026-09-13T08:00:00-03:00",
            fim="2026-09-13T09:00:00-03:00",
            periodo=True,
            descricao="Período de inscrição",
        ),
        ano=2027,
    )

    assert achados(snapshot, ato=ATO_DE_RETIFICACAO, agora=depois) == []
