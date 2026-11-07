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
    # O Anexo cujo modelo este requisito manda usar (020, FR-020). Anulável já é `N:1` por
    # construção, e não há o que escolher: o requisito ou fornece forma própria, ou não fornece.
    #
    # `SET_NULL` é a forma da resposta que o repositório já deu em `EtapaAvaliacao.evento` —
    # *"remover o Evento não pode remover a Etapa; o que não pode é o vínculo sobreviver a ele"*.
    # Remover o Anexo não remove o requisito: desfaz o vínculo, e requisito sem modelo é legítimo.
    anexo = models.ForeignKey(
        "editais.AnexoEdital",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="requisitos",
    )
    # O recorte transversal (044): a Modalidade deste **código** em todos os Perfis que a têm. É
    # texto, e não chave estrangeira, porque não há uma Modalidade só a apontar — o PcD do C1 e o
    # PcD do C2 são objetos distintos, e o que eles têm em comum é o código, que é estrutural.
    # Mesmo tamanho de `ModalidadeConcorrencia.code`, e `""` quando não recorta por código, pela
    # mesma convenção de `instructions`: uma segunda forma de ausência para texto faria o rascunho
    # admitir duas. No conteúdo publicado a ausência é `null`, como no degrau 17.
    modalidade_codigo = models.CharField(max_length=100, blank=True, default="")
    # **Quando** o documento é pedido: na inscrição ou na convocação (115, FR-3563). O vocabulário é
    # o do Requerimento de Matrícula, e a inscrição é o padrão porque é o que todo documento
    # anterior a esta feature significava.
    momento = models.CharField(
        max_length=20,
        choices=[("AT_ENROLLMENT", "Na inscrição"), ("AT_CALL", "Na convocação")],
        default="AT_ENROLLMENT",
    )
    # O documento da inscrição que atende este, da convocação, se enviado (115, FR-3566). **UUID, e
    # não chave estrangeira**: as linhas do rascunho são apagadas e recriadas a cada gravação, e uma
    # FK entre duas delas se perderia na recriação. A coerência é conferida na publicação, como a do
    # Perfil que o recorte aponta.
    aproveita = models.UUIDField(null=True, blank=True)
    # **A condição de exigência** (131, FR-4451): o caso em que o documento obrigatório da
    # convocação é exigido, como o Edital o publica — *"no caso de candidatos do sexo masculino,
    # maiores de 18 anos"*. É texto, e o sistema não o avalia (D-002): ele o publica, o congela pela
    # versão da lista e decide por ele se a conferência admite *"não se aplica"*. `""` quando não
    # há, pela convenção de `instructions`; no conteúdo publicado a ausência é `null` (degrau 19).
    condicao = models.CharField(max_length=300, blank=True, default="")

    class Meta:
        ordering = ["order", "id"]
        constraints = [
            models.UniqueConstraint(fields=["edital", "key"], name="uq_documento_edital_key"),
            models.UniqueConstraint(fields=["edital", "order"], name="uq_documento_edital_order"),
            # Cinco formas, mutuamente exclusivas (044, D-006). A recusa com mensagem é do domínio;
            # esta é a segunda barreira, a que não depende de a aplicação lembrar.
            models.CheckConstraint(
                condition=models.Q(modalidade_codigo="")
                | models.Q(perfil__isnull=True, modalidade__isnull=True),
                name="ck_documento_recorte_exclusivo",
            ),
            # Só o documento da convocação aproveita outro; a recusa com mensagem é do domínio.
            models.CheckConstraint(
                condition=models.Q(aproveita__isnull=True) | models.Q(momento="AT_CALL"),
                name="ck_documento_aproveita_so_na_convocacao",
            ),
        ]

    def __str__(self):
        return f"{self.order} — {self.name}"
