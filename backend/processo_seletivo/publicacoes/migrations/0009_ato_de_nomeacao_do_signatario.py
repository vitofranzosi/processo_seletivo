"""O ato de nomeação de quem assina, registrado na Publicação (054, FR-991).

`ADD COLUMN` com padrão constante é só metadado no PostgreSQL: nenhuma linha é reescrita, e o
gatilho append-only de `publicacoes_publicacao`, que recusa `UPDATE`, não dispara. As Publicações
anteriores ficam com o campo vazio, que é verdade — elas não registraram o ato de nomeação.
"""

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("publicacoes", "0008_remover_ancoras")]

    operations = [
        migrations.AddField(
            model_name="publicacao",
            name="signatory_appointment",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
    ]
