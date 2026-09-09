"""O instante em que a ocorrência aconteceu, como a fonte o publica (021, FR-016).

**O nome diz o que o dado é, e não mais do que ele é.** A precedência entre o congelamento e a
ocorrência era aferida pelo instante da **leitura**, e isso era contornável: bastava congelar a
relação depois de ver a extração e registrá-la em seguida.

A primeira correção comparou "quando a ocorrência aconteceu" — e o adaptador da Loteria Federal
carimbava `20:00` sobre a `dataApuracao`, que a fonte publica sem horário. O campo afirmava um
instante inventado, e um congelamento no mesmo dia passava ou falhava por causa dele.

O que se guarda é o **limite inferior verdadeiro**: o início do dia publicado. A comparação exige
que o congelamento seja anterior a ele, o que é conservador e honesto — onde a fonte publicar o
horário, o limite inferior é o próprio horário e a garantia fica mais apertada, sem mudar de forma.
"""

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("sorteios", "0002_imutabilidade"),
    ]

    operations = [
        migrations.AddField(
            model_name="ocorrenciadafonte",
            name="ocorrida_nao_antes_de",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
