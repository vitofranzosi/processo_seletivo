"""O manifesto dos cenários de treinamento (134, FR-4610 a FR-4614).

**Uma linha por rodada de cenário, e nenhuma linha de domínio.** O que o gerador cria — Processo,
Editais, inscrições, atos — é criado pelos comandos da aplicação, com a trilha deles; o que mora
aqui é só a prova de quem criou o quê, para que listar, verificar e restaurar não dependam do
prefixo do código, que qualquer pessoa pode digitar na tela de criação de Processo.

**Não é append-only, e de propósito**: a restauração marca a rodada anterior como substituída. O
que ela **nunca** faz é apagar — nem a linha daqui, nem o que a linha aponta (`on_delete=PROTECT`).
"""

import uuid

from django.db import models
from django.db.models import Q


class CenarioDeTreinamento(models.Model):
    class Situacao(models.TextChoices):
        # Gravada na mesma transação que criou o cenário, e por isso só existe se ele existe
        # inteiro: não há "em criação" persistido, porque não há criação pela metade (FR-4612).
        PRONTO = "PRONTO", "Pronto"
        # A rodada que uma restauração trocou por outra. Os registros dela continuam no banco,
        # com o Processo cancelado pelo comando de cancelamento — nada se exclui (FR-4621).
        SUBSTITUIDO = "SUBSTITUIDO", "Substituído"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    unidade = models.CharField(max_length=100)
    codigo = models.CharField(max_length=8)
    rodada = models.PositiveSmallIntegerField()
    versao_da_definicao = models.CharField(max_length=20)
    situacao = models.CharField(max_length=12, choices=Situacao.choices, default=Situacao.PRONTO)
    processo = models.OneToOneField(
        "processos.ProcessoSeletivo",
        on_delete=models.PROTECT,
        related_name="cenario_de_treinamento",
    )
    correlation_id = models.CharField(max_length=100)
    # Os identificadores de tudo o que a geração criou, por espécie — o que a verificação confere
    # e a listagem conta. Identificadores, e não cópia: o estado é sempre o do banco.
    registros = models.JSONField(default=dict)
    # As contagens do cenário no instante em que ficou pronto (`retrato.py`): é a comparação com
    # elas que diz se alguém já exercitou o cenário (FR-4613).
    retrato = models.JSONField(default=dict)
    banco = models.CharField(max_length=100)
    criado_em = models.DateTimeField()
    criado_por = models.CharField(max_length=100)
    substituido_em = models.DateTimeField(null=True, blank=True)
    substituido_por = models.OneToOneField(
        "self", null=True, blank=True, on_delete=models.PROTECT, related_name="substitui"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["unidade", "codigo", "rodada"], name="uq_cenario_unidade_codigo_rodada"
            ),
            # Uma rodada em uso por cenário e unidade: é o que torna "o C07" uma referência sem
            # ambiguidade para a restauração (FR-4622).
            models.UniqueConstraint(
                fields=["unidade", "codigo"],
                condition=Q(situacao="PRONTO"),
                name="uq_cenario_pronto_por_unidade",
            ),
        ]

    def __str__(self):
        return f"{self.codigo} rodada {self.rodada} ({self.get_situacao_display()})"
