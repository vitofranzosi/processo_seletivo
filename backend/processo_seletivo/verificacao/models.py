"""Os registros da verificação por vídeo (166, `data-model.md`).

Cinco, e só um deles muda: o envio em partes, que é a fila de um upload e não ato do certame. Os
outros quatro — o vídeo, a abertura, o encaminhamento e a eliminação — são append-only nas três
camadas de sempre: `save` só cria, o gatilho recusa `UPDATE` e `DELETE`, e o papel de runtime não
tem o privilégio (`seguranca/papeis.py::TABELAS_APPEND_ONLY`).

**Nenhum guarda o conteúdo do vídeo.** O arquivo vive no armazenamento privado; aqui ficam o caminho,
o resumo e o que a conferência técnica leu do contêiner (FR-7121, FR-7151).
"""

import uuid

from django.db import models
from django.db.models import Q

from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.processos.models import Edital
from processo_seletivo.verificacao.domain.conteiner import FORMATOS

_FORMATOS = [(formato, formato) for formato in FORMATOS]


class _SoCria(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValueError(f"{self._meta.verbose_name} é imutável.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError(f"{self._meta.verbose_name} não é excluído.")


class EnvioDoVideo(models.Model):
    """O envio em partes em andamento, de um titular para uma Etapa (FR-7118, FR-7125).

    **Transitório e mutável**: o deslocamento recebido muda a cada parte, e a linha some quando o envio
    conclui ou quando outro envio a substitui. Registrar cada parte em linha imutável guardaria o
    rastro de um upload, que não é ato (plano, *Complexity Tracking*).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inscricao = models.ForeignKey(Inscricao, on_delete=models.PROTECT, related_name="+")
    edital = models.ForeignKey(Edital, on_delete=models.PROTECT, related_name="+")
    etapa_id = models.UUIDField()
    tamanho = models.PositiveBigIntegerField()
    recebido = models.PositiveBigIntegerField(default=0)
    formato = models.CharField(max_length=20, choices=_FORMATOS)
    duracao_medida = models.DecimalField(max_digits=8, decimal_places=3)
    marcas = models.JSONField(default=list)
    roteiro = models.CharField(max_length=60)
    declarou_maioridade = models.BooleanField()
    iniciado_em = models.DateTimeField()
    arquivo = models.CharField(max_length=255)

    class Meta:
        db_table = "verificacao_envio_do_video"
        constraints = [
            models.UniqueConstraint(
                fields=["edital", "etapa_id", "inscricao"], name="uq_um_envio_por_inscricao"
            ),
            models.CheckConstraint(
                condition=Q(recebido__lte=models.F("tamanho")), name="ck_envio_recebido"
            ),
            models.CheckConstraint(condition=Q(declarou_maioridade=True), name="ck_envio_maior"),
        ]


class VideoDaVerificacao(_SoCria):
    """O vídeo recebido. O `id` é o número do comprovante (FR-7121, FR-7123).

    **Vigente** é o que nenhum outro substitui. A troca antes da primeira abertura da comissão cria um
    vídeo novo que aponta o anterior em `substitui`, e os dois continuam registrados (FR-7124). A
    unicidade de `substitui` impede que duas trocas concorrentes substituam o mesmo vídeo; o primeiro
    vídeo é único pela trava da inscrição na conclusão do envio (FR-7152).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inscricao = models.ForeignKey(Inscricao, on_delete=models.PROTECT, related_name="+")
    edital = models.ForeignKey(Edital, on_delete=models.PROTECT, related_name="+")
    etapa_id = models.UUIDField()
    arquivo = models.CharField(max_length=255)
    sha256 = models.CharField(max_length=64)
    tamanho = models.PositiveBigIntegerField()
    duracao = models.DecimalField(max_digits=8, decimal_places=3)
    formato = models.CharField(max_length=20, choices=_FORMATOS)
    roteiro = models.CharField(max_length=60)
    marcas = models.JSONField(default=list)
    declarou_maioridade = models.BooleanField()
    substitui = models.OneToOneField(
        "self", null=True, blank=True, on_delete=models.PROTECT, related_name="substituido_por"
    )
    recebido_em = models.DateTimeField()

    class Meta:
        db_table = "verificacao_video"
        verbose_name = "O vídeo da verificação"
        indexes = [models.Index(fields=["edital", "etapa_id", "inscricao"])]
        constraints = [
            models.CheckConstraint(condition=Q(declarou_maioridade=True), name="ck_video_maior"),
            models.CheckConstraint(condition=Q(sha256__regex=r"^[0-9a-f]{64}$"), name="ck_video_sha"),
        ]


class AberturaDoVideo(_SoCria):
    """Alguém abriu o vídeo (FR-7130). Só a abertura da comissão encerra a troca (FR-7124).

    O `id` é o identificador que a sessão guarda e que os pedidos com `Range` apresentam: a abertura é
    o ato, e os pedidos são só a entrega dele (D-007).
    """

    class Papel(models.TextChoices):
        COMISSAO = "COMISSAO"
        TITULAR = "TITULAR"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    video = models.ForeignKey(VideoDaVerificacao, on_delete=models.PROTECT, related_name="aberturas")
    pessoa = models.CharField(max_length=255)
    papel = models.CharField(max_length=20, choices=Papel.choices)
    aberta_em = models.DateTimeField()

    class Meta:
        db_table = "verificacao_abertura_do_video"
        verbose_name = "A abertura do vídeo"
        indexes = [models.Index(fields=["video", "papel"])]


class EncaminhamentoAoVivo(_SoCria):
    """O vídeo não confirmou, e a presidência encaminhou à entrevista ao vivo (FR-7140 a FR-7143).

    Único por inscrição e Etapa, e não se desfaz. Cita o vídeo vigente no ato e as Avaliações que a
    reabertura da `012` devolveu à Mesa.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inscricao = models.ForeignKey(Inscricao, on_delete=models.PROTECT, related_name="+")
    edital = models.ForeignKey(Edital, on_delete=models.PROTECT, related_name="+")
    etapa_id = models.UUIDField()
    video = models.ForeignKey(VideoDaVerificacao, on_delete=models.PROTECT, related_name="+")
    pareceres = models.JSONField(default=list)
    registrado_em = models.DateTimeField()
    registrado_por = models.CharField(max_length=255)

    class Meta:
        db_table = "verificacao_encaminhamento"
        verbose_name = "O encaminhamento à entrevista ao vivo"
        constraints = [
            models.UniqueConstraint(
                fields=["edital", "etapa_id", "inscricao"], name="uq_um_encaminhamento"
            )
        ]


class EliminacaoDoVideo(_SoCria):
    """O arquivo do vídeo foi eliminado pelo prazo de retenção (FR-7148).

    O vídeo continua: o resumo, o tamanho, a duração, as marcas e as aberturas são a prova do ato, e o
    arquivo era só a evidência (R-23 do estudo).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    video = models.OneToOneField(
        VideoDaVerificacao, on_delete=models.PROTECT, related_name="eliminacao"
    )
    eliminado_em = models.DateTimeField()
    prazo_em_dias = models.PositiveIntegerField()
    encerramento_em = models.DateTimeField()

    class Meta:
        db_table = "verificacao_eliminacao_do_video"
        verbose_name = "A eliminação do vídeo"
