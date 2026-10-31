"""O canal de atendimento ao candidato de cada unidade (109, FR-3211).

**Só acrescenta a coluna, vazia.** Nenhuma unidade ganha canal por migration: o canal é declarado
no `unidades.json` e aplicado pelo `sincronizar_unidades`, com trilha, como os demais campos. Vazio
quer dizer "não declarado", e então vale o `PORTAL_ATENDIMENTO` — que é o que o Cefor tinha antes
desta migration, e continua tendo depois dela.
"""

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("unidades", "0002_nada_se_exclui")]

    operations = [
        migrations.AddField(
            model_name="unidade",
            name="atendimento",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
    ]
