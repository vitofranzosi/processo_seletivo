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

from processo_seletivo.inscricoes.storage import ArmazenamentoPrivado, caminho_do_documento
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
            # O CPF que a `010` precisa poder ler: a reconciliação agrupa por ele, e a marcação de
            # coincidência compara por ele. Onze dígitos é **tudo** o que uma restrição
            # declarativa consegue afirmar — o algoritmo dos dígitos verificadores não cabe aqui,
            # e continua onde já estava: na captura, e na verificação que a implantação faz antes
            # de instalar esta restrição. Prometer no texto o que o banco não entrega é pior que
            # não prometer, porque ninguém confere (FR-063).
            models.CheckConstraint(
                condition=Q(status="RASCUNHO") | Q(cpf_normalizado__regex=r"^[0-9]{11}$"),
                name="ck_inscricao_submetida_com_cpf",
            ),
        ]
        indexes = [models.Index(fields=["edital", "status"])]

    def __str__(self):
        return f"Inscrição {self.protocolo or self.id}"

    def save(self, *args, **kwargs):
        """Enviada, não muda mais (FR-054, FR-064).

        Antes do envio a Inscrição muda o tempo todo — é um rascunho, e `revision` avança a cada
        gravação. Depois dele, nada: nem instante, nem protocolo, nem versão aceita, nem os dados
        pessoais. É o mesmo padrão de `Publicacao` e `VersaoConsolidada`, e vale para o registro
        inteiro porque é o registro inteiro que passa a ser peça de um ato administrativo.

        A transição em si não passa por aqui: ela acontece por `compare_and_swap`, que atualiza
        pelo queryset — e é justamente por isso que esta guarda pode ser total sem impedir o
        próprio envio.

        **O que ela não é**: garantia de banco. `Inscricao` muda legitimamente enquanto está em
        rascunho, então ela não entra nas tabelas append-only da `003` — pela mesma razão que
        `Retificacao` ficou de fora: imutabilidade condicional ao estado não cabe em privilégio de
        tabela.
        """
        if not self._state.adding:
            anterior = Inscricao.objects.filter(pk=self.pk).values("status").first()
            if anterior and anterior["status"] == self.Status.SUBMETIDA:
                raise TypeError("Inscrição submetida não é alterada.")
        return super().save(*args, **kwargs)


class DocumentoSubmetido(models.Model):
    """O arquivo que o candidato apresentou **para um Documento Exigido específico**.

    É esta ligação — e não uma pasta com o nome da pessoa — que permitirá à comissão abrir
    *Diploma exigido → documento apresentado*. Sem ela, o sistema teria transferido o Drive para
    dentro de uma aplicação web em vez de substituí-lo (P-006).

    `requirement_id` referencia o requisito no **conteúdo publicado**, pelo mesmo motivo que
    `profile_id` na Inscrição: é a identidade estável que sobrevive à Retificação.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inscricao = models.ForeignKey(Inscricao, on_delete=models.CASCADE, related_name="documentos")
    requirement_id = models.UUIDField()
    arquivo = models.FileField(
        storage=ArmazenamentoPrivado(), upload_to=caminho_do_documento, max_length=255
    )
    # O nome que a pessoa enviou, preservado para exibição e nada além: ele não decide caminho,
    # não decide identidade e não é confiável (FR-052).
    nome_original = models.CharField(max_length=255)
    tamanho = models.PositiveBigIntegerField()
    # Integridade do que foi recebido: permite afirmar depois que o arquivo consultado é o mesmo,
    # inclusive quando houve substituição antes do envio (FR-053).
    content_hash = models.CharField(max_length=64)
    uploaded_at = models.DateTimeField()

    class Meta:
        ordering = ["uploaded_at", "id"]
        constraints = [
            # Um arquivo por requisito (FR-043). Substituir é sobrescrever este registro, e não
            # acumular versões: a spec decidiu um arquivo, e acumular criaria a pergunta "qual
            # vale?" que ninguém respondeu.
            models.UniqueConstraint(
                fields=["inscricao", "requirement_id"], name="uq_documento_inscricao_requisito"
            )
        ]

    def __str__(self):
        return f"{self.nome_original} — {self.inscricao_id}"

    def save(self, *args, **kwargs):
        self._recusar_se_enviada("alterado")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self._recusar_se_enviada("removido")
        return super().delete(*args, **kwargs)

    def _recusar_se_enviada(self, verbo):
        """Documento de inscrição enviada não muda nem sai (FR-054).

        A camada de aplicação já recusa — `_rascunho_travado` para quem tenta pela tela. Esta
        guarda vale para o resto: um comando de manutenção, um shell, um caminho que ninguém
        escreveu ainda. O que sustenta a afirmação "o que a comissão abriu é o que o candidato
        enviou" não pode depender de todo caminho futuro lembrar de conferir.
        """
        estado = (
            Inscricao.objects.filter(pk=self.inscricao_id).values_list("status", flat=True).first()
        )
        if estado == Inscricao.Status.SUBMETIDA:
            raise TypeError(f"Documento de inscrição enviada não é {verbo}.")
