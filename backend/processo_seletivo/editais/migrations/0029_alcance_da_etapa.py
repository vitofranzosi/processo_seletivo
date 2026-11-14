from django.db import migrations, models


class Migration(migrations.Migration):
    """O alcance da Etapa por Modalidade (163, FR-6960, T-001).

    `alcance` é a lista dos códigos de Modalidade que a Etapa alcança, e `NULL` é "todas as
    inscrições" — o que toda Etapa significava antes desta coluna, e por isso ela nasce sem
    preenchimento. A constraint recusa a lista vazia, que seria contradição e não alcance.

    Não toca tabela append-only: `EtapaAvaliacao` é elaboração, e o `M` do provisionamento continua
    o mesmo.
    """

    dependencies = [
        ("editais", "0028_cadastro_limitado_sem_numero"),
        ("processos", "0005_escopo_imutavel"),
    ]

    operations = [
        migrations.AddField(
            model_name="etapaavaliacao",
            name="alcance",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddConstraint(
            model_name="etapaavaliacao",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("alcance__isnull", True),
                    models.Q(("alcance", []), _negated=True),
                    _connector="OR",
                ),
                name="ck_etapa_alcance_nao_vazio",
            ),
        ),
    ]
