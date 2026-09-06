"""O ato de divulgar um resultado, a situação individual que ele congela e o seu documento.

As três tabelas são append-only nas três camadas: `save` e `delete` recusam, a trigger recusa
mesmo quem tem privilégio, e o papel de runtime não possui `UPDATE` nem `DELETE` sobre elas
(FR-040, FR-071). **Toda sucessão é linha nova** — não há coluna de vigência a alternar, e vigente
é a publicação que ninguém sucedeu (T-002).

**O individual não mora no conteúdo publicado.** `PublicacaoResultado.conteudo_publico` guarda só
o que foi divulgado; a situação de cada participante considerado vai para `SituacaoDivulgada`. A
separação é de tabela, e não de chave dentro de um mesmo registro: é o que permite à leitura
pública **não ter caminho** para o dado individual, em vez de tê-lo e confiar que ninguém o
percorre (T-010, T-013).

O agregado **não tem máquina de estados** porque não tem ciclo de vida: nasce publicado e é
sucedido por outra linha, ou não é (FR-046).
"""

import uuid

from django.db import models
from django.db.models import Q

from processo_seletivo.classificacao.models import AtoDeOrdenacao
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.processos.models import Edital


class Natureza(models.TextChoices):
    """A ordem entre as duas tem sentido único: preliminar não sucede definitiva (D-007)."""

    PRELIMINAR = "PRELIMINAR", "Resultado preliminar"
    DEFINITIVA = "DEFINITIVA", "Resultado definitivo"


class PublicacaoResultado(models.Model):
    """O ato institucional de divulgação de um `AtoDeOrdenacao` (FR-001)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    edital = models.ForeignKey(
        Edital, on_delete=models.PROTECT, related_name="publicacoes_de_resultado"
    )
    # `PROTECT` porque a origem não pode desaparecer sob a publicação que a cita.
    ato = models.ForeignKey(
        AtoDeOrdenacao, on_delete=models.PROTECT, related_name="publicacoes_de_resultado"
    )
    # Identidades publicadas, e não FKs para a elaboração — a mesma razão da 015: Retificação pode
    # acrescentar e remover itens sem criar ou apagar a linha correspondente no rascunho.
    perfil_id = models.UUIDField()
    marco_id = models.UUIDField()
    natureza = models.CharField(max_length=20, choices=Natureza.choices)
    publicacao_anterior = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="sucessoras",
    )
    # Os bytes canônicos **do que foi divulgado**, e nada além (T-003). Congelar a projeção é o
    # que impede uma correção futura de reescrever em silêncio o que já foi publicado.
    conteudo_publico = models.BinaryField()
    conteudo_publico_hash = models.CharField(max_length=64, db_index=True)
    publicado_por = models.CharField(max_length=255)
    publicado_em = models.DateTimeField()
    signatario_id = models.UUIDField()
    # Nome e cargo são persistidos: retirar a autoridade do catálogo não altera ato já praticado.
    signatario_nome = models.CharField(max_length=255)
    signatario_cargo = models.CharField(max_length=255)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["edital", "perfil_id", "marco_id"],
                condition=Q(publicacao_anterior__isnull=True),
                name="uq_publicacao_raiz_por_marco",
            ),
            models.UniqueConstraint(
                fields=["publicacao_anterior"],
                condition=Q(publicacao_anterior__isnull=False),
                name="uq_publicacao_sucessora_unica",
            ),
            # A resposta a "o mesmo ato pode ser publicado duas vezes?": pode, **uma vez por
            # natureza** (D-007, FR-039). Um preliminar que ninguém contestou vira definitivo sem
            # que exista ato novo a emitir; a mesma natureza duas vezes é duplicidade, e o banco a
            # recusa — o que dá ao cenário das duas abas uma garantia de banco, e não só de
            # idempotência.
            models.UniqueConstraint(
                fields=["ato", "natureza"],
                name="uq_publicacao_por_ato_natureza",
            ),
        ]
        indexes = [models.Index(fields=["edital", "perfil_id", "marco_id"])]

    def __str__(self):
        return f"{self.get_natureza_display()} — {self.publicado_em}"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise TypeError("PublicacaoResultado é append-only")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise TypeError("PublicacaoResultado é append-only")


class SituacaoDivulgada(models.Model):
    """A situação de **uma** pessoa naquela divulgação — inclusive quem não recebeu posição.

    Não é segunda fonte de verdade (FR-058): nasce na mesma transação, do mesmo ato imutável que
    produziu a lista pública, e aponta para a publicação que a originou. O que a FR-058 proíbe é
    uma fonte **viva**, que mudasse com o ato enquanto a publicação permanece histórica.
    """

    class Situacao(models.TextChoices):
        CLASSIFICADA = "CLASSIFICADA", "Classificada"
        SEM_POSICAO = "SEM_POSICAO", "Sem posição"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # `CASCADE` descreve a pertinência — a projeção é parte da publicação e não tem vida sem ela.
    # Na prática nada é apagado: a publicação é append-only, e a exclusão não existe como operação.
    publicacao = models.ForeignKey(
        PublicacaoResultado, on_delete=models.CASCADE, related_name="situacoes"
    )
    # `PROTECT` pelo oposto: a Inscrição não pode desaparecer sob a divulgação que a nomeia.
    inscricao = models.ForeignKey(
        Inscricao, on_delete=models.PROTECT, related_name="situacoes_divulgadas"
    )
    situacao = models.CharField(max_length=20, choices=Situacao.choices)
    posicao = models.PositiveIntegerField(null=True, blank=True)
    compartilhada = models.BooleanField(default=False)
    # Já na apresentação institucional (`185,00`): texto, e não decimal — reformatar na leitura
    # seria decidir de novo o que o ato já decidiu.
    pontuacao = models.CharField(max_length=32, blank=True, default="")
    motivo = models.TextField(blank=True, default="")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["publicacao", "inscricao"],
                name="uq_situacao_por_publicacao_inscricao",
            )
        ]
        # Por este índice o acompanhamento encontra a linha da pessoa, sem varrer publicação.
        indexes = [models.Index(fields=["inscricao"])]

    def __str__(self):
        return f"{self.inscricao_id}: {self.situacao}"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise TypeError("SituacaoDivulgada é append-only")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise TypeError("SituacaoDivulgada é append-only")


class DocumentoDoResultado(models.Model):
    """Os bytes do documento oficial, no molde de `DocumentoPublicado`.

    Tabela própria, e não coluna anulável na publicação: até a US4 as publicações nascem sem
    documento, e a ausência de linha representa isso sem deixar coluna a limpar depois (T-007).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    publicacao = models.OneToOneField(
        PublicacaoResultado, on_delete=models.PROTECT, related_name="documento"
    )
    bytes = models.BinaryField()
    content_type = models.CharField(max_length=100, default="application/pdf")
    # Integridade, **não** unicidade: dois documentos idênticos são legítimos.
    documento_hash = models.CharField(max_length=64, db_index=True)

    def __str__(self):
        return f"Documento de {self.publicacao_id}"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise TypeError("DocumentoDoResultado é append-only")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise TypeError("DocumentoDoResultado é append-only")
