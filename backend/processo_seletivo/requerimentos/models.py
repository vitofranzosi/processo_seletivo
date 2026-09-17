"""O Requerimento de Matrícula e a base de referência de CEP.

**Uma entidade, e não três.** O endereço não tem ciclo de vida próprio, não é lista e não é
compartilhado com ninguém: uma entidade `Endereco` acrescentaria identidade e junção a um objeto
que nunca é endereçado sozinho. É a recusa que a `019` escreveu sobre a vaga individual e a `013`
sobre a ocorrência — a entidade nasce quando nasce a regra que a consome.

**Nenhum JSON e nenhum campo livre de configuração.** O conjunto é institucional e estável: o 46, o
58, o 69, o 77 e o 78 pedem os mesmos dados. Diferença pequena entre Editais não justifica
construtor de formulário — é a mesma recusa que o `DocumentoExigido` já registra ao admitir só
Perfil e modalidade como restrição.

**O que não existe aqui é requisito, e não esquecimento** (`FR-382`, `FR-391`): não há foto, tipo
sanguíneo, número de filhos, profissão, condição de trabalhador, composição do domicílio, telefone
residencial, latitude nem longitude. Oito informações do formulário em papel não são coletadas por
não terem finalidade demonstrada, e as coordenadas são recalculáveis a partir do CEP guardado.

**Esta tabela NÃO entra em `TABELAS_APPEND_ONLY`.** Ela muda legitimamente enquanto é rascunho,
exatamente como `Inscricao` e `Retificacao`, que a política de privilégios exclui de propósito: a
imutabilidade aqui é **condicional ao estado**, e privilégio de tabela não sabe ler estado. É por
isso que a garantia depois do envio é **gatilho** (migration `0002`), e não privilégio.
"""

import uuid

from django.db import models
from django.db.models import Q

from processo_seletivo.convocacao.models import Convocacao
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from processo_seletivo.requerimentos.domain import nomes


def _escolhas(valores):
    return [(valor, valor) for valor in valores]


class RequerimentoDeMatricula(models.Model):
    """O que a pessoa declara para que a candidatura vire dado apto à matrícula.

    **Uma raiz por Inscrição, e a correção é sucessão.** Enviado, o requerimento é peça de ato
    administrativo — a análise documental o lê, e o indeferimento se funda nele. Alterá-lo
    reescreveria o que fundamentou uma decisão já tomada. Mas proibir a correção sem mais nada abre
    um beco que o 77/2026 (8.2) percorre: quem é convocado **para regularizar** o indeferimento
    precisa poder corrigir. Por isso o sucessor existe, e por isso ele só nasce sob chamada em
    aberto (`FR-408`) — sem essa porta, sucessão seria edição com outro nome.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # `PROTECT`: a Inscrição não desaparece sob o requerimento que a cita.
    inscricao = models.ForeignKey(Inscricao, on_delete=models.PROTECT, related_name="requerimentos")
    status = models.CharField(
        max_length=20, choices=_escolhas(nomes.ESTADOS), default=nomes.RASCUNHO
    )
    disponibilizado_em = models.DateTimeField()
    enviado_em = models.DateTimeField(null=True, blank=True)
    revision = models.PositiveBigIntegerField(default=1)
    created_at = models.DateTimeField()

    # --- Sucessão ---------------------------------------------------------------------------
    requerimento_anterior = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.PROTECT, related_name="sucessores"
    )
    # **Qual chamada autorizou.** Preenchida também na raiz aberta por convocação, e não só no
    # sucessor: é o que torna reconstituível qual convocação abriu aquele requerimento (`FR-408`).
    convocacao_autorizadora = models.ForeignKey(
        Convocacao, null=True, blank=True, on_delete=models.PROTECT, related_name="requerimentos"
    )

    # --- Pessoa -----------------------------------------------------------------------------
    # **Anulável, e o rascunho é a razão.** Obrigatório aqui significa *obrigatório para enviar*,
    # e não *obrigatório para existir*: a pessoa preenche um formulário de vinte campos em mais de
    # uma sessão, e um rascunho que não pode nascer vazio não é rascunho. A completude do envio é
    # dita na `ck_requerimento_enviado_completo` e na validação do comando — é a mesma repartição
    # que `Inscricao` faz entre `blank=True` nos campos e o `CHECK` que só morde em `SUBMETIDA`.
    data_de_nascimento = models.DateField(null=True, blank=True)
    municipio_natal = models.CharField(max_length=120, blank=True, default="")
    uf_natal = models.CharField(max_length=2, blank=True, default="")
    # Texto, e não código: o código institucional de nacionalidade é da exportação, e o domínio não
    # o conhece (contrato §3, "sem fonte").
    nacionalidade = models.CharField(max_length=60, blank=True, default="")
    sexo = models.CharField(max_length=1, choices=_escolhas(nomes.SEXOS))
    cor_raca = models.CharField(
        max_length=20, choices=_escolhas(nomes.CORES), blank=True, default=""
    )
    estado_civil = models.CharField(
        max_length=20, choices=_escolhas(nomes.ESTADOS_CIVIS), blank=True, default=""
    )
    # `""` é ausência **declarada**, e ela não impede o envio (`FR-384`): pai não declarado é
    # situação comum e legítima, e travar o envio por isso inventaria exigência que Edital nenhum
    # faz.
    nome_da_mae = models.CharField(max_length=255, blank=True, default="")
    nome_do_pai = models.CharField(max_length=255, blank=True, default="")

    # --- Documento de identidade ------------------------------------------------------------
    rg = models.CharField(max_length=30, blank=True, default="")
    rg_orgao_emissor = models.CharField(max_length=30, blank=True, default="")
    rg_expedido_em = models.DateField(null=True, blank=True)

    # --- Contato ----------------------------------------------------------------------------
    # Pré-preenchido do telefone da Inscrição, que **congelou na submissão** e pode ter meses: ele
    # entra como ponto de partida a confirmar, nunca como verdade (`FR-379`).
    telefone_celular = models.CharField(max_length=30, blank=True, default="")

    # --- Acolhimento ------------------------------------------------------------------------
    # **Distinto da modalidade PcD** (`FR-385`): aquela é cota, com comprovação e análise; esta é
    # informação de acolhimento. Confundi-las faria a ausência de necessidade contradizer a cota
    # deferida.
    necessidade_especifica = models.TextField(blank=True, default="")

    # --- Renda ------------------------------------------------------------------------------
    # **Mede a soma da família**, e o destino significa per capita. A divergência é conhecida,
    # decidida e registrada no contrato de saída (`R-7`); não há conversão a fazer.
    renda_familiar_faixa = models.CharField(max_length=24, choices=_escolhas(nomes.FAIXAS_DE_RENDA))

    # --- Endereço ---------------------------------------------------------------------------
    cep = models.CharField(max_length=8, blank=True, default="")
    logradouro = models.CharField(max_length=255, blank=True, default="")
    # `""` admitido: "s/n" existe, e um número obrigatório obrigaria a inventá-lo.
    numero = models.CharField(max_length=20, blank=True, default="")
    complemento = models.CharField(max_length=120, blank=True, default="")
    bairro = models.CharField(max_length=120, blank=True, default="")
    municipio = models.CharField(max_length=120, blank=True, default="")
    uf = models.CharField(max_length=2, blank=True, default="")
    # **Nunca digitado pelo candidato** (`FR-388`), e `""` quando o CEP não foi reconhecido
    # (`FR-390`). Indisponibilidade da referência não impede preenchimento, envio, inscrição nem
    # matrícula: serviço externo é auxiliar, e não porta de entrada.
    codigo_ibge = models.CharField(max_length=7, blank=True, default="")
    endereco_conferido_por_referencia = models.BooleanField(default=False)

    # --- Aceite -----------------------------------------------------------------------------
    versao_aceita = models.ForeignKey(
        VersaoConsolidada,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="requerimentos_aceitos",
    )
    # O resumo do texto **exibido**, e não do texto de hoje: retificar a declaração depois não pode
    # reescrever o que a pessoa leu (`FR-393`).
    declaracao_hash = models.CharField(max_length=64, blank=True, default="")
    declaracao_aceita_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            # **Parciais, e as duas metades não são redundantes.** No PostgreSQL dois `NULL` não
            # colidem: uma restrição total sobre `inscricao` impediria o sucessor de existir, e uma
            # sobre `requerimento_anterior` colidiria entre todas as raízes. É a cirurgia que a
            # `019` documentou em `uq_convocacao_raiz_por_recorte`.
            models.UniqueConstraint(
                fields=["inscricao"],
                condition=Q(requerimento_anterior__isnull=True),
                name="uq_requerimento_raiz_por_inscricao",
            ),
            models.UniqueConstraint(
                fields=["requerimento_anterior"],
                condition=Q(requerimento_anterior__isnull=False),
                name="uq_requerimento_sucessor_unico",
            ),
            # Sucessor sem convocação autorizadora seria edição com outro nome (`FR-408`).
            models.CheckConstraint(
                condition=Q(requerimento_anterior__isnull=True)
                | Q(convocacao_autorizadora__isnull=False),
                name="ck_requerimento_sucessor_autorizado",
            ),
            # O que "enviado" significa, dito no banco — o molde de
            # `ck_inscricao_submetida_completa`. Sem instante, versão, resumo e aceite, o estado não
            # é alcançável (`FR-394`), e a garantia não depende de a aplicação lembrar.
            models.CheckConstraint(
                condition=Q(status=nomes.RASCUNHO)
                | Q(
                    status=nomes.ENVIADO,
                    enviado_em__isnull=False,
                    versao_aceita__isnull=False,
                    declaracao_aceita_em__isnull=False,
                    data_de_nascimento__isnull=False,
                    rg_expedido_em__isnull=False,
                )
                & ~Q(declaracao_hash=""),
                name="ck_requerimento_enviado_completo",
            ),
            models.CheckConstraint(
                condition=Q(status__in=list(nomes.ESTADOS)), name="ck_requerimento_status"
            ),
        ]
        indexes = [models.Index(fields=["inscricao", "status"])]

    def __str__(self):
        return f"Requerimento {self.id} — {self.inscricao_id}"

    def save(self, *args, **kwargs):
        """Enviado, não muda mais (`FR-396`).

        **Primeira camada, nunca a única.** A guarda da `Inscricao` declara, no próprio comentário,
        não ser garantia de banco — e foi esse o achado que trouxe o gatilho condicional da
        migration `0002`. Esta guarda recusa cedo, com mensagem legível; o gatilho recusa mesmo
        quem não passa por aqui.
        """
        self._recusar_se_enviado("alterado")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self._recusar_se_enviado("excluído")
        return super().delete(*args, **kwargs)

    def _recusar_se_enviado(self, verbo):
        if self._state.adding:
            return
        anterior = (
            RequerimentoDeMatricula.objects.filter(pk=self.pk)
            .values_list("status", flat=True)
            .first()
        )
        if anterior == nomes.ENVIADO:
            raise TypeError(f"Requerimento de Matrícula enviado não é {verbo}.")


class ReferenciaDeCep(models.Model):
    """O CEP e o que ele resolve — tabela de referência, e não dado de pessoa.

    **Não é dado pessoal**: nenhuma linha aqui se liga a candidato algum. É base pública carregada
    por comando, substituível por inteiro, e **ausente sem consequência** — a `FR-390` faz o sistema
    funcionar com a tabela vazia, e é isso que impede um serviço de referência de virar porta de
    entrada do processo.

    **Sem latitude e longitude** (`D-008`). A base de origem as oferece e adverte, ela própria, que
    a confiabilidade delas é variável — são montadas em três camadas, com raspagem como último
    recurso. Elas são recalculáveis a qualquer momento a partir do CEP guardado, e não têm
    consumidor nesta feature: guardar estrutura antes de existir a regra que a consome é o que
    este repositório já recusou ao modelar os campos descritivos do Perfil.
    """

    cep = models.CharField(max_length=8, primary_key=True)
    # `""` para CEP de localidade, que não nomeia logradouro.
    logradouro = models.CharField(max_length=255, blank=True, default="")
    bairro = models.CharField(max_length=120, blank=True, default="")
    municipio = models.CharField(max_length=120)
    uf = models.CharField(max_length=2)
    # O que a `FR-388` consome. Vem do IBGE por meio da base de origem — e é o campo que justifica
    # carregar a base em vez de consultar serviço de terceiro a cada preenchimento.
    codigo_ibge = models.CharField(max_length=7, blank=True, default="")

    class Meta:
        verbose_name = "referência de CEP"
        verbose_name_plural = "referências de CEP"

    def __str__(self):
        return f"{self.cep} — {self.municipio}/{self.uf}"
