"""A execução do trabalho: quem avalia qual inscrição, o que afirmou, e quem não pode avaliar.

A 011 respondeu quem pode atuar em cada Etapa. Aqui se responde quais inscrições cabem a cada uma
dessas pessoas — e a autorização é a conjunção das duas perguntas, nunca uma delas sozinha.

**Por que a Atribuição referencia o membro, e não a alocação.** Remover é inativar, e readicionar
cria linha nova: uma Atribuição pendurada na linha de alocação morreria a cada remoção, e a
presidência que retirasse alguém da Etapa por engano não teria como desfazer — as atribuições dela
ficariam órfãs para sempre. Ancorada no membro, a revogação passa a ser **computada**: tirar a
alocação faz o guard da 011 falhar sem que nenhuma linha daqui seja tocada, e devolvê-la restaura o
acesso às mesmas atribuições (012, D-004, FR-046, FR-069).

**Por que `etapa_id` não é chave estrangeira.** A mesma razão da 011: existe Etapa real no Edital
vigente sem linha de elaboração para uma FK apontar, porque a Retificação sabe acrescentar item a
coleção com chave e não escreve de volta em `editais`.

**Por que a conclusão única e o impedimento se ancoram na identidade, e não no vínculo.**
`MembroComissao` é vínculo: a remoção o inativa e a readmissão cria outro. Ancorar ali deixaria
remover-e-readicionar liberar uma segunda conclusão da mesma pessoa sobre a mesma inscrição, e
apagaria um impedimento que nomeia razão que não muda por reorganização administrativa (FR-074,
FR-099).
"""

import uuid

from django.db import models
from django.db.models import Q

from processo_seletivo.comissoes.models import MembroComissao
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada


class Atribuicao(models.Model):
    """Esta pessoa avalia esta inscrição, nesta Etapa."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    membro = models.ForeignKey(MembroComissao, on_delete=models.PROTECT, related_name="atribuicoes")
    edital = models.ForeignKey(Edital, on_delete=models.PROTECT, related_name="atribuicoes")
    # A identidade da Etapa no conteúdo publicado. Ver o docstring do módulo.
    etapa_id = models.UUIDField()
    inscricao = models.ForeignKey(Inscricao, on_delete=models.PROTECT, related_name="atribuicoes")
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField()
    criado_por = models.CharField(max_length=255)
    inativado_em = models.DateTimeField(null=True, blank=True)
    inativado_por = models.CharField(max_length=255, blank=True)

    class Meta:
        constraints = [
            # Parcial: redistribuir a mesma inscrição à mesma pessoa depois de removê-la cria
            # linha nova, e o histórico permanece — o padrão que a 011 já adotou (FR-003).
            models.UniqueConstraint(
                fields=["membro", "edital", "etapa_id", "inscricao"],
                condition=Q(ativo=True),
                name="uq_atribuicao_ativa",
            ),
            models.CheckConstraint(
                condition=Q(ativo=True, inativado_em__isnull=True)
                | Q(ativo=False, inativado_em__isnull=False),
                name="ck_atribuicao_inativacao_completa",
            ),
        ]
        indexes = [
            # A organização do trabalho, por Etapa.
            models.Index(fields=["edital", "etapa_id", "ativo"]),
            # A Mesa: as atribuições de uma pessoa numa Etapa, sem varrer o Edital.
            models.Index(fields=["membro", "edital", "etapa_id", "ativo"]),
        ]

    def __str__(self):
        return f"{self.membro_id} — {self.inscricao_id}"


class Avaliacao(models.Model):
    """O que esta pessoa afirmou sobre esta inscrição, e sob qual regra."""

    class Estado(models.TextChoices):
        RASCUNHO = "RASCUNHO"
        CONCLUIDA = "CONCLUIDA"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    atribuicao = models.OneToOneField(
        Atribuicao, on_delete=models.PROTECT, related_name="avaliacao"
    )
    # A tripla copiada da Atribuição, escrita **uma vez** na criação e nunca atualizada. Ela existe
    # para que "no máximo uma conclusão por pessoa, inscrição e Etapa" seja garantia de banco: a
    # condição atravessa `Avaliacao → Atribuicao → membro`, e índice não atravessa junção (FR-074).
    # A divergência que costuma condenar denormalização é impossível aqui — a quádrupla da
    # Atribuição nunca muda depois de criada.
    identity_subject = models.CharField(max_length=255)
    etapa_id = models.UUIDField()
    inscricao_id = models.UUIDField()
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.RASCUNHO)
    pontuacao = models.DecimalField(max_digits=7, decimal_places=4, null=True, blank=True)
    parecer = models.TextField(blank=True)
    # A regra que governou o ato. **Não** se copiam máxima, mínima e caráter: a versão os
    # reproduz, e duplicá-los criaria a segunda fonte divergente que o princípio da fonte
    # autoritativa única proíbe (FR-071, FR-072).
    versao = models.ForeignKey(
        VersaoConsolidada,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="avaliacoes",
    )
    revision = models.PositiveBigIntegerField(default=1)
    concluida_em = models.DateTimeField(null=True, blank=True)
    # Identificador estável, e não referência ao vínculo: a autoria é histórica e sobrevive à
    # saída da pessoa da comissão (FR-006).
    concluida_por = models.CharField(max_length=255, blank=True)

    class Meta:
        constraints = [
            # Uma conclusão por pessoa, inscrição e Etapa — qualquer que seja o número de
            # Atribuições, ou de vínculos, que tenham existido ali. É esta restrição que impede o
            # contorno "remover, reatribuir, avaliar de novo", e o caminho de volta é a reabertura
            # da presidência (FR-074).
            models.UniqueConstraint(
                fields=["identity_subject", "etapa_id", "inscricao_id"],
                condition=Q(estado="CONCLUIDA"),
                name="uq_avaliacao_concluida_por_pessoa",
            ),
            # O que "concluída" significa, dito no banco: sem pontuação, versão, instante e autor,
            # o estado não é alcançável. O mesmo padrão de `ck_inscricao_submetida_completa`.
            models.CheckConstraint(
                condition=Q(estado="RASCUNHO")
                | Q(
                    estado="CONCLUIDA",
                    pontuacao__isnull=False,
                    versao__isnull=False,
                    concluida_em__isnull=False,
                )
                & ~Q(concluida_por=""),
                name="ck_avaliacao_concluida_completa",
            ),
        ]
        indexes = [models.Index(fields=["identity_subject", "etapa_id", "estado"])]

    def __str__(self):
        return f"Avaliação {self.id} — {self.estado}"


class ConclusaoAvaliacao(models.Model):
    """O que havia sido concluído antes de cada reabertura.

    Append-only, como `AtoAdministrativo` e `VersaoConsolidada`. Existe porque reabrir **não pode
    destruir** o que foi concluído: depois de quantas reaberturas vierem, "o que aquela pessoa
    havia concluído antes da terceira" tem de ser uma consulta, e não arqueologia de trilha. A
    trilha registra que o ato aconteceu; o conteúdo do ato vive no domínio (FR-094, FR-054).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    avaliacao = models.ForeignKey(Avaliacao, on_delete=models.PROTECT, related_name="conclusoes")
    ordem = models.PositiveIntegerField()
    pontuacao = models.DecimalField(max_digits=7, decimal_places=4)
    parecer = models.TextField(blank=True)
    versao = models.ForeignKey(
        VersaoConsolidada, on_delete=models.PROTECT, related_name="conclusoes_de_avaliacao"
    )
    concluida_em = models.DateTimeField()
    concluida_por = models.CharField(max_length=255)

    class Meta:
        ordering = ["avaliacao", "ordem"]
        constraints = [
            models.UniqueConstraint(fields=["avaliacao", "ordem"], name="uq_conclusao_ordem")
        ]

    def __str__(self):
        return f"Conclusão {self.ordem} de {self.avaliacao_id}"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise TypeError("ConclusaoAvaliacao é append-only")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise TypeError("ConclusaoAvaliacao é append-only")


class Impedimento(models.Model):
    """Esta pessoa não avalia esta inscrição, e o motivo está escrito.

    Ancorado na **pessoa**, e não no vínculo: preso a `MembroComissao`, morreria quando ela saísse
    da comissão, e readicioná-la seria o caminho para contorná-lo (FR-099).

    Sem coluna de estado, de propósito: revogar impedimento não está na spec, e criar o campo agora
    seria inventar ciclo de vida sem caso de uso. A consulta é "existe Impedimento para este par".
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    identity_subject = models.CharField(max_length=255)
    # A inscrição já determina Edital e Processo; não há terceira coluna a guardar.
    inscricao = models.ForeignKey(Inscricao, on_delete=models.PROTECT, related_name="impedimentos")
    motivo = models.TextField()
    criado_em = models.DateTimeField()
    criado_por = models.CharField(max_length=255)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["identity_subject", "inscricao"], name="uq_impedimento_pessoa_inscricao"
            )
        ]
        indexes = [models.Index(fields=["inscricao"])]

    def __str__(self):
        return f"{self.identity_subject} — {self.inscricao_id}"
