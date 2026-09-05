"""O ato que constitui uma ordem e as posições que formam o seu snapshot.

Vigência, obsolescência e recomputabilidade não são colunas. O ato nasce imutável e uma sucessão
é outra linha que aponta para ele; vigente é, portanto, o ato que ninguém sucedeu. Isso mantém a
história append-only também para o papel de runtime, que não possui ``UPDATE`` nessas tabelas.
"""

import uuid

from django.db import models
from django.db.models import Q

from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada


class AtoDeOrdenacao(models.Model):
    """A ordem emitida sob uma regra e uma versão normativa determinadas."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    edital = models.ForeignKey(Edital, on_delete=models.PROTECT, related_name="atos_de_ordenacao")
    # Identidades publicadas, e não FKs para a elaboração: Retificação pode acrescentar e remover
    # itens sem criar ou apagar a linha correspondente nos modelos de rascunho.
    perfil_id = models.UUIDField()
    marco_id = models.UUIDField()
    versao = models.ForeignKey(
        VersaoConsolidada, on_delete=models.PROTECT, related_name="atos_de_ordenacao"
    )
    ato_anterior = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="sucessores",
    )
    motivo_da_sucessao = models.TextField(blank=True, default="")
    # Resumo suficiente para identificar entradas e comparar obsolescência; a regra continua sob
    # a autoridade única de ``versao`` e não é copiada para cá.
    universo = models.JSONField(default=dict)
    emitido_por = models.CharField(max_length=255)
    emitido_em = models.DateTimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["edital", "perfil_id", "marco_id"],
                condition=Q(ato_anterior__isnull=True),
                name="uq_ato_raiz_por_marco",
            ),
            models.UniqueConstraint(
                fields=["ato_anterior"],
                condition=Q(ato_anterior__isnull=False),
                name="uq_ato_sucessor_unico",
            ),
            models.CheckConstraint(
                condition=Q(ato_anterior__isnull=True) | ~Q(motivo_da_sucessao=""),
                name="ck_sucessao_com_motivo",
            ),
        ]
        indexes = [models.Index(fields=["edital", "perfil_id", "marco_id"])]

    def __str__(self):
        return f"Ordem {self.marco_id} — {self.emitido_em}"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise TypeError("AtoDeOrdenacao é append-only")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise TypeError("AtoDeOrdenacao é append-only")


class PosicaoNaOrdem(models.Model):
    """Uma participante considerada, com posição ou com o motivo de não a receber."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ato = models.ForeignKey(AtoDeOrdenacao, on_delete=models.CASCADE, related_name="posicoes")
    inscricao = models.ForeignKey(
        Inscricao, on_delete=models.PROTECT, related_name="posicoes_na_ordem"
    )
    posicao = models.PositiveIntegerField(null=True, blank=True)
    # A entrada possui quatro casas e o arredondamento publicado usa de zero a quatro. Os dígitos
    # inteiros adicionais evitam transformar o armazenamento numa restrição normativa da soma.
    pontuacao_combinada = models.DecimalField(
        max_digits=19, decimal_places=4, null=True, blank=True
    )
    modalidade_id = models.UUIDField(null=True, blank=True)
    consequencia = models.CharField(max_length=20)
    motivo = models.TextField(blank=True, default="")
    empate_residual = models.BooleanField(default=False)
    desempate = models.JSONField(default=list)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["ato", "inscricao"], name="uq_posicao_por_ato_inscricao"
            ),
            models.CheckConstraint(
                condition=(
                    Q(posicao__isnull=False, posicao__gte=1, motivo="")
                    | Q(posicao__isnull=True) & ~Q(motivo="")
                ),
                name="ck_posicao_ou_motivo",
            ),
        ]
        indexes = [models.Index(fields=["ato", "posicao"])]

    def __str__(self):
        return f"{self.ato_id} — {self.inscricao_id}: {self.posicao or 'sem posição'}"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise TypeError("PosicaoNaOrdem é append-only")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise TypeError("PosicaoNaOrdem é append-only")
