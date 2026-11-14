"""A agenda da Etapa: a configuração e quem está em que horário agora (167, entrega A).

**Quatro tabelas operacionais**, e nenhuma lista de participantes (`D-002`): quem precisa de horário
é quem a participação da Etapa põe nela, a cada leitura. Os horários não são gravados (`D-003`):
são derivados da configuração, e só o agendamento é linha — com as duas unicidades no banco, que
são a última guarda da FR-7211 sob operações simultâneas (T-009).

**A Etapa é referida pelo `etapa_id`, sem chave estrangeira**, como a alocação da comissão: depois
da publicação, a fonte dela é a Versão Consolidada, e a Etapa acrescentada por Retificação não tem
linha em `EtapaAvaliacao` (FR-7201, T-002).

**Os atos são append-only** (entrega B): a publicação, e depois a remarcação, a inclusão e o
cancelamento. "Publicada" não é coluna: é existir o ato de publicação da agenda, e a leitura é uma
consulta por índice — não há dois fatos para divergir.
"""

import uuid

from django.db import models
from django.db.models import Q
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


# -------------------------------------------------------------------------------------------------
# Os atos da agenda (entrega B): append-only nas três camadas
# -------------------------------------------------------------------------------------------------


class _AppendOnly(models.Model):
    """`save` só de linha nova e `delete` recusado — a primeira das três camadas.

    As outras duas são os gatilhos da `0002` e a falta de `UPDATE` e `DELETE` do papel de runtime
    (`TABELAS_APPEND_ONLY`). Cada uma independe das outras: o gatilho segura quem tem privilégio, e
    o privilégio segura quem desligasse o gatilho.
    """

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise TypeError(f"{type(self).__name__} é append-only")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise TypeError(f"{type(self).__name__} é append-only")


class AtoDaAgenda(_AppendOnly):
    """Publicação, remarcação, inclusão ou cancelamento (FR-7224, FR-7241 a FR-7243).

    **A natureza é a da relação de convocados da `149`** (`D-008`): autoridade e unidade congeladas
    como estavam no dia, conteúdo público em bytes canônicos e o resumo deles. O veículo, que na
    `159` é escolha do fluxo e não coluna, aqui **é** coluna, porque a agenda não tem outra linha
    onde guardá-lo (research T-012).

    **A agenda publica uma vez** (`uq_ato_da_agenda_uma_publicacao`): a confirmação repetida com
    outra chave encontra este índice e devolve o ato existente, sem segundo aviso (SC-2396). O que
    muda depois é ato individual, de uma pessoa (`D-006`).
    """

    class Especie(models.TextChoices):
        PUBLICACAO = nomes.PUBLICACAO, "Publicação"
        REMARCACAO = nomes.REMARCACAO, "Remarcação"
        INCLUSAO = nomes.INCLUSAO, "Inclusão"
        CANCELAMENTO = nomes.CANCELAMENTO, "Cancelamento"

    class Veiculo(models.TextChoices):
        GPS = nomes.VEICULO_GPS, "Página pública do GPS"
        EXTERNO = nomes.VEICULO_EXTERNO, "Fora do GPS"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agenda = models.ForeignKey(AgendaDaEtapa, on_delete=models.PROTECT, related_name="atos")
    # Denormalizado para a página pública da seleção achar as agendas do Edital por índice.
    edital = models.ForeignKey(
        "processos.Edital", on_delete=models.PROTECT, related_name="atos_das_agendas"
    )
    especie = models.CharField(max_length=20, choices=Especie.choices)
    praticado_por = models.CharField(max_length=255)
    praticado_em = models.DateTimeField()
    # Obrigatório nas três individuais e vazio na publicação: fica na trilha e no ato, e nunca
    # aparece ao candidato (FR-7246).
    motivo = models.TextField(blank=True, default="")
    veiculo = models.CharField(max_length=10, choices=Veiculo.choices, blank=True, default="")
    # Onde o Edital admite a página pública do GPS como veículo, nas palavras de quem publica (a
    # FR-5703 da `149`); obrigatória com o veículo GPS.
    declaracao_do_veiculo = models.TextField(blank=True, default="")
    publicado_fora_onde = models.TextField(blank=True, default="")
    publicado_fora_em = models.DateField(null=True, blank=True)
    signatario_id = models.UUIDField(null=True, blank=True)
    signatario_nome = models.CharField(max_length=255, blank=True, default="")
    signatario_cargo = models.CharField(max_length=255, blank=True, default="")
    signatario_ato_de_nomeacao = models.CharField(max_length=255, blank=True, default="")
    unidade_codigo = models.CharField(max_length=100, blank=True, default="")
    unidade_sigla = models.CharField(max_length=30, blank=True, default="")
    unidade_nome = models.CharField(max_length=255, blank=True, default="")
    unidade_cabecalho = models.JSONField(default=list)
    unidade_local = models.CharField(max_length=120, blank=True, default="")
    # `canonical_bytes` do conteúdo publicado (T-014); na individual, só a linha da pessoa.
    conteudo_publico = models.BinaryField()
    conteudo_publico_hash = models.CharField(max_length=64)
    # A assinatura que a confirmação conferiu (T-010): prova de que o publicado é o conferido.
    assinatura_conferida = models.CharField(max_length=64, blank=True, default="")
    idempotency_key = models.CharField(max_length=128, blank=True, default="")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["agenda"],
                condition=Q(especie=nomes.PUBLICACAO),
                name="uq_ato_da_agenda_uma_publicacao",
            ),
            models.CheckConstraint(
                condition=Q(especie__in=list(nomes.ESPECIES)), name="ck_ato_da_agenda_especie"
            ),
            models.CheckConstraint(
                condition=(Q(especie=nomes.PUBLICACAO) & Q(motivo=""))
                | (~Q(especie=nomes.PUBLICACAO) & ~Q(motivo="")),
                name="ck_ato_da_agenda_motivo",
            ),
            models.CheckConstraint(
                condition=(
                    ~Q(especie=nomes.PUBLICACAO)
                    & Q(veiculo="")
                    & Q(declaracao_do_veiculo="")
                    & Q(publicado_fora_onde="")
                    & Q(publicado_fora_em__isnull=True)
                )
                | (
                    Q(especie=nomes.PUBLICACAO)
                    & Q(veiculo=nomes.VEICULO_GPS)
                    & ~Q(declaracao_do_veiculo="")
                    & Q(publicado_fora_onde="")
                    & Q(publicado_fora_em__isnull=True)
                )
                | (
                    Q(especie=nomes.PUBLICACAO)
                    & Q(veiculo=nomes.VEICULO_EXTERNO)
                    & Q(declaracao_do_veiculo="")
                    & ~Q(publicado_fora_onde="")
                    & Q(publicado_fora_em__isnull=False)
                ),
                name="ck_ato_da_agenda_veiculo",
            ),
            models.CheckConstraint(
                condition=(
                    Q(especie=nomes.PUBLICACAO)
                    & Q(signatario_id__isnull=False)
                    & ~Q(signatario_cargo="")
                )
                | (
                    ~Q(especie=nomes.PUBLICACAO)
                    & Q(signatario_id__isnull=True)
                    & Q(signatario_nome="")
                    & Q(signatario_cargo="")
                ),
                name="ck_ato_da_agenda_signatario",
            ),
        ]
        indexes = [models.Index(fields=["edital", "especie"], name="ix_ato_da_agenda_edital")]

    def __str__(self):
        return f"{self.especie} da agenda {self.agenda_id}"


class HorarioPublicado(_AppendOnly):
    """O que cada ato publicou, por pessoa (FR-7224, FR-7241).

    **Vigente** é o item não substituído (nenhum outro o aponta em `substitui`) e `AGENDADO`; a
    página pública e a área do candidato leem só isso, e nunca o `Agendamento`, que é rascunho
    operacional (T-016, T-017). A cadeia de `substitui` é uma lista, e não uma árvore: um item é
    trocado no máximo uma vez.

    `banca_nome` é congelado: a banca, depois de publicada, não muda de nome (T-015), mas o que o
    ato publicou se lê do ato.
    """

    class Situacao(models.TextChoices):
        AGENDADO = nomes.AGENDADO, "Agendado"
        CANCELADO = nomes.CANCELADO, "Cancelado"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ato = models.ForeignKey(AtoDaAgenda, on_delete=models.PROTECT, related_name="horarios")
    inscricao = models.ForeignKey(
        "inscricoes.Inscricao", on_delete=models.PROTECT, related_name="horarios_publicados"
    )
    situacao = models.CharField(max_length=10, choices=Situacao.choices)
    banca = models.ForeignKey(
        BancaDaAgenda,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="horarios_publicados",
    )
    banca_nome = models.CharField(max_length=80, blank=True, default="")
    inicio = models.DateTimeField(null=True, blank=True)
    fim = models.DateTimeField(null=True, blank=True)
    # Chave estrangeira com `UNIQUE` nomeado, e não `OneToOneField`: o nome da constraint é o
    # contrato do data-model, e os testes o reconhecem na recusa.
    substitui = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="substituicoes",
    )
    # O aviso desta pessoa neste ato (T-018). Existe desde a entrega B e fica nulo até a C, que
    # traz a origem `AGENDA` aos avisos da `066`.
    aviso = models.ForeignKey(
        "avisos.Aviso",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="horarios_da_agenda",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["ato", "inscricao"], name="uq_horario_publicado_por_ato"
            ),
            models.UniqueConstraint(
                fields=["substitui"], name="uq_horario_publicado_substituido_uma_vez"
            ),
            models.UniqueConstraint(fields=["aviso"], name="uq_horario_publicado_aviso"),
            models.CheckConstraint(
                condition=(
                    Q(situacao=nomes.AGENDADO)
                    & Q(banca__isnull=False)
                    & ~Q(banca_nome="")
                    & Q(inicio__isnull=False)
                    & Q(fim__isnull=False)
                    & Q(inicio__lt=models.F("fim"))
                )
                | (
                    Q(situacao=nomes.CANCELADO)
                    & Q(banca__isnull=True)
                    & Q(inicio__isnull=True)
                    & Q(fim__isnull=True)
                ),
                name="ck_horario_publicado_forma",
            ),
        ]
        indexes = [
            models.Index(fields=["inscricao"], name="ix_horario_publicado_inscricao"),
        ]

    def __str__(self):
        return f"{self.situacao} {self.inscricao_id} em {self.inicio}"


class DocumentoDoAtoDaAgenda(_AppendOnly):
    """Os bytes do documento oficial de um ato, gerados uma vez, na transação dele (`D-012`).

    O molde de `DocumentoDaPublicacaoDeConvocados` (`149`): tabela própria, para a ausência de
    documento ser a ausência de linha, e o resumo como integridade. **O que se preserva são os bytes
    como saíram**: um compositor que mude depois não muda o documento que já foi publicado — a
    página serve o gravado, e nunca recompõe.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ato = models.OneToOneField(AtoDaAgenda, on_delete=models.PROTECT, related_name="documento")
    bytes = models.BinaryField()
    content_type = models.CharField(max_length=100, default="application/pdf")
    documento_hash = models.CharField(max_length=64)

    def __str__(self):
        return f"documento do ato {self.ato_id}"
