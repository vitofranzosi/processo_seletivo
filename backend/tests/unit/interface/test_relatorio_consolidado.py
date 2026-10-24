"""A soma do relatório consolidado (100), sobre fatos sintéticos — sem banco.

A soma é função pura de `FatosDoEdital`: cada caso aqui monta os fatos que a derivação da `099`
produziria e confere a regra escrita da spec — universo, razão, ausências, cancelados, privacidade.
"""

import uuid
from collections import Counter
from datetime import date, datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest
from django.http import QueryDict

from processo_seletivo.interface import relatorio_consolidado as rc
from processo_seletivo.interface import relatorio_do_edital as rel
from processo_seletivo.interface.visao_geral import Numero
from processo_seletivo.processos.models import Edital
from processo_seletivo.shared.api.problems import DomainError

ZONA = ZoneInfo("America/Sao_Paulo")
AGORA = datetime(2026, 10, 24, 14, 0, tzinfo=ZONA)
PALAVRAS_PROIBIDAS = (
    "candidatos por vaga",
    "aprovad",
    "vaga preenchida",
    "vaga ocupada",
    "pessoas",
)


def perfil(vagas, inscricoes, *, reserva="não há", reservadas=0, omitido=False):
    listas = (("Ampla concorrência", vagas - reservadas),) + (
        (("Pessoas pretas, pardas e indígenas", reservadas),) if reservadas else ()
    )
    return rel.LinhaDoPerfil(
        id=str(uuid.uuid4()),
        nome="Perfil",
        local="",
        vagas=Numero.de(vagas),
        vagas_por_lista=listas if vagas else (),
        reserva=reserva,
        inscricoes=Numero.de(inscricoes),
        rascunhos=Numero.de(0),
        por_vaga=Numero.de(Decimal("1.0")),
        classificadas=Numero.de(0),
        natureza_do_resultado="",
        habilitadas_nas_vagas=Numero.de(0),
        convocacoes=None,
        recursos=None,
        situacao_das_vagas="",
        etapas=(),
        listas=(),
        omitido=omitido,
    )


def fatos(
    numero="1",
    *,
    status=Edital.Status.ENCERRADO,
    perfis=(),
    pendencias=(),
    aberto=False,
    envios=(),
    marcos=(1, 1),
    apuradas=0,
    habilitadas=None,
    desatualizadas=0,
    convocacoes=(0, 0, 0, 0),
    recursos=(0, 0, 0, 0, 0),
    total_omitido=False,
    posteriores=(),
    retificacoes=0,
    prorrogado=False,
    especie=None,
):
    edital = Edital(id=uuid.uuid4(), number=numero, year=2026, status=status, title=f"E{numero}")
    perfis = list(perfis)
    realizadas, aceitas, aguardando, vencidas = convocacoes
    if especie is None:
        especie = (
            rel.INTERRUPCAO
            if status == Edital.Status.CANCELADO
            else rel.ENCERRAMENTO
            if status == Edital.Status.ENCERRADO and not pendencias
            else rel.ACOMPANHAMENTO
        )
    return rel.FatosDoEdital(
        edital=edital,
        referencia=AGORA,
        unidade={},
        especie=especie,
        desfecho_em=datetime(2026, 9, 1, tzinfo=ZONA)
        if status != Edital.Status.PUBLICADO
        else None,
        perfis=perfis,
        pendencias=tuple(pendencias),
        vagas=sum(p.vagas.valor for p in perfis),
        inscricoes=sum(p.inscricoes.valor for p in perfis),
        rascunhos=0,
        periodo_aberto=aberto,
        prorrogado=prorrogado,
        envios=tuple(envios),
        marcos_declarados=marcos[0],
        marcos_definitivos=marcos[1],
        datas_definitivas=(),
        vagas_habilitadas=habilitadas,
        vagas_apuradas=apuradas,
        vagas_desatualizadas=desatualizadas,
        retificacoes=retificacoes,
        perfis_com_marca=(),
        convocacoes=rel.Convocacoes(realizadas, aceitas, aguardando, None, vencidas),
        recursos=rel.Recursos(*recursos),
        posteriores=list(posteriores),
        cadastros_distintos=0,
        omitidos=frozenset(),
        complementares=frozenset(),
        total_omitido=total_omitido,
    )


def conjunto(*lista):
    return rc.Conjunto(
        criterio=rc.Criterio(
            modo=rc.PUBLICACAO,
            ano=2026,
            atalho=rc.PRIMEIRO_SEMESTRE,
            inicio=date(2026, 1, 1),
            fim=date(2026, 6, 30),
        ),
        alcancados=tuple(f.edital for f in lista),
        incluidos=tuple(f.edital for f in lista),
        retirados=(),
        fora=(),
        escolha=False,
    )


def somar(*lista):
    return rc.consolidar(list(lista), conjunto(*lista), agora=AGORA)


def textos(c):
    return " ".join(
        c.frases
        + [i.base for i in c.indicadores]
        + [t for par in c.pontos_de_atencao for t in par]
        + [rel.interpretar(i.numero) for i in c.indicadores]
    ).lower()


# --- Agregação ----------------------------------------------------------------------------------


def test_a_razao_e_soma_sobre_soma_e_nao_media_das_razoes():
    """FR-2572: 100 inscrições para 42 vagas é 2,4 — a média das razões daria 6,0."""
    c = somar(fatos("1", perfis=[perfil(40, 80)]), fatos("2", perfis=[perfil(2, 20)]))
    assert c.vagas == 42
    assert c.inscricoes.valor == 100
    assert c.razao.valor == Decimal("2.4")


def test_cadastro_de_reserva_fica_fora_dos_dois_termos_da_razao():
    """D-012 da 040: 200 inscrições no cadastro de reserva não disputam as 40 vagas."""
    c = somar(fatos("1", perfis=[perfil(40, 80), perfil(0, 200, reserva="sem limite")]))
    assert c.inscricoes.valor == 280
    assert c.razao.valor == Decimal("2.0")
    assert c.perfis_so_reserva == 1
    assert c.numerador == 80


def test_reservadas_somam_so_no_total():
    c = somar(fatos("1", perfis=[perfil(40, 80, reservadas=20), perfil(10, 30, reservadas=5)]))
    assert c.vagas_reservadas == 25


def test_cada_numero_e_a_soma_dos_fatos_de_cada_edital():
    """SC-939: a soma é a dos números que o relatório de cada Edital diz."""
    a = fatos(
        "1",
        perfis=[perfil(10, 30)],
        apuradas=10,
        habilitadas=9,
        convocacoes=(12, 8, 2, 1),
        recursos=(4, 1, 2, 1, 0),
        retificacoes=2,
        prorrogado=True,
        marcos=(2, 2),
    )
    b = fatos(
        "2",
        perfis=[perfil(5, 15)],
        apuradas=0,
        desatualizadas=5,
        convocacoes=(3, 1, 0, 0),
        recursos=(1, 0, 0, 0, 1),
        marcos=(1, 0),
    )
    c = somar(a, b)
    assert (c.vagas_habilitadas, c.vagas_apuradas, c.vagas_desatualizadas) == (9, 10, 5)
    assert c.vagas_nao_apuradas == 0
    assert c.convocacoes == {
        "realizadas": 15,
        "aceitas": 9,
        "aguardando": 2,
        "vencidas": 1,
        "outros": 3,
    }
    assert c.recursos == rel.Recursos(5, 1, 2, 1, 1)
    assert (c.retificacoes, c.editais_retificados, c.prorrogados) == (2, 1, 1)
    assert (c.marcos_declarados, c.marcos_definitivos) == (3, 2)
    assert (c.editais_com_resultado_previsto, c.editais_definitivos) == (2, 1)


def test_envios_por_mes_no_horario_institucional():
    """23h de 30/06 em Brasília é 02h de 01/07 em UTC — e é junho."""
    envio = datetime(2026, 7, 1, 2, 0, tzinfo=ZoneInfo("UTC"))
    c = somar(fatos("1", perfis=[perfil(1, 2)], envios=[envio, datetime(2026, 7, 2, tzinfo=ZONA)]))
    assert c.envios_por_mes == [((2026, 6), 1), ((2026, 7), 1)]


# --- Universos e ausências ------------------------------------------------------------------------


def test_cancelado_conta_como_edital_e_fica_fora_de_todo_numero():
    """FR-2571, D-005."""
    cancelado = fatos(
        "9",
        status=Edital.Status.CANCELADO,
        perfis=[perfil(8, 14)],
        envios=[datetime(2026, 5, 2, tzinfo=ZONA)],
        convocacoes=(3, 3, 0, 0),
        retificacoes=1,
    )
    c = somar(fatos("1", perfis=[perfil(10, 20)]), cancelado)
    assert c.editais == 2 and c.cancelados == 1 and c.universo == 1
    assert c.vagas == 10 and c.inscricoes.valor == 20
    assert c.envios_por_mes == []
    assert [linha.edital for linha in c.linhas] == [c.relacao[0].edital]
    assert c.convocacoes["realizadas"] == 0
    assert c.retificacoes == 0
    assert "fora o edital cancelado" in textos(c)
    assert [linha.especie for linha in c.relacao] == ["encerramento", "interrupção"]


def test_so_cancelados_nao_produz_numero():
    c = somar(fatos("1", status=Edital.Status.CANCELADO, perfis=[perfil(3, 4)]))
    assert all(not i.numero.existe for i in c.indicadores)
    assert c.frases == ["O Edital do conjunto foi cancelado."]


def test_periodo_aberto_marca_inscricoes_e_razao_parciais():
    c = somar(fatos("1", status=Edital.Status.PUBLICADO, perfis=[perfil(10, 4)], aberto=True))
    assert c.inscricoes.parcial and c.razao.parcial
    assert "1 edital segue com inscrições abertas" in textos(c)


def test_sem_vaga_imediata_a_razao_nao_se_aplica_e_nunca_e_zero():
    c = somar(fatos("1", perfis=[perfil(0, 30, reserva="até 5")]))
    assert not c.razao.existe
    assert rel.interpretar(c.razao) == "nenhum perfil do conjunto tem vaga imediata"


def test_sem_apuracao_e_sem_convocacao_dizem_a_ausencia():
    c = somar(fatos("1", perfis=[perfil(10, 30)]))
    habilitadas = c.indicadores[4]
    aceitas = c.indicadores[5]
    assert rel.interpretar(habilitadas.numero) == "nenhuma vaga apurada ainda"
    assert rel.interpretar(aceitas.numero) == "nenhuma convocação registrada"


def test_resultado_incompleto_nao_conta_como_edital_com_todos_os_definitivos():
    c = somar(fatos("1", perfis=[perfil(1, 9)], marcos=(3, 2)))
    definitivos = c.indicadores[3]
    assert (definitivos.numero.valor, definitivos.de) == (0, 1)
    assert definitivos.base == "2 de 3 resultados previstos já são definitivos"


def test_conjunto_vazio_e_grande_demais_sao_recusados():
    with pytest.raises(DomainError) as vazio:
        conjunto().exigir_emissivel()
    assert vazio.value.code == "conjunto_vazio"
    muitos = [fatos(str(i), perfis=[perfil(1, 1)]) for i in range(rc.LIMITE_DE_EDITAIS + 1)]
    with pytest.raises(DomainError) as grande:
        conjunto(*muitos).exigir_emissivel()
    assert grande.value.code == "conjunto_grande_demais"


# --- Providências e trilha ------------------------------------------------------------------------


def test_pendencias_por_tipo_contam_editais_e_ocorrencias():
    a = fatos(
        "1",
        perfis=[perfil(10, 30)],
        pendencias=[rel.Pendencia(rel.CONVOCACAO_AGUARDANDO, "p", 3)],
    )
    b = fatos(
        "2",
        perfis=[perfil(10, 30)],
        pendencias=[
            rel.Pendencia(rel.CONVOCACAO_AGUARDANDO, "p", 2),
            rel.Pendencia(rel.DEFINITIVO_NAO_PUBLICADO, "p", marco="Final"),
        ],
    )
    c = somar(a, b)
    assert c.pendencias_por_tipo == [
        ("resultado definitivo ainda não publicado", 1, 1),
        ("convocação aguardando resposta", 2, 5),
    ]
    assert c.encerrados_com_pendencia == 2
    assert c.pontos_de_atencao[0][0] == (
        "2 Editais estão encerrados no GPS, mas ainda têm providência registrada."
    )


def test_registros_posteriores_sao_ditos_como_trilha():
    """FR-2581: a contagem é da trilha, e o texto diz que não é todo acontecimento."""
    a = fatos("1", perfis=[perfil(1, 9)], posteriores=[("desfecho de convocação", 2, AGORA)])
    c = somar(a)
    assert c.posteriores_por_edital == [(a.edital, a.desfecho_em, 2)]
    titulo, texto = c.pontos_de_atencao[0]
    assert titulo == "1 Edital tem registros na trilha de auditoria depois do encerramento."
    assert "não todo acontecimento" in texto
    assert c.pontos_de_atencao[-1] == rc.MATRICULA


# --- Privacidade ----------------------------------------------------------------------------------


def _grande():
    return fatos(
        "1",
        perfis=[perfil(10, 30)],
        apuradas=10,
        habilitadas=10,
        convocacoes=(12, 9, 3, 0),
        recursos=(4, 0, 4, 0, 0),
        pendencias=[rel.Pendencia(rel.CONVOCACAO_AGUARDANDO, "p", 3)],
    )


def _pequeno():
    return fatos(
        "2",
        perfis=[perfil(2, 4)],
        apuradas=2,
        habilitadas=1,
        convocacoes=(2, 1, 1, 0),
        recursos=(1, 0, 0, 0, 1),
        pendencias=[
            rel.Pendencia(rel.CONVOCACAO_AGUARDANDO, "p", 1),
            rel.Pendencia(rel.RECURSO_AGUARDANDO, None, 1),
        ],
        total_omitido=True,
    )


def test_edital_pequeno_nao_entra_em_numero_nao_publico():
    """FR-2592: com e sem o Edital de 4 inscrições, os números não públicos são os mesmos."""
    grande = _grande()
    sem = somar(grande)
    com = somar(grande, _pequeno())
    for campo in ("vagas_habilitadas", "vagas_apuradas", "convocacoes", "recursos"):
        assert getattr(com, campo) == getattr(sem, campo), campo
    assert [p[1:] for p in com.pendencias_por_tipo] == [p[1:] for p in sem.pendencias_por_tipo]
    # Vagas e inscrições — que o relatório do Edital diz mesmo pequeno — continuam somadas.
    assert com.vagas == sem.vagas + 2
    assert "fora 1 edital com menos de 5 inscrições enviadas" in textos(com)
    pequeno = next(p for p in com.providencias_por_edital if p.edital.number == "2")
    assert pequeno.omitido and pequeno.itens == ()


def test_conjunto_so_de_editais_pequenos_omite_os_totais_nao_publicos():
    c = somar(_pequeno())
    assert c.convocacoes is None and c.recursos is None
    assert not c.indicadores[5].numero.existe
    assert "detalhe omitido" in rel.interpretar(c.indicadores[5].numero)


# --- Vocabulário ----------------------------------------------------------------------------------


def test_o_texto_nao_afirma_pessoa_aprovacao_ou_matricula():
    """FR-2583."""
    c = somar(_grande(), fatos("3", status=Edital.Status.CANCELADO, perfis=[perfil(1, 1)]))
    texto = textos(c)
    for palavra in PALAVRAS_PROIBIDAS:
        assert palavra not in texto.replace("e não pessoas", ""), palavra
    assert "matrículas efetivadas" in texto  # só como fato não registrado


# --- O critério ---------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("consulta", "inicio", "fim", "rotulo"),
    [
        ("", date(2026, 1, 1), date(2026, 12, 31), "publicados em 2026"),
        ("atalho=s1&ano=2026", date(2026, 1, 1), date(2026, 6, 30), "1º semestre de 2026"),
        ("atalho=s2&ano=2025", date(2025, 7, 1), date(2025, 12, 31), "2º semestre de 2025"),
        (
            "atalho=datas&inicio=2026-03-01&fim=2026-04-15",
            date(2026, 3, 1),
            date(2026, 4, 15),
            "publicados de 01/03/2026 a 15/04/2026",
        ),
        ("atalho=xyz&criterio=abc", date(2026, 1, 1), date(2026, 12, 31), "publicados em 2026"),
    ],
)
def test_o_criterio_de_publicacao_e_seus_atalhos(consulta, inicio, fim, rotulo):
    criterio = rc.criterio_de(QueryDict(consulta), hoje=date(2026, 10, 24))
    assert (criterio.modo, criterio.inicio, criterio.fim) == (rc.PUBLICACAO, inicio, fim)
    assert criterio.periodo_curto == rotulo
    assert criterio.rotulo.startswith("Editais com primeira publicação entre")


def test_datas_invertidas_sao_recusadas():
    with pytest.raises(DomainError) as falha:
        rc.criterio_de(QueryDict("atalho=datas&inicio=2026-05-01&fim=2026-04-01"))
    assert falha.value.code == "periodo_invertido"


def test_o_criterio_por_numero_e_o_manual():
    numero = rc.criterio_de(QueryDict("criterio=numero&ano=2025"), hoje=date(2026, 1, 1))
    assert numero.rotulo == "Editais com número de 2025"
    manual = rc.criterio_de(QueryDict("criterio=manual&busca=Letras"))
    assert (manual.modo, manual.busca, manual.rotulo) == (
        rc.MANUAL,
        "Letras",
        "Editais escolhidos um a um",
    )


def test_a_situacao_no_gps_e_as_providencias_da_ficha():
    c = somar(
        _grande(),
        fatos("2", perfis=[perfil(1, 9)]),
        fatos("3", status=Edital.Status.CANCELADO, perfis=[perfil(1, 1)]),
    )
    assert c.situacao_no_gps == "2 encerrados · 1 cancelado"
    assert c.providencias == "1 Edital com providência registrada em curso · 1 sem nenhuma"
    assert c.por_especie == Counter(
        {rel.ACOMPANHAMENTO: 1, rel.ENCERRAMENTO: 1, rel.INTERRUPCAO: 1}
    )
