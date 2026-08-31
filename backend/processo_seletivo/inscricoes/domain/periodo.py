"""Quando as inscrições estão abertas — lido do conteúdo publicado, e de mais nada.

A regra vive aqui, e não na view, porque ela decide direito: quem chega antes do início não pode
começar, e quem chega depois do fim não pode enviar. As duas telas do portal e a camada de
aplicação leem daqui, de modo que a resposta seja a mesma nos três lugares.

Nada procura texto em `type` ou `description`. O Evento designado se diz designado, e é isso que
torna a situação uma leitura em vez de um palpite sobre o que alguém digitou (FR-002).
"""

from dataclasses import dataclass
from datetime import datetime

from django.utils.dateparse import parse_datetime

FUTURO, ABERTO, ENCERRADO, NAO_DESIGNADO = "futuro", "aberto", "encerrado", "nao-designado"


@dataclass(frozen=True)
class Periodo:
    estado: str
    inicio: datetime | None = None
    fim: datetime | None = None

    @property
    def aberto(self) -> bool:
        return self.estado == ABERTO

    @property
    def designado(self) -> bool:
        return self.estado != NAO_DESIGNADO


def evento_designado(conteudo: dict) -> dict | None:
    return next(
        (
            evento
            for evento in conteudo.get("schedule") or []
            if isinstance(evento, dict) and evento.get("isRegistrationPeriod")
        ),
        None,
    )


def periodo_de_inscricoes(conteudo: dict, agora: datetime) -> Periodo:
    """Três estados e uma ausência.

    A ausência não é um quarto estado da inscrição: é o Edital que não recebe inscrição por este
    sistema, e a página simplesmente não fala de prazo.

    Sem término declarado o período segue aberto, porque é o que o Evento diz — inventar um
    fechamento seria o sistema criando prazo que o Edital não fixou.
    """
    designado = evento_designado(conteudo)
    if designado is None:
        return Periodo(NAO_DESIGNADO)
    inicio = parse_datetime(designado.get("startAt") or "")
    fim = parse_datetime(designado.get("endAt") or "") if designado.get("endAt") else None
    if inicio is not None and agora < inicio:
        return Periodo(FUTURO, inicio, fim)
    if fim is not None and agora > fim:
        return Periodo(ENCERRADO, inicio, fim)
    return Periodo(ABERTO, inicio, fim)
