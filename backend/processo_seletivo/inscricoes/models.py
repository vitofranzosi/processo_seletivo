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


class ValorDeFato(models.Model):
    """O que a inscrição congelou na submissão, sob a versão que então vigorava (015, D-2).

    **Nasce na submissão, e não na abertura do rascunho.** É a fronteira que a `009` já usa para
    tudo o mais que a inscrição afirma, e usar outra faria os fatos e as declarações responderem a
    versões diferentes do mesmo Edital.

    **Nasce e não muda mais.** O valor que entra na classificação tem de ser o do momento da
    inscrição: sem isso, editar o perfil depois mudaria classificação histórica. A tabela entra em
    `TABELAS_APPEND_ONLY`, e por isso `inscricao` é `PROTECT` e não `CASCADE` — o runtime não tem
    `DELETE`, e um `CASCADE` que jamais poderia executar seria promessa falsa no esquema.

    Da `015` até a `inscricoes/0006`, o privilégio foi a única camada: sem gatilho e sem recusa,
    quem conectava com privilégio reescrevia o valor em silêncio. A `0006` pôs o gatilho, e
    `save`/`delete` abaixo recusam antes do banco (`doc/achado-valor-de-fato-sem-gatilho.md`). O
    `bulk_create` do envio não passa por `save`, e é a única escrita que a tabela admite.

    **A consequência precisa ser dita:** o candidato **não corrige** o que informou depois de
    submeter. A `009` não tem retificação de inscrição, e esta feature não a cria. É o que D-2
    pede, porque congelar é o ponto inteiro.

    `fato_id` guarda a identidade **publicada** do fato, e não chave estrangeira para a linha de
    elaboração — mesma razão de `ResultadoEtapa.etapa_id`: a Retificação sabe acrescentar item a
    coleção e não escreve de volta em `editais`.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inscricao = models.ForeignKey(Inscricao, on_delete=models.PROTECT, related_name="fatos")
    fato_id = models.UUIDField()
    valor_data = models.DateField(null=True, blank=True)
    valor_inteiro = models.IntegerField(null=True, blank=True)
    congelado_em = models.DateTimeField()
    versao = models.ForeignKey(
        "publicacoes.VersaoConsolidada", on_delete=models.PROTECT, related_name="fatos_congelados"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["inscricao", "fato_id"], name="uq_valor_por_inscricao_fato"
            ),
            # Um dos dois, nunca os dois e nunca nenhum: o tipo declarado diz qual, e uma linha com
            # os dois preenchidos admitiria duas leituras do mesmo fato.
            models.CheckConstraint(
                condition=Q(valor_data__isnull=False, valor_inteiro__isnull=True)
                | Q(valor_data__isnull=True, valor_inteiro__isnull=False),
                name="ck_valor_conforme_tipo",
            ),
        ]

    def __str__(self):
        return f"{self.fato_id} — {self.valor_data or self.valor_inteiro}"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise TypeError("O valor de fato é append-only: ele é o que o envio congelou.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise TypeError("O valor de fato é append-only.")


class ItemDaListaExigida(models.Model):
    """O que foi pedido a uma inscrição, documento a documento, gravado no envio (044, D4).

    A Constituição pede que o sistema **reproduza** os documentos exigidos de cada Inscrição. Antes
    desta tabela ele os **recalculava**: a Mesa refazia o recorte sobre a versão aceita, e herdava o
    erro dele — no 903/2026, o laudo que o portal dispensou por erro sumiu também da análise, e o
    analista indeferiu por um documento que o sistema nunca tinha pedido.

    **Um item por Documento Exigido da versão aceita, inclusive os que não se aplicam** (D-003).
    "Não se aplica" é informação registrada, e não ausência de linha: gravar só os aplicáveis
    deixaria o resto para ser deduzido na leitura, e deduzir é recalcular.

    **O que ela protege, dito com precisão.** Os leitores já liam a versão aceita, que é imutável:
    uma Retificação posterior não mudava a Mesa. O que muda sem esta tabela é a **regra**, no
    código — como a que a própria `044` mudou em `aplicaveis`. A lista é a leitura que não depende
    da regra do dia (R-006).

    **Append-only, nas duas camadas**: `TABELAS_APPEND_ONLY` tira do runtime `UPDATE` e `DELETE`, e
    o gatilho recusa a mutação mesmo de quem tem privilégio. `ValorDeFato`, gravado no mesmo ato,
    tem só a primeira — a lista não repete isso (R-005). Por isso `inscricao` é `PROTECT`: um
    `CASCADE` que jamais poderia executar seria promessa falsa no esquema.

    **O que o gatilho não garante** é o preenchimento retroativo: quem copiar `submitted_at` para
    `gravada_em` passa. Essa garantia é da aplicação — só o envio e a semente gravam (D-004).

    Não guarda nome, instrução nem arquivo: a versão aceita é imutável e está na linha, e ler o nome
    dela não é recalcular recorte. Copiar o texto seria uma segunda fonte para o mesmo valor.
    """

    class Situacao(models.TextChoices):
        OBRIGATORIO = "OBRIGATORIO"
        FACULTATIVO = "FACULTATIVO"
        NAO_SE_APLICA = "NAO_SE_APLICA"

    class Forma(models.TextChoices):
        TODOS = "TODOS"
        PERFIL = "PERFIL"
        PERFIL_E_MODALIDADE = "PERFIL_E_MODALIDADE"
        MODALIDADE_EM_TODOS_OS_PERFIS = "MODALIDADE_EM_TODOS_OS_PERFIS"
        TODOS_COM_MODALIDADE_DE_UM_PERFIL = "TODOS_COM_MODALIDADE_DE_UM_PERFIL"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inscricao = models.ForeignKey(Inscricao, on_delete=models.PROTECT, related_name="lista_exigida")
    versao = models.ForeignKey(
        VersaoConsolidada, on_delete=models.PROTECT, related_name="listas_exigidas"
    )
    # A identidade **publicada** do documento, e não chave estrangeira para a linha de elaboração,
    # pela razão de `ValorDeFato.fato_id`.
    requisito_id = models.UUIDField()
    chave = models.CharField(max_length=100)
    situacao = models.CharField(max_length=16, choices=Situacao.choices)
    forma_do_recorte = models.CharField(max_length=40, choices=Forma.choices)
    perfil_id = models.UUIDField(null=True, blank=True)
    modalidade_id = models.UUIDField(null=True, blank=True)
    modalidade_codigo = models.CharField(max_length=100, blank=True, default="")
    # O documento publicado o exigia de quem concorre nesta modalidade, e o portal não o pediu:
    # a forma que a #161 passou a recusar, em versão publicada antes dela (FR-727, D-007).
    divergente_do_publicado = models.BooleanField(default=False)
    gravada_em = models.DateTimeField()

    class Meta:
        ordering = ["gravada_em", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["inscricao", "requisito_id"], name="uq_item_da_lista_por_requisito"
            ),
            models.CheckConstraint(
                condition=Q(situacao__in=["OBRIGATORIO", "FACULTATIVO", "NAO_SE_APLICA"]),
                name="ck_item_da_lista_situacao",
            ),
            # Os parâmetros coerentes com a forma: cada forma usa exatamente os seus.
            models.CheckConstraint(
                condition=(
                    Q(
                        forma_do_recorte="TODOS",
                        perfil_id__isnull=True,
                        modalidade_id__isnull=True,
                        modalidade_codigo="",
                    )
                    | Q(
                        forma_do_recorte="PERFIL",
                        perfil_id__isnull=False,
                        modalidade_id__isnull=True,
                        modalidade_codigo="",
                    )
                    | Q(
                        forma_do_recorte="PERFIL_E_MODALIDADE",
                        perfil_id__isnull=False,
                        modalidade_id__isnull=False,
                        modalidade_codigo="",
                    )
                    | (
                        Q(
                            forma_do_recorte="MODALIDADE_EM_TODOS_OS_PERFIS",
                            perfil_id__isnull=True,
                            modalidade_id__isnull=True,
                        )
                        & ~Q(modalidade_codigo="")
                    )
                    | Q(
                        forma_do_recorte="TODOS_COM_MODALIDADE_DE_UM_PERFIL",
                        perfil_id__isnull=True,
                        modalidade_id__isnull=False,
                        modalidade_codigo="",
                    )
                ),
                name="ck_item_da_lista_forma",
            ),
            models.CheckConstraint(
                condition=Q(divergente_do_publicado=False)
                | Q(forma_do_recorte="TODOS_COM_MODALIDADE_DE_UM_PERFIL"),
                name="ck_item_da_lista_divergencia",
            ),
        ]
        indexes = [models.Index(fields=["inscricao"])]

    def __str__(self):
        return f"{self.inscricao_id} — {self.chave} — {self.situacao}"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise TypeError("A lista exigida é append-only: ela é o que foi pedido no envio.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise TypeError("A lista exigida é append-only.")


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
