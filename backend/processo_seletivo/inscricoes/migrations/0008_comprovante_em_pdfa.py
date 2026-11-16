"""Registra, em cada inscrição, qual escritor compõe o comprovante dela (178, FR-8163, D-005).

**Duas operações, e a ordem é o requisito.** A coluna nasce falsa em toda linha que já existe — as
enviadas antes da `178`, cujo comprovante continua byte a byte o de antes (D-002) —, e só depois o
padrão passa a verdadeiro, para toda linha criada daqui em diante. Uma `AddField` só, com o padrão
verdadeiro, marcaria como PDF/A o comprovante de quem já viu o resumo do arquivo antigo.

**A enviada é imutável por gatilho** (`0007`), e acrescentar a coluna não a toca: `ADD COLUMN` com
padrão constante é alteração de catálogo no PostgreSQL, e nenhum `UPDATE` de linha dispara o
`inscricao_enviada_imutavel`. O rascunho anterior ao corte também nasce falso, e o envio dele grava
verdadeiro (`submissao.py`) — nenhum resumo tinha sido mostrado antes do envio.

**Desfazer é recusado enquanto houver enviada com o comprovante em PDF/A.** Desfazer apaga a coluna,
e refazer a recria falsa em toda linha: a inscrição enviada depois da `178`, cujo resumo do PDF/A a
página já mostrou, passaria a receber o comprovante antigo, e o resumo anotado deixaria de conferir
sem aviso. Antes do primeiro envio, desfazer não perde nada, e é permitido.
"""

from django.db import migrations, models

# Copiado de `Inscricao.Status.SUBMETIDA`, e **não** importado, como na `0007`.
SUBMETIDA = "SUBMETIDA"


def recusar_se_ja_ha_promessa(apps, schema_editor):
    """O desfazer: só passa quando nenhuma enviada tem o comprovante em PDF/A."""
    Inscricao = apps.get_model("inscricoes", "Inscricao")
    quantas = Inscricao.objects.filter(status=SUBMETIDA, comprovante_em_pdfa=True).count()
    if quantas:
        raise RuntimeError(
            f"{quantas} inscrições enviadas já têm o comprovante em PDF/A, e o resumo dele foi "
            "mostrado ao candidato. Desfazer a inscricoes/0008 apagaria esse registro, e refazê-la "
            "trocaria o comprovante dessas pessoas pelo antigo (178, FR-8164)."
        )


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
        # Por último, para que o desfazer comece por ela, com a coluna ainda de pé.
        migrations.RunPython(migrations.RunPython.noop, recusar_se_ja_ha_promessa),
    ]
