import uuid

from django.db import models


class ProcessoSeletivo(models.Model):
    class Status(models.TextChoices):
        EM_ELABORACAO = "EM_ELABORACAO"
        ATIVO = "ATIVO"
        ENCERRADO = "ENCERRADO"
        CANCELADO = "CANCELADO"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    institution_scope = models.CharField(max_length=100)
    institutional_code = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.EM_ELABORACAO)
    revision = models.PositiveBigIntegerField(default=1)
    created_at = models.DateTimeField()
    created_by = models.CharField(max_length=255)
    last_changed_at = models.DateTimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["institution_scope", "institutional_code"],
                name="uq_processo_scope_institutional_code",
            )
        ]

    def __str__(self):
        return f"{self.institutional_code} — {self.title}"


class Edital(models.Model):
    class Status(models.TextChoices):
        EM_ELABORACAO = "EM_ELABORACAO"
        EM_REVISAO = "EM_REVISAO"
        HOMOLOGADO = "HOMOLOGADO"
        PUBLICADO = "PUBLICADO"
        ENCERRADO = "ENCERRADO"
        CANCELADO = "CANCELADO"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    processo = models.ForeignKey(ProcessoSeletivo, on_delete=models.PROTECT, related_name="editais")
    institution_scope = models.CharField(max_length=100)
    number = models.CharField(max_length=50)
    year = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.EM_ELABORACAO)
    revision = models.PositiveBigIntegerField(default=1)
    next_publication_order = models.PositiveBigIntegerField(default=1)
    # Quantas Inscrições um candidato pode ter **neste Edital**. Anulável, e a ausência significa
    # sem limite, que é o comportamento de hoje (D-3).
    #
    # **Do Edital, e não do Perfil.** A restrição existente é
    # `uq_inscricao_identidade_edital_perfil` — uma inscrição por Perfil, várias por Edital. Um teto
    # por Perfil com valor 1 repetiria essa constraint, e com valor maior descreveria o que ela
    # proíbe. O que os Editais 14 (7.8) e 57 exigem é uma por **Edital**, que é limite sobre o
    # total; e total é do certame, não de um dos Perfis dele. A constraint permanece: ela impede a
    # duplicata por Perfil, e este campo limita o total (015, FR-063).
    max_inscricoes_por_candidato = models.PositiveIntegerField(null=True, blank=True)
    # **Se este certame exige Requerimento de Matrícula, e quando** (029, `FR-368`, `FR-369`).
    #
    # **Vazio significa que este Edital não declarou** — nunca "faz do jeito comum". É a grafia que
    # `especie_de_reversao` e `forma_de_convocacao` já usam, e pela mesma razão: escolher um padrão
    # por omissão inventaria norma. No conteúdo publicado a ausência tem outra grafia — a chave
    # presente com `null` —, e as duas não se misturam: `""` é coluna, `null` é snapshot.
    #
    # **Do Edital, e não do Perfil.** O requerimento é o mesmo conjunto institucional para todo
    # Perfil do certame; repartir por Perfil criaria configuração sem caso.
    #
    # **É esta declaração que confina a feature a processos de alunos.** O sistema não tem taxonomia
    # de natureza do Processo, e criá-la seria inventar um eixo que nenhuma outra feature consome:
    # um Edital de tutores, bolsistas ou servidores simplesmente não declara, e nele a capacidade
    # não existe — não fica escondida, não fica desabilitada, não existe (029, `D-002`).
    requerimento_momento = models.CharField(
        max_length=32,
        blank=True,
        default="",
        choices=[
            ("AT_ENROLLMENT", "Na inscrição"),
            ("AT_CALL", "Na convocação"),
        ],
    )
    # O texto da declaração de veracidade que o candidato aceita (029, `D-011`, `FR-407`).
    #
    # **É norma do Edital, e não literal de código**: ela varia entre certames, é o que a pessoa
    # assina, e é o que fundamenta o cancelamento por informação falsa. Por isso entra no conteúdo
    # publicado e se corrige por Retificação como todo texto normativo — e por isso o aceite guarda
    # o **resumo do texto exibido**, de modo que retificar depois não reescreva o que alguém leu.
    #
    # Edital que declara momento e não tem texto **não publica**: aceite sem texto é aceite de nada.
    requerimento_declaracao = models.TextField(blank=True, default="")
    created_at = models.DateTimeField()
    created_by = models.CharField(max_length=255)
    last_edited_by = models.CharField(max_length=255)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["institution_scope", "number", "year"],
                name="uq_edital_scope_number_year",
            )
        ]
        indexes = [models.Index(fields=["processo", "status"])]

    def __str__(self):
        return f"Edital {self.number}/{self.year}"


class AtoAdministrativo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    aggregate_type = models.CharField(max_length=50)
    aggregate_id = models.UUIDField()
    operation = models.CharField(max_length=50)
    actor_subject = models.CharField(max_length=255)
    reason = models.TextField()
    occurred_at = models.DateTimeField()

    def __str__(self):
        return f"{self.operation}:{self.aggregate_type}:{self.aggregate_id}"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise TypeError("AtoAdministrativo é append-only")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise TypeError("AtoAdministrativo é append-only")
