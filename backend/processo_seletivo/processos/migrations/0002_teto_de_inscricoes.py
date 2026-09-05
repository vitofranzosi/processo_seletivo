"""O Edital passa a poder limitar quantas Inscrições um candidato tem nele (015, D-3).

Anulável, e a ausência significa **sem limite** — que é exatamente o comportamento de hoje, e é por
isso que a coluna não precisa de default: toda linha existente nasce com `NULL` e continua se
comportando como antes.

**No Edital, e não no Perfil.** `uq_inscricao_identidade_edital_perfil` já garante uma Inscrição por
Perfil; um teto por Perfil repetiria essa constraint com valor 1 e descreveria o que ela proíbe com
valor maior. O que os Editais 14 e 57 exigem é uma por Edital, que é limite sobre o total.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processos', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='edital',
            name='max_inscricoes_por_candidato',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
