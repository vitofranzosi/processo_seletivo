"""Os rótulos da forma de convocação na redação 2 (069, R-004, R-015).

"Por publicação", sem "no endereço eletrônico do certame": o lugar da publicação é texto de quem
elabora. Só as `choices` mudam — o banco não recebe SQL, e os valores gravados (`PUBLICATION`,
`INDIVIDUAL_MESSAGE`) continuam os mesmos.
"""

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("editais", "0022_documento_modalidade_codigo"),
    ]

    operations = [
        migrations.AlterField(
            model_name="perfilvaga",
            name="forma_de_convocacao",
            field=models.CharField(
                blank=True,
                choices=[
                    ("PUBLICATION", "Por publicação"),
                    ("INDIVIDUAL_MESSAGE", "Por mensagem individual à pessoa convocada"),
                ],
                default="",
                max_length=32,
            ),
        ),
    ]
