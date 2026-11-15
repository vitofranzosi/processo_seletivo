"""Quantos avisos da agenda saíram, quantos estão na fila e quais não foram entregues (FR-7233).

**O estado é o da `066`, derivado das tentativas** (`avisos/domain/estado.py`), e nunca coluna. Cada
cadeia — o aviso que o `HorarioPublicado` aponta e os reenvios dele — conta uma vez, pelo último
elo: o que o reenvio entregou deixa de ser falha, porque o filho é o que vale.

**Em lote** (`R-015` da `066`): a agenda de quarenta pessoas lê os avisos, os destinatários com as
tentativas e as interrupções em quatro consultas, e não quarenta vezes cada uma.
"""

from dataclasses import dataclass, field

from django.conf import settings
from django.db.models import Prefetch

from processo_seletivo.agendamento.domain import recusas
from processo_seletivo.agendamento.models import HorarioPublicado
from processo_seletivo.avisos.application.selectors import tentativas_de
from processo_seletivo.avisos.domain import estado as estado_
from processo_seletivo.avisos.domain import nomes as nomes_dos_avisos
from processo_seletivo.avisos.models import (
    Aviso,
    DestinatarioDoAviso,
    InterrupcaoDoAviso,
    TentativaDeEnvio,
)

ACEITOS = {nomes_dos_avisos.ESTADO_ACEITA}
NA_FILA = {
    nomes_dos_avisos.PENDENTE,
    nomes_dos_avisos.EM_ENVIO,
    nomes_dos_avisos.ESTADO_FALHA_TEMPORARIA,
}
REENVIAVEIS = set(nomes_dos_avisos.ALCANCE_DO_REENVIO[nomes_dos_avisos.REENVIO_DE_FALHAS])


@dataclass
class Falha:
    nome: str
    protocolo: str
    rotulo: str
    aviso_id: object
    reenviavel: bool

    @property
    def frase(self):
        return recusas.nao_entregue(self.nome, self.rotulo)


@dataclass
class SituacaoDosAvisos:
    total: int = 0
    aceitos: int = 0
    na_fila: int = 0
    falhas: list = field(default_factory=list)

    @property
    def resumo(self):
        return recusas.resumo_dos_avisos(self.aceitos, self.na_fila, len(self.falhas))


def situacao_dos_avisos(agenda, *, agora):
    raizes = list(
        HorarioPublicado.objects.filter(ato__agenda=agenda, aviso__isnull=False)
        .select_related("inscricao")
        .order_by("inscricao__nome", "inscricao__protocolo", "id")
        .values_list("aviso_id", "inscricao__nome", "inscricao__protocolo")
    )
    situacao = SituacaoDosAvisos(total=len(raizes))
    if not raizes:
        return situacao
    # Os reenvios moram na mesma tabela, ligados pelo `aviso_anterior`: lidos todos de uma vez, a
    # cadeia se percorre em memória. O Edital filtra pelo índice; a origem, pelo que importa aqui.
    filhos = {}
    for identidade, anterior in (
        Aviso.objects.filter(
            edital_id=agenda.edital_id,
            origem=nomes_dos_avisos.AGENDA,
            aviso_anterior__isnull=False,
        )
        .order_by("solicitado_em", "id")
        .values_list("id", "aviso_anterior_id")
    ):
        filhos[anterior] = identidade
    ultimos = {}
    for raiz, nome, protocolo in raizes:
        ultimo = raiz
        while ultimo in filhos:
            ultimo = filhos[ultimo]
        ultimos[ultimo] = (nome or protocolo or "", protocolo or "")
    avisos = {aviso.id: aviso for aviso in Aviso.objects.filter(id__in=list(ultimos))}
    interrompidos = set(
        InterrupcaoDoAviso.objects.filter(aviso_id__in=list(ultimos)).values_list(
            "aviso_id", flat=True
        )
    )
    destinatarios = (
        DestinatarioDoAviso.objects.filter(aviso_id__in=list(ultimos))
        .prefetch_related(
            Prefetch(
                "tentativas",
                queryset=TentativaDeEnvio.objects.select_related("resultado").order_by("numero"),
            )
        )
        .order_by("aviso_id", "id")
    )
    for destinatario in destinatarios:
        aviso = avisos[destinatario.aviso_id]
        estado = estado_.estado_do_destinatario(
            elegibilidade=destinatario.elegibilidade,
            endereco=destinatario.endereco,
            tentativas=tentativas_de(destinatario),
            interrompido=aviso.id in interrompidos,
            solicitado_em=aviso.solicitado_em,
            agora=agora,
            max_tentativas=settings.AVISOS_MAX_TENTATIVAS,
            janela_horas=settings.AVISOS_JANELA_DE_DESPACHO_HORAS,
        )
        if estado in ACEITOS:
            situacao.aceitos += 1
        elif estado in NA_FILA:
            situacao.na_fila += 1
        else:
            nome, protocolo = ultimos[aviso.id]
            situacao.falhas.append(
                Falha(
                    nome=nome,
                    protocolo=protocolo,
                    rotulo=nomes_dos_avisos.ROTULO_DO_ESTADO[estado],
                    aviso_id=aviso.id,
                    reenviavel=estado in REENVIAVEIS,
                )
            )
    situacao.falhas.sort(key=lambda falha: (falha.nome.casefold(), falha.protocolo))
    return situacao
