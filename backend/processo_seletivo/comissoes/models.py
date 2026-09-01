"""A comissão do Processo e a alocação de seus membros às Etapas.

Duas entidades operacionais, e nenhuma normativa. Nada daqui entra no conteúdo publicado, na
Versão Consolidada ou no hash: a comissão é quem trabalha, não o que o Edital diz (D-005).

**Por que `etapa_id` não é chave estrangeira.** A linha de elaboração e a Etapa publicada podem
não coincidir: `EtapaAvaliacao` é lida uma única vez fora da elaboração, para montar o snapshot, e
depois disso o conteúdo evolui por Retificação — que não escreve de volta nas tabelas de `editais`
e sabe acrescentar item a coleção com chave. Existe, portanto, Etapa real no Edital vigente sem
linha alguma para uma FK apontar. A integridade é preservada no comando, que confere existência e
pertinência a cada operação e a cada acesso (D-002). O precedente é `Inscricao.profile_id`.

**Remover é inativar.** A trilha de auditoria referencia o agregado pelo `id`; apagar a linha
deixaria o evento apontando para o nada, e a Constituição proíbe excluir fisicamente o que
compromete rastreabilidade. Readicionar cria linha nova, e o histórico permanece (D-013).
"""

import uuid

from django.db import models
from django.db.models import Q

from processo_seletivo.processos.models import Edital, ProcessoSeletivo


class Funcao(models.TextChoices):
    PRESIDENTE = "PRESIDENTE"
    MEMBRO = "MEMBRO"


class MembroComissao(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    processo = models.ForeignKey(
        ProcessoSeletivo, on_delete=models.PROTECT, related_name="membros_da_comissao"
    )
    # O identificador estável do provedor, e nunca o nome: a identidade da pessoa não pode
    # depender de dado editável (FR-002).
    identity_subject = models.CharField(max_length=255)
    # Leitura humana da lista, e nada além. Não é pesquisável, não participa de comparação
    # nenhuma e nunca vai para a trilha — não há diretório para verificá-lo (FR-019, D-003).
    display_label = models.CharField(max_length=255, blank=True)
    funcao = models.CharField(max_length=20, choices=Funcao.choices, default=Funcao.MEMBRO)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField()
    criado_por = models.CharField(max_length=255)
    inativado_em = models.DateTimeField(null=True, blank=True)
    inativado_por = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["funcao", "identity_subject"]
        constraints = [
            # Parcial: readicionar quem saiu cria linha nova, e o histórico sobrevive (FR-003).
            models.UniqueConstraint(
                fields=["processo", "identity_subject"],
                condition=Q(ativo=True),
                name="uq_membro_ativo_por_processo",
            ),
            # O que "inativo" significa, dito no banco: sem instante de inativação, o estado não
            # é alcançável.
            models.CheckConstraint(
                condition=Q(ativo=True, inativado_em__isnull=True)
                | Q(ativo=False, inativado_em__isnull=False),
                name="ck_membro_inativacao_completa",
            ),
        ]
        indexes = [models.Index(fields=["processo", "ativo"])]

    def __str__(self):
        return f"{self.identity_subject} — {self.funcao}"

    @property
    def e_presidente(self):
        return self.ativo and self.funcao == Funcao.PRESIDENTE


class AlocacaoEtapa(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # A alocação existe **através** do vínculo, nunca ao lado dele: não há alocação de quem não
    # é membro da comissão (FR-034).
    membro = models.ForeignKey(MembroComissao, on_delete=models.PROTECT, related_name="alocacoes")
    edital = models.ForeignKey(Edital, on_delete=models.PROTECT, related_name="alocacoes")
    # A identidade da Etapa no conteúdo publicado. Ver o docstring do módulo.
    etapa_id = models.UUIDField()
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField()
    criado_por = models.CharField(max_length=255)
    inativado_em = models.DateTimeField(null=True, blank=True)
    inativado_por = models.CharField(max_length=255, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["membro", "edital", "etapa_id"],
                condition=Q(ativo=True),
                name="uq_alocacao_ativa_por_membro_e_etapa",
            ),
            models.CheckConstraint(
                condition=Q(ativo=True, inativado_em__isnull=True)
                | Q(ativo=False, inativado_em__isnull=False),
                name="ck_alocacao_inativacao_completa",
            ),
        ]
        indexes = [models.Index(fields=["edital", "etapa_id", "ativo"])]

    def __str__(self):
        return f"{self.membro.identity_subject} — {self.etapa_id}"
