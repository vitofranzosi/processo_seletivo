"""A projeção da Agenda dos Editais (101) — marcos, períodos, janelas, síntese e grade, sem banco.

O conteúdo aqui é sintético, na forma da versão consolidada: é o que `ler` entrega a estas funções
depois de ler o banco. Cada caso fixa o instante da leitura, porque a fase de todo marco é resposta
sobre um agora.
"""

from datetime import date, datetime
from zoneinfo import ZoneInfo

import pytest

from processo_seletivo.interface import agenda as ag

ZONA = ZoneInfo("America/Sao_Paulo")
AGORA = datetime(2026, 11, 10, 10, 0, tzinfo=ZONA)
HOJE = date(2026, 11, 10)

EDITAL_A = ag.EditalDaAgenda(
    id="a", numero="12", ano=2026, processo="Processo A", status="PUBLICADO"
)
EDITAL_B = ag.EditalDaAgenda(
    id="b", numero="3", ano=2026, processo="Processo B", status="PUBLICADO"
)
ENCERRADO = ag.EditalDaAgenda(
    id="c", numero="7", ano=2026, processo="Processo C", status="ENCERRADO"
)


def quando(dia, hora=0, minuto=0, mes=11, ano=2026):
    return datetime(ano, mes, dia, hora, minuto, tzinfo=ZONA).isoformat()


def evento(identidade, inicio, fim=None, ordem=0, **extra):
    return {
        "id": identidade,
        "type": f"Espécie {identidade}",
        "description": f"Evento {identidade}",
        "startAt": inicio,
        "endAt": fim,
        "order": ordem,
        "status": "PLANEJADO",
        "location": "",
        **extra,
    }


def conteudo(*eventos, etapas=()):
    return {
        "schedule": list(eventos),
        "stages": [
            {"id": f"etapa-{n}", "scheduleEventId": ligado} for n, ligado in enumerate(etapas)
        ],
    }


def marcos(*eventos, edital=EDITAL_A, agora=AGORA, etapas=()):
    return ag.marcos_do_conteudo(edital, conteudo(*eventos, etapas=etapas), agora)


# ---- marco pontual × período (FR-2618 a FR-2620, D-002) --------------------------------------


def test_evento_sem_termino_e_um_marco_no_seu_dia_com_a_hora():
    (marco,) = marcos(evento("p", quando(12, 14)))
    assert (marco.tipo, marco.dia, marco.hora, marco.intervalo) == (
        ag.PONTUAL,
        date(2026, 11, 12),
        "14h",
        "",
    )


def test_termino_no_mesmo_dia_e_pontual_com_as_duas_horas():
    (marco,) = marcos(evento("p", quando(12, 8), quando(12, 12, 30)))
    assert (marco.tipo, marco.hora) == (ag.PONTUAL, "8h–12h30")


def test_meia_noite_sem_termino_nao_inventa_hora():
    """O Edital que declarou só a data: a meia-noite não é hora que alguém publicou."""
    (marco,) = marcos(evento("p", quando(12)))
    assert marco.hora == ""


def test_periodo_lanca_abertura_e_encerramento_e_nada_entre_eles():
    abertura, encerramento = marcos(evento("i", quando(3, 9), quando(15, 23, 59)))
    assert (abertura.tipo, abertura.dia) == (ag.ABERTURA, date(2026, 11, 3))
    assert (encerramento.tipo, encerramento.dia) == (ag.ENCERRAMENTO, date(2026, 11, 15))
    assert abertura.intervalo == encerramento.intervalo == "03/11 a 15/11"
    assert abertura.evento_id == encerramento.evento_id == "i"


def test_periodo_de_inscricoes_sem_termino_so_abre():
    (abertura,) = marcos(evento("i", quando(3, 9), isRegistrationPeriod=True))
    assert (abertura.tipo, abertura.intervalo) == (ag.ABERTURA, "desde 03/11")


def test_evento_comum_sem_termino_e_pontual_e_nao_periodo_aberto():
    (marco,) = marcos(evento("p", quando(3, 9)))
    assert marco.tipo == ag.PONTUAL


def test_o_dia_e_o_da_zona_institucional_e_nao_o_de_utc():
    """31/12 às 23:30 em Vitória é 01/01 em UTC."""
    (marco,) = marcos(evento("v", quando(31, 23, 30, mes=12)))
    assert marco.dia == date(2026, 12, 31)


def test_o_nome_e_a_descricao_publicada_ou_a_especie():
    sem_descricao = evento("s", quando(12, 9), description="")
    nomes = [m.nome for m in marcos(evento("d", quando(12, 8)), sem_descricao)]
    assert nomes == ["Evento d", "Espécie s"]


def test_o_local_vazio_nao_e_dito():
    com, sem = marcos(evento("c", quando(12, 9), location=" Sala 4 "), evento("s", quando(12, 10)))
    assert (com.local, sem.local) == ("Sala 4", "")


# ---- cancelado, espécie e fase (FR-2617, FR-2621, FR-2622, FR-2642, D-006) -------------------


def test_cancelado_e_marcado_e_continua_na_projecao():
    (marco,) = marcos(evento("x", quando(12, 9), status="CANCELADO"))
    assert marco.cancelado


def test_especie_vem_das_marcas_estruturais_e_o_periodo_prevalece():
    resultado = marcos(
        evento("i", quando(12, 9), isRegistrationPeriod=True),
        evento("e", quando(13, 9)),
        evento("d", quando(14, 9)),
        etapas=("i", "e"),
    )
    assert [(m.evento_id, m.especie) for m in resultado] == [
        ("i", ag.INSCRICOES),
        ("e", ag.ETAPA),
        ("d", ag.DEMAIS),
    ]


def test_a_fase_e_dita_sem_afirmar_execucao():
    passado, em_curso, futuro = marcos(
        evento("p", quando(9, 9)),
        evento("c", quando(10, 8), quando(10, 12)),
        evento("f", quando(11, 9)),
    )
    assert [passado.fase, em_curso.fase, futuro.fase] == [ag.PASSADA, ag.EM_CURSO, ag.POR_VIR]
    assert passado.rotulo_da_fase == "data passada"
    assert em_curso.rotulo_da_fase == "em curso agora, pelo cronograma"
    assert futuro.rotulo_da_fase == ""


def test_marcos_de_periodo_tem_a_posicao_do_proprio_instante():
    abertura, encerramento = marcos(evento("i", quando(3, 9), quando(15, 18)))
    assert (abertura.fase, encerramento.fase) == (ag.PASSADA, ag.POR_VIR)


def test_edital_encerrado_mostra_so_o_evento_que_ja_passou():
    """D-009: o que a instituição encerrou não se anuncia; o que passou continua consultável."""
    resultado = marcos(
        evento("passou", quando(2, 9)),
        evento("vem", quando(20, 9)),
        evento("correndo", quando(5, 9), quando(25, 9)),
        edital=ENCERRADO,
    )
    assert [m.evento_id for m in resultado] == ["passou"]


# ---- períodos (FR-2627, FR-2633) --------------------------------------------------------------


def test_periodos_ditos_uma_vez_sem_os_cancelados():
    periodos = ag.periodos_do_conteudo(
        EDITAL_A,
        conteudo(
            evento("i", quando(3, 9), quando(15, 18)),
            evento("x", quando(4, 9), quando(16, 18), status="CANCELADO"),
            evento("p", quando(12, 9)),
        ),
        AGORA,
    )
    assert [(p.evento_id, p.intervalo, p.fase) for p in periodos] == [
        ("i", "03/11 a 15/11", ag.EM_CURSO)
    ]


def test_periodo_de_inscricoes_sem_termino_segue_em_curso_pela_regua_do_periodo():
    (periodo,) = ag.periodos_do_conteudo(
        EDITAL_A, conteudo(evento("i", quando(3, 9), isRegistrationPeriod=True)), AGORA
    )
    assert periodo.fase == ag.EM_CURSO
    assert periodo.restante(HOJE) == "sem término declarado"


@pytest.mark.parametrize(
    ("fim", "esperado"),
    [(10, "encerra hoje"), (11, "encerra em 1 dia"), (20, "encerra em 10 dias")],
)
def test_o_tempo_que_falta_e_em_dias_corridos(fim, esperado):
    (periodo,) = ag.periodos_do_conteudo(
        EDITAL_A, conteudo(evento("i", quando(3, 9), quando(fim, 23))), AGORA
    )
    assert periodo.restante(HOJE) == esperado


def test_periodo_toca_e_abrange_um_dia_com_as_bordas():
    (periodo,) = ag.periodos_do_conteudo(
        EDITAL_A, conteudo(evento("i", quando(3, 9), quando(15, 18))), AGORA
    )
    assert periodo.abrange(date(2026, 11, 10))
    assert periodo.abrange(date(2026, 11, 3)) and periodo.abrange(date(2026, 11, 15))
    assert not periodo.abrange(date(2026, 11, 2)) and not periodo.abrange(date(2026, 11, 16))
    assert periodo.toca(ag.janela_do_mes(2026, 11))
    assert not periodo.toca(ag.janela_do_mes(2026, 12))


def test_periodo_aberto_sem_termino_toca_todo_mes_depois_do_inicio():
    (periodo,) = ag.periodos_do_conteudo(
        EDITAL_A, conteudo(evento("i", quando(3, 9), isRegistrationPeriod=True)), AGORA
    )
    assert periodo.toca(ag.janela_do_mes(2027, 3))
    assert not periodo.toca(ag.janela_do_mes(2026, 10))


# ---- janelas, ordem, filtros, síntese (FR-2631, FR-2632, FR-2634, FR-2637) --------------------


def test_janela_proxima_comeca_no_comeco_do_dia_de_hoje():
    sete = ag.janela_proxima(HOJE, 7)
    trinta = ag.janela_proxima(HOJE, 30)
    assert (sete.inicio, sete.fim) == (HOJE, date(2026, 11, 16))
    assert (trinta.inicio, trinta.fim) == (HOJE, date(2026, 12, 9))


def test_o_marco_de_hoje_que_ja_passou_continua_na_janela():
    resultado = ag.na_janela(marcos(evento("manha", quando(10, 8))), ag.janela_proxima(HOJE, 7))
    assert [(m.evento_id, m.fase) for m in resultado] == [("manha", ag.PASSADA)]


def test_ordem_do_dia_e_instante_depois_edital_depois_nome():
    do_a = marcos(evento("z", quando(12, 9), description="Zeta"), evento("m", quando(12, 8)))
    do_b = marcos(evento("a", quando(12, 9), description="Alfa"), edital=EDITAL_B)
    ordem = ag.ordenar(do_a + do_b)
    assert [m.nome for m in ordem] == ["Evento m", "Alfa", "Zeta"]


def test_filtros_de_edital_e_de_especie():
    todos = marcos(
        evento("i", quando(12, 9), isRegistrationPeriod=True), evento("d", quando(13, 9))
    ) + marcos(evento("b", quando(12, 9)), edital=EDITAL_B)
    assert {m.evento_id for m in ag.filtrar(todos, ag.Filtros(edital="b"))} == {"b"}
    assert {m.evento_id for m in ag.filtrar(todos, ag.Filtros(especie=ag.INSCRICOES))} == {"i"}
    assert {m.evento_id for m in ag.filtrar(todos, ag.Filtros(edital="a", especie=ag.DEMAIS))} == {
        "d"
    }


def test_sintese_conta_o_exibido_sem_os_cancelados():
    exibidos = marcos(
        evento("i", quando(12, 9), quando(14, 18)),
        evento("p", quando(12, 10)),
        evento("x", quando(12, 11), status="CANCELADO"),
    ) + marcos(evento("b", quando(14, 9)), edital=EDITAL_B)
    sintese = ag.sintese(exibidos)
    assert (sintese.marcos, sintese.editais, sintese.encerramentos) == (4, 2, 1)
    assert sintese.dias_com_varios == 2
    assert sintese.dia_mais_carregado == (date(2026, 11, 12), 2)


def test_sem_dia_com_mais_de_um_marco_nao_ha_dia_mais_carregado():
    sintese = ag.sintese(marcos(evento("a", quando(12, 9)), evento("b", quando(13, 9))))
    assert (sintese.dias_com_varios, sintese.dia_mais_carregado) == (0, None)


# ---- a grade do mês (FR-2624 a FR-2626, FR-2635, D-010) ---------------------------------------


@pytest.mark.parametrize(("ano", "mes", "semanas"), [(2026, 2, 4), (2026, 11, 5), (2026, 8, 6)])
def test_a_grade_tem_as_semanas_que_o_mes_ocupa(ano, mes, semanas):
    grade = ag.semanas_do_mes(ano, mes, [], HOJE)
    assert len(grade) == semanas
    assert all(len(semana) == 7 for semana in grade)


def test_a_semana_comeca_no_domingo_e_os_dias_de_fora_ficam_vazios():
    grade = ag.semanas_do_mes(2026, 11, [], HOJE)
    # 01/11/2026 é domingo; 30/11 é segunda.
    assert grade[0][0].data == date(2026, 11, 1)
    assert [dia.data for dia in grade[-1][2:]] == [None] * 5
    assert all(dia.data.weekday() == 6 for dia in (semana[0] for semana in grade) if dia.data)


def test_a_celula_conta_destaca_e_nomeia_dois_na_ordem_do_dia():
    do_dia = marcos(
        evento("c", quando(12, 11), description="Terceiro"),
        evento("a", quando(12, 8), description="Primeiro"),
        evento("b", quando(12, 9), description="Segundo"),
        evento("x", quando(12, 7), status="CANCELADO"),
        evento("so", quando(13, 9)),
    )
    grade = ag.semanas_do_mes(2026, 11, do_dia, HOJE)
    dias = {dia.data: dia for semana in grade for dia in semana if dia.data}
    doze, treze = dias[date(2026, 11, 12)], dias[date(2026, 11, 13)]
    assert (doze.quantidade, doze.destaque, doze.mais) == (3, True, 1)
    assert [m.nome for m in doze.nomeados] == ["Primeiro", "Segundo"]
    assert (treze.quantidade, treze.destaque) == (1, False)
    assert dias[HOJE].hoje and not doze.hoje


def test_dia_so_com_cancelado_nao_tem_contagem():
    grade = ag.semanas_do_mes(
        2026, 11, marcos(evento("x", quando(12, 7), status="CANCELADO")), HOJE
    )
    dias = {dia.data: dia for semana in grade for dia in semana if dia.data}
    assert dias[date(2026, 11, 12)].quantidade == 0


def test_a_soma_das_celulas_e_a_sintese_do_mes():
    do_mes = marcos(
        evento("i", quando(3, 9), quando(15, 18)),
        evento("p", quando(12, 10)),
        evento("q", quando(12, 11)),
        evento("x", quando(20, 9), status="CANCELADO"),
        evento("fora", quando(2, 9, mes=12)),
    )
    janela = ag.janela_do_mes(2026, 11)
    no_mes = ag.na_janela(do_mes, janela)
    grade = ag.semanas_do_mes(2026, 11, no_mes, HOJE)
    soma = sum(dia.quantidade for semana in grade for dia in semana)
    assert soma == ag.sintese(no_mes).marcos == 4


# ---- o dia muito cheio (FR-2630) --------------------------------------------------------------


def test_dia_com_mais_de_oito_marcos_agrupa_por_edital_e_ate_oito_nao():
    do_a = marcos(*(evento(f"a{n}", quando(12, 8 + n)) for n in range(5)))
    do_b = marcos(*(evento(f"b{n}", quando(12, 8 + n)) for n in range(4)), edital=EDITAL_B)
    (cheio,) = ag.dias_da_lista(do_a + do_b)
    assert [edital.id for edital, _ in cheio.grupos] == ["b", "a"]
    assert sum(len(itens) for _, itens in cheio.grupos) == 9
    (comum,) = ag.dias_da_lista(do_a[:4] + do_b)
    assert comum.grupos == ()


def test_o_dia_conta_os_cancelados_a_parte():
    """`FR-2632`: a quantidade não conta o cancelado, e o título diz quantos são."""
    (dia,) = ag.dias_da_lista(
        marcos(evento("x", quando(12, 9), status="CANCELADO"), evento("y", quando(12, 10)))
    )
    assert (dia.quantidade, dia.cancelados) == (1, 1)


# ---- o indicador de períodos (FR-2619, FR-2669, SC-959, revisão de 29/10) ----------------------


def grade_com(*eventos, ano=2026, mes=11, edital=EDITAL_A, agora=AGORA):
    dados = conteudo(*eventos)
    janela = ag.janela_do_mes(ano, mes)
    marcos_do_mes = ag.na_janela(ag.marcos_do_conteudo(edital, dados, agora), janela)
    periodos = ag.periodos_do_conteudo(edital, dados, agora)
    grade = ag.semanas_do_mes(ano, mes, marcos_do_mes, HOJE, periodos=periodos)
    return {dia.data: dia for semana in grade for dia in semana if dia.data}, marcos_do_mes


def test_periodo_que_atravessa_o_mes_inteiro_conta_um_em_todo_dia_e_nenhum_marco():
    dias, marcos_do_mes = grade_com(evento("s", quando(19, 9, mes=10), quando(13, 18, mes=12)))
    assert {dia.periodos for dia in dias.values()} == {1}
    assert {dia.quantidade for dia in dias.values()} == {0}
    assert marcos_do_mes == []


def test_periodos_sobrepostos_contam_cada_um_uma_vez_e_os_marcos_so_nas_bordas():
    dias, _ = grade_com(*(evento(f"i{n}", quando(3, 9), quando(15, 18)) for n in range(5)))
    assert dias[date(2026, 11, 9)].periodos == 5
    assert dias[date(2026, 11, 9)].quantidade == 0
    assert (dias[date(2026, 11, 3)].periodos, dias[date(2026, 11, 3)].quantidade) == (5, 5)
    assert (dias[date(2026, 11, 2)].periodos, dias[date(2026, 11, 16)].periodos) == (0, 0)


def test_periodo_sem_termino_abrange_todo_dia_a_partir_do_inicio():
    aberto = evento("i", quando(3, 9), isRegistrationPeriod=True)
    dias, _ = grade_com(aberto)
    assert (dias[date(2026, 11, 2)].periodos, dias[date(2026, 11, 3)].periodos) == (0, 1)
    dezembro, _ = grade_com(aberto, mes=12)
    assert {dia.periodos for dia in dezembro.values()} == {1}


def test_periodo_cancelado_e_de_edital_encerrado_que_nao_passou_nao_contam():
    dias, _ = grade_com(evento("x", quando(3, 9), quando(15, 18), status="CANCELADO"))
    assert {dia.periodos for dia in dias.values()} == {0}
    encerrado, _ = grade_com(
        evento("passou", quando(1, 9), quando(4, 18)),
        evento("vem", quando(5, 9), quando(20, 18)),
        edital=ENCERRADO,
    )
    assert (encerrado[date(2026, 11, 2)].periodos, encerrado[date(2026, 11, 10)].periodos) == (1, 0)


def test_o_indicador_le_o_dia_na_zona_institucional():
    """Termina às 23:30 de 31/12 em Vitória: em UTC já seria 01/01."""
    fim_de_ano = evento("v", quando(20, 9, mes=12), quando(31, 23, 30, mes=12))
    dezembro, _ = grade_com(fim_de_ano, mes=12)
    janeiro, _ = grade_com(fim_de_ano, ano=2027, mes=1)
    assert dezembro[date(2026, 12, 31)].periodos == 1
    assert janeiro[date(2027, 1, 1)].periodos == 0


def test_o_indicador_nao_entra_na_quantidade_no_destaque_nem_na_sintese():
    dias, marcos_do_mes = grade_com(
        *(evento(f"i{n}", quando(3, 9), quando(15, 18)) for n in range(3)),
        evento("p", quando(9, 10)),
    )
    nove = dias[date(2026, 11, 9)]
    assert (nove.quantidade, nove.periodos, nove.destaque) == (1, 3, False)
    assert ag.sintese(marcos_do_mes).marcos == sum(dia.quantidade for dia in dias.values()) == 7


def test_a_fase_do_periodo_nao_diz_em_curso_de_outro_dia():
    """`FR-2671`: a fase é sobre hoje, e dita sem ambiguidade."""
    passado, hoje, futuro = ag.periodos_do_conteudo(
        EDITAL_A,
        conteudo(
            evento("p", quando(1, 9), quando(4, 18)),
            evento("h", quando(5, 9), quando(20, 18)),
            evento("f", quando(21, 9), quando(25, 18)),
        ),
        AGORA,
    )
    assert [passado.rotulo_da_fase, hoje.rotulo_da_fase, futuro.rotulo_da_fase] == [
        "já passou",
        "em curso hoje, pelo cronograma",
        "ainda não começou",
    ]
