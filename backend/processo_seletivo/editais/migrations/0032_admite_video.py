
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('editais', '0031_regra_de_deliberacao'),
    ]

    operations = [
        migrations.AddField(
            model_name='etapaavaliacao',
            name='admite_video',
            field=models.BooleanField(default=False),
        ),
    ]
