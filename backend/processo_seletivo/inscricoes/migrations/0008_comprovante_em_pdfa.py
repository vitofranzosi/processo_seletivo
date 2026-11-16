"""Registra, em cada inscrição, qual escritor compõe o comprovante dela (178, FR-8163, D-005).

**Duas operações, e a ordem é o requisito.** A coluna nasce falsa em toda linha que já existe — as
enviadas antes da `178`, cujo comprovante continua byte a byte o de antes (D-002) —, e só depois o
padrão passa a verdadeiro, para toda linha criada daqui em diante. Uma `AddField` só, com o padrão
verdadeiro, marcaria como PDF/A o comprovante de quem já viu o resumo do arquivo antigo.

**A enviada é imutável por gatilho** (`0007`), e acrescentar a coluna não a toca: `ADD COLUMN` com
padrão constante é alteração de catálogo no PostgreSQL, e nenhum `UPDATE` de linha dispara o
`inscricao_enviada_imutavel`. O rascunho anterior ao corte também nasce falso, e o envio dele grava
verdadeiro (`submissao.py`) — nenhum resumo tinha sido mostrado antes do envio.
"""

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("inscricoes", "0007_imutabilidade_da_enviada")]

    operations = [
        migrations.AddField(
            model_name="inscricao",
            name="comprovante_em_pdfa",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="inscricao",
            name="comprovante_em_pdfa",
            field=models.BooleanField(default=True),
        ),
    ]
