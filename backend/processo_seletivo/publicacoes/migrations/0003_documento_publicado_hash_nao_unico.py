from django.db import migrations, models


class Migration(migrations.Migration):
    """Remove a unicidade global de DocumentoPublicado.document_hash.

    O hash identifica a integridade do documento (FR-023) e não é chave de
    unicidade: uma Retificação que reverte outra reproduz exatamente o conteúdo
    já publicado, e Editais distintos podem produzir documentos idênticos. A
    unicidade que o domínio exige — um documento por Publicação — permanece
    garantida pela OneToOne com Publicacao.
    """

    dependencies = [
        ("publicacoes", "0002_retificacoes"),
    ]

    operations = [
        migrations.AlterField(
            model_name="documentopublicado",
            name="document_hash",
            field=models.CharField(db_index=True, max_length=64),
        ),
    ]
