"""Cabe todo mundo? O veredito do simulador e os atalhos que resolvem a falta (167, FR-7205).

**A capacidade é contada pela mesma `derivar`** que a montagem usa, e não por uma fórmula ao lado:
uma segunda conta seria a segunda fonte da FR-7203, e as duas poderiam divergir no dia em que uma
janela ficasse menor que a duração.

**O veredito vem antes do detalhe** (04-redesign, decisão 2): "Faltam 11 horários para as 43
pessoas" é a resposta que a comissão procura, e a conta por janela é o porquê. E a falta se resolve
onde é dita (decisão 3): cada atalho diz o ganho, calculado sobre a configuração acrescida, e o que
resolve sozinho ganha destaque.
"""

from dataclasses import dataclass, replace
from datetime import timedelta

from processo_seletivo.agendamento.domain import recusas
from processo_seletivo.agendamento.domain.horarios import (
    Banca,
    derivar,
    dia_curto,
    janelas,
    sobras,
)
from processo_seletivo.agendamento.domain.recusas import plural

ACRESCENTAR_DIA = "dia"
ACRESCENTAR_BANCA = "banca"
TIRAR_O_INTERVALO = "intervalo"


@dataclass(frozen=True)
class Capacidade:
    horarios: int
    por_janela: tuple
    participantes: int
    falta: int
    sobra: int
    sobras: tuple
    lista_aberta: bool
    bancas: int
    dias: int

    @property
    def cabe(self):
        return self.falta == 0

    @property
    def taxa(self):
        """Quanto da necessidade os horários cobrem, de 0 a 100 — o medidor."""
        if not self.participantes:
            return 100
        return min(100, round(100 * self.horarios / self.participantes))

    @property
    def veredito(self):
        """A frase do topo do simulador (contracts/recusas.md §2)."""
        if not self.participantes:
            return f"Ninguém participa da Etapa hoje. A agenda tem {self._horarios()}."
        if self.falta:
            faltam = "Falta 1 horário" if self.falta == 1 else f"Faltam {self.falta} horários"
            para = (
                "para a pessoa que participa"
                if self.participantes == 1
                else f"para as {self.participantes} pessoas"
            )
            return f"{faltam} {para}."
        cabem = (
            "Cabe a pessoa que participa."
            if self.participantes == 1
            else f"Cabem todas as {self.participantes} pessoas."
        )
        if not self.sobra:
            return f"{cabem} Nenhum horário sobra."
        sobram = "Sobra 1 horário." if self.sobra == 1 else f"Sobram {self.sobra} horários."
        return f"{cabem} {sobram}"

    @property
    def explicacao(self):
        participam = (
            "1 pessoa participa hoje"
            if self.participantes == 1
            else f"{self.participantes} pessoas participam hoje"
        )
        return f"{participam}, e a agenda tem {self._horarios()}."

    @property
    def conta(self):
        """`16 atendimentos por banca × 1 banca`, por janela (US1, cenário 2)."""
        return [
            {
                "dia": dia_curto(janela.dia),
                "janela": f"{janela.inicio:%H:%M}–{janela.fim:%H:%M}",
                "frase": (
                    f"{plural(janela.por_banca, 'atendimento', 'atendimentos')} por banca × "
                    f"{plural(self.bancas, 'banca', 'bancas')}"
                ),
            }
            for janela in self.por_janela
        ]

    @property
    def frases_de_sobra(self):
        return [recusas.sobra_no_fim(janela) for janela in self.sobras]

    @property
    def frase_da_lista_aberta(self):
        return recusas.lista_aberta(self.participantes) if self.lista_aberta else ""

    def _horarios(self):
        return plural(self.horarios, "horário", "horários")


@dataclass(frozen=True)
class Atalho:
    codigo: str
    rotulo: str
    ganho: int
    resolve: bool


def calcular(configuracao, participantes, *, lista_aberta=False):
    horarios = len(derivar(configuracao))
    return Capacidade(
        horarios=horarios,
        por_janela=tuple(janelas(configuracao)),
        participantes=participantes,
        falta=max(participantes - horarios, 0),
        sobra=max(horarios - participantes, 0),
        sobras=tuple(sobras(configuracao)),
        lista_aberta=lista_aberta,
        bancas=len(configuracao.bancas),
        dias=len({dia for dia, _ in configuracao.dias if dia is not None}),
    )


def proximo_dia(configuracao, periodo):
    """O dia seguinte ao último configurado que ainda não está na agenda, dentro do período.

    Sem período (Etapa sem Evento), o dia seguinte do calendário. Sem dia nenhum, o primeiro do
    período. `None` quando o período acabou: o atalho não oferece dia que a gravação recusaria.
    """
    usados = {dia for dia, _ in configuracao.dias if dia is not None}
    if usados:
        candidato = max(usados) + timedelta(days=1)
    elif periodo is not None:
        candidato = periodo[0]
    else:
        return None
    while candidato in usados:
        candidato += timedelta(days=1)
    if periodo is not None and not periodo[0] <= candidato <= periodo[1]:
        return None
    return candidato


def com_dia(configuracao, dia):
    """A configuração com mais um dia, nas mesmas janelas do último — é o que "o dia seguinte" é."""
    dias = [par for par in configuracao.dias if par[0] is not None]
    modelo = dias[-1][1] if dias else ()
    return replace(configuracao, dias=(*configuracao.dias, (dia, tuple(modelo))))


def com_banca(configuracao, *, identidade=""):
    ordem = max((banca.ordem for banca in configuracao.bancas), default=0) + 1
    usados = {(banca.nome or "").strip().casefold() for banca in configuracao.bancas}
    numero = len(configuracao.bancas) + 1
    while f"banca {numero}" in usados:
        numero += 1
    banca = Banca(identidade or f"nova-{ordem}", f"Banca {numero}", "", ordem)
    return replace(configuracao, bancas=(*configuracao.bancas, banca))


def sem_intervalo(configuracao):
    return replace(configuracao, intervalo=0)


def atalhos(configuracao, participantes, periodo):
    """Os três atalhos do simulador, com o ganho de cada um, quando falta horário.

    O ganho é a diferença de `derivar` sobre a configuração acrescida, e não uma estimativa: "+32"
    é exatamente o que o clique dá.
    """
    if not configuracao.valida_para_derivar:
        return []
    atuais = len(derivar(configuracao))
    falta = participantes - atuais
    if falta <= 0:
        return []
    candidatos = []
    dia = proximo_dia(configuracao, periodo)
    if dia is not None and configuracao.dias:
        candidatos.append(
            (ACRESCENTAR_DIA, f"Acrescentar {dia_curto(dia)}", com_dia(configuracao, dia))
        )
    if configuracao.bancas:
        candidatos.append((ACRESCENTAR_BANCA, "Acrescentar uma banca", com_banca(configuracao)))
    if configuracao.intervalo:
        candidatos.append((TIRAR_O_INTERVALO, "Tirar o intervalo", sem_intervalo(configuracao)))
    lista = []
    for codigo, rotulo, acrescida in candidatos:
        ganho = len(derivar(acrescida)) - atuais
        if ganho > 0:
            lista.append(Atalho(codigo, rotulo, ganho, ganho >= falta))
    return lista
