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
from processo_seletivo.duvidas.domain.habilitacao import PAGINA_PUBLICA, PILOTO


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


class HabilitacaoDoAssistente(models.Model):
    """Um ato de habilitar ou desabilitar uma frente do assistente (170, data-model.md).

    **Append-only, com as duas travas de sempre** (FR-7527): o gatilho que recusa `UPDATE` e
    `DELETE`, e o privilégio ausente, pela entrada em `seguranca/papeis.py`. Desabilitar é ato
    novo, e o estado de uma frente é o último ato dela — sem ato nenhum, desabilitada.

    **A ordem é da frente, e não do relógio** (R-2). Os atos de uma frente são serializados por
    trava consultiva, e a ordem é alocada sob ela, como a da `TrocaDoPiloto`. A chave é UUID porque
    a trilha guarda o agregado como UUID: uma chave inteira viraria `UUID(int=pk)` em silêncio,
    defeito que a `108` registrou no aviso interrompido.

    **Nenhum valor do ambiente vem para cá** (FR-7500): nem serviço, nem modelo, nem credencial. O
    que se guarda é a decisão, o motivo e quem decidiu.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    frente = models.CharField(max_length=16)
    # Só da página pública, e obrigatório nela: o piloto é um por implantação (Q-1).
    edital = models.ForeignKey(
        "processos.Edital",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="habilitacoes_do_assistente",
    )
    ordem = models.PositiveIntegerField()
    habilitada = models.BooleanField()
    motivo = models.TextField()
    # O `subject` da pessoa institucional; o nome se resolve como na trilha da `108`.
    autor = models.CharField(max_length=255)
    criado_em = models.DateTimeField()

    class Meta:
        db_table = "duvidas_habilitacao_do_assistente"
        ordering = ("frente", "edital", "ordem")
        constraints = [
            models.CheckConstraint(
                condition=(Q(frente=PILOTO) & Q(edital__isnull=True))
                | (Q(frente=PAGINA_PUBLICA) & Q(edital__isnull=False)),
                name="ck_habilitacao_frente_e_edital",
            ),
            models.CheckConstraint(condition=Q(ordem__gte=1), name="ck_habilitacao_ordem_positiva"),
            models.CheckConstraint(
                condition=~Q(motivo__regex=r"^\s*$"), name="ck_habilitacao_motivo_preenchido"
            ),
            models.UniqueConstraint(
                fields=("ordem",),
                condition=Q(frente=PILOTO),
                name="uq_habilitacao_ordem_do_piloto",
            ),
            models.UniqueConstraint(
                fields=("edital", "ordem"),
                condition=Q(frente=PAGINA_PUBLICA),
                name="uq_habilitacao_ordem_do_edital",
            ),
        ]

    def __str__(self):
        sentido = "habilitada" if self.habilitada else "desabilitada"
        return f"{self.frente} {self.edital_id or ''} #{self.ordem} — {sentido}"
