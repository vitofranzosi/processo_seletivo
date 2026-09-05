"""O Resultado da Etapa: a consequência administrativa de uma Avaliação concluída.

Nasce e não muda mais. É a fronteira em que a `012` parou de propósito — ela executa avaliações e
não diz o que fazer com elas — e é o agregado sobre o qual a classificação, a publicação e o
recurso serão construídos depois.

**Ele nasce de duas origens, e essa é a invariante I-1 do briefing dita em coluna.** `AVALIACAO`
é o que existia: a Etapa foi avaliada, e o Resultado copia a conclusão. `OCORRENCIA` é o desfecho
de quem **não foi avaliado** — faltou à entrevista, descumpriu pré-requisito, não compareceu ao
procedimento de verificação —, constatado pela presidência. Não é conclusão decisória: avaliar não
é decidir, e ninguém julgou quem não compareceu (D-1).

**O que ele não guarda.** Nem nota mínima, nem pontuação máxima, nem caráter da Etapa. A versão
normativa, sim: sem Avaliação não há `avaliacao__versao` a percorrer, e o Resultado por Ocorrência
ficaria sem a norma que o fundamentou — contra I-2, que exige o resultado reproduzível a partir das
regras que o produziram. Guardá-la só no ramo sem Avaliação criaria duas formas de responder à
mesma pergunta, então ela é campo do Resultado, exigido sempre, e a trigger confere que ela
coincide com a da Avaliação quando há Avaliação (D-1).

**O que ele guarda de redundante, e por quê.** `inscricao` e `etapa_id` sustentam a unicidade que é
a invariante central da feature, e unicidade precisa ser constraint. `edital` acompanha `etapa_id`
pelo padrão que `AlocacaoEtapa` já usa. `pontuacao` descreve o **Resultado**, e não a fonte: a V1 a
copia porque consolida leitura única, e a regra de combinação que vier depois não necessariamente
copiará. Nenhum dos quatro é confiado a promessa de código — a trigger `resultado_etapa_coerente`
os confere contra a Avaliação fonte no `INSERT`.
"""

import uuid

from django.db import models
from django.db.models import Q

from processo_seletivo.avaliacoes.domain.formas import Forma, Sentido
from processo_seletivo.avaliacoes.models import Avaliacao
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada


class ResultadoEtapa(models.Model):
    class Consequencia(models.TextChoices):
        HABILITADA = "HABILITADA"
        ELIMINADA = "ELIMINADA"

    class Origem(models.TextChoices):
        """De onde veio a evidência do desfecho — e **não** o que ele decidiu.

        Discriminador, e não entidade própria de Ocorrência. Uma entidade seria mais expressiva e
        criaria estrutura antes da regra que a consome: há um consumidor só, e ele cabe aqui.
        Quando houver ocorrência que precise de ciclo de vida próprio — contestada, revista,
        anulada —, a entidade nasce com o caso que a justifica (D-1).
        """

        AVALIACAO = "AVALIACAO"
        OCORRENCIA = "OCORRENCIA"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inscricao = models.ForeignKey(Inscricao, on_delete=models.PROTECT, related_name="resultados")
    edital = models.ForeignKey(Edital, on_delete=models.PROTECT, related_name="resultados")
    # Identidade da Etapa no **conteúdo publicado**, e não chave estrangeira para a linha de
    # elaboração: existe Etapa real no Edital vigente sem linha correspondente, porque a
    # Retificação sabe acrescentar item a coleção e não escreve de volta em `editais`. É a mesma
    # decisão que a 011 e a 012 tomaram, pelo mesmo motivo.
    etapa_id = models.UUIDField()
    origem = models.CharField(max_length=20, choices=Origem.choices)
    # `OneToOne` porque uma Avaliação fundamenta no máximo um Resultado — a recíproca da unicidade
    # do par. `PROTECT` porque apagar a fonte deixaria o Resultado sem origem identificável.
    # `resultado_da_etapa`, e não `resultado`: o nome do agregado é `ResultadoEtapa`, e a 012
    # guarda um teste que recusa qualquer campo chamado `resultado` na Avaliação. Aquele guard
    # existe para impedir que a **012** volte a calcular consequência, e uma relação reversa
    # apontando para outro app não é isso — o nome preciso o satisfaz sem enfraquecê-lo.
    #
    # **Anulável desde D-1**, e a nulabilidade é amarrada a `origem` por constraint e por trigger:
    # nula quando a origem é Ocorrência, presente quando é Avaliação. `null=True` sozinho abriria
    # o Resultado sem fonte e sem constatação, que não é nenhuma das duas coisas.
    avaliacao = models.OneToOneField(
        Avaliacao,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="resultado_da_etapa",
    )
    # A norma que fundamentou o desfecho — a da Avaliação fonte, quando há uma; a vigente no
    # instante do ato, quando a presidência constata a ocorrência. Campo do Resultado, e não
    # caminho até a fonte, porque no ramo sem Avaliação não há caminho (D-1, I-2).
    versao = models.ForeignKey(
        VersaoConsolidada, on_delete=models.PROTECT, related_name="resultados"
    )
    # A forma sob a qual a fonte foi concluída, copiada com ela. O Resultado guarda a conclusão
    # **conforme a forma**, e não uma nota sempre: a Etapa decisória não produz número nenhum, e
    # inventar um seria afirmar uma grandeza que o Edital não publicou (012, D-008; 013, D-008).
    #
    # **Vazia na Ocorrência**, e a ausência é a afirmação certa: ela não pontua, não registra
    # sentido e não tem forma — não houve conclusão sob forma nenhuma. Carimbar `DECISORIA` diria
    # que alguém avaliou quem não compareceu (D-1).
    forma = models.CharField(max_length=20, choices=Forma.choices, blank=True, default="")
    pontuacao = models.DecimalField(max_digits=7, decimal_places=4, null=True, blank=True)
    sentido = models.CharField(max_length=20, choices=Sentido.choices, blank=True, default="")
    consequencia = models.CharField(max_length=20, choices=Consequencia.choices)
    # A causa da consequência, em texto exibível. Consequência sem causa é rótulo: quem consulta
    # precisa ler "pontuação inferior à nota mínima da Etapa (55,0000 < 60,0000)", e não apenas
    # "eliminada".
    motivo = models.TextField()
    consolidado_em = models.DateTimeField()
    # Identificador estável, e não referência ao vínculo: a autoria é histórica e sobrevive à saída
    # da pessoa da comissão, como a `Avaliacao.concluida_por` da 012.
    consolidado_por = models.CharField(max_length=255)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["inscricao", "etapa_id"], name="uq_resultado_inscricao_etapa"
            ),
            # `TextChoices` valida no formulário e no `full_clean`, e **não** cria constraint:
            # `bulk_create`, SQL direto ou código futuro gravariam qualquer texto. Num registro
            # append-only isso é pior que em qualquer outro — a consequência inválida entraria uma
            # vez e ficaria, porque nada a corrige depois.
            models.CheckConstraint(
                condition=Q(consequencia__in=("HABILITADA", "ELIMINADA")),
                name="ck_resultado_consequencia",
            ),
            models.CheckConstraint(condition=~Q(motivo=""), name="ck_resultado_motivo_presente"),
            # A origem amarrada ao que ela implica. Sem isto, `null=True` em `avaliacao` seria uma
            # permissão solta: uma linha `AVALIACAO` sem fonte, ou uma `OCORRENCIA` com fonte,
            # atravessaria — e a trigger, que confere a fonte, não tem o que conferir num nulo que
            # a coluna passou a admitir. `forma` entra aqui porque ela é o que distingue "não
            # houve conclusão" de "houve, e sob esta forma" (D-1).
            models.CheckConstraint(
                # Literais, como `ck_resultado_consequencia` ao lado: `Origem` é classe aninhada
                # e não está em escopo dentro de `Meta`.
                condition=Q(origem="AVALIACAO", avaliacao__isnull=False) & ~Q(forma="")
                | Q(origem="OCORRENCIA", avaliacao__isnull=True, forma=""),
                name="ck_resultado_origem",
            ),
            # O que a coluna `NOT NULL` garantia sozinha, dito agora por forma. A trigger confere o
            # Resultado contra a fonte; esta confere que ele é internamente coerente, e as duas
            # precisam existir — a trigger sozinha aprovaria uma linha sem forma se a fonte também
            # não a tivesse, e num registro append-only o inválido entra uma vez e fica.
            #
            # **O terceiro ramo é a Ocorrência**, e ele é todo de ausências: sem forma, sem
            # pontuação e sem sentido. Ela não pontua e não registra sentido — o Edital não
            # publicou grandeza nenhuma para quem não compareceu, e a linha não pode afirmar uma
            # (D-1).
            models.CheckConstraint(
                condition=Q(forma=Forma.PONTUADA, pontuacao__isnull=False, sentido="")
                | Q(forma=Forma.DECISORIA, pontuacao__isnull=True, sentido__in=Sentido.values)
                | Q(forma="", pontuacao__isnull=True, sentido=""),
                name="ck_resultado_completo_por_forma",
            ),
            models.CheckConstraint(
                condition=~Q(consolidado_por=""), name="ck_resultado_autor_presente"
            ),
        ]
        indexes = [models.Index(fields=["edital", "etapa_id"])]

    def __str__(self):
        return f"{self.inscricao_id} — {self.consequencia}"

    def save(self, *args, **kwargs):
        """Cria, e nunca atualiza.

        Primeira das três camadas do regime append-only; as outras duas são a trigger e o
        privilégio negado ao papel de runtime. Três porque cada uma cobre um caminho: esta cobre o
        ORM, a trigger cobre quem chega por fora, e o privilégio cobre quem chega com o cliente do
        banco na mão.
        """
        if not self._state.adding:
            raise ValueError("Resultado da Etapa é imutável: consolidar acontece uma vez.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError(
            "Resultado da Etapa não é excluído: ele é a consequência registrada de um ato."
        )
