"""A versão do modelo da mensagem na comunicação emitida (121, D-009, FR-3889, FR-3891).

**Só acrescenta a coluna, com padrão constante.** O PostgreSQL aplica `ADD COLUMN … DEFAULT ''` sem
reescrever linha, e o gatilho append-only de `UPDATE` não dispara: a tabela continua protegida nas
duas camadas, e a segunda passada do provisionamento continua `53 de 53`, porque coluna nova não
muda privilégio de tabela.

**Sem `RunPython` e sem atribuir versão a nada** (FR-3889): as comunicações gravadas antes da `121`
ficam com o vazio, que é verdade — elas não registraram o modelo. Deduzir a versão delas pelo
histórico de implantação seria a afirmação que a R-001 mostrou que ele não sustenta.
"""

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("convocacao", "0005_documentos_da_convocacao"),
    ]

    operations = [
        migrations.AddField(
            model_name="comunicacaoemitida",
            name="modelo_da_mensagem",
            field=models.CharField(blank=True, default="", max_length=100),
        ),
    ]
