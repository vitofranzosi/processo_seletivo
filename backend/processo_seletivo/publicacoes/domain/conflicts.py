"""Detecção de base obsoleta por caminho alterado (FR-026, FR-036).

`expectedPreviousHash` identifica o conteúdo que a pessoa responsável enxergava ao
elaborar a Alteração Normativa. Comparar esse hash com o conteúdo efetivamente vigente
no `targetPath` impede que uma Retificação sobrescreva silenciosamente outra publicada
no intervalo entre a elaboração e a Publicação.
"""

from processo_seletivo.publicacoes.domain.changes import ABSENT, resolve_path
from processo_seletivo.shared.canonical import canonical_sha256


def previous_hash(content, target_path):
    """Hash canônico do conteúdo em `target_path`; vazio quando o caminho não existe."""
    value = resolve_path(content, target_path)
    return "" if value is ABSENT else canonical_sha256(value)


def conflicting_paths(content, changes):
    """Caminhos cujo `expectedPreviousHash` não corresponde ao conteúdo em `content`.

    Alterações sem `expectedPreviousHash` não são verificadas: o campo é opcional no
    contrato e a ausência significa que a elaboração não declarou conteúdo anterior.
    """
    return [
        change["targetPath"]
        for change in changes
        if change.get("expectedPreviousHash")
        and change["expectedPreviousHash"] != previous_hash(content, change["targetPath"])
    ]
