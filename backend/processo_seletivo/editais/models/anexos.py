"""O documento em forma própria que o Edital publica junto com o seu texto.

O Anexo é **conteúdo normativo binário**: o formulário que o candidato baixa, preenche, assina,
digitaliza e devolve. O sistema nunca lê o que há dentro dele — é essa recusa que separa isto de
um construtor de formulários, e é ela que a `009` já escreveu para o outro lado do ciclo.

Duas tabelas, e a razão de serem duas é o ciclo de vida, não a arrumação. A identidade normativa
sobrevive à Retificação e é o que o conteúdo publicado endereça; os bytes são substituíveis
enquanto ninguém os publicou e imutáveis depois disso. Fundi-las obrigaria a linha a ser as duas
coisas ao mesmo tempo.

**Não há tabela de versões por Anexo**, pela mesma razão que não há por Seção: as versões são
**do Edital**. Qual artefato cada versão publicou está no conteúdo canônico daquela versão, que já
é histórico e imutável (020, D-001).
"""

import uuid

from django.db import models

from processo_seletivo.processos.models import Edital


class ArtefatoAnexo(models.Model):
    """Os bytes. Substituíveis no rascunho, imutáveis depois que uma versão os publicou.

    **`congelado_em` responde duas perguntas com uma coluna**, e é de propósito: nulo significa
    rascunho — substituível, apagável e sem endereço público; não nulo significa publicado —
    imutável por trigger e público por natureza, porque é norma. A alternativa seria uma coluna de
    imutabilidade e outra de visibilidade, que poderiam divergir e diriam a mesma coisa.

    A forma é a que a `0007` das publicações já usou para a Retificação: o que muda enquanto o ato
    corre não pode ser congelado por completo, e o que já produziu efeito não pode mudar. A trigger
    é condicional ao estado final nos dois casos.

    Os bytes moram em coluna binária, como em `DocumentoPublicado`, e não em disco. Não é
    preferência: a publicação é atômica, e o congelamento precisa entrar na mesma transação em que
    a `Publicacao` nasce. Em disco, um `rollback` deixaria conteúdo publicado apontando para bytes
    que não existem — o próprio defeito que esta feature veio corrigir (020, R-001).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bytes = models.BinaryField()
    content_type = models.CharField(max_length=100, default="application/pdf")
    tamanho = models.PositiveBigIntegerField()
    # Integridade do artefato, e **não** chave de unicidade — a mesma nota que
    # `DocumentoPublicado.document_hash` carrega, e pela mesma razão: dois artefatos de conteúdo
    # idêntico são legítimos, porque uma Retificação pode reverter outra e reproduzir exatamente os
    # bytes já publicados. Quem endereça é o `id` (FR-011).
    document_hash = models.CharField(max_length=64, db_index=True)
    # O nome que quem elabora enviou, preservado para exibição e nada além: ele não decide caminho,
    # não decide identidade e não é confiável (FR-014).
    nome_original = models.CharField(max_length=255)
    enviado_por = models.CharField(max_length=255)
    enviado_em = models.DateTimeField()
    congelado_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["enviado_em", "id"]

    def __str__(self):
        return f"{self.nome_original} — {self.document_hash[:16]}…"

    @property
    def publicado(self) -> bool:
        return self.congelado_em is not None


class AnexoEdital(models.Model):
    """A identidade normativa do Anexo, e o artefato que ela referencia agora.

    O rótulo é **um texto só** — "ANEXO VI — AUTODECLARAÇÃO ÉTNICO-RACIAL" —, escrito inteiro pelo
    autor. Dois campos, designação e título, convidariam a preencher o numeral pela posição, e é
    justamente isso que o sistema não pode fazer: os bytes do PDF podem trazer "ANEXO VI" impresso,
    e ninguém aqui lê nem reescreve PDF. Um rótulo derivado divergiria do artefato em silêncio
    (FR-005, FR-006).

    A ordem é campo próprio, e alterá-la não altera rótulo nenhum. Remover deixa **lacuna** na
    sequência, porque renumerar de verdade é substituir o artefato — ato do autor (FR-007, FR-008).

    **Não existe Anexo sem artefato.** Subir o arquivo é o que o cria, e por isso não há estado
    intermediário a validar nem publicação que possa prometer um anexo vazio (FR-015a).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    edital = models.ForeignKey(Edital, on_delete=models.PROTECT, related_name="anexos")
    rotulo = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)
    artefato = models.ForeignKey(ArtefatoAnexo, on_delete=models.PROTECT, related_name="anexos")

    class Meta:
        ordering = ["order", "id"]
        constraints = [
            models.UniqueConstraint(fields=["edital", "order"], name="uq_anexo_edital_order"),
        ]

    def __str__(self):
        return self.rotulo or f"Anexo sem rótulo — {self.id}"
