"""Concluir deixa de significar pontuar, e a verificação de banco passa a alternar (012, D-008).

**Três operações, e a ordem entre elas é imposta por dado**: a coluna nasce, ela é preenchida, e só
então a verificação é criada. Invertida, a criação da constraint reprovaria toda avaliação já
concluída — o PostgreSQL valida a tabela inteira ao criá-la —, e a migration falharia num banco de
produção justamente por causa do histórico que ela existe para preservar.

**Por que não há `DROP TRIGGER` aqui.** `conclusao_avaliacao_append_only` recusa `UPDATE` e `DELETE`
por linha, e o plano previa derrubá-la em torno do preenchimento. Não é necessário: o preenchimento
da conclusão preservada é feito pelo `DEFAULT` do próprio `ADD COLUMN`, que é DDL e não dispara
trigger de linha, e o `preserve_default=False` remove o default logo em seguida — de modo que ele
não sobrevive no esquema afirmando, para sempre, que conclusão sem forma é pontuada. Só a
`Avaliacao`, que não é append-only e cujo preenchimento é condicional ao estado, usa `UPDATE`.
"""

from django.db import migrations, models

# O que toda linha existente era: até esta revisão o domínio não admitia outra forma, e escrever
# `PONTUADA` não afirma nada que o registro já não dissesse (012, D-008, FR-120).
PONTUADA = "PONTUADA"
FORMAS = [("PONTUADA", "Pontuada"), ("DECISORIA", "Decisoria")]
SENTIDOS = [("FAVORAVEL", "Favoravel"), ("DESFAVORAVEL", "Desfavoravel")]

# **Só as concluídas.** O rascunho continua sem forma, e isso não é economia: a forma é lida no ato
# de concluir, do conteúdo da versão validada (FR-117), e carimbá-la no nascimento faria um rascunho
# aberto antes de uma Retificação concluir sob a forma que já não vige.
PREENCHER_AVALIACAO = """
UPDATE avaliacoes_avaliacao SET forma = 'PONTUADA' WHERE estado = 'CONCLUIDA' AND forma = '';
"""
DESPREENCHER_AVALIACAO = """
UPDATE avaliacoes_avaliacao SET forma = '' WHERE forma = 'PONTUADA';
"""


# A reversão só é válida enquanto **nenhuma conclusão decisória existir**, e isso não é descuido:
# desfazer este passo é afirmar de novo que concluída significa "tem nota", e uma linha decisória
# não tem nota para oferecer. Sem esta guarda, o `migrate` para trás falharia lá adiante, com um
# `IntegrityError` de coluna nula que não diz o que aconteceu.
#
# A recusa vem **primeiro** na reversão — por isso a operação é a última da lista —, e ela nomeia o
# que precisa acontecer antes: as conclusões decisórias são histórico, e desfazê-las é decisão
# administrativa, não de implantação.
RECUSAR = (
    "Existem {quantas} conclusões na forma decisória. Reverter esta migration afirmaria de novo "
    "que concluir exige nota, e essas conclusões não têm nota. Desfazê-las é ato administrativo, "
    "e precisa acontecer antes."
)


def _recusar_se_houver_decisoria(apps, schema_editor):
    from django.db.migrations.exceptions import IrreversibleError

    quantas = 0
    for rotulo, modelo in (("avaliacoes", "Avaliacao"), ("avaliacoes", "ConclusaoAvaliacao")):
        quantas += apps.get_model(rotulo, modelo).objects.filter(forma="DECISORIA").count()
    if quantas:
        raise IrreversibleError(RECUSAR.format(quantas=quantas))


class Migration(migrations.Migration):
    dependencies = [
        ("avaliacoes", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="avaliacao",
            name="forma",
            field=models.CharField(blank=True, choices=FORMAS, default="", max_length=20),
        ),
        migrations.AddField(
            model_name="avaliacao",
            name="sentido",
            field=models.CharField(blank=True, choices=SENTIDOS, default="", max_length=20),
        ),
        migrations.RunSQL(PREENCHER_AVALIACAO, DESPREENCHER_AVALIACAO),
        migrations.AddField(
            model_name="conclusaoavaliacao",
            name="forma",
            field=models.CharField(choices=FORMAS, default=PONTUADA, max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="conclusaoavaliacao",
            name="sentido",
            field=models.CharField(blank=True, choices=SENTIDOS, default="", max_length=20),
        ),
        migrations.AlterField(
            model_name="conclusaoavaliacao",
            name="pontuacao",
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=7, null=True),
        ),
        migrations.RemoveConstraint(
            model_name="avaliacao",
            name="ck_avaliacao_concluida_completa",
        ),
        migrations.AddConstraint(
            model_name="avaliacao",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("estado", "RASCUNHO"),
                    models.Q(
                        ("concluida_em__isnull", False),
                        ("estado", "CONCLUIDA"),
                        ("versao__isnull", False),
                        models.Q(("concluida_por", ""), _negated=True),
                        models.Q(
                            models.Q(
                                ("forma", "PONTUADA"), ("pontuacao__isnull", False), ("sentido", "")
                            ),
                            models.Q(
                                ("forma", "DECISORIA"),
                                ("pontuacao__isnull", True),
                                models.Q(("sentido", ""), _negated=True),
                            ),
                            _connector="OR",
                        ),
                    ),
                    _connector="OR",
                ),
                name="ck_avaliacao_concluida_completa",
            ),
        ),
        migrations.AddConstraint(
            model_name="conclusaoavaliacao",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("forma", "PONTUADA"), ("pontuacao__isnull", False), ("sentido", "")
                )
                | models.Q(("forma", "DECISORIA"), ("pontuacao__isnull", True))
                & ~models.Q(("sentido", "")),
                name="ck_conclusao_completa_por_forma",
            ),
        ),
        # Última na lista, e por isso **primeira** na reversão.
        migrations.RunPython(migrations.RunPython.noop, _recusar_se_houver_decisoria),
    ]
