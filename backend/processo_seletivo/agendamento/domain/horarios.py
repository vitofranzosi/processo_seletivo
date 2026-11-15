"""Os horários da agenda são uma função pura da configuração (167, FR-7203, D-003, T-003).

**Nada daqui toca o banco.** A tela de configurar chama `derivar` sobre o que está sendo digitado,
sem gravar (UX-760), e os comandos a chamam sobre o que está gravado: é uma fonte só da FR-7203, e o
SC-2391 tem uma prova só. Gravar os horários seria a segunda fonte, que a `D-003` recusa.

**A conta é em minutos sobre a data e a hora locais**, convertidas em instante uma vez, na zona
institucional. Somar `timedelta` a um instante perto de uma transição de horário erraria a hora; o
Brasil não tem horário de verão hoje, mas a zona tem, na história, e um Edital de acervo a alcança.

A identidade de um horário é `(banca, início)` — a mesma do `UNIQUE` do agendamento. A ordem
natural é `(início, ordem da banca)`: as bancas lado a lado em cada horário (FR-7213).
"""

from dataclasses import dataclass, field
from datetime import date, datetime, time
from zoneinfo import ZoneInfo

from django.conf import settings

DIAS_DA_SEMANA = (
    "Segunda-feira",
    "Terça-feira",
    "Quarta-feira",
    "Quinta-feira",
    "Sexta-feira",
    "Sábado",
    "Domingo",
)
DIAS_CURTOS = ("Seg.", "Ter.", "Qua.", "Qui.", "Sex.", "Sáb.", "Dom.")


def zona():
    """A zona institucional (`settings.TIME_ZONE`), e não a do servidor."""
    return ZoneInfo(settings.TIME_ZONE)


@dataclass(frozen=True)
class Banca:
    """Um ponto de atendimento simultâneo (`D-004`): não é grupo de avaliadores."""

    id: str
    nome: str
    acesso: str = ""
    ordem: int = 0


@dataclass(frozen=True)
class Configuracao:
    """O que a comissão configura, como valor — o digitado ou o gravado, tanto faz.

    `dias` é `((dia, ((início, fim), …)), …)`, na ordem em que foram dados; `duracao` e `intervalo`
    podem chegar `None` do formulário, e então não há horário nenhum, e `problemas` diz por quê.
    """

    forma: str
    duracao: int | None
    intervalo: int | None
    dias: tuple = ()
    bancas: tuple = ()
    orientacoes: str = field(default="", compare=False)

    @property
    def valida_para_derivar(self):
        return bool(self.duracao and self.duracao > 0 and (self.intervalo or 0) >= 0)


@dataclass(frozen=True, order=True)
class Horario:
    """Um horário de uma banca. `inicio` e `fim` são instantes com fuso."""

    inicio: datetime
    banca_ordem: int
    banca_id: str = field(compare=False)
    fim: datetime = field(compare=False)

    @property
    def dia(self) -> date:
        return self.inicio.astimezone(zona()).date()

    @property
    def chave(self):
        return (str(self.banca_id), self.inicio)


@dataclass(frozen=True)
class Janela:
    """Uma janela de um dia, com o que ela rende por banca e a sobra no fim (FR-7206)."""

    dia: date
    inicio: time
    fim: time
    por_banca: int
    ultimo_fim: time | None
    sobra: int


def minutos(hora: time) -> int:
    return hora.hour * 60 + hora.minute


def _hora(minutos: int) -> time:
    return time(minutos // 60, minutos % 60)


def _instante(dia: date, minutos: int) -> datetime:
    return datetime.combine(dia, _hora(minutos), tzinfo=zona())


def _inicios(inicio: time, fim: time, duracao: int, intervalo: int):
    """Os inícios, em minutos, dentro de `[início, fim]`: o último termina até o fim (FR-7203)."""
    if not duracao or duracao <= 0 or (intervalo or 0) < 0:
        return []
    passo = duracao + (intervalo or 0)
    t, limite = minutos(inicio), minutos(fim)
    inicios = []
    while t + duracao <= limite:
        inicios.append(t)
        t += passo
    return inicios


def janelas(configuracao: Configuracao) -> list[Janela]:
    """Cada janela com quantos atendimentos ela rende por banca e a sobra no fim.

    A sobra é `fim − fim do último atendimento − intervalo` (T-004): o intervalo depois do último
    atendimento é a pausa que a própria configuração pede, e não tempo perdido. 08:00–12:00 com 10
    + 5 termina às 11:55, e os 5 minutos não são sobra.
    """
    resultado = []
    for dia, pares in configuracao.dias:
        for inicio, fim in pares:
            if inicio is None or fim is None:
                continue
            inicios = _inicios(inicio, fim, configuracao.duracao, configuracao.intervalo)
            if inicios:
                ultimo_fim = inicios[-1] + configuracao.duracao
                sobra = minutos(fim) - ultimo_fim - (configuracao.intervalo or 0)
                resultado.append(
                    Janela(dia, inicio, fim, len(inicios), _hora(ultimo_fim), max(sobra, 0))
                )
            else:
                resultado.append(Janela(dia, inicio, fim, 0, None, 0))
    return resultado


def derivar(configuracao: Configuracao) -> tuple[Horario, ...]:
    """Todos os horários, em todas as bancas, do mais cedo ao mais tarde (FR-7203).

    Dia repetido não duplica horário: a identidade é `(banca, início)`, e o `UNIQUE` do agendamento
    também. `problemas` recusa a repetição antes de gravar; aqui ela só não pode inventar horário.
    """
    vistos = {}
    for dia, pares in configuracao.dias:
        if dia is None:
            continue
        for inicio, fim in pares:
            if inicio is None or fim is None:
                continue
            for t in _inicios(inicio, fim, configuracao.duracao, configuracao.intervalo):
                comeco = _instante(dia, t)
                termino = _instante(dia, t + configuracao.duracao)
                for banca in configuracao.bancas:
                    horario = Horario(comeco, banca.ordem, str(banca.id), termino)
                    vistos.setdefault(horario.chave, horario)
    return tuple(sorted(vistos.values()))


def sobras(configuracao: Configuracao) -> list[Janela]:
    """As janelas cujo fim deixa minutos que não cabem outro atendimento (FR-7206): informação."""
    return [janela for janela in janelas(configuracao) if janela.por_banca and janela.sobra > 0]


# --- como a tela e as frases escrevem datas e horas ---------------------------------------------


def dia_curto(dia: date) -> str:
    """`Seg., 23/11` — o rótulo das abas, das janelas e das frases curtas."""
    return f"{DIAS_CURTOS[dia.weekday()]}, {dia:%d/%m}"


def dia_por_extenso(dia: date) -> str:
    """`Segunda-feira, 23/11/2026`."""
    return f"{DIAS_DA_SEMANA[dia.weekday()]}, {dia:%d/%m/%Y}"


def hora(valor) -> str:
    """`08:15`, de um `time` ou de um instante (na zona institucional)."""
    if isinstance(valor, datetime):
        valor = valor.astimezone(zona())
    return f"{valor:%H:%M}"


def faixa(inicio: time, fim: time) -> str:
    return f"{hora(inicio)}–{hora(fim)}"


def horario_curto(instante: datetime) -> str:
    """`Seg., 23/11, 09:30` — o horário de uma pessoa, nas frases da montagem."""
    local = instante.astimezone(zona())
    return f"{dia_curto(local.date())}, {hora(local)}"


def periodo_por_extenso(periodo) -> str:
    """`de 23 a 25/11/2026`, `de 30/11 a 02/12/2026`, ou `em 23/11/2026` num dia só."""
    inicio, fim = periodo
    if inicio == fim:
        return f"em {inicio:%d/%m/%Y}"
    if inicio.year != fim.year:
        return f"de {inicio:%d/%m/%Y} a {fim:%d/%m/%Y}"
    if inicio.month != fim.month:
        return f"de {inicio:%d/%m} a {fim:%d/%m/%Y}"
    return f"de {inicio:%d} a {fim:%d/%m/%Y}"
