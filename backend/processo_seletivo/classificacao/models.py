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


class OrigemDaOrdem(models.TextChoices):
    """De onde a ordem veio: do cálculo por Etapas, ou de um sorteio (021, FR-034)."""

    COMPUTADO = "COMPUTADO", "Computado a partir de Etapas"
    SORTEIO = "SORTEIO", "Constituído por sorteio"


class AtoDeOrdenacao(models.Model):
    """A ordem emitida sob uma regra e uma versão normativa determinadas."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    edital = models.ForeignKey(Edital, on_delete=models.PROTECT, related_name="atos_de_ordenacao")
    # Identidades publicadas, e não FKs para a elaboração: Retificação pode acrescentar e remover
    # itens sem criar ou apagar a linha correspondente nos modelos de rascunho.
    perfil_id = models.UUIDField()
    marco_id = models.UUIDField()
    # A dimensão da lista de concorrência (021, D-006, FR-035). `NULL` = ampla concorrência, que é
    # o que todo ato emitido antes desta feature é.
    lista_id = models.UUIDField(null=True, blank=True)
    # **Com default e não anulável**, pela razão que `EtapaAvaliacao.forma` já registrou: `NULL` e
    # `"COMPUTADO"` descreveriam o mesmo ato com bytes diferentes, e todo ato existente **é**
    # computado (021, FR-034).
    origem = models.CharField(
        max_length=20, choices=OrigemDaOrdem.choices, default=OrigemDaOrdem.COMPUTADO
    )
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
    #
    # **Num ato constituído por sorteio ele guarda a proveniência, e não um resumo de Etapas**
    # (021, FR-069):
    #
    #     {"editalId": …, "profileId": …, "milestoneId": …, "versionId": …,
    #      "stageResults": [],
    #      "origem": "SORTEIO", "sorteioId": …, "relacaoId": …,
    #      "relationHash": …, "quantidade": N}
    #
    # **As cinco primeiras chaves não são escolha nossa**: a trigger `check_ordering_act_provenance`
    # exige que as quatro identidades coincidam com as colunas do ato e que o marco exista na
    # versão citada, e confere cada item de `stageResults` contra a linha append-only do Resultado.
    # `[]` é a resposta verdadeira para um sorteio — nenhuma Etapa o produziu —, e a trigger a
    # aceita porque já lê a coleção com `COALESCE`.
    #
    # As duas alternativas erradas foram consideradas e recusadas. Deixá-lo `{}` sequer atravessa a
    # trigger, e antes disso faria o ato passar pela leitura sem denunciar nada e quebrar na
    # comparação, longe da causa. Enchê-lo com a forma de um ato computado mentiria sobre a origem,
    # e faria `comparar()` acusar divergência a cada mudança de Etapa num marco que não depende de
    # Etapa nenhuma. É a chave ``origem`` daqui que `estado_do_marco` usa para despachar.
    universo = models.JSONField(default=dict)
    emitido_por = models.CharField(max_length=255)
    emitido_em = models.DateTimeField()

    class Meta:
        constraints = [
            # **A constraint parte em duas parciais** (021, R-001, D-006). A primeira mantém,
            # palavra por palavra, a garantia de hoje para o ato sem lista: dois atos raiz de ampla
            # concorrência no mesmo marco continuam sendo recusados. A segunda abre a dimensão que
            # o certame com cotas exige — três listas, três atos raiz, um marco só, porque a janela
            # recursal é do marco e os Editais publicam **um** período para as três.
            models.UniqueConstraint(
                fields=["edital", "perfil_id", "marco_id"],
                condition=Q(ato_anterior__isnull=True, lista_id__isnull=True),
                name="uq_ato_raiz_por_marco",
            ),
            models.UniqueConstraint(
                fields=["edital", "perfil_id", "marco_id", "lista_id"],
                condition=Q(ato_anterior__isnull=True, lista_id__isnull=False),
                name="uq_ato_raiz_por_marco_e_lista",
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


class CitacaoDeDecisao(models.Model):
    """O ato de ordenação declara **qual decisão de recurso ele executa**.

    A providência a jusante nomeia o remédio e não o executa (FR-049): quem executa é quem tem a
    autoridade da 015. O que prova o cumprimento é esta citação — e ela prova de verdade **só quando
    o ato é publicado**, porque um ato que fica obsoleto antes disso não corrigiu coisa alguma
    (T-015, FR-112).

    **`UNIQUE(ato, decisao)` e nada mais.** Um `UNIQUE(decisao)` — que uma redação anterior previa —
    criaria dois defeitos de uma vez:

    - **um beco permanente**: ficando obsoleto o ato citante antes da publicação, nenhum sucessor
      poderia recitar a decisão, e a definitiva daquele marco ficaria impedida para sempre;
    - **pertinência a um marco só**: uma decisão cuja providência é normativa alcança todos os
      marcos que a regra retificada governa, e cada um precisa do seu ato citante publicado.

    Ela é **proveniência do ato**, do mesmo tipo de `motivo_da_sucessao`: não tem autoridade,
    instante nem motivo próprios, e não é passo humano separado que se possa esquecer. Nasce com o
    ato, na mesma transação, por quem já tem autoridade para emiti-lo.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ato = models.ForeignKey(AtoDeOrdenacao, on_delete=models.PROTECT, related_name="citacoes")
    decisao = models.ForeignKey(
        "recursos.DecisaoRecurso", on_delete=models.PROTECT, related_name="citacoes"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["ato", "decisao"], name="uq_citacao_ato_decisao"),
        ]
        indexes = [models.Index(fields=["decisao"])]

    def __str__(self):
        return f"{self.ato_id} cita {self.decisao_id}"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise TypeError("CitacaoDeDecisao é append-only")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise TypeError("CitacaoDeDecisao é append-only")
