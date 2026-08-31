"""Inscrição: o vínculo entre uma identidade e um Perfil de um Edital.

Dois estados e nada mais (FR-027). `status` e `revision` existem porque a auditoria e o controle
de concorrência do projeto os leem do agregado — reusar os dois mecanismos custa dois campos, e
inventar um terceiro estado custaria uma máquina que ninguém pediu.

**Por que `profile_id` e `modality_id` não são chaves estrangeiras.** O candidato se inscreve para
o Perfil do **conteúdo publicado**, cuja identidade é estável e sobrevive à Retificação. Amarrar à
linha de elaboração faria a inscrição depender de um registro que a Retificação altera depois, e
contradiria FR-011 — o que o candidato vê e o que a submissão valida vêm do publicado.
"""

import uuid

from django.db import models
from django.db.models import Q

from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada


class Inscricao(models.Model):
    class Status(models.TextChoices):
        RASCUNHO = "RASCUNHO"
        SUBMETIDA = "SUBMETIDA"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # O identificador estável do provedor, e nunca o nome: propriedade de inscrição não pode
    # depender de dado editável (FR-022).
    identity_subject = models.CharField(max_length=255)
    edital = models.ForeignKey(Edital, on_delete=models.PROTECT, related_name="inscricoes")
    profile_id = models.UUIDField()
    modality_id = models.UUIDField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.RASCUNHO)
    revision = models.PositiveBigIntegerField(default=1)
    nome = models.CharField(max_length=255, blank=True)
    cpf = models.CharField(max_length=20, blank=True)
    # Forma normalizada para comparação (FR-073). O CPF exibido preserva a pontuação de quem o
    # digitou; a comparação nunca depende dela.
    cpf_normalizado = models.CharField(max_length=11, blank=True)
    email = models.EmailField(blank=True)
    telefone = models.CharField(max_length=30, blank=True)
    # O que o candidato viu e confirmou durante o preenchimento (FR-059a) e o que ele aceitou no
    # envio (FR-058). São duas coisas, e confundi-las faria o aviso de Retificação se repetir para
    # sempre ou nunca aparecer.
    versao_reconhecida = models.ForeignKey(
        VersaoConsolidada,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="inscricoes_reconhecidas",
    )
    versao_aceita = models.ForeignKey(
        VersaoConsolidada,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="inscricoes_aceitas",
    )
    declaracoes_aceitas_em = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    # Texto sempre presente e `""` quando ainda não há protocolo — a convenção que o projeto já
    # aplica a `description` e `locality`. A unicidade se restringe ao que não é vazio, de modo
    # que os rascunhos convivam sem que `null` precise significar "ainda não".
    protocolo = models.CharField(max_length=32, blank=True, default="")
    created_at = models.DateTimeField()

    class Meta:
        constraints = [
            # Em **qualquer** estado (FR-028). Rascunho duplicado e envio duplicado são a mesma
            # violação, e uma restrição só responde pelas duas.
            models.UniqueConstraint(
                fields=["identity_subject", "edital", "profile_id"],
                name="uq_inscricao_identidade_edital_perfil",
            ),
            models.UniqueConstraint(
                fields=["protocolo"],
                condition=~Q(protocolo=""),
                name="uq_inscricao_protocolo",
            ),
            # O que "submetida" significa, dito no banco: sem instante, protocolo, versão aceita e
            # aceite das declarações, o estado não é alcançável.
            models.CheckConstraint(
                condition=Q(status="RASCUNHO")
                | (
                    Q(
                        status="SUBMETIDA",
                        submitted_at__isnull=False,
                        versao_aceita__isnull=False,
                        declaracoes_aceitas_em__isnull=False,
                    )
                    & ~Q(protocolo="")
                ),
                name="ck_inscricao_submetida_completa",
            ),
        ]
        indexes = [models.Index(fields=["edital", "status"])]

    def __str__(self):
        return f"Inscrição {self.protocolo or self.id}"

    def save(self, *args, **kwargs):
        """O que o envio fixa não se altera depois (FR-064, FR-054).

        A Inscrição inteira não é imutável — `revision` avança até o envio. O que é imutável é o
        que o ato produziu: instante, protocolo e versão aceita. Mesmo padrão de `Publicacao` e
        `VersaoConsolidada`, restrito aos campos que carregam efeito.
        """
        if not self._state.adding:
            anterior = (
                Inscricao.objects.filter(pk=self.pk)
                .values("submitted_at", "protocolo", "versao_aceita")
                .first()
            )
            for campo, atributo in (
                ("submitted_at", "submitted_at"),
                ("protocolo", "protocolo"),
                ("versao_aceita", "versao_aceita_id"),
            ):
                gravado = (anterior or {}).get(campo)
                if gravado not in (None, "") and gravado != getattr(self, atributo):
                    raise TypeError(f"Inscrição submetida não altera {campo}")
        return super().save(*args, **kwargs)
