"""Reconstrói a precondição das Retificações elaboradas antes de ela existir.

A precondição é função determinística de `base_snapshot.content` e da sequência ordenada de
alterações — exatamente o que `derive_preconditions` calcula na elaboração. Por isso o backfill
não adivinha nada: recalcula o que teria sido gravado se a regra já existisse.

Só Retificações ainda em curso são tocadas. Publicada e Cancelada são finais e imutáveis: uma
Publicação já produziu seus efeitos e reescrevê-la seria falsificar histórico, e a Constituição
proíbe. As em curso são justamente as que ainda vão publicar, que é onde o risco está.

A função do domínio é importada em vez de copiada: é pura, e uma cópia divergiria em silêncio
da regra que a aplicação passa a usar — que é o oposto do que este backfill precisa garantir.
"""

from django.db import migrations

from processo_seletivo.publicacoes.domain.conflicts import derive_preconditions

EM_CURSO = ("EM_ELABORACAO", "EM_REVISAO", "HOMOLOGADA")


def preencher(apps, schema_editor):
    Retificacao = apps.get_model("publicacoes", "Retificacao")
    AlteracaoNormativa = apps.get_model("publicacoes", "AlteracaoNormativa")
    for retificacao in (
        Retificacao.objects.filter(status__in=EM_CURSO)
        .select_related("base_snapshot")
        .prefetch_related("alteracoes")
    ):
        alteracoes = list(retificacao.alteracoes.order_by("order"))
        if not alteracoes:
            continue
        preconditions = derive_preconditions(
            retificacao.base_snapshot.content,
            [
                {
                    "targetPath": item.target_path,
                    "operation": item.operation,
                    "newValue": item.new_value,
                    "expectedPreviousHash": item.expected_previous_hash,
                }
                for item in alteracoes
            ],
        )
        for item, precondition in zip(alteracoes, preconditions, strict=True):
            item.expected_previous_hash = precondition["hash"]
            item.expected_anchors = precondition["anchors"]
        AlteracaoNormativa.objects.bulk_update(
            alteracoes, ["expected_previous_hash", "expected_anchors"]
        )


def esvaziar(apps, schema_editor):
    """A reversão devolve o estado anterior; a coluna some junto na 0005."""
    AlteracaoNormativa = apps.get_model("publicacoes", "AlteracaoNormativa")
    AlteracaoNormativa.objects.update(expected_anchors={})


class Migration(migrations.Migration):
    dependencies = [("publicacoes", "0005_ancoras_de_alteracao")]

    operations = [migrations.RunPython(preencher, esvaziar)]
