"""Quantas vezes a confirmação da inscrição sai, e o que aconteceu com cada tentativa (181).

**A confirmação já existia** (010, FR-084): `mensagem.py` a monta e a entrega. O que faltava era a
regra em volta dela, e as duas faltas tinham custo concreto. Sem registro, a falha ia ao log sem
dizer de qual inscrição, e nem a pessoa nem a equipe sabiam que a mensagem não tinha saído. Sem
trava, o duplo clique simultâneo mandava duas: `enviar_inscricao` é idempotente e devolve a mesma
inscrição à segunda requisição, e a view mandava a mensagem de novo.

**A tentativa mora na trilha de auditoria, e não numa tabela** (181, D-002, R1). A trilha já é
append-only e indexada por agregado, e a `134` já grava nela o resultado de cada envio do aviso de
pendência. Uma tabela de envios responderia a mesma pergunta em dois lugares. E não é o despacho dos
avisos da `066`: o aviso é decisão de uma pessoa da equipe sobre um ato publicado, e só sai no
minuto seguinte — quando a tela já teria dito à pessoa o que aconteceu.

**A ordem é a do contrato** (R2): travar a inscrição, ler as tentativas, não enviar se uma foi
aceita ou se a última é de menos de um minuto, enviar, registrar. A trava é consultiva e da
transação: ela serializa duas requisições da mesma inscrição sem tocar a linha dela, e só é liberada
depois de a tentativa estar gravada.

**A trava não espera** (revisão de 18/11). A conversa com o servidor de correio acontece sob ela, e
pode levar até `EMAIL_TIMEOUT`. Esperar empilharia requisições — e workers — atrás de um servidor
fora do ar; quem não consegue a trava sabe que outra tentativa da mesma inscrição está em curso, e
volta sem enviar: a outra registra o que acontecer. O intervalo de um minuto entre tentativas faz o
mesmo para os cliques em sequência.

**Nenhuma falha daqui chega à pessoa** (FR-8352). A inscrição já está gravada quando `confirmar` é
chamado, e uma queda de banco, um dado que falte para montar a mensagem ou um erro de regra viram
registro técnico — e a pessoa chega ao comprovante do mesmo jeito.
"""

import logging
from dataclasses import dataclass
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from processo_seletivo.auditoria.application import record_event
from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.inscricoes.application import mensagem
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.shared.concurrency import travar_consultivamente

logger = logging.getLogger("processo_seletivo.inscricoes")

#: A operação na trilha. Uma por tentativa, sob o agregado da inscrição.
OPERACAO = "CONFIRMAR_POR_EMAIL"

#: **Aceita pelo servidor de correio**, e nada além disso (FR-8359): entrega, spam e leitura estão
#: fora do alcance do sistema, como já está escrito para os avisos da `066`.
ENVIADA = "ENVIADA"
NAO_ENVIADA = "NAO_ENVIADA"

#: O menor intervalo entre duas tentativas da mesma inscrição (FR-8363). Cada tentativa pode prender
#: um worker até `EMAIL_TIMEOUT`; sem intervalo, os cliques de quem espera um servidor fora do ar
#: viram carga sobre ele e sobre o portal.
INTERVALO_ENTRE_TENTATIVAS = timedelta(minutes=1)


@dataclass(frozen=True)
class Tentativa:
    numero: int
    em: object
    resultado: str

    @property
    def enviada(self):
        return self.resultado == ENVIADA


def tentativas(inscricao):
    """As tentativas de confirmação da inscrição, da primeira à última."""
    registros = RegistroAuditoria.objects.filter(
        aggregate_type=Inscricao.__name__, aggregate_id=inscricao.pk, operation=OPERACAO
    ).values_list("occurred_at", "detalhe")
    lidas = [
        Tentativa(numero=int(detalhe["tentativa"]), em=quando, resultado=detalhe["resultado"])
        for quando, detalhe in registros
    ]
    # O número desempata o instante: duas tentativas no mesmo microssegundo não existem, mas a ordem
    # da leitura não pode depender da ordem física das linhas (ver a limpeza dos casos
    # transacionais).
    return sorted(lidas, key=lambda tentativa: (tentativa.numero, tentativa.em))


def ultima(inscricao):
    """A última tentativa, ou `None` — e então a tela não diz nada (FR-8362)."""
    lidas = tentativas(inscricao)
    return lidas[-1] if lidas else None


def espera_para_tentar_de_novo(tentativa, agora=None):
    """Quanto falta para a próxima tentativa poder sair — `timedelta(0)` quando já pode."""
    if tentativa is None:
        return timedelta(0)
    restante = tentativa.em + INTERVALO_ENTRE_TENTATIVAS - (agora or timezone.now())
    return max(restante, timedelta(0))


def confirmar(*, inscricao, ator, montar_dados, correlation_id=""):
    """Envia a confirmação, se ela ainda não saiu, e registra a tentativa.

    Devolve a `Tentativa` registrada, ou `None` quando não tentou: inscrição que não está enviada
    (FR-8350) ou sem endereço, confirmação já aceita (FR-8351), outra tentativa em curso ou a última
    de menos de um minuto (FR-8363) — e também quando algo falhou no caminho, que vai ao registro
    técnico. `montar_dados` só é chamado quando há envio, porque montar os dados lê o comprovante
    inteiro — e a repetição não precisa dele.

    **Chamado depois do commit do envio**, nunca dentro dele (FR-084b da `010`, FR-8352): a
    transação daqui é outra, e a falha de qualquer coisa nela não alcança a inscrição gravada.
    """
    if inscricao.status != Inscricao.Status.SUBMETIDA:
        return None
    if not inscricao.email:
        # Sem endereço, tentar seria registrar uma falha que nenhuma nova tentativa resolve, e a
        # tela ofereceria um botão que sempre falha. Sem tentativa, ela não diz nada (FR-8362).
        logger.warning(
            "A inscrição %s não tem endereço: a confirmação não foi tentada.", inscricao.pk
        )
        return None
    try:
        return _tentar(inscricao, ator, montar_dados, correlation_id)
    except Exception:  # noqa: BLE001 — a inscrição já está gravada; a falha não chega à pessoa
        logger.exception("A confirmação da inscrição %s não foi tentada até o fim.", inscricao.pk)
        return None


def _tentar(inscricao, ator, montar_dados, correlation_id):
    with transaction.atomic():
        if not travar_consultivamente(f"inscricao:confirmar:{inscricao.pk}", esperar=False):
            return None
        anteriores = tentativas(inscricao)
        if any(tentativa.enviada for tentativa in anteriores):
            return None
        if anteriores and espera_para_tentar_de_novo(anteriores[-1]):
            return None
        aceita = mensagem.enviar_comprovante(
            para=inscricao.email, dados=montar_dados(), inscricao_id=inscricao.pk
        )
        tentativa = Tentativa(
            numero=len(anteriores) + 1,
            em=timezone.now(),
            resultado=ENVIADA if aceita else NAO_ENVIADA,
        )
        # **Num ponto de salvamento** (como o despacho da `134`): a mensagem já saiu ou já falhou, e
        # uma trilha que falhasse aqui não pode levar junto a resposta da pessoa. A falha vai ao
        # log.
        try:
            with transaction.atomic():
                record_event(
                    actor=ator,
                    permission="",
                    operation=OPERACAO,
                    aggregate=inscricao,
                    now=tentativa.em,
                    correlation_id=correlation_id or str(inscricao.pk),
                    # Sem endereço, nome, protocolo nem a mensagem de erro do servidor (FR-8358).
                    reason=(
                        f"Tentativa {tentativa.numero} da confirmação por e-mail: "
                        f"{'enviada' if aceita else 'não enviada'}."
                    ),
                    new_state="",
                    new_revision=None,
                    detalhe={"tentativa": tentativa.numero, "resultado": tentativa.resultado},
                )
        except Exception:  # noqa: BLE001 — a trilha não desfaz o que o servidor de correio respondeu
            logger.exception(
                "A trilha da tentativa %s da confirmação da inscrição %s não foi gravada.",
                tentativa.numero,
                inscricao.pk,
            )
            return None
    return tentativa
