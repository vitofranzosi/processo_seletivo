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

from processo_seletivo.avaliacoes.domain.formas import Forma, Sentido
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
    # A forma sob a qual esta avaliação foi concluída, lida do conteúdo da versão validada dentro da
    # transação que conclui, e gravada aqui (FR-117). **É a única cópia que a Avaliação faz**, e a
    # exceção a FR-072 tem um motivo que mínima, máxima e caráter não têm: uma `CheckConstraint`
    # do PostgreSQL não referencia outra tabela, e sem a forma na linha a regra que define
    # "concluída" sairia do banco e voltaria para a aplicação — a camada de que esta spec desconfiou
    # quando escreveu a constraint. Onde a cópia não compra invariante, ela continua proibida.
    #
    # **Vazio, e não nulo**, como `concluida_por` na linha abaixo: o projeto não usa `NULL` em campo
    # de texto, e a mesma constraint já compara `~Q(concluida_por="")`. Vazio aqui significa "ainda
    # não concluída": a forma é lida no ato de concluir, e carimbá-la no nascimento faria um
    # rascunho aberto hoje concluir sob a forma de ontem.
    forma = models.CharField(max_length=20, choices=Forma.choices, blank=True, default="")
    pontuacao = models.DecimalField(max_digits=7, decimal_places=4, null=True, blank=True)
    # O que o avaliador afirmou, na forma decisória. Não se chama `decisão`: avaliar não é decidir,
    # e duas análises documentais podem afirmar sentidos opostos — resolver isso é da 013 (P-006).
    sentido = models.CharField(max_length=20, choices=Sentido.choices, blank=True, default="")
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
            # O que "concluída" significa, dito no banco. **Completa deixou de significar "tem
            # nota" e passou a significar "tem o que a forma exige"** (D-008, FR-116): o invariante
            # forte não foi relaxado, e o que mudou foi o que ele afirma. Sem versão, instante,
            # autor e forma o estado continua inalcançável; e, dentro da forma, cada uma exige o
            # que é seu e recusa o que é da outra.
            models.CheckConstraint(
                condition=Q(estado="RASCUNHO")
                | (
                    Q(
                        estado="CONCLUIDA",
                        versao__isnull=False,
                        concluida_em__isnull=False,
                    )
                    & ~Q(concluida_por="")
                    & (
                        Q(forma=Forma.PONTUADA, pontuacao__isnull=False, sentido="")
                        | Q(forma=Forma.DECISORIA, pontuacao__isnull=True) & ~Q(sentido="")
                    )
                ),
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
    # A forma que governou aquela conclusão, preservada pela mesma razão que a versão é (FR-071,
    # FR-117): se uma Retificação mudar a natureza da Etapa depois, a conclusão antiga precisa
    # continuar interpretável sob a regra que a governou. Não anulável — não existe conclusão sem
    # forma —, e as linhas que já existiam receberam `PONTUADA`, que é o que todas eram.
    forma = models.CharField(max_length=20, choices=Forma.choices)
    # `pontuacao` deixou de ser `NOT NULL`, e a completude passou a ser verificada por forma: a
    # coluna sozinha não sabe mais dizer o que "concluída" significa.
    pontuacao = models.DecimalField(max_digits=7, decimal_places=4, null=True, blank=True)
    sentido = models.CharField(max_length=20, choices=Sentido.choices, blank=True, default="")
    parecer = models.TextField(blank=True)
    versao = models.ForeignKey(
        VersaoConsolidada, on_delete=models.PROTECT, related_name="conclusoes_de_avaliacao"
    )
    concluida_em = models.DateTimeField()
    concluida_por = models.CharField(max_length=255)

    class Meta:
        ordering = ["avaliacao", "ordem"]
        constraints = [
            models.UniqueConstraint(fields=["avaliacao", "ordem"], name="uq_conclusao_ordem"),
            # O que a coluna `NOT NULL` garantia sozinha, dito agora por forma. Sem isto, a
            # preservação histórica aceitaria uma conclusão vazia — e numa tabela append-only o
            # registro inválido entraria uma vez e ficaria, porque nada o corrige depois.
            models.CheckConstraint(
                condition=Q(forma=Forma.PONTUADA, pontuacao__isnull=False, sentido="")
                | Q(forma=Forma.DECISORIA, pontuacao__isnull=True) & ~Q(sentido=""),
                name="ck_conclusao_completa_por_forma",
            ),
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
