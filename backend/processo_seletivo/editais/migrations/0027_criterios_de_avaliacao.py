import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    """O barema da Etapa (146, FR-5200, FR-5201).

    Uma tabela nova, filha da Etapa. Só acrescenta: nenhuma linha existente muda, e a Etapa sem
    critério é exatamente a de antes. **Não é append-only** — é elaboração, como a Etapa —, e por
    isso o `M` do provisionamento continua 53.
    """

    dependencies = [
        ("editais", "0026_visibilidade_do_evento_no_pdf"),
    ]

    operations = [
        migrations.CreateModel(
            name="CriterioAvaliacao",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("ordem", models.PositiveIntegerField()),
                ("nome", models.CharField(max_length=200)),
                ("descricao", models.TextField(blank=True, default="")),
                ("maxima", models.DecimalField(decimal_places=4, max_digits=7)),
                (
                    "pontos_por_unidade",
                    models.DecimalField(blank=True, decimal_places=4, max_digits=7, null=True),
                ),
                ("unidade", models.CharField(blank=True, default="", max_length=60)),
                ("documento", models.UUIDField(blank=True, null=True)),
                (
                    "etapa",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="criterios",
                        to="editais.etapaavaliacao",
                    ),
                ),
            ],
            options={
                "ordering": ["ordem", "id"],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("etapa", "ordem"), name="uq_criterio_avaliacao_ordem"
                    ),
                    models.UniqueConstraint(
                        fields=("etapa", "nome"), name="uq_criterio_avaliacao_nome"
                    ),
                    models.CheckConstraint(
                        condition=models.Q(("maxima__gt", 0)),
                        name="ck_criterio_avaliacao_maxima_positiva",
                    ),
                    models.CheckConstraint(
                        condition=models.Q(
                            ("pontos_por_unidade__isnull", True),
                            models.Q(
                                ("pontos_por_unidade__gt", 0),
                                ("pontos_por_unidade__lte", models.F("maxima")),
                            ),
                            _connector="OR",
                        ),
                        name="ck_criterio_avaliacao_pontos_na_faixa",
                    ),
                    models.CheckConstraint(
                        condition=models.Q(
                            models.Q(("pontos_por_unidade__isnull", True), ("unidade", "")),
                            models.Q(
                                ("pontos_por_unidade__isnull", False),
                                models.Q(("unidade", ""), _negated=True),
                            ),
                            _connector="OR",
                        ),
                        name="ck_criterio_avaliacao_unidade_com_pontos",
                    ),
                ],
            },
        ),
    ]
