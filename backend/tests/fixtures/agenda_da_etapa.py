"""O cenário da agenda da Etapa (167): o Processo A publicado e a sua segunda Etapa.

A segunda Etapa, a *Prova didática*, não tem Evento no cronograma da fixture — a configuração não
confere período — e a primeira não tem Resultado: a lista está aberta, e a participação é a de
todas as inscrições enviadas. Uma Ocorrência na primeira elimina quem ela alcança, e é assim que
os casos produzem "não participa mais".
"""

from datetime import date, time

from processo_seletivo.agendamento.domain.horarios import Banca, Configuracao

SEG = date(2026, 11, 23)
TER = date(2026, 11, 24)
MANHA_E_TARDE = ((time(8), time(12)), (time(13), time(17)))
UMA_HORA = ((time(8), time(9)),)


def configuracao(dias=((SEG, UMA_HORA),), *, duracao=10, intervalo=5, bancas=None, forma="REMOTA"):
    """Por padrão, quatro horários: 08:00, 08:15, 08:30 e 08:45, numa banca."""
    if bancas is None:
        bancas = (Banca("nova-1", "Banca 1", "https://sala.exemplo/1", 1),)
    return Configuracao(forma, duracao, intervalo, tuple(dias), tuple(bancas), "Tenha o documento.")


def eliminar_na_primeira(gestor, edital, etapa_a1, inscricoes, *, chave="ocorrencia-agenda"):
    from processo_seletivo.resultados.application.ocorrencia import registrar_ocorrencia

    registrar_ocorrencia(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        etapa_id=etapa_a1,
        inscricao_ids=[inscricao.id for inscricao in inscricoes],
        motivo="Não compareceu.",
        idempotency_key=chave,
        correlation_id="teste-agenda",
    )


# --- a entrega B: conferir e publicar -------------------------------------------------------------

DUAS_HORAS = ((time(8), time(10)),)  # oito horários de 10 + 5 numa banca
DECLARACAO = "item 7.2 do Edital"


def montar_completa(gestor, edital, etapa, *, config=None):
    """A agenda configurada e preenchida pelo automático: todos os participantes com horário."""
    from processo_seletivo.agendamento.application import configurar, montar

    configurar.salvar(
        actor=gestor,
        edital=edital,
        etapa_id=etapa,
        configuracao=config or configuracao(dias=((SEG, DUAS_HORAS),)),
    )
    previa = montar.previa_do_preenchimento(actor=gestor, edital=edital, etapa_id=etapa)
    montar.aplicar_preenchimento(
        actor=gestor, edital=edital, etapa_id=etapa, assinatura=previa.assinatura
    )


def publicar_agenda(gestor, edital, etapa, *, chave="publicar-agenda", **campos):
    """Confere e publica no GPS, com a autoridade da suíte; `campos` troca o que a tela enviaria."""
    from processo_seletivo.agendamento.application import conferir, publicar
    from tests.fixtures.autoridades import AUTORIDADE_DA_SUITE

    if "assinatura" not in campos:
        campos["assinatura"] = conferir.conferencia(
            actor=gestor, edital=edital, etapa_id=etapa
        ).assinatura
    valores = {
        "autoridade_id": AUTORIDADE_DA_SUITE,
        "veiculo": "GPS",
        "declaracao": DECLARACAO,
        **campos,
    }
    return publicar.publicar(
        actor=gestor, edital=edital, etapa_id=etapa, idempotency_key=chave, **valores
    )
