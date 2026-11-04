"""A conferência da referência, feita **fora** da transação do ato (116, FR-3631–FR-3633, FR-3647).

**Por que fora.** A consulta é de rede, e rede dentro de `command_context()` seria trava de linha
segurada enquanto a Caixa demora a responder — até 5 segundos por chamada. O padrão de todo ato que
confere é, por isso, o mesmo:

    leitura sem trava → referencias_a_conferir → conferir (rede) → transação do ato
                                                                     └ relê o conteúdo travado
                                                                     └ conferidas(): a referência
                                                                       sem consulta é inconclusiva
                                                                     └ achados, recusa, registro

**Dentro da transação a conferência só vale para o conteúdo efetivamente travado** (FR-3632): se o
rascunho mudou entre a leitura e a trava, a referência nova não foi consultada, e é inconclusiva —
nunca "ainda não realizado". O instante da consulta fica registrado, separado do instante do ato.

**A garantia final continua sendo a constituição do sorteio** (a FR-016 da `021`). Um concurso
realizado nos segundos entre a consulta e a trava escapa daqui e é recusado lá, como hoje.
"""

import json
import logging
from dataclasses import dataclass

from django.utils import timezone

from processo_seletivo.editais.domain import marcos
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.sorteios.domain import conferencia as dominio
from processo_seletivo.sorteios.infrastructure import fontes

logger = logging.getLogger(__name__)

COMUM = "/drawMethod"


@dataclass(frozen=True)
class Referencia:
    """Uma referência declarada num método que governa marco com sorteio a fazer."""

    fonte: str
    referencia: str
    caminho: str
    alvo: str
    ocorre_em: str = ""

    @property
    def chave(self):
        return (self.fonte, self.referencia)


@dataclass(frozen=True)
class ReferenciaConferida:
    """A referência do conteúdo travado, com a situação que a consulta deu a ela."""

    referencia: Referencia
    situacao: dominio.Situacao

    def decisao(self, ato):
        return dominio.decisao(self.situacao, ato)

    def mensagem(self, ato):
        return dominio.mensagem(
            self.situacao, ato, declarada_em=_dia_declarado(self.referencia.ocorre_em)
        )


def _dia_declarado(ocorre_em):
    from django.utils.dateparse import parse_datetime

    from processo_seletivo.shared.tempo import ZONA

    lido = parse_datetime(str(ocorre_em or ""))
    if lido is None or lido.utcoffset() is None:
        return None
    return lido.astimezone(ZONA).date()


def _iso(dia):
    return dia.isoformat() if dia else None


def _governados(conteudo, marcos_sorteados):
    """Marco com sorteio a fazer → a referência do método que o governa.

    **A mesma pergunta que a `102` faz** (`validation._extracao_inviavel`): o método que governa sai
    de `marcos.metodo_que_governa`, o marco precisa ordenar por sorteio, e o marco já sorteado em
    todos os recortes fica de fora. O método comum governa vários marcos e aparece uma vez por
    marco aqui; quem chama agrupa pelo caminho.
    """
    governados = {}
    perfis = conteudo.get("profiles") if isinstance(conteudo, dict) else None
    sorteados = {str(identidade) for identidade in marcos_sorteados}
    for perfil in perfis if isinstance(perfis, list) else []:
        if not isinstance(perfil, dict):
            continue
        lista = perfil.get("classificationMilestones")
        for marco in lista if isinstance(lista, list) else []:
            if not isinstance(marco, dict) or not marco.get("id"):
                continue
            identidade = str(marco["id"])
            if identidade in sorteados:
                continue
            metodo = marcos.metodo_que_governa(
                conteudo, perfil_id=perfil.get("id"), marco_id=identidade
            )
            if not isinstance(metodo, dict) or not marcos.ordena_por_sorteio(
                marco.get("orderProduction") or "", metodo_declarado=True
            ):
                continue
            proprio = bool(marco.get("drawMethod"))
            governados[identidade] = Referencia(
                fonte=str(metodo.get("source") or ""),
                referencia=str(metodo.get("occurrence") or ""),
                caminho=(
                    f"/profiles/id={perfil.get('id', '')}"
                    f"/classificationMilestones/id={identidade}/drawMethod"
                    if proprio
                    else COMUM
                ),
                alvo=(
                    f"O marco {marco.get('code') or marco.get('name') or identidade}"
                    if proprio
                    else "O método comum a este Edital"
                ),
                ocorre_em=str(metodo.get("occurrenceAt") or ""),
            )
    return governados


def referencias_a_conferir(conteudo, *, base=None, marcos_sorteados=frozenset()):
    """As referências que o ato confere (FR-3633), uma por método, na ordem do conteúdo.

    **Só as fontes que sabem conferir** (D-008): fonte que não declara conferência não recebe
    consulta, achado nem advertência.

    **Com `base`, a Retificação, só as introduzidas** (FR-3635, D-006): a referência do marco
    diferente da do mesmo marco no conteúdo-base. A comparação é por valor — fonte e referência do
    método que governa —, e não pelo caminho que a Retificação declarou: assim ela pega também a
    troca do método inteiro, e a troca da fonte para uma que confere. A Retificação que não toca a
    referência devolve a lista vazia, e o ato não faz consulta nenhuma (SC-1100).
    """
    atuais = _governados(conteudo, marcos_sorteados)
    if base is not None:
        anteriores = {
            identidade: referencia.chave
            for identidade, referencia in _governados(base, frozenset()).items()
        }
        atuais = {
            identidade: referencia
            for identidade, referencia in atuais.items()
            if anteriores.get(identidade) != referencia.chave
        }
    por_caminho = {}
    for referencia in atuais.values():
        if fontes.sabe_conferir(referencia.fonte) is not True:
            continue
        # O método que espera a extração não tem o que perguntar à Caixa; o impeditivo dele é do
        # próprio método (FR-3717).
        if not referencia.referencia:
            continue
        por_caminho.setdefault(referencia.caminho, referencia)
    return list(por_caminho.values())


def conferir(referencias, *, agora=None):
    """A consulta: `(fonte, referência) → Situacao`. **Faz rede, e nunca dentro de transação.**

    Uma chamada ao último concurso por fonte, qualquer que seja o número de referências, e uma por
    referência realizada distinta (FR-3631). Quem faz a conta é o adaptador
    (`FonteExterna.conferir_referencias`), porque a fonte de demonstração responde por tabela.
    """
    agora = agora or timezone.now()
    por_fonte = {}
    for referencia in referencias:
        por_fonte.setdefault(referencia.fonte, [])
        if referencia.referencia not in por_fonte[referencia.fonte]:
            por_fonte[referencia.fonte].append(referencia.referencia)
    situacoes = {}
    for fonte, declaradas in por_fonte.items():
        try:
            adaptador = fontes.fonte_declarada(fonte)
        except DomainError:
            # Fonte fora do vocabulário já tem achado próprio; a conferência se cala.
            continue
        if not getattr(adaptador, "SABE_CONFERIR", False):
            continue
        for referencia, situacao in adaptador.conferir_referencias(
            declaradas, fonte=fonte, agora=agora
        ).items():
            situacoes[(fonte, referencia)] = situacao
    return situacoes


def conferidas(referencias, situacoes, *, agora):
    """As referências **do conteúdo travado**, cada uma com a sua situação (FR-3632).

    A que não tem consulta correspondente — o conteúdo mudou entre a leitura sem trava e a trava —
    é inconclusiva. O motivo é "não foi possível falar com a Caixa", que é verdade sobre ela: a
    Caixa não foi consultada sobre essa referência.
    """
    return [
        ReferenciaConferida(
            referencia,
            situacoes.get(referencia.chave)
            or dominio.inconclusiva(
                fonte=referencia.fonte,
                referencia=referencia.referencia,
                consultada_em=agora,
                motivo=dominio.SEM_CONEXAO,
            ),
        )
        for referencia in referencias
    ]


def detalhe(itens, ato):
    """O `detalhe` do registro de auditoria do ato (FR-3647), ou `None` sem nada conferido."""
    if not itens:
        return None
    return {
        "conferenciaDaReferencia": [
            {
                **dominio.registro(item.situacao, item.decisao(ato)),
                # Além das seis perguntas, o que a tela precisa para repetir a mensagem do ato a
                # partir do registro, sem consultar de novo (FR-3646): de que método se fala, em
                # que ato e com que data declarada.
                "ato": ato,
                "caminho": item.referencia.caminho,
                "alvo": item.referencia.alvo,
                "declaradaEm": _iso(_dia_declarado(item.referencia.ocorre_em)),
            }
            for item in itens
        ]
    }


def registrar_no_log(itens, ato, *, correlation_id, desfecho):
    """A conferência no log estruturado, com a correlação do pedido (FR-3649, D-004).

    É o único registro do ato **recusado**: a trilha registra o ato que aconteceu, e gravar trilha
    fora da transação revertida seria mecanismo novo. O ato concluído também passa por aqui, com a
    mesma forma, para que a busca pela correlação encontre os dois.
    """
    if not itens:
        return
    logger.info(
        "conferencia_da_referencia %s",
        json.dumps(
            {
                "ato": ato,
                "desfecho": desfecho,
                "conferencias": [
                    dominio.registro(item.situacao, item.decisao(ato)) for item in itens
                ],
            },
            ensure_ascii=False,
            sort_keys=True,
        ),
        extra={"correlationId": correlation_id, "operation": ato},
    )


def ja_concluido(*, actor, operation, key):
    """O ato com esta chave já respondeu? A repetição não consulta de novo (*Edge Cases*).

    Leitura sem trava, antes da consulta: quem decide é a reserva dentro da transação, e um falso
    "não" aqui só custa uma consulta a mais.
    """
    from processo_seletivo.auditoria.models import IdempotencyRecord

    if not key:
        return False
    return IdempotencyRecord.objects.filter(
        institution_scope=actor.institution_scope,
        actor_subject=actor.subject,
        operation=operation,
        key=key,
        response_status__isnull=False,
    ).exists()


__all__ = [
    "Referencia",
    "ReferenciaConferida",
    "conferidas",
    "conferir",
    "detalhe",
    "ja_concluido",
    "referencias_a_conferir",
    "registrar_no_log",
]
