"""A verificação por vídeo (166): as cinco tabelas e os quatro gatilhos append-only.

O vídeo, a abertura, o encaminhamento e a eliminação têm as duas travas de sempre: o gatilho que
recusa `UPDATE` e `DELETE`, e o privilégio ausente, pela entrada em
`seguranca/papeis.py::TABELAS_APPEND_ONLY`. Numa base já provisionada é preciso **rodar o comando de
novo** depois desta migration. O envio em partes é transitório e fica de fora (plano,
*Complexity Tracking*).
"""


import django.db.models.deletion
import uuid
from django.db import migrations, models



TABELAS = {
    "verificacao_video": "verificacao_video_append_only",
    "verificacao_abertura_do_video": "verificacao_abertura_append_only",
    "verificacao_encaminhamento": "verificacao_encaminhamento_append_only",
    "verificacao_eliminacao_do_video": "verificacao_eliminacao_append_only",
}

FUNCAO = """
CREATE OR REPLACE FUNCTION reject_video_verification_mutation() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'video verification records are append-only';
END;
$$ LANGUAGE plpgsql;
"""


def proteger(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute(FUNCAO)
    for tabela, gatilho in TABELAS.items():
        schema_editor.execute(
            f"CREATE TRIGGER {gatilho} BEFORE UPDATE OR DELETE ON {tabela} "
            "FOR EACH ROW EXECUTE FUNCTION reject_video_verification_mutation();"
        )


def desproteger(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    for tabela, gatilho in TABELAS.items():
        schema_editor.execute(f"DROP TRIGGER IF EXISTS {gatilho} ON {tabela};")
    schema_editor.execute("DROP FUNCTION IF EXISTS reject_video_verification_mutation();")


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('inscricoes', '0007_imutabilidade_da_enviada'),
        ('processos', '0005_escopo_imutavel'),
    ]

    operations = [
        migrations.CreateModel(
            name='VideoDaVerificacao',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('etapa_id', models.UUIDField()),
                ('arquivo', models.CharField(max_length=255)),
                ('sha256', models.CharField(max_length=64)),
                ('tamanho', models.PositiveBigIntegerField()),
                ('duracao', models.DecimalField(decimal_places=3, max_digits=8)),
                ('formato', models.CharField(choices=[('video/mp4', 'video/mp4'), ('video/webm', 'video/webm')], max_length=20)),
                ('roteiro', models.CharField(max_length=60)),
                ('marcas', models.JSONField(default=list)),
                ('declarou_maioridade', models.BooleanField()),
                ('recebido_em', models.DateTimeField()),
                ('edital', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='processos.edital')),
                ('inscricao', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='inscricoes.inscricao')),
                ('substitui', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='substituido_por', to='verificacao.videodaverificacao')),
            ],
            options={
                'verbose_name': 'O vídeo da verificação',
                'db_table': 'verificacao_video',
            },
        ),
        migrations.CreateModel(
            name='EncaminhamentoAoVivo',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('etapa_id', models.UUIDField()),
                ('pareceres', models.JSONField(default=list)),
                ('registrado_em', models.DateTimeField()),
                ('registrado_por', models.CharField(max_length=255)),
                ('edital', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='processos.edital')),
                ('inscricao', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='inscricoes.inscricao')),
                ('video', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='verificacao.videodaverificacao')),
            ],
            options={
                'verbose_name': 'O encaminhamento à entrevista ao vivo',
                'db_table': 'verificacao_encaminhamento',
            },
        ),
        migrations.CreateModel(
            name='EliminacaoDoVideo',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('eliminado_em', models.DateTimeField()),
                ('prazo_em_dias', models.PositiveIntegerField()),
                ('encerramento_em', models.DateTimeField()),
                ('video', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='eliminacao', to='verificacao.videodaverificacao')),
            ],
            options={
                'verbose_name': 'A eliminação do vídeo',
                'db_table': 'verificacao_eliminacao_do_video',
            },
        ),
        migrations.CreateModel(
            name='AberturaDoVideo',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('pessoa', models.CharField(max_length=255)),
                ('papel', models.CharField(choices=[('COMISSAO', 'Comissao'), ('TITULAR', 'Titular')], max_length=20)),
                ('aberta_em', models.DateTimeField()),
                ('video', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='aberturas', to='verificacao.videodaverificacao')),
            ],
            options={
                'verbose_name': 'A abertura do vídeo',
                'db_table': 'verificacao_abertura_do_video',
            },
        ),
        migrations.CreateModel(
            name='EnvioDoVideo',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('etapa_id', models.UUIDField()),
                ('tamanho', models.PositiveBigIntegerField()),
                ('recebido', models.PositiveBigIntegerField(default=0)),
                ('formato', models.CharField(choices=[('video/mp4', 'video/mp4'), ('video/webm', 'video/webm')], max_length=20)),
                ('duracao_medida', models.DecimalField(decimal_places=3, max_digits=8)),
                ('marcas', models.JSONField(default=list)),
                ('roteiro', models.CharField(max_length=60)),
                ('declarou_maioridade', models.BooleanField()),
                ('iniciado_em', models.DateTimeField()),
                ('arquivo', models.CharField(max_length=255)),
                ('edital', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='processos.edital')),
                ('inscricao', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='inscricoes.inscricao')),
            ],
            options={
                'db_table': 'verificacao_envio_do_video',
                'constraints': [models.UniqueConstraint(fields=('edital', 'etapa_id', 'inscricao'), name='uq_um_envio_por_inscricao'), models.CheckConstraint(condition=models.Q(('recebido__lte', models.F('tamanho'))), name='ck_envio_recebido'), models.CheckConstraint(condition=models.Q(('declarou_maioridade', True)), name='ck_envio_maior')],
            },
        ),
        migrations.AddIndex(
            model_name='videodaverificacao',
            index=models.Index(fields=['edital', 'etapa_id', 'inscricao'], name='verificacao_edital__f4807f_idx'),
        ),
        migrations.AddConstraint(
            model_name='videodaverificacao',
            constraint=models.CheckConstraint(condition=models.Q(('declarou_maioridade', True)), name='ck_video_maior'),
        ),
        migrations.AddConstraint(
            model_name='videodaverificacao',
            constraint=models.CheckConstraint(condition=models.Q(('sha256__regex', '^[0-9a-f]{64}$')), name='ck_video_sha'),
        ),
        migrations.AddConstraint(
            model_name='encaminhamentoaovivo',
            constraint=models.UniqueConstraint(fields=('edital', 'etapa_id', 'inscricao'), name='uq_um_encaminhamento'),
        ),
        migrations.AddIndex(
            model_name='aberturadovideo',
            index=models.Index(fields=['video', 'papel'], name='verificacao_video_i_86aaa7_idx'),
        ),
        migrations.RunPython(proteger, desproteger),
    ]
