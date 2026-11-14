"""A agenda da Etapa: a configuração e quem está em que horário agora (167, entrega A).

**Quatro tabelas operacionais**, e nenhuma lista de participantes (`D-002`): quem precisa de horário
é quem a participação da Etapa põe nela, a cada leitura. Os horários não são gravados (`D-003`):
são derivados da configuração, e só o agendamento é linha — com as duas unicidades no banco, que
são a última guarda da FR-7211 sob operações simultâneas (T-009).

**A Etapa é referida pelo `etapa_id`, sem chave estrangeira**, como a alocação da comissão: depois
da publicação, a fonte dela é a Versão Consolidada, e a Etapa acrescentada por Retificação não tem
linha em `EtapaAvaliacao` (FR-7201, T-002).

Os atos — a publicação, a remarcação, a inclusão e o cancelamento — são append-only e chegam na
entrega B. "Publicada" não será coluna: será existir o ato.
"""

import uuid

from django.db import models
from django.db.models.functions import Lower

from processo_seletivo.agendamento.domain import nomes


class AgendaDaEtapa(models.Model):
    """A configuração de uma Etapa: forma, duração, intervalo, orientações. Uma por Etapa."""

    class Forma(models.TextChoices):
        REMOTA = nomes.REMOTA, "Videoconferência"
        PRESENCIAL = nomes.PRESENCIAL, "Presencial"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    edital = models.ForeignKey(
        "processos.Edital", on_delete=models.PROTECT, related_name="agendas_das_etapas"
    )
    etapa_id = models.UUIDField()
    forma = models.CharField(max_length=20, choices=Forma.choices)
    duracao_minutos = models.IntegerField()
    intervalo_minutos = models.IntegerField()
    orientacoes = models.TextField(blank=True)
    # **Sobe a cada escrita da agenda** — configuração, agendamento, preenchimento —, e entra na
    # assinatura da prévia (T-010). Sozinha ela não basta: a participação muda sem tocar a agenda.
    revision = models.PositiveIntegerField(default=1)
    criada_por = models.CharField(max_length=255)
    criada_em = models.DateTimeField()
    atualizada_por = models.CharField(max_length=255)
    atualizada_em = models.DateTimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["edital", "etapa_id"], name="uq_agenda_por_etapa"),
            models.CheckConstraint(
                condition=models.Q(duracao_minutos__gt=0), name="ck_agenda_duracao_positiva"
            ),
            models.CheckConstraint(
                condition=models.Q(intervalo_minutos__gte=0),
                name="ck_agenda_intervalo_nao_negativo",
            ),
        ]

    def __str__(self):
        return f"agenda da Etapa {self.etapa_id} do Edital {self.edital_id}"


class JanelaDaAgenda(models.Model):
    """Um dia e um intervalo de horas. Sobreposição e "menor que a duração" são do domínio, porque
    dependem de outras linhas e da duração da agenda (`configuracao.problemas`)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agenda = models.ForeignKey(AgendaDaEtapa, on_delete=models.CASCADE, related_name="janelas")
    dia = models.DateField()
    inicio = models.TimeField()
    fim = models.TimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["agenda", "dia", "inicio"], name="uq_janela_inicio"),
            models.CheckConstraint(
                condition=models.Q(inicio__lt=models.F("fim")),
                name="ck_janela_inicio_antes_do_fim",
            ),
        ]

    def __str__(self):
        return f"janela {self.dia} {self.inicio}–{self.fim}"


class BancaDaAgenda(models.Model):
    """O ponto de atendimento (`D-004`), com identidade estável entre edições da configuração.

    `acesso` é o local, no presencial, ou o endereço da sala, no remoto. Nunca entra na trilha
    (FR-7256), e o endereço da sala nunca entra no que é público (FR-7226).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agenda = models.ForeignKey(AgendaDaEtapa, on_delete=models.CASCADE, related_name="bancas")
    nome = models.CharField(max_length=80)
    acesso = models.TextField(blank=True)
    ordem = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.CheckConstraint(condition=~models.Q(nome=""), name="ck_banca_com_nome"),
            models.UniqueConstraint(Lower("nome"), "agenda", name="uq_banca_nome"),
        ]

    def __str__(self):
        return self.nome


class Agendamento(models.Model):
    """Quem está em que horário agora, com a origem, o autor e o instante (FR-7216).

    **É o estado corrente**, e a montagem o cria, o muda e o apaga. Apagar a linha não perde
    história: a trilha guarda o estado anterior e o posterior de cada gesto (FR-7256), e o que vier
    a ser publicado mora no append-only da entrega B. É a leitura que a Constituição faz da exclusão
    física — proibida quando compromete a rastreabilidade —, e o mesmo estatuto do rascunho.
    """

    class Origem(models.TextChoices):
        MANUAL = nomes.MANUAL, "à mão"
        AUTOMATICA = nomes.AUTOMATICA, "automático"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agenda = models.ForeignKey(AgendaDaEtapa, on_delete=models.CASCADE, related_name="agendamentos")
    inscricao = models.ForeignKey(
        "inscricoes.Inscricao", on_delete=models.PROTECT, related_name="agendamentos_da_etapa"
    )
    banca = models.ForeignKey(BancaDaAgenda, on_delete=models.PROTECT, related_name="agendamentos")
    inicio = models.DateTimeField()
    fim = models.DateTimeField()
    origem = models.CharField(max_length=20, choices=Origem.choices)
    feito_por = models.CharField(max_length=255)
    feito_em = models.DateTimeField()

    class Meta:
        constraints = [
            # As duas unicidades da FR-7211, e a última guarda delas (T-009): a trava da agenda
            # serializa os gestos, e estas recusam o que escapasse dela.
            models.UniqueConstraint(
                fields=["agenda", "inscricao"], name="uq_agendamento_inscricao"
            ),
            models.UniqueConstraint(
                fields=["agenda", "banca", "inicio"], name="uq_agendamento_horario"
            ),
        ]

    def __str__(self):
        return f"agendamento {self.inscricao_id} em {self.inicio}"
