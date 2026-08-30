from django.db import models

from processo_seletivo.processos.models import Edital


class SecaoEdital(models.Model):
    """Guarda **apenas** o conteúdo redigido das seções textuais.

    A estrutura do documento — quais seções existem, em que ordem, de que tipo, com que título —
    é declaração em `editais/domain/secoes.py`, e não linha de tabela. O Edital que ainda não teve
    uma seção textual editada simplesmente não tem a linha: o conteúdo é o padrão do catálogo. Uma
    seção gerada nunca tem linha.

    **A chave primária é a mesma identidade do snapshot** — `uuid5` sobre `(edital.id, key)` — para
    que a seção tenha uma identidade só. Gerar aqui um UUID aleatório criaria duas: a que o
    conteúdo publicado carrega e a que a persistência conhece, e a Retificação endereçaria uma
    enquanto a edição escreveria na outra.
    """

    id = models.UUIDField(primary_key=True, editable=False)
    edital = models.ForeignKey(Edital, on_delete=models.CASCADE, related_name="secoes")
    key = models.CharField(max_length=60)
    content = models.TextField()

    class Meta:
        ordering = ["key"]
        constraints = [
            models.UniqueConstraint(fields=["edital", "key"], name="uq_secao_edital_key")
        ]

    def __str__(self):
        return f"{self.key} — {self.edital}"
