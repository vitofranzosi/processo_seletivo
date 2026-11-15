"""O que cada identidade da gestão já viu das Novidades do GPS (168, FR-7419).

**Uma linha por identidade, e nenhum dado do certame.** A nota mora no arquivo versionado
(`novidades.toml`), e não aqui: a tabela guarda só os identificadores das notas vistas e o instante
da última visita. Não é ato nem dado normativo — muda a cada visita, e por isso não é append-only.

O identificador é o `subject` do ator, o mesmo que a trilha usa: o identificador escolhido no
seletor de demonstração, ou `pessoa-<uuid>` na entrada institucional. Duas pessoas que declaram a
mesma identidade no seletor compartilham a linha — é a natureza da demonstração.
"""

from django.db import models


class LeituraDasNovidades(models.Model):
    subject = models.CharField(max_length=150, unique=True)
    # Os identificadores, e não a data da última visita, decidem o que é novo (`D-002`): uma nota
    # integrada antes da última visita e implantada depois dela continua não vista.
    vistas = models.JSONField(default=list)
    ultima_visita = models.DateTimeField()

    class Meta:
        verbose_name = "leitura das novidades"
        verbose_name_plural = "leituras das novidades"

    def __str__(self):
        return f"{self.subject}: {len(self.vistas)} vistas"
