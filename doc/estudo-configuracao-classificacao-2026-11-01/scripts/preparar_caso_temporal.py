"""Preparação sintética auditada; execute por manage.py shell no banco exclusivo do estudo."""

from datetime import timedelta
from django.utils import timezone
from processo_seletivo.processos.models import Edital
from processo_seletivo.processos.management.commands.seed_demo import (
    ator,
    CARGO_DO_EDITAL,
)
from processo_seletivo.publicacoes.application.retificacoes import (
    create_retification,
    transition_retification,
    publish_retification,
)
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.unidades.models import AutoridadeHabilitada

edital = Edital.objects.get(
    number="26", processo__institutional_code="UX-CLASS-20261101"
)
base = effective_version(edital_id=edital.id)
perfil = base.content["profiles"][0]
marco = perfil["classificationMilestones"][0]
prefixo = (
    f"/profiles/id={perfil['id']}/classificationMilestones/id={marco['id']}/drawMethod"
)
if not marco.get("drawMethod"):
    prefixo = "/drawMethod"
elaborador = ator("ana.elaboradora", "retificacao:elaborar", "retificacao:submeter")
r, _ = create_retification(
    actor=elaborador,
    edital_id=edital.id,
    data={
        "baseSnapshotId": base.id,
        "justification": "Caso sintético do estudo de UX: fonte que só publica a data, para reproduzir o aviso temporal sem rede.",
        "changes": [
            {
                "targetPath": f"{prefixo}/{campo}",
                "operation": "REPLACE",
                "newValue": valor,
            }
            for campo, valor in [
                ("source", "Fonte de demonstração (só a data)"),
                ("occurrence", "9001"),
                ("occurrenceAt", (timezone.now() - timedelta(minutes=1)).isoformat()),
            ]
        ],
    },
    idempotency_key="ux-temporal-elaborar",
    correlation_id="ux-classificacao-temporal",
)
for acao, autor in [
    ("submeter", elaborador),
    ("homologar", ator("bruno.homologador", "retificacao:homologar")),
]:
    r, _ = transition_retification(
        actor=autor,
        retificacao_id=r.id,
        expected_revision=r.revision,
        action=acao,
        reason="Exemplo sintético de investigação.",
        idempotency_key="ux-temporal-" + acao,
        correlation_id="ux-classificacao-temporal",
    )
publish_retification(
    actor=ator("carla.publicadora", "retificacao:publicar"),
    retificacao_id=r.id,
    expected_revision=r.revision,
    autoridade_id=AutoridadeHabilitada.objects.filter(
        unidade__codigo="cefor", cargo=CARGO_DO_EDITAL
    )
    .first()
    .pk,
    idempotency_key="ux-temporal-publicar",
    correlation_id="ux-classificacao-temporal",
)
print("Caso temporal preparado por Retificação:", edital.id, marco["id"])
