from django.db import migrations, models


class Migration(migrations.Migration):
    """A visibilidade do Evento no PDF (144, FR-5100).

    Coluna com padrão verdadeiro: todo Evento já gravado continua saindo na tabela do Cronograma,
    que é o que todo Edital anterior a ela imprimiu. Nada se apaga; a tabela não é append-only.
    """

    dependencies = [
        ("editais", "0025_condicao_do_documento_exigido"),
    ]

    operations = [
        migrations.AddField(
            model_name="eventocronograma",
            name="shown_in_pdf",
            field=models.BooleanField(default=True),
        ),
    ]
