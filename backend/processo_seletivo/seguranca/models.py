"""A identidade institucional e os vínculos de acesso (106, data-model).

**A pessoa é o `auth.User` do Django, e não um modelo daqui** (`D-001`). O `username` é o
identificador interno estável, `pessoa-<uuid4>`, e é ele que vai ao `subject` dos atos (`D-002`).
O `User` não autoriza nada: `is_superuser`, `is_staff`, os grupos e as permissões do framework são
ignorados, e quem decide o que a pessoa pode é o vínculo (`D-008`).

As três tabelas são append-only nas duas camadas — gatilho e privilégio ausente — e o `save()` é a
terceira, a única que um `QuerySet.update()` não atravessa. "Quem tinha o papel X na unidade Y na
data D" é a pergunta da fiscalização, e tem resposta aqui, e não só na trilha.
"""

import uuid

from django.conf import settings
from django.db import models


class _SoInclui(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise TypeError(f"{self.__class__.__name__} é append-only")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise TypeError(f"{self.__class__.__name__} é append-only")


class IdentidadeExterna(_SoInclui):
    """Um identificador do provedor, associado a uma pessoa (`D-003`).

    Só localiza a pessoa: o que vai aos atos é o `username`. Trocar de provedor é acrescentar uma
    linha, e o `subject` gravado não muda. **Nunca se associa pelo e-mail**, que muda e se recicla.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pessoa = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="identidades_externas"
    )
    provedor = models.CharField(max_length=64)
    identificador = models.CharField(max_length=255)
    associada_em = models.DateTimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["provedor", "identificador"], name="uq_identidade_externa_por_provedor"
            ),
            models.UniqueConstraint(
                fields=["pessoa", "provedor"], name="uq_uma_identidade_por_pessoa_e_provedor"
            ),
        ]

    def __str__(self):
        return f"{self.provedor}:{self.identificador}"


class Vinculo(_SoInclui):
    """Pessoa × escopo × papel, com quem concedeu, quando e por quê (`FR-3008`).

    Não tem `ativo`: encerra-se por uma `RevogacaoDeVinculo`. O modelo da comissão sobrescreve a
    função com `UPDATE`, e o histórico dela fica só na trilha; para acesso, isso não basta.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pessoa = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="vinculos"
    )
    escopo = models.CharField(max_length=100)
    papel = models.CharField(max_length=64)
    concedido_em = models.DateTimeField()
    concedido_por = models.CharField(max_length=255)
    motivo = models.TextField()

    class Meta:
        indexes = [models.Index(fields=["pessoa", "escopo"], name="vinculo_pessoa_escopo")]

    def __str__(self):
        return f"{self.papel}@{self.escopo}"


class RevogacaoDeVinculo(_SoInclui):
    """O encerramento de um vínculo. Um por vínculo: o segundo o banco recusa (`FR-3014`)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vinculo = models.OneToOneField(Vinculo, on_delete=models.PROTECT, related_name="revogacao")
    revogado_em = models.DateTimeField()
    revogado_por = models.CharField(max_length=255)
    motivo = models.TextField()

    def __str__(self):
        return f"revogação de {self.vinculo_id}"
