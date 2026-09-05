"""O Perfil passa a declarar os fatos que exige do candidato (015, D-2).

Coleção nova de elaboração, no molde de `ModalidadeConcorrencia`: identidade estável, unicidade de
código por Perfil, e `CASCADE` porque remover o Perfil leva junto o que só existia dentro dele.

`tipo` nasce restrito a `DATA` e `INTEIRO`, que são os que os Editais lidos de fato usam — idade sai
de data de nascimento, tempo de experiência sai de meses. Nenhuma linha existe ainda, e por isso
nada precisa de default: um Edital que não declara fato nenhum continua sem campo nenhum.
"""

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('editais', '0008_forma_da_conclusao'),
    ]

    operations = [
        migrations.CreateModel(
            name='FatoDeclarado',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=100)),
                ('label', models.CharField(max_length=255)),
                ('tipo', models.CharField(choices=[('DATA', 'Data'), ('INTEIRO', 'Inteiro')], max_length=20)),
                ('perfil', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fatos', to='editais.perfilvaga')),
            ],
            options={
                'constraints': [models.UniqueConstraint(fields=('perfil', 'code'), name='uq_fato_perfil_code')],
            },
        ),
    ]
