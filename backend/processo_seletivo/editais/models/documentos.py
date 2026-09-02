"""O que o Edital exige que o candidato apresente.

`Documento Exigido` é termo da Constituição e chega ao domínio com esse nome. Ele é **do Edital**,
e não do Perfil: o caso mais comum nos Editais reais — documento de identificação para todo mundo —
não pertence a Perfil nenhum. Perfil e modalidade entram como restrição opcional de aplicabilidade,
e são as únicas duas dimensões que existem (FR-006 da 009).

A ausência é o que dá as quatro combinações: sem os dois, aplica-se a todos; com um, restringe por
ele; com os dois, pela combinação. Não há quinta forma, não há operador e não há expressão — e é
essa recusa que separa isto de um construtor de formulários.
"""

import uuid

from django.db import models

from processo_seletivo.editais.models.perfis import ModalidadeConcorrencia, PerfilVaga
from processo_seletivo.processos.models import Edital


class DocumentoExigido(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    edital = models.ForeignKey(Edital, on_delete=models.PROTECT, related_name="documentos_exigidos")
    key = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    # Instrução curta, do tipo "frente e verso, em arquivo único". Texto sempre presente e `""`
    # quando ausente, como `description` no Perfil: uma segunda convenção para texto faria a
    # versão canônica admitir mais de uma forma.
    instructions = models.TextField(blank=True)
    required = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    perfil = models.ForeignKey(
        PerfilVaga,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="documentos_exigidos",
    )
    modalidade = models.ForeignKey(
        ModalidadeConcorrencia,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="documentos_exigidos",
    )

    class Meta:
        ordering = ["order", "id"]
        constraints = [
            models.UniqueConstraint(fields=["edital", "key"], name="uq_documento_edital_key"),
            models.UniqueConstraint(fields=["edital", "order"], name="uq_documento_edital_order"),
        ]

    def __str__(self):
        return f"{self.order} — {self.name}"
