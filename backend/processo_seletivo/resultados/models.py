"""O Resultado da Etapa: a consequência administrativa de uma Avaliação concluída.

Nasce e não muda mais. É a fronteira em que a `012` parou de propósito — ela executa avaliações e
não diz o que fazer com elas — e é o agregado sobre o qual a classificação, a publicação e o
recurso serão construídos depois.

**O que ele não guarda.** Nem nota mínima, nem pontuação máxima, nem caráter da Etapa, nem a
`VersaoConsolidada`. A norma histórica é reproduzida pela versão da Avaliação fonte, alcançada por
`avaliacao__versao` na mesma consulta. Materializar a versão aqui não economizaria junção nenhuma e
abriria uma quinta forma de o Resultado se contradizer (013, T-011).

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

from processo_seletivo.avaliacoes.models import Avaliacao
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.processos.models import Edital


class ResultadoEtapa(models.Model):
    class Consequencia(models.TextChoices):
        HABILITADA = "HABILITADA"
        ELIMINADA = "ELIMINADA"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inscricao = models.ForeignKey(Inscricao, on_delete=models.PROTECT, related_name="resultados")
    edital = models.ForeignKey(Edital, on_delete=models.PROTECT, related_name="resultados")
    # Identidade da Etapa no **conteúdo publicado**, e não chave estrangeira para a linha de
    # elaboração: existe Etapa real no Edital vigente sem linha correspondente, porque a
    # Retificação sabe acrescentar item a coleção e não escreve de volta em `editais`. É a mesma
    # decisão que a 011 e a 012 tomaram, pelo mesmo motivo.
    etapa_id = models.UUIDField()
    # `OneToOne` porque uma Avaliação fundamenta no máximo um Resultado — a recíproca da unicidade
    # do par. `PROTECT` porque apagar a fonte deixaria o Resultado sem origem identificável.
    # `resultado_da_etapa`, e não `resultado`: o nome do agregado é `ResultadoEtapa`, e a 012
    # guarda um teste que recusa qualquer campo chamado `resultado` na Avaliação. Aquele guard
    # existe para impedir que a **012** volte a calcular consequência, e uma relação reversa
    # apontando para outro app não é isso — o nome preciso o satisfaz sem enfraquecê-lo.
    avaliacao = models.OneToOneField(
        Avaliacao, on_delete=models.PROTECT, related_name="resultado_da_etapa"
    )
    pontuacao = models.DecimalField(max_digits=7, decimal_places=4)
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
