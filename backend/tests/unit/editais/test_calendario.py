"""O predicado de vencimento e a leitura do ano (028, FR-341 a FR-343a, SC-118).

**Sem banco e sem relógio.** Todo instante é fixado no teste, porque a feature inteira julga contra
o instante do ato: um teste que dependesse do dia em que a suíte rodasse passaria hoje e reprovaria
em janeiro, que é o defeito que a SC-118 existe para impedir.
"""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from processo_seletivo.editais.domain.calendario import ano_do_evento, instante_vencido, vencido

VITORIA = ZoneInfo("America/Sao_Paulo")
AGORA = datetime(2026, 9, 15, 12, 0, tzinfo=VITORIA)


def em(**delta):
    return AGORA + timedelta(**delta)


# --- vencido -----------------------------------------------------------------------------------


def test_instante_igual_ao_do_ato_nao_venceu():
    """O `<` é estrito, e é a mesma régua que decide se o período de inscrições encerrou.

    Trocado por `<=`, o selo diria "vencido" no mesmo segundo em que o impedimento diria "ainda
    não encerrado" — e o sistema discordaria de si mesmo por um microssegundo.
    """
    assert vencido(AGORA, None, agora=AGORA) is False
    assert vencido(None, AGORA, agora=AGORA) is False


def test_um_microssegundo_antes_venceu():
    assert vencido(AGORA - timedelta(microseconds=1), None, agora=AGORA) is True


def test_termino_ausente_nao_vence_por_si():
    """Evento sem término é Evento que o Edital não fechou (FR-347)."""
    assert vencido(em(days=3), None, agora=AGORA) is False


def test_inicio_ausente_nao_responde():
    assert vencido(None, None, agora=AGORA) is False


def test_evento_em_curso_nao_vence():
    """037, `FR-545`: período em curso não é período vencido.

    **Este caso afirmava o contrário, e o nome dele defendia o defeito**: *"vence pelo início"*.
    A régua vencia pelo **ou** dos dois instantes, e com isso o Edital que abre inscrições no dia
    em que é publicado ficava com a etapa do Cronograma impossível de concluir — enquanto o canal
    do candidato lia o mesmo Evento como acontecendo agora.

    Renomear foi obrigatório e não é cosmético: um caso chamado *"vence pelo início"* que passasse
    a afirmar *"não vence"* é a forma mais discreta de a suíte mentir.
    """
    assert vencido(em(days=-1), em(days=2), agora=AGORA) is False


def test_evento_inteiro_no_futuro_nao_vence():
    assert vencido(em(days=1), em(days=2), agora=AGORA) is False


def test_evento_inteiro_no_passado_vence():
    assert vencido(em(days=-9), em(days=-1), agora=AGORA) is True


# --- instante_vencido: a precedência da FR-343a ------------------------------------------------


def test_com_os_dois_vencidos_a_mensagem_nomeia_o_termino():
    """FR-343a: o término é o mais tardio, e é o que diz que o Evento inteiro acabou."""
    inicio, termino = em(days=-9), em(days=-1)
    assert instante_vencido(inicio, termino, agora=AGORA) == termino


def test_sem_termino_declarado_a_mensagem_nomeia_o_inicio():
    inicio = em(days=-9)
    assert instante_vencido(inicio, None, agora=AGORA) == inicio


def test_evento_em_curso_nao_nomeia_instante_nenhum():
    """037, `FR-546a`: a escolha do instante muda **junto com** a régua, e no mesmo ato.

    Este caso é o que prende isso. Ele afirmava que o Evento em curso nomeia o início — coerente
    enquanto o predicado o vencia —, e continuaria verde se só o predicado mudasse: as duas
    funções do mesmo módulo passariam a discordar sobre o mesmo Evento, uma dizendo que ele não
    venceu e a outra escolhendo um instante vencido para ele. É a divergência que a `028` criou
    este módulo para impedir.

    O Evento não venceu; não há instante a nomear. Quem escolhe o início é o Evento **pontual**,
    e o caso dele está logo acima.
    """
    assert instante_vencido(em(days=-1), em(days=2), agora=AGORA) is None


def test_evento_que_nao_venceu_nao_nomeia_instante_nenhum():
    assert instante_vencido(em(days=1), em(days=2), agora=AGORA) is None


# --- ano_do_evento: a leitura na zona institucional --------------------------------------------


def test_o_ano_do_ultimo_horario_do_ano_e_lido_em_vitoria():
    """SC-118. Em UTC este instante é 2027-01-01T02:30Z, e o Edital de 2026 seria acusado de
    divergir de si mesmo — só nos últimos horários do ano, que é quando ninguém está olhando."""
    virada = datetime(2026, 12, 31, 23, 30, tzinfo=VITORIA)
    assert ano_do_evento(virada) == 2026


def test_o_ano_de_um_instante_gravado_em_utc_tambem_e_lido_em_vitoria():
    """O conteúdo publicado materializa o instante com deslocamento; quem o reconstrói em UTC
    tem de chegar ao mesmo ano — ou a conferência dependeria de como o instante foi escrito."""
    virada = datetime(2027, 1, 1, 2, 30, tzinfo=ZoneInfo("UTC"))
    assert ano_do_evento(virada) == 2026


def test_o_primeiro_horario_do_ano_em_vitoria_e_do_ano_novo():
    assert ano_do_evento(datetime(2027, 1, 1, 0, 30, tzinfo=VITORIA)) == 2027
