from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("editais", "0024_momento_do_documento_exigido"),
    ]

    operations = [
        migrations.AddField(
            model_name="documentoexigido",
            name="condicao",
            field=models.CharField(blank=True, default="", max_length=300),
        ),
    ]
