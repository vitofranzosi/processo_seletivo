"""A entrega de um documento ao seu titular — mediada, e nunca por endereço direto.

Nada serve o diretório dos candidatos. Chegar a um arquivo significa passar por aqui, e aqui a
primeira coisa que acontece é a conferência de titularidade: conhecer o identificador não autoriza
(FR-051, FR-071).

`inline` porque o candidato quer **ver** o que enviou, e não baixar de novo o que já tem. E
`no-store`, porque um PDF com dado pessoal no cache do navegador é o mesmo vazamento que a tela.
"""

from django.http import FileResponse

from processo_seletivo.inscricoes.domain.titularidade import exigir_titularidade
from processo_seletivo.inscricoes.models import DocumentoSubmetido
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.http import marcar_como_privada


def entregar_ao_titular(*, inscricao, identidade, requirement_id):
    exigir_titularidade(inscricao, identidade)
    documento = DocumentoSubmetido.objects.filter(
        inscricao=inscricao, requirement_id=requirement_id
    ).first()
    if documento is None:
        raise DomainError("not_found", "Recurso não encontrado.", 404)
    return entregar(documento)


def entregar(documento, *, anexo=False):
    """Streaming, e não leitura para a memória: o arquivo pode ter dez megabytes."""
    resposta = FileResponse(
        documento.arquivo.open("rb"),
        content_type="application/pdf",
        as_attachment=anexo,
        filename=documento.nome_original,
    )
    return marcar_como_privada(resposta)
