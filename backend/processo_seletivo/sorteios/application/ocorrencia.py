"""Observar a ocorrência da fonte — que **não** é o ato, e não decide nada (021, R-006, FR-019).

**A fronteira que a D-010 de fato traça.** O que a proibição alcança é calcular e constituir; ir à
rede não produz ordem nenhuma. Este comando busca o material na fonte e o registra, e para aí: não
calcula chave, não ordena, não cria ato. Fundir a chamada de rede com a transação de banco não
acrescentaria garantia — trocaria uma falha de rede por uma transação longa.

**Toda observação fica registrada, inclusive a que não vira sorteio.** É o controle que torna
visível o descarte de ocorrência: sem ele, alguém poderia observar até a semente agradar e usar só
a última, e o registro contaria uma história limpa (R-006).

**A semente normalizada não nasce aqui** (D-016). Normalizar é regra do método; esta linha é única
por `(fonte, referência)`, e guardar a derivada aqui congelaria a regra do primeiro método que
passasse por ela.
"""

from django.utils import timezone

from processo_seletivo.avaliacoes.application.trilha import auditar
from processo_seletivo.comissoes.application import comando_de_comissao
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.sorteios.infrastructure.fontes import fonte_declarada
from processo_seletivo.sorteios.models import OcorrenciaDaFonte

OBSERVAR = "SORTEIO_OBSERVAR_OCORRENCIA"
ATO = "sorteios:observar-ocorrencia"


def observar_ocorrencia(
    *,
    actor,
    processo_id,
    fonte,
    referencia,
    idempotency_key,
    correlation_id,
    fonte_externa=None,
    ocorre_em=None,
):
    """Busca na fonte e registra. Idempotente por `(fonte, referência)`, por constraint.

    **A ida à rede acontece antes da transação**, de propósito: manter a conexão aberta enquanto o
    banco espera trocaria um problema por outro, e não há nada a proteger — a leitura da fonte não
    escreve linha nenhuma.
    """
    ja_registrada = OcorrenciaDaFonte.objects.filter(fonte=fonte, referencia=referencia).first()
    if ja_registrada is not None:
        # Observar duas vezes devolve a mesma linha, e é o que torna a observação idempotente. Não
        # é atalho de desempenho: reobservar e regravar permitiria trocar o material bruto de uma
        # ocorrência já conhecida.
        return _declarado(ja_registrada)

    observacao = (fonte_externa or fonte_declarada(fonte)).observar(
        fonte=fonte, referencia=referencia
    )
    if observacao.indisponivel and ocorre_em is not None and timezone.now() < ocorre_em:
        # **"Ainda não" não é "não haverá"** (FR-077). Registrar a ausência como definitiva antes da
        # hora publicada seria consumir a cadeia de substituição de propósito: bastava observar de
        # manhã, a fonte não teria o que publicar, e a regra avançaria sozinha para a extração
        # seguinte — devolvendo à mesa a escolha da ocorrência, com aparência de automatismo.
        raise DomainError(
            "occurrence_not_due_yet",
            f"A ocorrência {referencia!r} está publicada para "
            f"{timezone.localtime(ocorre_em).strftime('%d/%m/%Y às %H:%M')}, e ainda não chegou. "
            "Antes desse instante, a fonte não ter publicado significa que ela ainda não "
            "publicou — e não que não publicará. Observe depois da hora declarada.",
            409,
        )
    if observacao.indisponivel and not observacao.evidencia:
        raise DomainError(
            "source_unavailable_without_evidence",
            "A fonte foi declarada indisponível sem evidência do que se observou. Aplicar a regra "
            "de substituição sem registrar o que a motivou seria afirmar indisponibilidade sem "
            "lastro.",
            502,
        )

    with comando_de_comissao(
        actor=actor,
        processo_id=processo_id,
        operation=ATO,
        payload={"fonte": str(fonte), "referencia": str(referencia)},
        idempotency_key=idempotency_key,
    ) as ctx:
        if ctx.repetido:
            return ctx.desfecho_anterior
        ocorrencia, _criada = OcorrenciaDaFonte.objects.get_or_create(
            fonte=fonte,
            referencia=referencia,
            defaults={
                "material_bruto": observacao.material_bruto,
                "ocorrida_nao_antes_de": observacao.ocorrida_nao_antes_de,
                "observada_em": ctx.now,
                "observada_por": actor.subject,
                "indisponivel": observacao.indisponivel,
                "evidencia": observacao.evidencia,
            },
        )
        auditar(
            actor=actor,
            permissao=ctx.base.permissao,
            operation=OBSERVAR,
            aggregate=ocorrencia,
            now=ctx.now,
            correlation_id=correlation_id,
            reason=(
                observacao.evidencia
                if observacao.indisponivel
                else f"Ocorrência {referencia} de {fonte} observada."
            ),
            idempotency_key=idempotency_key,
        )
        declarado = _declarado(ocorrencia)
        ctx.concluir_sem_resultado(201, declarado)
        return declarado


def _declarado(ocorrencia):
    return {
        "ocorrencia": str(ocorrencia.id),
        "fonte": ocorrencia.fonte,
        "referencia": ocorrencia.referencia,
        "materialBruto": ocorrencia.material_bruto,
        "ocorridaNaoAntesDe": (
            ocorrencia.ocorrida_nao_antes_de.isoformat()
            if ocorrencia.ocorrida_nao_antes_de
            else None
        ),
        "indisponivel": ocorrencia.indisponivel,
        "evidencia": ocorrencia.evidencia,
    }


__all__ = ["ATO", "OBSERVAR", "observar_ocorrencia"]
