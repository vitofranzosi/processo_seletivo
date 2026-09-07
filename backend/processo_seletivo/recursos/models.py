"""A peça recursal, o juízo que a admite e a decisão que a julga.

Os três nascem e não mudam mais, nas três camadas: `save`/`delete` recusam, a trigger recusa mesmo
quem tem privilégio, e o papel de runtime não tem `UPDATE` nem `DELETE` sobre eles.

**Nenhum dos três tem coluna de situação**, e é decisão (D-010). O que aconteceu com uma peça é a
existência dos atos que a alcançaram: sem juízo, aguarda admissibilidade; com juízo negativo, está
inadmitida; admitida e sem decisão, aguarda julgamento. Uma coluna seria estado a manter coerente
onde a existência de linha já responde — o mesmo idioma de `PENDENTE`/`CONSOLIDADO` na `013` e da
vigência na `015` e na `017`.

**O objeto atacado são duas chaves anuláveis, e não uma abstração de "recorrível".** Generalizar
sobre dois casos concretos, conhecidos e finitos produz indireção sem consumidor — é a mesma recusa
que a `017` fez com `Publicavel`. Duas colunas e um `CHECK` dizem a mesma coisa, e o banco as
verifica (018, T-003).
"""

import uuid

from django.db import models
from django.db.models import Q

from processo_seletivo.avaliacoes.domain.formas import Forma, Sentido
from processo_seletivo.divulgacao.models import PublicacaoResultado
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from processo_seletivo.resultados.models import ResultadoEtapa


class Recurso(models.Model):
    """A contestação interposta pelo titular contra um ato vigente que lhe diz respeito.

    **A janela é gravada, e não recalculada na leitura.** Recalcular responderia com a norma de hoje
    sobre um ato de ontem; a peça precisa registrar se estava dentro do prazo computável **quando
    ele existia**. É proveniência, pela mesma razão que `ResultadoEtapa.versao` é campo e não
    caminho até a fonte (FR-024).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Legível porque é ditado ao telefone, e opaco porque identificador publicado não é credencial.
    # O alfabeto é o mesmo da Inscrição, e é importado de lá — duplicá-lo criaria dois alfabetos que
    # podem divergir, e o segundo divergiria em silêncio (T-012).
    protocolo = models.CharField(max_length=32, unique=True)
    # A Inscrição **é** a titularidade, e é ela que o contrato do portal verifica. Ela determina
    # Edital e Processo; não há terceira coluna a guardar.
    inscricao = models.ForeignKey(Inscricao, on_delete=models.PROTECT, related_name="recursos")
    # Identificador estável, e não vínculo: a autoria é histórica e sobrevive à saída da pessoa.
    interposto_por = models.CharField(max_length=255)
    interposto_em = models.DateTimeField()
    fundamentacao = models.TextField()
    # Os dois objetos atacáveis da V1, e exatamente um por peça (D-001). `PROTECT` nos dois porque
    # o objeto atacado não pode desaparecer sob o recurso que o nomeia.
    publicacao_atacada = models.ForeignKey(
        PublicacaoResultado,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="recursos",
    )
    resultado_atacado = models.ForeignKey(
        ResultadoEtapa,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="recursos",
    )
    versao = models.ForeignKey(VersaoConsolidada, on_delete=models.PROTECT, related_name="recursos")
    # Os dois juntos são "havia prazo, e era este". Nulos quando o Edital não declarou janela: o
    # sistema não inventa prazo, e a ausência é a afirmação certa (FR-028).
    janela_abriu_em = models.DateTimeField(null=True, blank=True)
    janela_fecha_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            # Exatamente um objeto atacado. `XOR` escrito como desigualdade entre as duas
            # nulidades: a forma que o Django gera é a que o PostgreSQL entende sem extensão.
            models.CheckConstraint(
                condition=(
                    Q(publicacao_atacada__isnull=True, resultado_atacado__isnull=False)
                    | Q(publicacao_atacada__isnull=False, resultado_atacado__isnull=True)
                ),
                name="ck_recurso_objeto_unico",
            ),
            models.CheckConstraint(condition=~Q(fundamentacao=""), name="ck_recurso_fundamentacao"),
            # Ou há janela computável, ou não há. Metade dela seria um prazo que não fecha.
            models.CheckConstraint(
                condition=(
                    Q(janela_abriu_em__isnull=True, janela_fecha_em__isnull=True)
                    | Q(janela_abriu_em__isnull=False, janela_fecha_em__isnull=False)
                ),
                name="ck_recurso_janela_completa",
            ),
            # A FR-011 no banco: um recurso por titular e objeto atacado, pendente ou já decidido.
            # Parciais porque só uma das duas colunas está preenchida por vez.
            models.UniqueConstraint(
                fields=["inscricao", "publicacao_atacada"],
                condition=Q(publicacao_atacada__isnull=False),
                name="uq_recurso_por_publicacao",
            ),
            models.UniqueConstraint(
                fields=["inscricao", "resultado_atacado"],
                condition=Q(resultado_atacado__isnull=False),
                name="uq_recurso_por_resultado",
            ),
        ]
        indexes = [models.Index(fields=["inscricao"])]

    def __str__(self):
        return self.protocolo

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise TypeError("Recurso é append-only: a peça interposta não muda.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise TypeError("Recurso é append-only: a peça interposta não é excluída.")


class JuizoDeAdmissibilidade(models.Model):
    """Receber a peça não é admiti-la, e este é o ato que as separa (FR-031).

    **O motivo é obrigatório nas duas direções.** Exigi-lo só na inadmissão faria a admissão parecer
    automática, e ela não é: admitir também é ato de autoridade sobre um direito.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recurso = models.ForeignKey(Recurso, on_delete=models.PROTECT, related_name="juizos")
    admitido = models.BooleanField()
    motivo = models.TextField()
    decidido_por = models.CharField(max_length=255)
    decidido_em = models.DateTimeField()

    class Meta:
        constraints = [
            # Um por recurso. A segunda tentativa concorrente perde **no banco**, e recebe recusa
            # por estado obsoleto — não por leitura prévia, que é conforto de mensagem e não
            # garantia.
            models.UniqueConstraint(fields=["recurso"], name="uq_juizo_por_recurso"),
            models.CheckConstraint(condition=~Q(motivo=""), name="ck_juizo_motivo"),
        ]

    def __str__(self):
        return f"{self.recurso_id} — {'admitido' if self.admitido else 'inadmitido'}"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise TypeError("Juízo de admissibilidade é append-only.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise TypeError("Juízo de admissibilidade é append-only.")


class DecisaoRecurso(models.Model):
    """O julgamento do mérito, e a fonte jurídica que o Resultado sucessor cita.

    **As espécies são quatro, e a quarta não é invenção** (D-009). Ela vem do mapa dos seis lugares
    em que o erro pode estar: três têm remédio fora do `ResultadoEtapa`, e sem ela um recurso
    procedente contra a norma ou contra a forma da divulgação obrigaria o julgador a indeferir um
    recurso procedente, ou a fabricar sucessor para um erro que não está lá.

    **O que a espécie discrimina é o efeito**, e é o efeito que o esquema e a aferição de
    definitividade precisam distinguir. *Qual* providência a decisão determina é fundamentação
    escrita: o cumprimento é verificado pela citação do ato que a executa, e não por espécie
    (T-015).
    """

    class Especie(models.TextChoices):
        INDEFERIDO = "INDEFERIDO"
        CORRECAO_FIXADA = "CORRECAO_FIXADA"
        REAVALIACAO_DETERMINADA = "REAVALIACAO_DETERMINADA"
        PROVIDENCIA_A_JUSANTE = "PROVIDENCIA_A_JUSANTE"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recurso = models.ForeignKey(Recurso, on_delete=models.PROTECT, related_name="decisoes")
    especie = models.CharField(max_length=30, choices=Especie.choices)
    motivacao = models.TextField()
    versao = models.ForeignKey(
        VersaoConsolidada, on_delete=models.PROTECT, related_name="decisoes_de_recurso"
    )
    decidido_por = models.CharField(max_length=255)
    decidido_em = models.DateTimeField()
    # O vigente do par quando se decidiu. **FK, e não derivado**: derivá-lo exigiria perguntar "qual
    # era o vigente naquele instante", que é consulta temporal sobre uma cadeia. Uma FK responde em
    # uma junção e é honesta — a decisão de fato se referiu àquele Resultado. É contra ele que a
    # *non reformatio* compara, inclusive no caminho da reavaliação (T-011, FR-073).
    resultado_protegido = models.ForeignKey(
        ResultadoEtapa,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="decisoes_que_o_protegem",
    )
    # Identidade da Etapa no conteúdo publicado, como em `ResultadoEtapa.etapa_id` e pela mesma
    # razão: existe Etapa real no Edital vigente sem linha correspondente em elaboração.
    etapa_id = models.UUIDField(null=True, blank=True)
    consequencia = models.CharField(
        max_length=20, choices=ResultadoEtapa.Consequencia.choices, blank=True, default=""
    )
    # A conclusão fixada, quando a decisão a fixa. Vazias no desfecho **sem grandeza** — o recurso
    # contra Ocorrência que a decisão acolhe sem que ninguém tenha avaliado nada (FR-059).
    forma = models.CharField(max_length=20, choices=Forma.choices, blank=True, default="")
    pontuacao = models.DecimalField(max_digits=7, decimal_places=4, null=True, blank=True)
    sentido = models.CharField(max_length=20, choices=Sentido.choices, blank=True, default="")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["recurso"], name="uq_decisao_por_recurso"),
            models.CheckConstraint(condition=~Q(motivacao=""), name="ck_decisao_motivacao"),
            # `TextChoices` valida no formulário e **não** cria constraint: num registro append-only
            # a espécie inválida entraria uma vez e ficaria, porque nada a corrige depois. É a mesma
            # razão de `ck_resultado_consequencia` na 013.
            models.CheckConstraint(
                condition=Q(
                    especie__in=(
                        "INDEFERIDO",
                        "CORRECAO_FIXADA",
                        "REAVALIACAO_DETERMINADA",
                        "PROVIDENCIA_A_JUSANTE",
                    )
                ),
                name="ck_decisao_especie",
            ),
            # A correção fixada declara o par que alcança, o que protege e o que decide.
            models.CheckConstraint(
                condition=(
                    ~Q(especie="CORRECAO_FIXADA")
                    | Q(
                        etapa_id__isnull=False,
                        resultado_protegido__isnull=False,
                    )
                    & ~Q(consequencia="")
                ),
                name="ck_decisao_correcao_completa",
            ),
            # A reavaliação alcança um par e protege um Resultado, e **não** declara consequência:
            # o resultado corrigido ainda não existe para ser declarado (D-009).
            models.CheckConstraint(
                condition=(
                    ~Q(especie="REAVALIACAO_DETERMINADA")
                    | Q(
                        etapa_id__isnull=False,
                        resultado_protegido__isnull=False,
                        consequencia="",
                    )
                ),
                name="ck_decisao_reavaliacao",
            ),
            # As duas espécies sem efeito sobre Resultado não declaram consequência nem protegem
            # Resultado nenhum — declarar seria afirmar um efeito que a espécie não produz.
            models.CheckConstraint(
                condition=(
                    ~Q(especie__in=("INDEFERIDO", "PROVIDENCIA_A_JUSANTE"))
                    | Q(resultado_protegido__isnull=True, consequencia="")
                ),
                name="ck_decisao_sem_efeito",
            ),
            # **A decisão é append-only, e por isso a lista fechada precisa ser constraint.**
            # `choices` valida no formulário e no `full_clean`; `bulk_create`, SQL direto e código
            # futuro gravariam qualquer texto — e num registro que nada corrige depois, o valor
            # inventado entra uma vez e fica. É a mesma razão de `ck_resultado_consequencia` na
            # 013, aplicada aos três campos que carregam o que a decisão afirma.
            models.CheckConstraint(
                condition=Q(consequencia__in=("", "HABILITADA", "ELIMINADA")),
                name="ck_decisao_consequencia",
            ),
            # A conclusão fixada é internamente coerente, na mesma forma que
            # `ck_resultado_completo_por_forma` exige do Resultado — e pela mesma razão: o
            # Resultado sucessor **copia** o que a decisão declarou, de modo que uma decisão
            # incoerente produziria um Resultado incoerente ou um sucessor impossível.
            models.CheckConstraint(
                condition=(
                    Q(forma="PONTUADA", pontuacao__isnull=False, sentido="")
                    | Q(
                        forma="DECISORIA",
                        pontuacao__isnull=True,
                        sentido__in=("FAVORAVEL", "DESFAVORAVEL"),
                    )
                    | Q(forma="", pontuacao__isnull=True, sentido="")
                ),
                name="ck_decisao_conclusao_por_forma",
            ),
            # **Só a correção fixada carrega grandeza.** Indeferir, ordenar reavaliação e determinar
            # providência não declaram conclusão nenhuma: uma pontuação pendurada numa delas seria
            # afirmação sem efeito — e, pior, um convite a que alguém a consumisse depois como se
            # fosse a decisão.
            models.CheckConstraint(
                condition=(
                    Q(especie="CORRECAO_FIXADA") | Q(forma="", pontuacao__isnull=True, sentido="")
                ),
                name="ck_decisao_sem_grandeza_residual",
            ),
        ]
        indexes = [models.Index(fields=["especie"])]

    def __str__(self):
        return f"{self.recurso_id} — {self.especie}"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise TypeError("Decisão de recurso é append-only: julgar acontece uma vez.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise TypeError("Decisão de recurso é append-only.")
