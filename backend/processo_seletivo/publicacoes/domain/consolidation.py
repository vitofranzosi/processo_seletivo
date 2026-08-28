from processo_seletivo.publicacoes.domain.changes import apply_changes


def consolidate(base, acts):
    content = base
    provenance = {}
    for act in sorted(acts, key=lambda item: (item["effectiveAt"], item["publicationOrder"])):
        content, current = apply_changes(
            content, act["changes"], publication_id=act["publicationId"]
        )
        provenance.update(current)
    return content, provenance
