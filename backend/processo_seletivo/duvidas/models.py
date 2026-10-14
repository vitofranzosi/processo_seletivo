"""O registro do piloto do assistente do Edital (071, data-model §3).

**Uma tabela, duas funções** (`R-011`). `TrocaDoPiloto` é o histórico da conversa — o que o servidor
lê para montar o contexto da pergunta seguinte, e que por isso o navegador não pode forjar
(`FR-1494`) — e é o registro da avaliação (`FR-1509`). Duas estruturas para os mesmos turnos teriam
de concordar; uma só não tem como divergir.

**Nenhuma coluna identifica o participante** (`FR-1509`). O alcance e a permissão se verificam pela
identidade da sessão, a cada pergunta, e não ficam aqui. A pergunta e a resposta chegam mascaradas
— CPF, e-mail e telefone —, o que **não** é anonimização: um nome escrito por extenso passa.

**Não é append-only, e não é dado normativo.** Nada aqui é ato do certame: é a evidência de uma
avaliação, excluída por comando 90 dias depois do relatório final (`R-021`). O "nada é excluído" do
projeto é sobre dado normativo, e esta tabela não está em `TABELAS_APPEND_ONLY`.
"""

import uuid

from django.db import models
from django.db.models import Q

from processo_seletivo.duvidas.domain.estruturas_do_piloto import ESTADOS, ORIGENS, TIPOS


class TrocaDoPiloto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversa = models.UUIDField(db_index=True)
    # Alocada na gravação, sob trava da conversa, e não antes da chamada: duas abas gravam na ordem
    # em que terminam, sem estado intermediário (data-model §3).
    ordem = models.PositiveIntegerField()
    edital = models.ForeignKey(
        "processos.Edital", on_delete=models.PROTECT, related_name="trocas_do_piloto"
    )
    criada_em = models.DateTimeField(auto_now_add=True)
    # O instante em que a versão foi determinada: o da gravação na tela, o do caso na avaliação. Os
    # dois coincidem na tela, e por isso parecem um só — na avaliação não coincidem (princípio II).
    instante = models.DateTimeField()
    origem = models.CharField(max_length=16)
    versao = models.UUIDField(null=True, blank=True)
    versao_curta = models.CharField(max_length=32, blank=True)
    pergunta = models.TextField()
    estado = models.CharField(max_length=40)
    # Vazio quando a saída não chegou a ter forma: recusa antes da chamada, falha do serviço.
    tipo = models.CharField(max_length=40, blank=True)
    trechos = models.JSONField(null=True, blank=True)
    fontes_citadas = models.JSONField(null=True, blank=True)
    conferencia = models.JSONField(null=True, blank=True)
    historico_desde = models.PositiveIntegerField(null=True, blank=True)
    chamou_o_servico = models.BooleanField(default=False)
    servico = models.CharField(max_length=16)
    modelo_configurado = models.CharField(max_length=200)
    modelo_que_respondeu = models.CharField(max_length=200, blank=True)
    parametros = models.JSONField(default=dict)
    impressao_das_fontes = models.CharField(max_length=64, blank=True)
    versao_das_instrucoes = models.CharField(max_length=16)

    class Meta:
        ordering = ("conversa", "ordem")
        constraints = [
            models.UniqueConstraint(fields=("conversa", "ordem"), name="uq_troca_conversa_ordem"),
            models.CheckConstraint(condition=Q(ordem__gte=1), name="ck_troca_ordem_positiva"),
            models.CheckConstraint(condition=Q(estado__in=ESTADOS), name="ck_troca_estado"),
            models.CheckConstraint(condition=Q(tipo="") | Q(tipo__in=TIPOS), name="ck_troca_tipo"),
            models.CheckConstraint(condition=Q(origem__in=ORIGENS), name="ck_troca_origem"),
        ]

    def __str__(self):
        return f"{self.conversa} #{self.ordem} — {self.estado}"
