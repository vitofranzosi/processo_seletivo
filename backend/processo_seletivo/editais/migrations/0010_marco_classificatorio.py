"""O Perfil passa a declarar marcos classificatórios e seus critérios de desempate (015, D-001).

Duas coleções de elaboração no molde de `ModalidadeConcorrencia`, com `CASCADE` porque nem o marco
nem o critério existem fora do que os contém.

As duas unicidades são a norma no banco: `uq_marco_perfil_code` dá ao marco identidade legível
dentro do Perfil, e `uq_criterio_marco_ordem` impede dois critérios na mesma posição — sem ela, a
ordem publicada admitiria empate, e a regra de desempate precisaria de uma regra de desempate.

Nenhuma linha existe ainda; um Edital que não declara marco nenhum não classifica, e continua sem
coleção nenhuma.
"""

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('editais', '0009_fato_declarado'),
    ]

    operations = [
        migrations.CreateModel(
            name='MarcoClassificatorio',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=255)),
                ('etapas', models.JSONField(blank=True, default=list)),
                ('operacao', models.CharField(choices=[('SOMA_PONDERADA', 'Soma Ponderada'), ('MEDIA_PONDERADA', 'Media Ponderada')], max_length=30)),
                ('normalizacao', models.CharField(choices=[('NENHUMA', 'Nenhuma'), ('PELA_SOMA_DOS_PESOS', 'Pela Soma Dos Pesos')], max_length=30)),
                ('arredondamento', models.JSONField(blank=True, default=dict)),
                ('perfil', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='marcos', to='editais.perfilvaga')),
            ],
        ),
        migrations.CreateModel(
            name='CriterioDesempate',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('ordem', models.PositiveIntegerField()),
                ('tipo', models.CharField(choices=[('MAIOR_PONTUACAO_NA_ETAPA', 'Maior Pontuacao Na Etapa'), ('MAIOR_VALOR_DE_FATO', 'Maior Valor De Fato'), ('MENOR_VALOR_DE_FATO', 'Menor Valor De Fato')], max_length=40)),
                ('parametros', models.JSONField(blank=True, default=dict)),
                ('quando_ausente', models.CharField(choices=[('ULTIMO_NO_CRITERIO', 'Ultimo No Criterio'), ('CRITERIO_NAO_SE_APLICA', 'Criterio Nao Se Aplica')], max_length=30)),
                ('marco', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='criterios', to='editais.marcoclassificatorio')),
            ],
        ),
        migrations.AddConstraint(
            model_name='marcoclassificatorio',
            constraint=models.UniqueConstraint(fields=('perfil', 'code'), name='uq_marco_perfil_code'),
        ),
        migrations.AddConstraint(
            model_name='criteriodesempate',
            constraint=models.UniqueConstraint(fields=('marco', 'ordem'), name='uq_criterio_marco_ordem'),
        ),
    ]
