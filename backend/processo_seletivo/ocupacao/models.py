"""A apuração de ocupação e o movimento de vaga — os dois append-only (016, `D-008`).

**Ato, e não projeção.** A decisão do usuário de 12/09/2026 fechou que a apuração é ato sucedido a
cada mudança, como a ordem da `015` e o corte da `014` já são. Projeção foi recusada pelo que ela
perde: o número de ontem não é recuperável se os atos-fonte mudarem de leitura, e ocupação é
exatamente o número que alguém vai contestar.

**Vigência e obsolescência não são colunas.** Mantê-las exigiria `UPDATE`, operação proibida nestas
tabelas — o provisionamento instala e verifica a proibição. Vigente é a apuração que ninguém
sucedeu no recorte; obsolescência é **calculada**, com as causas nomeadas, em
`application/selectors.py`. Quem acrescentar a coluna não é barrado ao criá-la: é barrado quando
tentar atualizá-la, que é o modo de falha mais tardio possível.
"""

import uuid

from django.db import models
from django.db.models import F, Q

from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.ocupacao.domain import nomes
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.models import VersaoConsolidada


class ApuracaoDeOcupacao(models.Model):
    """Quantas vagas um recorte publicou, quantas tem efetivamente, e quantas estão ocupadas.

    **Três quantidades são colunas e a quarta não é.** `faltando` é `efetivas - ocupadas`,
    aritmética da mesma linha — guardá-la seria armazenar o derivável. `efetivas`, ao contrário,
    **precisa** ser coluna: depende de somar movimentos, e `CHECK` não agrega (016, `R-006`).

    **`publicadas` nunca muda por movimento** (`FR-239a`). O que a reversão move é a quantidade
    efetiva; o publicado é intocável, e sem esta separação reverter faria o sistema afirmar que o
    Edital publicou um número que ele não publicou.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    edital = models.ForeignKey(Edital, on_delete=models.PROTECT, related_name="apuracoes")
    # Identidades publicadas, e não FKs para a elaboração, pela razão que `AtoDeOrdenacao` e
    # `Corte` já registram: Retificação acrescenta e remove itens sem criar ou apagar a linha do
    # rascunho.
    perfil_id = models.UUIDField()
    marco_id = models.UUIDField()
    # `NULL` = ampla concorrência, a mesma grafia da ordem, do corte e do quadro de vagas.
    lista_id = models.UUIDField(null=True, blank=True)
    ato = models.ForeignKey(
        "classificacao.AtoDeOrdenacao", on_delete=models.PROTECT, related_name="apuracoes"
    )
    # Nula onde o recorte não tem corte: marco que não corta continua podendo ter ocupação apurada,
    # e nesse caso a faixa é o universo inteiro do ato.
    corte = models.ForeignKey(
        "classificacao.Corte",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="apuracoes",
    )
    versao = models.ForeignKey(
        VersaoConsolidada, on_delete=models.PROTECT, related_name="apuracoes"
    )
    apuracao_anterior = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.PROTECT, related_name="sucessoras"
    )
    motivo_da_sucessao = models.TextField(blank=True, default="")
    publicadas = models.PositiveIntegerField()
    efetivas = models.PositiveIntegerField()
    ocupadas = models.PositiveIntegerField()
    # **Qual** linha do quadro foi lida. É a lição literal do `Corte`, que guarda o `rowId` do alvo
    # derivado: sem ela, retificado o quadro, não há como dizer se **esta** apuração ficou para
    # trás — a quantidade sozinha não identifica a linha (`FR-263`).
    linha_do_quadro_id = models.UUIDField(null=True, blank=True)
    # Quadro, declaração de reversão, recusas e `movimentosLidos` congelados no instante da
    # emissão. Os ids dos movimentos não são decoração: reproduzir é reler **aqueles** ids, e não
    # os movimentos de hoje (`FR-244`).
    universo = models.JSONField(default=dict)
    emitida_por = models.CharField(max_length=255)
    emitida_em = models.DateTimeField()

    class Meta:
        constraints = [
            # **As duas de primeira apuração não são redundantes**: no PostgreSQL dois `NULL` não
            # colidem, e uma só deixaria passar duas primeiras apurações de ampla concorrência no
            # mesmo marco. É a cirurgia de `uq_corte_raiz_por_marco`, e pela mesma razão —
            # verificada contra o banco antes de entrar aqui.
            models.UniqueConstraint(
                fields=["edital", "perfil_id", "marco_id"],
                condition=Q(apuracao_anterior__isnull=True, lista_id__isnull=True),
                name="uq_apuracao_primeira_por_marco",
            ),
            models.UniqueConstraint(
                fields=["edital", "perfil_id", "marco_id", "lista_id"],
                condition=Q(apuracao_anterior__isnull=True, lista_id__isnull=False),
                name="uq_apuracao_primeira_por_marco_e_lista",
            ),
            # **Uma sucessora por apuração.** Sem esta, duas apurações sucedem a mesma anterior e o
            # recorte fica com duas vigentes — e vigência é derivada justamente de "ninguém me
            # sucedeu". É a cópia de `uq_geracao_sucessora_unica`, que existe pela mesma razão.
            models.UniqueConstraint(
                fields=["apuracao_anterior"],
                condition=Q(apuracao_anterior__isnull=False),
                name="uq_apuracao_sucessora_unica",
            ),
            # O limite é contra **efetivas**, e não contra publicadas: recebida a reversão, a linha
            # geral passa de 28 para 35, e as 35 são ocupáveis. Comparar com `publicadas` recusaria
            # o ato justamente no cenário de sucesso da feature.
            models.CheckConstraint(
                condition=Q(ocupadas__lte=F("efetivas")), name="ck_apuracao_ocupadas_no_limite"
            ),
            # Sucessão exige motivo, e a primeira apuração não o tem. É a mesma forma que o
            # `AtoDeOrdenacao` usa para `motivo_da_sucessao`.
            models.CheckConstraint(
                condition=Q(apuracao_anterior__isnull=True) | ~Q(motivo_da_sucessao=""),
                name="ck_apuracao_sucessao_com_motivo",
            ),
        ]
        indexes = [
            models.Index(
                fields=["edital", "perfil_id", "marco_id", "lista_id"],
                name="ix_apuracao_recorte",
            )
        ]

    def __str__(self):
        return f"{self.perfil_id}/{self.lista_id or 'ampla'} — {self.ocupadas}/{self.efetivas}"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise TypeError("ApuracaoDeOcupacao é append-only")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise TypeError("ApuracaoDeOcupacao é append-only")

    @property
    def faltando(self):
        """`efetivas - ocupadas`, nunca negativo. Não é coluna, de propósito."""
        return max(self.efetivas - self.ocupadas, 0)


class MovimentoDeVaga(models.Model):
    """A vaga que muda de recorte — nos **dois** sentidos, na mesma entidade.

    Reversão move quantidade da cota para a linha geral; liberação devolve ao recorte reservado a
    vaga de quem ocupou pela ampla. São o mesmo fato — uma quantidade que sai de um recorte e entra
    em outro — e separá-los faria o invariante da soma ter de somar duas tabelas.

    **Trocar os sentidos mantém a soma certa com o recorte errado**, e é o defeito mais provável
    desta feature: só asserção de recorte o pega (`FR-253`).

    **O movimento nasce com a apuração da origem**, na mesma transação que o determina; a apuração
    do destino o **lê** por `destino_lista_id` e nunca cria um segundo registro.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    apuracao = models.ForeignKey(
        ApuracaoDeOcupacao, on_delete=models.PROTECT, related_name="movimentos"
    )
    especie = models.CharField(
        max_length=32,
        choices=[
            (nomes.MOVIMENTO_REVERSAO, "Reversão de cota"),
            (nomes.MOVIMENTO_LIBERACAO, "Liberação por concorrência concomitante"),
        ],
    )
    origem_lista_id = models.UUIDField(null=True, blank=True)
    destino_lista_id = models.UUIDField(null=True, blank=True)
    quantidade = models.PositiveIntegerField()
    causa = models.TextField()
    # Preenchida só na liberação, que é movimento **de pessoa**: é a vaga reservada de quem ocupou
    # pela ampla. A reversão é de quantidade, e não tem inscrição a nomear.
    inscricao = models.ForeignKey(
        Inscricao,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="movimentos_de_vaga",
    )
    registrado_por = models.CharField(max_length=255)
    registrado_em = models.DateTimeField()

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(quantidade__gt=0), name="ck_movimento_quantidade_positiva"
            ),
            # Origem e destino distintos. **`NULL` exige o cuidado de sempre**: em SQL,
            # `NULL = NULL` não é verdadeiro, então a comparação direta deixaria passar
            # `(NULL, NULL)` — a ampla cedendo para a ampla. As duas metades abaixo cobrem isso.
            models.CheckConstraint(
                condition=(
                    Q(origem_lista_id__isnull=True, destino_lista_id__isnull=False)
                    | Q(origem_lista_id__isnull=False, destino_lista_id__isnull=True)
                    | (
                        Q(origem_lista_id__isnull=False, destino_lista_id__isnull=False)
                        & ~Q(origem_lista_id=F("destino_lista_id"))
                    )
                ),
                name="ck_movimento_recortes_distintos",
            ),
            # A liberação é de pessoa; a reversão é de quantidade.
            models.CheckConstraint(
                condition=(
                    Q(especie=nomes.MOVIMENTO_REVERSAO, inscricao__isnull=True)
                    | Q(especie=nomes.MOVIMENTO_LIBERACAO, inscricao__isnull=False)
                ),
                name="ck_movimento_inscricao_conforme_especie",
            ),
        ]
        indexes = [
            models.Index(fields=["destino_lista_id"], name="ix_movimento_destino"),
        ]

    def __str__(self):
        return f"{self.especie} {self.quantidade}: {self.origem_lista_id} → {self.destino_lista_id}"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise TypeError("MovimentoDeVaga é append-only")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise TypeError("MovimentoDeVaga é append-only")
