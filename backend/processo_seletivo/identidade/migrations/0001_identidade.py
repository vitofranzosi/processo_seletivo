"""As três tabelas da identidade do candidato.

Reformatada à mão para caber no limite do projeto, como as migrações anteriores. O conteúdo é o
que `makemigrations` produziu: o que muda é a largura das linhas.
"""

import uuid

import django.db.models.deletion
import django.db.models.functions.text
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="CandidateIdentity",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("subject", models.CharField(max_length=255, unique=True)),
                ("nome", models.CharField(blank=True, max_length=255)),
                ("cpf_normalizado", models.CharField(blank=True, max_length=11)),
                ("created_at", models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name="CandidateEmail",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("email_canonico", models.CharField(max_length=254)),
                ("email_como_informado", models.CharField(max_length=254)),
                ("principal", models.BooleanField(default=False)),
                ("verified_at", models.DateTimeField()),
                ("created_at", models.DateTimeField()),
                (
                    "identidade",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="credenciais",
                        to="identidade.candidateidentity",
                    ),
                ),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(
                        django.db.models.functions.text.Lower("email_canonico"),
                        name="uq_credencial_email_canonico",
                    ),
                    models.UniqueConstraint(
                        condition=models.Q(("principal", True)),
                        fields=("identidade",),
                        name="uq_credencial_principal_por_identidade",
                    ),
                ],
            },
        ),
        migrations.CreateModel(
            name="DesafioDeAcesso",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("email_canonico", models.CharField(max_length=254)),
                (
                    "finalidade",
                    models.CharField(
                        choices=[
                            ("ENTRAR", "Entrar"),
                            ("ADICIONAR_CREDENCIAL", "Adicionar Credencial"),
                        ],
                        max_length=30,
                    ),
                ),
                ("codigo_hash", models.CharField(max_length=255)),
                ("origem_hash", models.CharField(blank=True, max_length=64)),
                ("expira_em", models.DateTimeField()),
                ("tentativas_codigo", models.PositiveSmallIntegerField(default=0)),
                ("tentativas_cpf", models.PositiveSmallIntegerField(default=0)),
                ("consumido_em", models.DateTimeField(blank=True, null=True)),
                ("reconciliacao_ate", models.DateTimeField(blank=True, null=True)),
                ("criado_em", models.DateTimeField()),
                (
                    "reconciliacao_alvo",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="identidade.candidateidentity",
                    ),
                ),
            ],
            options={
                "indexes": [
                    models.Index(
                        fields=["email_canonico", "criado_em"],
                        name="identidade__email_c_05577b_idx",
                    ),
                    models.Index(
                        fields=["origem_hash", "criado_em"],
                        name="identidade__origem__caeac6_idx",
                    ),
                ],
            },
        ),
    ]
