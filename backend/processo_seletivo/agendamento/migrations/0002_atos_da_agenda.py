"""Os atos da agenda da Etapa: o ato, o horário publicado de cada pessoa e o documento (167, B).

**Nascem append-only, nas três camadas**: `save`/`delete` recusam na aplicação, os gatilhos abaixo
recusam a mutação mesmo de quem tem privilégio, e o papel de runtime não recebe `UPDATE` nem
`DELETE` — o terceiro vem de `TABELAS_APPEND_ONLY`, e é por isso que o provisionamento precisa rodar
de novo depois desta migration (o `M` passa de 65 a 68).

**O gatilho de coerência confere o que `CHECK` não alcança**, porque atravessa tabelas: o item que
este substitui é da mesma inscrição e de um ato da mesma agenda; a banca é da agenda do ato; só a
remarcação e o cancelamento substituem; e só o cancelamento cancela. Sem ele, um caminho que não
passasse pela aplicação poderia pôr numa agenda o horário de outra — e a página pública mostraria
uma sala que a pessoa nunca recebeu.
"""

import uuid

import django.db.models.deletion
from django.db import migrations, models

PROTEGER = """
CREATE OR REPLACE FUNCTION reject_schedule_act_mutation() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'schedule acts are append-only';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER ato_da_agenda_append_only
BEFORE UPDATE OR DELETE ON agendamento_atodaagenda
FOR EACH ROW EXECUTE FUNCTION reject_schedule_act_mutation();

CREATE TRIGGER horario_publicado_append_only
BEFORE UPDATE OR DELETE ON agendamento_horariopublicado
FOR EACH ROW EXECUTE FUNCTION reject_schedule_act_mutation();

CREATE TRIGGER documento_do_ato_da_agenda_append_only
BEFORE UPDATE OR DELETE ON agendamento_documentodoatodaagenda
FOR EACH ROW EXECUTE FUNCTION reject_schedule_act_mutation();

CREATE OR REPLACE FUNCTION check_published_slot_coherence() RETURNS trigger AS $$
DECLARE
    ato RECORD;
    anterior RECORD;
    agenda_da_banca uuid;
BEGIN
    SELECT a.agenda_id, a.especie INTO ato
      FROM agendamento_atodaagenda a WHERE a.id = NEW.ato_id;
    IF NEW.banca_id IS NOT NULL THEN
        SELECT b.agenda_id INTO agenda_da_banca
          FROM agendamento_bancadaagenda b WHERE b.id = NEW.banca_id;
        IF agenda_da_banca IS DISTINCT FROM ato.agenda_id THEN
            RAISE EXCEPTION 'published slot in a desk of another schedule';
        END IF;
    END IF;
    IF ato.especie IN ('REMARCACAO', 'CANCELAMENTO') AND NEW.substitui_id IS NULL THEN
        RAISE EXCEPTION 'a rescheduling or cancellation replaces a published slot';
    END IF;
    IF ato.especie IN ('PUBLICACAO', 'INCLUSAO') AND NEW.substitui_id IS NOT NULL THEN
        RAISE EXCEPTION 'a publication or inclusion replaces nothing';
    END IF;
    IF NEW.situacao = 'CANCELADO' AND ato.especie IS DISTINCT FROM 'CANCELAMENTO' THEN
        RAISE EXCEPTION 'only a cancellation cancels';
    END IF;
    IF NEW.substitui_id IS NOT NULL THEN
        SELECT h.inscricao_id, a.agenda_id INTO anterior
          FROM agendamento_horariopublicado h
          JOIN agendamento_atodaagenda a ON a.id = h.ato_id
         WHERE h.id = NEW.substitui_id;
        IF anterior.inscricao_id IS DISTINCT FROM NEW.inscricao_id THEN
            RAISE EXCEPTION 'published slot replaces a slot of another registration';
        END IF;
        IF anterior.agenda_id IS DISTINCT FROM ato.agenda_id THEN
            RAISE EXCEPTION 'published slot replaces a slot of another schedule';
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER horario_publicado_coerente
BEFORE INSERT ON agendamento_horariopublicado
FOR EACH ROW EXECUTE FUNCTION check_published_slot_coherence();
"""

DESPROTEGER = """
DROP TRIGGER IF EXISTS horario_publicado_coerente ON agendamento_horariopublicado;
DROP FUNCTION IF EXISTS check_published_slot_coherence();
DROP TRIGGER IF EXISTS documento_do_ato_da_agenda_append_only
    ON agendamento_documentodoatodaagenda;
DROP TRIGGER IF EXISTS horario_publicado_append_only ON agendamento_horariopublicado;
DROP TRIGGER IF EXISTS ato_da_agenda_append_only ON agendamento_atodaagenda;
DROP FUNCTION IF EXISTS reject_schedule_act_mutation();
"""


def proteger(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute(PROTEGER)


def desproteger(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute(DESPROTEGER)


class Migration(migrations.Migration):
    dependencies = [
        ("agendamento", "0001_agenda_da_etapa"),
        ("avisos", "0002_origem_pendencia"),
        ("inscricoes", "0007_imutabilidade_da_enviada"),
        ("processos", "0005_escopo_imutavel"),
    ]

    operations = [
        migrations.CreateModel(
            name="AtoDaAgenda",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                (
                    "especie",
                    models.CharField(
                        choices=[
                            ("PUBLICACAO", "Publicação"),
                            ("REMARCACAO", "Remarcação"),
                            ("INCLUSAO", "Inclusão"),
                            ("CANCELAMENTO", "Cancelamento"),
                        ],
                        max_length=20,
                    ),
                ),
                ("praticado_por", models.CharField(max_length=255)),
                ("praticado_em", models.DateTimeField()),
                ("motivo", models.TextField(blank=True, default="")),
                (
                    "veiculo",
                    models.CharField(
                        blank=True,
                        choices=[("GPS", "Página pública do GPS"), ("EXTERNO", "Fora do GPS")],
                        default="",
                        max_length=10,
                    ),
                ),
                ("declaracao_do_veiculo", models.TextField(blank=True, default="")),
                ("publicado_fora_onde", models.TextField(blank=True, default="")),
                ("publicado_fora_em", models.DateField(blank=True, null=True)),
                ("signatario_id", models.UUIDField(blank=True, null=True)),
                ("signatario_nome", models.CharField(blank=True, default="", max_length=255)),
                ("signatario_cargo", models.CharField(blank=True, default="", max_length=255)),
                (
                    "signatario_ato_de_nomeacao",
                    models.CharField(blank=True, default="", max_length=255),
                ),
                ("unidade_codigo", models.CharField(blank=True, default="", max_length=100)),
                ("unidade_sigla", models.CharField(blank=True, default="", max_length=30)),
                ("unidade_nome", models.CharField(blank=True, default="", max_length=255)),
                ("unidade_cabecalho", models.JSONField(default=list)),
                ("unidade_local", models.CharField(blank=True, default="", max_length=120)),
                ("conteudo_publico", models.BinaryField()),
                ("conteudo_publico_hash", models.CharField(max_length=64)),
                ("assinatura_conferida", models.CharField(blank=True, default="", max_length=64)),
                ("idempotency_key", models.CharField(blank=True, default="", max_length=128)),
                (
                    "agenda",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="atos",
                        to="agendamento.agendadaetapa",
                    ),
                ),
                (
                    "edital",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="atos_das_agendas",
                        to="processos.edital",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="DocumentoDoAtoDaAgenda",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("bytes", models.BinaryField()),
                ("content_type", models.CharField(default="application/pdf", max_length=100)),
                ("documento_hash", models.CharField(max_length=64)),
                (
                    "ato",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="documento",
                        to="agendamento.atodaagenda",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="HorarioPublicado",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                (
                    "situacao",
                    models.CharField(
                        choices=[("AGENDADO", "Agendado"), ("CANCELADO", "Cancelado")],
                        max_length=10,
                    ),
                ),
                ("banca_nome", models.CharField(blank=True, default="", max_length=80)),
                ("inicio", models.DateTimeField(blank=True, null=True)),
                ("fim", models.DateTimeField(blank=True, null=True)),
                (
                    "ato",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="horarios",
                        to="agendamento.atodaagenda",
                    ),
                ),
                (
                    "aviso",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="horarios_da_agenda",
                        to="avisos.aviso",
                    ),
                ),
                (
                    "banca",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="horarios_publicados",
                        to="agendamento.bancadaagenda",
                    ),
                ),
                (
                    "inscricao",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="horarios_publicados",
                        to="inscricoes.inscricao",
                    ),
                ),
                (
                    "substitui",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="substituicoes",
                        to="agendamento.horariopublicado",
                    ),
                ),
            ],
        ),
        migrations.AddIndex(
            model_name="atodaagenda",
            index=models.Index(fields=["edital", "especie"], name="ix_ato_da_agenda_edital"),
        ),
        migrations.AddConstraint(
            model_name="atodaagenda",
            constraint=models.UniqueConstraint(
                condition=models.Q(("especie", "PUBLICACAO")),
                fields=("agenda",),
                name="uq_ato_da_agenda_uma_publicacao",
            ),
        ),
        migrations.AddConstraint(
            model_name="atodaagenda",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("especie__in", ["PUBLICACAO", "REMARCACAO", "INCLUSAO", "CANCELAMENTO"])
                ),
                name="ck_ato_da_agenda_especie",
            ),
        ),
        migrations.AddConstraint(
            model_name="atodaagenda",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(("especie", "PUBLICACAO"), ("motivo", "")),
                    models.Q(
                        models.Q(("especie", "PUBLICACAO"), _negated=True),
                        models.Q(("motivo", ""), _negated=True),
                    ),
                    _connector="OR",
                ),
                name="ck_ato_da_agenda_motivo",
            ),
        ),
        migrations.AddConstraint(
            model_name="atodaagenda",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(
                        models.Q(("especie", "PUBLICACAO"), _negated=True),
                        ("veiculo", ""),
                        ("declaracao_do_veiculo", ""),
                        ("publicado_fora_onde", ""),
                        ("publicado_fora_em__isnull", True),
                    ),
                    models.Q(
                        ("especie", "PUBLICACAO"),
                        ("veiculo", "GPS"),
                        models.Q(("declaracao_do_veiculo", ""), _negated=True),
                        ("publicado_fora_onde", ""),
                        ("publicado_fora_em__isnull", True),
                    ),
                    models.Q(
                        ("especie", "PUBLICACAO"),
                        ("veiculo", "EXTERNO"),
                        ("declaracao_do_veiculo", ""),
                        models.Q(("publicado_fora_onde", ""), _negated=True),
                        ("publicado_fora_em__isnull", False),
                    ),
                    _connector="OR",
                ),
                name="ck_ato_da_agenda_veiculo",
            ),
        ),
        migrations.AddConstraint(
            model_name="atodaagenda",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(
                        ("especie", "PUBLICACAO"),
                        ("signatario_id__isnull", False),
                        models.Q(("signatario_cargo", ""), _negated=True),
                    ),
                    models.Q(
                        models.Q(("especie", "PUBLICACAO"), _negated=True),
                        ("signatario_id__isnull", True),
                        ("signatario_nome", ""),
                        ("signatario_cargo", ""),
                    ),
                    _connector="OR",
                ),
                name="ck_ato_da_agenda_signatario",
            ),
        ),
        migrations.AddIndex(
            model_name="horariopublicado",
            index=models.Index(fields=["inscricao"], name="ix_horario_publicado_inscricao"),
        ),
        migrations.AddConstraint(
            model_name="horariopublicado",
            constraint=models.UniqueConstraint(
                fields=("ato", "inscricao"), name="uq_horario_publicado_por_ato"
            ),
        ),
        migrations.AddConstraint(
            model_name="horariopublicado",
            constraint=models.UniqueConstraint(
                fields=("substitui",), name="uq_horario_publicado_substituido_uma_vez"
            ),
        ),
        migrations.AddConstraint(
            model_name="horariopublicado",
            constraint=models.UniqueConstraint(
                fields=("aviso",), name="uq_horario_publicado_aviso"
            ),
        ),
        migrations.AddConstraint(
            model_name="horariopublicado",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(
                        ("situacao", "AGENDADO"),
                        ("banca__isnull", False),
                        models.Q(("banca_nome", ""), _negated=True),
                        ("inicio__isnull", False),
                        ("fim__isnull", False),
                        ("inicio__lt", models.F("fim")),
                    ),
                    models.Q(
                        ("situacao", "CANCELADO"),
                        ("banca__isnull", True),
                        ("inicio__isnull", True),
                        ("fim__isnull", True),
                    ),
                    _connector="OR",
                ),
                name="ck_horario_publicado_forma",
            ),
        ),
        migrations.RunPython(proteger, desproteger),
    ]
