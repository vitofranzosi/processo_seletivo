"""A agenda dentro da Distribuição e da agenda publicada: horário, sessão e coerência (179).

**Um módulo de interface, e não de domínio**: aqui se compõe o que a tela mostra a partir do que
`agendamento` e `avaliacoes` já calculam — o horário de cada inscrição, as sessões (dia × banca) do
filtro, os conflitos e quem falta. As regras moram em `avaliacoes/domain/conflito.py` e em
`avaliacoes/application/programacao.py`.

**A sessão é dia e banca, e não uma composição.** O filtro recorta as inscrições daquele dia e
daquela banca para a comissão atribuí-las num gesto (FR-8204); quem avalia continua sendo a
Atribuição de cada uma, e por isso a composição pode variar por dia sem entidade nova.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from processo_seletivo.agendamento.application.leitura import MONTAGEM, horarios_do_edital
from processo_seletivo.agendamento.domain.horarios import dia_curto, zona
from processo_seletivo.avaliacoes.application import programacao


@dataclass
class AgendaNaDistribuicao:
    horarios: dict = field(default_factory=dict)  # o de `horarios_do_edital`, inteiro
    dias: list = field(default_factory=list)  # [(iso, rótulo)]
    bancas: list = field(default_factory=list)  # [(id, nome)]
    em_montagem: bool = False
    coerencia: object = None
    marcas: dict = field(default_factory=dict)  # inscricao_id → [frase]

    @property
    def existe(self):
        return bool(self.dias)


def _frase_da_marca(rotulos, conflito, inscricao_id):
    """O que a linha de uma inscrição diz do conflito: quem, a que horas e onde é a outra."""
    outro = (
        conflito.segundo if conflito.primeiro.inscricao_id == inscricao_id else conflito.primeiro
    )
    quando = outro.inicio.astimezone(zona())
    return (
        f"{rotulos.get(conflito.pessoa, conflito.pessoa)} tem outra entrevista às {quando:%H:%M}"
        f"{f' ({outro.banca_nome})' if outro.banca_nome else ''}"
    )


def contexto(edital, etapa_id, *, previstas) -> AgendaNaDistribuicao:
    """Tudo o que a Distribuição e a agenda publicada precisam da agenda, em leituras fixas.

    Sem agenda no Edital, uma consulta (as agendas) e um contexto vazio: a tela é a de antes.
    """
    horarios = horarios_do_edital(edital)
    etapa = str(etapa_id)
    da_etapa = [h for (e, _), h in horarios.items() if e == etapa]
    if not da_etapa:
        return AgendaNaDistribuicao(horarios=horarios)
    dias = sorted({h.inicio.astimezone(zona()).date() for h in da_etapa})
    bancas = sorted({(str(h.banca_id), h.banca_nome) for h in da_etapa}, key=lambda b: b[1])
    from processo_seletivo.agendamento.application.leitura import participacao

    coerencia = programacao.coerencia(
        edital,
        etapa_id,
        previstas=previstas,
        horarios=horarios,
        participantes=participacao(edital, etapa_id).participantes,
    )
    marcas: dict = {}
    for conflito in coerencia.conflitos_vigentes:
        for compromisso in (conflito.primeiro, conflito.segundo):
            if str(compromisso.etapa_id) == etapa:
                marcas.setdefault(compromisso.inscricao_id, []).append(
                    _frase_da_marca(coerencia.rotulos, conflito, compromisso.inscricao_id)
                )
    return AgendaNaDistribuicao(
        horarios=horarios,
        dias=[(d.isoformat(), dia_curto(d)) for d in dias],
        bancas=bancas,
        em_montagem=any(h.fonte == MONTAGEM for h in da_etapa),
        coerencia=coerencia,
        marcas=marcas,
    )


def conflitos_da_pessoa(coerencia) -> dict:
    """`{subject: [frase]}` dos conflitos vigentes, para "Quem está alocado"."""
    por_pessoa: dict = {}
    if coerencia is None:
        return por_pessoa
    for conflito in coerencia.conflitos_vigentes:
        por_pessoa.setdefault(conflito.pessoa, []).append(coerencia.frase_do_conflito(conflito))
    return por_pessoa
