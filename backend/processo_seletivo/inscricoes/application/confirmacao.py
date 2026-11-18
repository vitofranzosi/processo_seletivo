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
aceita, enviar, registrar. A trava é consultiva e da transação: ela serializa duas requisições da
mesma inscrição sem tocar a linha dela, e só é liberada depois de a tentativa estar gravada — a
segunda requisição a encontra e não envia.
"""

import hashlib
import logging
from dataclasses import dataclass

from django.db import connection, transaction
from django.utils import timezone

from processo_seletivo.auditoria.application import record_event
from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.inscricoes.application import mensagem
from processo_seletivo.inscricoes.models import Inscricao

logger = logging.getLogger("processo_seletivo.inscricoes")

#: A operação na trilha. Uma por tentativa, sob o agregado da inscrição.
OPERACAO = "CONFIRMAR_POR_EMAIL"

#: **Aceita pelo servidor de correio**, e nada além disso (FR-8359): entrega, spam e leitura estão
#: fora do alcance do sistema, como já está escrito para os avisos da `066`.
ENVIADA = "ENVIADA"
NAO_ENVIADA = "NAO_ENVIADA"


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


def _travar(inscricao):
    """A trava consultiva da inscrição, liberada no fim da transação.

    A técnica de `submissao._travar_o_par`, e pela mesma razão: serializa sem travar linha. Fora do
    PostgreSQL é no-op, e é honesto que seja — o SQLite serializa a escrita inteira.
    """
    if connection.vendor != "postgresql":
        return
    material = f"inscricao:confirmar:{inscricao.pk}".encode()
    chave = int.from_bytes(hashlib.sha256(material).digest()[:8], "big", signed=True)
    with connection.cursor() as cursor:
        cursor.execute("SELECT pg_advisory_xact_lock(%s)", [chave])


def confirmar(*, inscricao, ator, montar_dados, correlation_id=""):
    """Envia a confirmação, se ela ainda não saiu, e registra a tentativa.

    Devolve a `Tentativa` registrada, ou `None` quando não tentou: inscrição que não está enviada
    (FR-8350), ou confirmação já aceita (FR-8351). `montar_dados` só é chamado quando há envio,
    porque montar os dados lê o comprovante inteiro — e a repetição não precisa dele.

    **Chamado depois do commit do envio**, nunca dentro dele (FR-084b da `010`, FR-8352): a
    transação daqui é outra, e a falha de qualquer coisa nela não alcança a inscrição gravada.
    """
    if inscricao.status != Inscricao.Status.SUBMETIDA:
        return None
    with transaction.atomic():
        _travar(inscricao)
        anteriores = tentativas(inscricao)
        if any(tentativa.enviada for tentativa in anteriores):
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
