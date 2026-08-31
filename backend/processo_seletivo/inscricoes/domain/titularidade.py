"""De quem é a Inscrição — a pergunta que a autorização institucional não responde.

`require_permission` decide "este ator pode praticar esta operação neste escopo?". A pergunta do
candidato é outra: "este registro é dele?". Nenhuma composição das permissões existentes responde
a segunda, e escrever a segunda como se fosse a primeira é como se cria um IDOR com aparência de
autorização (FR-071).

A recusa é 404, e não 403, pelo mesmo motivo que `require_permission` devolve 404 quando o escopo
não confere: dizer "existe, mas não é seu" já entrega que existe.
"""

from processo_seletivo.shared.api.problems import DomainError


def e_titular(inscricao, identidade) -> bool:
    return bool(identidade) and inscricao.identity_subject == identidade.subject


def exigir_titularidade(inscricao, identidade):
    if not e_titular(inscricao, identidade):
        raise DomainError("not_found", "Recurso não encontrado.", 404)
    return inscricao
