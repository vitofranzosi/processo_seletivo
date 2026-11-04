"""As quatro tabelas da entrega documental à formalização (117): append-only, sem arquivo.

**Quatro atos, quatro donos** (Complexity Tracking do plano): a condução define **o quê**, a gestão
de acessos define **quem** e a revoga, e o setor **exporta**. Cada um grava a própria linha, e
nenhuma muda depois: a versão nova da definição é linha nova, a revogação é linha nova, e o registro
da exportação existe só para pacote gerado (FR-3697).

**Três camadas**: `save` e `delete` recusam aqui, o gatilho da `0001` recusa no banco, e o papel de
runtime não tem `UPDATE` nem `DELETE` (`TABELAS_APPEND_ONLY`).

**Nada pessoal**: só identificadores, hashes e o motivo de quem decidiu (FR-3700). O nome e o
protocolo da pessoa vão no pacote e no manifesto, e nunca numa linha daqui.

**Nenhuma coluna presume que a unidade do ator é a do Edital** (FR-3708): a unidade de atuação é
gravada em cada linha, ao lado do Edital, e nenhuma unicidade as combina.
"""

import uuid

from django.db import models
from django.db.models import Q

from processo_seletivo.formalizacao.domain import nomes
from processo_seletivo.processos.models import Edital


class _AppendOnly(models.Model):
    """`save` só de linha nova e `delete` recusado — a primeira das três camadas."""

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise TypeError(f"{type(self).__name__} é append-only")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise TypeError(f"{type(self).__name__} é append-only")


class DefinicaoDosDocumentosDaFormalizacao(_AppendOnly):
    """Uma versão da lista de requisitos que vão ao setor que formaliza (FR-3653 a FR-3660).

    **A vigente é a mais recente**, e vazia é uma versão legítima: a condução que retira tudo diz,
    com motivo, que nada vai ao setor. Sem linha nenhuma, nada vai também (FR-3660).

    **Lista de UUID, e não FK** (data-model): o requisito é identificado pela identidade publicada,
    estável entre versões, como o `requisito_id` do item da convocação da `115`. As linhas do
    rascunho são recriadas a cada gravação, e uma FK se perderia.

    **Fora do conteúdo publicado** (FR-3657, D-009): nada aqui entra no snapshot, no hash ou no PDF,
    e corrigir a favor da minimização não pede Retificação.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    edital = models.ForeignKey(
        Edital, on_delete=models.PROTECT, related_name="definicoes_da_formalizacao"
    )
    #: Os ids dos requisitos, como texto. JSON, e não `ArrayField`: nenhum app usa tipo exclusivo
    #: do PostgreSQL, e a suíte em modo padrão perderia a tabela inteira por um campo.
    requisitos = models.JSONField(default=list, blank=True)
    motivo = models.TextField()
    definido_por = models.CharField(max_length=255)
    unidade_de_atuacao = models.CharField(max_length=100)
    definido_em = models.DateTimeField()

    class Meta:
        ordering = ["definido_em", "id"]
        constraints = [
            models.CheckConstraint(
                condition=~Q(motivo=""), name="ck_definicao_formalizacao_com_motivo"
            ),
        ]
        indexes = [
            models.Index(fields=["edital", "definido_em"], name="ix_definicao_formalizacao"),
        ]

    def __str__(self):
        return f"definição {self.id} do Edital {self.edital_id}"


class DesignacaoParaFormalizacao(_AppendOnly):
    """A pessoa do setor que alcança os documentos de um Edital, com Perfis opcionais (FR-3662).

    **Vigente é a que não tem revogação.** O papel vigente e a pessoa não suspensa se conferem no
    predicado, a cada requisição, e não aqui: é assim que revogar o papel corta todas as designações
    de uma vez (FR-3667).

    **Uma vigente por (Edital, pessoa)**, garantida na aplicação com a pessoa trancada, como a
    concessão da `107`: a regra depende da ausência de linha noutra tabela, e não cabe em índice.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    edital = models.ForeignKey(
        Edital, on_delete=models.PROTECT, related_name="designacoes_da_formalizacao"
    )
    #: O `identity_subject` da pessoa, que é o `subject` do ator dela.
    pessoa = models.CharField(max_length=255)
    #: Vazio é todos os Perfis do Edital.
    perfis = models.JSONField(default=list, blank=True)
    motivo = models.TextField()
    designado_por = models.CharField(max_length=255)
    unidade_de_atuacao = models.CharField(max_length=100)
    designado_em = models.DateTimeField()

    class Meta:
        ordering = ["designado_em", "id"]
        constraints = [
            models.CheckConstraint(
                condition=~Q(motivo=""), name="ck_designacao_formalizacao_com_motivo"
            ),
            # **A autodesignação recusada pelo banco também** (FR-3663): a aplicação recusa antes,
            # com código próprio; esta é a camada que vale para quem chegar por fora dela.
            models.CheckConstraint(
                condition=~Q(designado_por=models.F("pessoa")),
                name="ck_designacao_formalizacao_sem_autodesignacao",
            ),
        ]
        indexes = [
            models.Index(fields=["edital", "pessoa"], name="ix_designacao_formalizacao"),
            models.Index(fields=["pessoa"], name="ix_designacao_formalizacao_pes"),
        ]

    def __str__(self):
        return f"designação {self.id} no Edital {self.edital_id}"

    def cobre(self, perfil_id):
        return not self.perfis or str(perfil_id) in {str(perfil) for perfil in self.perfis}


class RevogacaoDaDesignacao(_AppendOnly):
    """O fim de uma designação. Uma por designação: a segunda o banco recusa."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    designacao = models.OneToOneField(
        DesignacaoParaFormalizacao, on_delete=models.PROTECT, related_name="revogacao"
    )
    motivo = models.TextField()
    revogado_por = models.CharField(max_length=255)
    unidade_de_atuacao = models.CharField(max_length=100)
    revogado_em = models.DateTimeField()

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=~Q(motivo=""), name="ck_revogacao_formalizacao_com_motivo"
            ),
        ]

    def __str__(self):
        return f"revogação da designação {self.designacao_id}"


class ExportacaoDeFormalizacao(_AppendOnly):
    """O registro de um pacote gerado e disponibilizado para download (FR-3697, FR-3700).

    **Só existe para pacote gerado.** A verificação, a verificação defasada, a recusa e a
    interrupção vão para a trilha, e não para cá: um registro aqui afirma que o GPS montou aquele
    pacote, com aquele hash, e o serviu.

    **Gravado depois de o pacote estar montado e antes de a resposta começar** (FR-3698): uma
    transferência cortada não o altera, e ele diz só o que é verdade — gerado e disponibilizado.

    **JSON, e não tabelas filhas** (data-model), como a `GeracaoDeArquivo` da `031`: o registro é
    lido inteiro, para o histórico e a auditoria, e duas tabelas filhas seriam mais duas
    append-only sem consulta que as exija.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    edital = models.ForeignKey(
        Edital, on_delete=models.PROTECT, related_name="exportacoes_da_formalizacao"
    )
    designacao = models.ForeignKey(
        DesignacaoParaFormalizacao, on_delete=models.PROTECT, related_name="exportacoes"
    )
    definicao = models.ForeignKey(
        DefinicaoDosDocumentosDaFormalizacao, on_delete=models.PROTECT, related_name="exportacoes"
    )
    alcance = models.CharField(max_length=16)
    perfil_id = models.UUIDField(null=True, blank=True)
    resultado = models.CharField(max_length=16)
    #: `[{inscricao, convocacao, situacao, motivo?}]`, como a verificação as mostrou.
    pessoas = models.JSONField(default=list)
    #: `[{inscricao, origem, id, sha256}]`, só dos documentos incluídos.
    documentos = models.JSONField(default=list)
    quantidade_de_arquivos = models.PositiveIntegerField()
    tamanho = models.PositiveBigIntegerField()
    hash_do_pacote = models.CharField(max_length=64)
    exportado_por = models.CharField(max_length=255)
    unidade_de_atuacao = models.CharField(max_length=100)
    exportado_em = models.DateTimeField()

    class Meta:
        ordering = ["-exportado_em", "-id"]
        constraints = [
            models.CheckConstraint(
                condition=Q(alcance__in=list(nomes.ALCANCES)),
                name="ck_exportacao_formalizacao_alcance",
            ),
            models.CheckConstraint(
                condition=Q(resultado__in=list(nomes.RESULTADOS)),
                name="ck_exportacao_formalizacao_resultado",
            ),
            models.CheckConstraint(
                condition=~Q(hash_do_pacote=""), name="ck_exportacao_formalizacao_hash"
            ),
            models.CheckConstraint(
                condition=Q(quantidade_de_arquivos__gt=0),
                name="ck_exportacao_formalizacao_com_arquivo",
            ),
            # **A pessoa única com falha não gera pacote** (FR-3685): o registro de uma pessoa só é
            # sempre completo, e não tem recorte.
            models.CheckConstraint(
                condition=~Q(alcance=nomes.PESSOA)
                | Q(perfil_id__isnull=True, resultado=nomes.COMPLETO),
                name="ck_exportacao_formalizacao_pessoa",
            ),
        ]
        indexes = [
            models.Index(fields=["edital", "exportado_em"], name="ix_exportacao_formalizacao"),
        ]

    def __str__(self):
        return f"exportação {self.id} do Edital {self.edital_id}"

    @property
    def incluidas(self):
        return [p for p in self.pessoas if p.get("situacao") == nomes.INCLUIDA]

    @property
    def nao_incluidas(self):
        return [p for p in self.pessoas if p.get("situacao") == nomes.NAO_INCLUIDA]
