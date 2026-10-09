"""As tabelas dos avisos: seis append-only e uma mutável que nunca se exclui (066, data-model §1).

**O estado do envio não é coluna.** Cada destinatário tem tentativas, e cada tentativa tem, ou não,
um resultado; pendente, em envio, aceita, expirada são **derivados** disso
(`avisos/domain/estado.py`).
Uma coluna de estado exigiria `UPDATE`, e o registro de envio passaria a ser a única coisa do
sistema que muda depois de escrita — justo a que diz se uma mensagem saiu.

**A tentativa tem duas gravações** (`R-003`): o início, confirmado antes de o servidor de correio
ser chamado, e o resultado, depois. É o que torna a queda observável: tentativa sem resultado é,
por definição, indeterminada, e o despacho nunca a repete (`FR-1266`, `FR-1267`).
"""

import uuid

from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower

from processo_seletivo.avisos.domain import nomes


def _escolhas(valores):
    return [(valor, valor) for valor in valores]


class _AppendOnly(models.Model):
    """A primeira camada: o ORM recusa alterar e excluir. O gatilho e o privilégio são as outras."""

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise TypeError(f"{type(self).__name__} é append-only")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise TypeError(f"{type(self).__name__} é append-only")


class ModeloDeAviso(models.Model):
    """Texto reutilizável da unidade: muda, e nunca se exclui (`FR-1260`).

    **Mutável, ao contrário das demais**, porque o modelo é instrumento de trabalho da seleção e não
    registro do que foi enviado: o aviso guarda o texto como saiu (`FR-1261`), e por isso editar o
    modelo não reescreve história nenhuma. Cada mudança passa pela trilha com o antes e o depois
    (`FR-1277`).

    **Fora de `TABELAS_APPEND_ONLY`**: a role de runtime precisa de `UPDATE`, e
    `provisionar_papeis` só sabe revogar `UPDATE` e `DELETE` juntos. As duas camadas contra a
    exclusão são este `delete()` e o gatilho da migration.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    institution_scope = models.CharField(max_length=100)
    nome = models.CharField(max_length=nomes.NOME_DO_MODELO_MAXIMO)
    assunto = models.CharField(max_length=nomes.ASSUNTO_MAXIMO)
    corpo = models.TextField()
    ativo = models.BooleanField(default=True)
    # A marca dos três de `D-008`. **Nunca muda**, e é ela que torna a criação idempotente: a
    # unidade que já teve modelo inicial não ganha outro, ainda que tenha inativado os três.
    modelo_inicial = models.BooleanField(default=False)
    criado_por = models.CharField(max_length=255)
    criado_em = models.DateTimeField()
    alterado_por = models.CharField(max_length=255, blank=True, default="")
    alterado_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            # Dois modelos com o mesmo nome no seletor seriam indistinguíveis para quem escolhe, e o
            # índice é também a última porta contra a cópia que duas sincronizações simultâneas
            # produziriam se a trava delas faltasse (`R-012`).
            models.UniqueConstraint(
                "institution_scope", Lower("nome"), name="uq_modelo_de_aviso_nome_por_escopo"
            ),
        ]
        indexes = [
            models.Index(fields=["institution_scope", "ativo"], name="ix_modelo_aviso_escopo")
        ]

    def __str__(self):
        return f"{self.nome} ({self.institution_scope})"

    def delete(self, *args, **kwargs):
        raise TypeError("ModeloDeAviso não se exclui: inative-o")


class Aviso(_AppendOnly):
    """Um envio decidido por uma pessoa, sobre um ato que já existe (`FR-1241`).

    **`assunto` e `corpo` são os finais** (`R-007`): com o rodapé, a linha de retificação e os links
    já resolvidos na confirmação. Só `{nome_do_candidato}` fica por resolver, no envio, e vem de
    `Inscricao.nome`, que não muda depois da submissão. O registro diz o que saiu.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    edital = models.ForeignKey("processos.Edital", on_delete=models.PROTECT, related_name="avisos")
    institution_scope = models.CharField(max_length=100)
    origem = models.CharField(max_length=16, choices=_escolhas(nomes.ORIGENS))
    motivo = models.CharField(max_length=24, choices=_escolhas(nomes.MOTIVOS))
    aviso_anterior = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.PROTECT, related_name="reenvios"
    )
    justificativa = models.TextField(blank=True, default="")
    perfil_id = models.UUIDField()
    marco_id = models.UUIDField()
    lista_id = models.UUIDField(null=True, blank=True)
    natureza = models.CharField(
        max_length=16, choices=_escolhas(nomes.NATUREZAS), blank=True, default=""
    )
    referencia_da_publicacao = models.TextField(blank=True, default="")
    retificadora = models.BooleanField(default=False)
    assunto = models.CharField(max_length=nomes.ASSUNTO_MAXIMO)
    corpo = models.TextField()
    modelo = models.ForeignKey(
        ModeloDeAviso, null=True, blank=True, on_delete=models.PROTECT, related_name="avisos"
    )
    solicitado_por = models.CharField(max_length=255)
    solicitado_em = models.DateTimeField()
    idempotency_key = models.CharField(max_length=128)
    correlation_id = models.CharField(max_length=100, blank=True, default="")

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(origem__in=nomes.ORIGENS), name="ck_aviso_origem_conhecida"
            ),
            models.CheckConstraint(
                condition=Q(motivo__in=nomes.MOTIVOS), name="ck_aviso_motivo_conhecido"
            ),
            # **Cada origem cita o seu ato, e só ele.** O resultado tem natureza e não tem
            # referência; a chamada tem a referência declarada e não tem natureza.
            models.CheckConstraint(
                condition=(
                    Q(
                        origem=nomes.RESULTADO,
                        natureza__in=nomes.NATUREZAS,
                        referencia_da_publicacao="",
                    )
                    | (Q(origem=nomes.CHAMADA, natureza="") & ~Q(referencia_da_publicacao=""))
                ),
                name="ck_aviso_ato_da_origem",
            ),
            # Reenvio sem o aviso de que ele é reenvio perderia a história (`R-011`).
            models.CheckConstraint(
                condition=Q(motivo=nomes.PRIMEIRO_AVISO) | Q(aviso_anterior__isnull=False),
                name="ck_aviso_reenvio_tem_anterior",
            ),
            models.CheckConstraint(
                condition=~Q(motivo=nomes.REENVIO_JUSTIFICADO) | ~Q(justificativa=""),
                name="ck_aviso_reenvio_justificado_tem_texto",
            ),
        ]
        indexes = [
            models.Index(fields=["edital", "marco_id"], name="ix_aviso_edital_marco"),
            models.Index(fields=["solicitado_em"], name="ix_aviso_solicitado_em"),
        ]

    def __str__(self):
        return f"aviso {self.origem} {self.motivo} — edital {self.edital_id}"


class PublicacaoDoAviso(_AppendOnly):
    """Cada publicação de resultado que o aviso cita (`FR-1247`)."""

    aviso = models.ForeignKey(Aviso, on_delete=models.PROTECT, related_name="publicacoes")
    publicacao = models.ForeignKey(
        "divulgacao.PublicacaoResultado", on_delete=models.PROTECT, related_name="avisos"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["aviso", "publicacao"], name="uq_publicacao_do_aviso")
        ]
        # A pergunta "esta publicação já foi avisada?" é a que a prévia faz sempre (`D-002`).
        indexes = [models.Index(fields=["publicacao"], name="ix_publicacao_do_aviso")]

    def __str__(self):
        return f"publicação {self.publicacao_id} no aviso {self.aviso_id}"


class DestinatarioDoAviso(_AppendOnly):
    """Uma inscrição do universo do ato citado, com a elegibilidade e o endereço congelados.

    **O universo inteiro, e não só quem recebe** (`D-003`): na chamada, quem já tem desfecho fica
    aqui como não elegível, com o motivo, para que a lista do ato continue rastreável. Recebe
    mensagem quem é elegível **e** tem endereço.
    """

    aviso = models.ForeignKey(Aviso, on_delete=models.PROTECT, related_name="destinatarios")
    inscricao = models.ForeignKey(
        "inscricoes.Inscricao", on_delete=models.PROTECT, related_name="avisos"
    )
    convocacao = models.ForeignKey(
        "convocacao.Convocacao",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="avisos",
    )
    elegibilidade = models.CharField(max_length=32, choices=_escolhas(nomes.ELEGIBILIDADES))
    # Vazio é "sem endereço" (`FR-1252`).
    endereco = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        constraints = [
            # **A deduplicação da `FR-1249`**: quem concorre na ampla e numa reserva aparece nas
            # duas publicações do marco e recebe uma mensagem só.
            models.UniqueConstraint(fields=["aviso", "inscricao"], name="uq_destinatario_do_aviso"),
            models.CheckConstraint(
                condition=Q(elegibilidade__in=nomes.ELEGIBILIDADES),
                name="ck_destinatario_elegibilidade",
            ),
        ]

    def __str__(self):
        return f"inscrição {self.inscricao_id} no aviso {self.aviso_id}"


class TentativaDeEnvio(_AppendOnly):
    """O início de uma tentativa, gravado **antes** de chamar o servidor de correio (`R-003`)."""

    destinatario = models.ForeignKey(
        DestinatarioDoAviso, on_delete=models.PROTECT, related_name="tentativas"
    )
    numero = models.PositiveSmallIntegerField()
    iniciada_em = models.DateTimeField()

    class Meta:
        constraints = [
            # **A última porta contra a tentativa duplicada** (`R-002`): duas inserções da mesma
            # tentativa colidem no banco, venham de onde vierem.
            models.UniqueConstraint(fields=["destinatario", "numero"], name="uq_tentativa_de_envio")
        ]

    def __str__(self):
        return f"tentativa {self.numero} do destinatário {self.destinatario_id}"


class ResultadoDaTentativa(_AppendOnly):
    """O que o servidor respondeu, classificado pela fase em que respondeu (`R-004`).

    **Nenhum campo diz entregue, recebida ou lida** (`UX-172`): o que o sistema sabe é o que o
    servidor de correio aceitou ou recusou. O detalhe técnico não leva endereço nem nome
    (`FR-1279`).
    """

    tentativa = models.OneToOneField(
        TentativaDeEnvio, on_delete=models.PROTECT, related_name="resultado"
    )
    resultado = models.CharField(max_length=24, choices=_escolhas(nomes.RESULTADOS))
    registrado_em = models.DateTimeField()
    detalhe_tecnico = models.TextField(blank=True, default="")

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(resultado__in=nomes.RESULTADOS), name="ck_resultado_da_tentativa"
            )
        ]

    def __str__(self):
        return f"{self.resultado} — tentativa {self.tentativa_id}"


class InterrupcaoDoAviso(_AppendOnly):
    """O ato de parar um aviso, com autor e motivo (`D-006`). Um aviso se interrompe uma vez."""

    aviso = models.OneToOneField(Aviso, on_delete=models.PROTECT, related_name="interrupcao")
    motivo = models.TextField()
    interrompido_por = models.CharField(max_length=255)
    interrompido_em = models.DateTimeField()

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=~Q(motivo=""), name="ck_interrupcao_do_aviso_com_motivo"
            )
        ]

    def __str__(self):
        return f"interrupção do aviso {self.aviso_id}"
