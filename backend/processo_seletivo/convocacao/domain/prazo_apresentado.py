"""O prazo como o candidato o lê: data, hora, dia da semana e contagem (121, FR-3873 a FR-3875).

**Uma função só, para o portal e para o e-mail** (FR-3873). Havia três formatos de hora — *"às
HHhMM"* no portal, *"às HH:MM"* no e-mail e *"HH:MM"* na gestão — e quatro funções `data`
duplicadas. A pessoa lia o mesmo prazo de dois jeitos, na tela e na mensagem, e a diferença entre
17h e 14h decide se alguém perde a vaga.

**No fuso da instalação, recebido de quem chama, e nunca o do servidor** (R-003). O domínio não lê
`settings`: o fuso chega como parâmetro, e o instante de referência também. A função não lê relógio,
e por isso o mesmo par de entradas dá a mesma frase em qualquer máquina — o que o SC-1154 prova
trocando o `TZ` do processo.

**Dias de calendário, e não blocos de 24 horas** (FR-3874). Um vencimento às 09h de amanhã, lido às
22h de hoje, é *"termina amanhã"*: contar horas diria *"falta menos de 1 dia"*, e arredondar para
cima diria *"falta 1 dia"* a quem tem onze horas. A contagem nunca arredonda para cima.

**O dia da semana vem de tabela própria** (R-003). O `locale` do sistema depende do servidor, e
`interface/agenda.py` já tem uma tabela — mas o domínio importaria a interface.
"""

from dataclasses import dataclass
from datetime import datetime, tzinfo

#: Segunda a domingo, na ordem de `date.weekday()`: por extenso e em minúsculas (FR-3874).
DIAS_DA_SEMANA = (
    "segunda-feira",
    "terça-feira",
    "quarta-feira",
    "quinta-feira",
    "sexta-feira",
    "sábado",
    "domingo",
)


@dataclass(frozen=True)
class PrazoApresentado:
    """O vencimento lido num instante, no fuso da instalação. Nasce e morre com a requisição."""

    #: *"12/11/2026"*
    data: str
    #: *"17h00"* — `HHhMM`, nunca `HH:MM` (FR-3875, SC-1155).
    hora: str
    #: *"quinta-feira"*
    dia_da_semana: str
    #: *"12/11"* — só no assunto da mensagem (FR-3875).
    data_curta: str
    #: *"faltam 7 dias"*, *"termina amanhã"*, *"termina hoje, às 17h00"*, ou vazio quando vencido.
    contagem: str
    #: O instante de referência passou do vencimento: é o estado encerrado, e não há linha (FR-3874).
    vencido: bool

    @property
    def ate(self):
        """*"até 12/11/2026, às 17h00"* — o formato único das telas do candidato (FR-3747 da 118)."""
        return f"até {self.data}, às {self.hora}"

    @property
    def data_e_hora(self):
        """*"12/11/2026, às 17h00"*."""
        return f"{self.data}, às {self.hora}"

    @property
    def por_extenso(self):
        """*"quinta-feira, 12/11/2026, às 17h00"* — o prazo no corpo da mensagem (FR-3875)."""
        return f"{self.dia_da_semana}, {self.data}, às {self.hora}"

    @property
    def linha(self):
        """A linha abaixo da data no cartão do prazo (FR-3861, FR-3874).

        *"termina hoje, às HHhMM"* sem o dia da semana — ele seria o de hoje, que a pessoa sabe —, e
        *"‹dia› · ‹contagem›"* nos demais. Vencido, nenhuma: é o estado encerrado (FR-3748 da 118).
        """
        if self.vencido or not self.contagem:
            return ""
        if self.contagem.startswith("termina hoje"):
            return self.contagem
        return f"{self.dia_da_semana} · {self.contagem}"


def apresentar(vencimento: datetime, agora: datetime, fuso: tzinfo) -> PrazoApresentado:
    """O prazo de `vencimento` lido em `agora`, no `fuso` da instalação (FR-3873, FR-3874).

    Os dois instantes são cientes de fuso; a data, a hora, o dia e a contagem são os do **dia local**
    — um vencimento às 23h30 em São Paulo é 02h30 UTC do dia seguinte, e a pessoa lê o dia dela.

    Os casos sem linha que não são o vencido — a comunicação não enviada e a convocação sem
    vencimento — são de quem chama, que já os distingue, e não chamam esta função.
    """
    local = vencimento.astimezone(fuso)
    hoje = agora.astimezone(fuso).date()
    dia = local.date()
    hora = f"{local.hour:02d}h{local.minute:02d}"
    vencido = agora > vencimento
    if vencido:
        contagem = ""
    elif dia == hoje:
        contagem = f"termina hoje, às {hora}"
    else:
        faltam = (dia - hoje).days
        contagem = "termina amanhã" if faltam == 1 else f"faltam {faltam} dias"
    return PrazoApresentado(
        data=f"{dia.day:02d}/{dia.month:02d}/{dia.year}",
        hora=hora,
        dia_da_semana=DIAS_DA_SEMANA[dia.weekday()],
        data_curta=f"{dia.day:02d}/{dia.month:02d}",
        contagem=contagem,
        vencido=vencido,
    )


__all__ = ["DIAS_DA_SEMANA", "PrazoApresentado", "apresentar"]
