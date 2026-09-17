"""A base de CEP passa a ser carregada por **geração**, com ativação atômica (029, `T-015`).

**Por que a tabela é recriada em vez de migrada.** `ReferenciaDeCep` é dado de **referência**: ela
não guarda fato de ninguém, é reconstruída por comando a partir de um arquivo público, e a `FR-390`
faz o sistema funcionar com ela vazia. Inventar uma geração para as linhas existentes seria afirmar
de qual instantâneo elas vieram — e ninguém sabe, porque a carga anterior não registrava. Apagar e
mandar recarregar é a resposta honesta, e custa 31 segundos.

**Isto não contraria "nada é excluído".** A Constituição protege dado **normativo** e ato praticado;
uma tabela de CEPs do Correios não é nem um nem outro. A regra que vale aqui é a de que o sistema
funciona sem ela.

**A escrita é `DELETE`, e não `TRUNCATE`.** `TRUNCATE` é mais rápido e toma `ACCESS EXCLUSIVE` na
tabela — que, numa migration que roda junto de um deploy, é justamente a trava que faz requisição em
curso esperar. O volume aqui é conhecido e a lentidão é aceitável.
"""

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("requerimentos", "0003_rascunho_nasce_vazio")]

    operations = [
        migrations.CreateModel(
            name="CargaDeCep",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("geracao", models.PositiveIntegerField(unique=True)),
                ("origem", models.CharField(max_length=255)),
                ("checksum", models.CharField(max_length=64)),
                ("iniciada_em", models.DateTimeField()),
                ("concluida_em", models.DateTimeField(blank=True, null=True)),
                ("linhas", models.PositiveIntegerField(default=0)),
                ("vigente", models.BooleanField(default=False)),
                ("falha", models.TextField(blank=True, default="")),
            ],
            options={
                "verbose_name": "carga de CEP",
                "verbose_name_plural": "cargas de CEP",
            },
        ),
        migrations.AddConstraint(
            model_name="cargadecep",
            constraint=models.UniqueConstraint(
                condition=models.Q(("vigente", True)),
                fields=("vigente",),
                name="uq_carga_de_cep_vigente_unica",
            ),
        ),
        migrations.AddIndex(
            model_name="cargadecep",
            index=models.Index(fields=["-geracao"], name="requeriment_geracao_fd68d8_idx"),
        ),
        # A tabela antiga sai inteira: sem geração, não há como dizer de qual instantâneo cada
        # linha veio. `reverse_sql` devolve a forma anterior, e o conteúdo se recarrega — que é o
        # que ele é.
        migrations.RunSQL(
            sql="DELETE FROM requerimentos_referenciadecep",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RemoveField(model_name="referenciadecep", name="cep"),
        migrations.AddField(
            model_name="referenciadecep",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="referenciadecep",
            name="cep",
            field=models.CharField(default="", max_length=8),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="referenciadecep",
            name="carga",
            field=models.ForeignKey(
                default=None,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="referencias",
                to="requerimentos.cargadecep",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="referenciadecep",
            name="carga",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="referencias",
                to="requerimentos.cargadecep",
            ),
        ),
        migrations.AddConstraint(
            model_name="referenciadecep",
            constraint=models.UniqueConstraint(
                fields=("carga", "cep"), name="uq_referencia_de_cep_por_carga"
            ),
        ),
        migrations.AddIndex(
            model_name="referenciadecep",
            index=models.Index(fields=["carga", "cep"], name="requeriment_carga_i_49df8f_idx"),
        ),
    ]
