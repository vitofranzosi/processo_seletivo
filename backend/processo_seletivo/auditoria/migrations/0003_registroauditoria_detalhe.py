"""A trilha passa a guardar o alcance de um gesto em lote (051, FR-921, FR-935).

"Aplicar a todos" grava N valores num gesto, e a Revisão precisa dizer, depois, de onde veio cada
um — e se ele ainda é o que o gesto gravou. A trilha já é o lugar da autoria, e já é append-only nas
duas camadas: uma tabela própria exigiria gatilho e privilégio novos para guardar o que ela guarda.

Coluna anulável e aditiva: nenhuma linha existente muda, e o gatilho `auditoria_append_only`
continua valendo para ela, porque é por linha e não por coluna.
"""

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("auditoria", "0002_desfecho_do_lote"),
    ]

    operations = [
        migrations.AddField(
            model_name="registroauditoria",
            name="detalhe",
            field=models.JSONField(blank=True, null=True),
        ),
    ]
