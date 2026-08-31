"""O que a equipe consulta — e sob qual autorização.

A permissão é `inscricao:consultar`, e ela é nova. As existentes não serviam: nenhuma delas
significa "pode ler dado pessoal de candidato", e reaproveitar `processo:encerrar` ou
`edital:elaborar` para abrir documento comprobatório seria decidir por omissão o que a
Constituição manda decidir explicitamente. O papel, esse sim, é o que já existia — a permissão
entra no Gestor, que é quem conduz a seleção.

O escopo institucional é conferido junto: um Edital de outro escopo não é "sem permissão", é
inexistente para quem pergunta — a mesma resposta que `require_permission` já dá (FR-072).
"""

from processo_seletivo.inscricoes.application.rascunho import requisitos_da_inscricao
from processo_seletivo.inscricoes.domain.pessoais import mascarar_cpf
from processo_seletivo.inscricoes.models import DocumentoSubmetido, Inscricao
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.application import selectors
from processo_seletivo.seguranca.application.authorization import require_permission
from processo_seletivo.shared.api.problems import DomainError

CONSULTAR = "inscricao:consultar"


def _edital_no_escopo(actor, edital_id):
    require_permission(actor, CONSULTAR)
    try:
        return Edital.objects.get(pk=edital_id, institution_scope=actor.institution_scope)
    except Edital.DoesNotExist as exc:
        raise DomainError("not_found", "Recurso não encontrado.", 404) from exc


def _nome_no_conteudo(conteudo, inscricao):
    perfil = next(
        (
            item
            for item in conteudo.get("profiles") or []
            if str(item.get("id")) == str(inscricao.profile_id)
        ),
        {},
    )
    modalidade = next(
        (
            item.get("name", "")
            for item in perfil.get("competitionModalities") or []
            if str(item.get("id")) == str(inscricao.modality_id)
        ),
        "",
    )
    return perfil.get("name", ""), modalidade


def inscricoes_do_edital(*, actor, edital_id):
    """A lista do que chegou, com o que decide a conferência — e nada de avaliação (FR-067).

    A contagem de documentos é sobre os **obrigatórios aplicáveis àquela inscrição**, e não sobre
    o total do Edital: um candidato de ampla concorrência com dois de dois está completo, e exibir
    "2 de 3" por causa de um requisito que não é dele diria que falta algo que não falta.
    """
    edital = _edital_no_escopo(actor, edital_id)
    versao = selectors.selecao_publica(edital_id=edital.id)
    conteudo = versao.content
    enviados = {}
    for documento in DocumentoSubmetido.objects.filter(inscricao__edital=edital):
        enviados.setdefault(documento.inscricao_id, set()).add(str(documento.requirement_id))
    linhas = []
    for inscricao in Inscricao.objects.filter(edital=edital).order_by(
        "-submitted_at", "-created_at"
    ):
        perfil, modalidade = _nome_no_conteudo(conteudo, inscricao)
        obrigatorios = [
            str(requisito["id"])
            for requisito in requisitos_da_inscricao(conteudo, inscricao)
            if requisito.get("required", True)
        ]
        recebidos = enviados.get(inscricao.id, set())
        linhas.append(
            {
                "id": inscricao.id,
                "protocolo": inscricao.protocolo,
                "candidato": inscricao.nome,
                "cpf": mascarar_cpf(inscricao.cpf),
                "perfil": perfil,
                "modalidade": modalidade,
                "situacao": inscricao.get_status_display(),
                "enviada": inscricao.status == Inscricao.Status.SUBMETIDA,
                "recebidos": len([item for item in obrigatorios if item in recebidos]),
                "esperados": len(obrigatorios),
                "quando": inscricao.submitted_at or inscricao.created_at,
            }
        )
    return edital, linhas


def inscricao_para_consulta(*, actor, inscricao_id):
    """O detalhe, com cada documento **sob o requisito que ele atende** (FR-068).

    É a diferença entre o que este sistema entrega e uma pasta de arquivos: a lista é a dos
    requisitos, e o arquivo aparece dentro do seu. Requisito sem arquivo aparece como requisito
    sem arquivo, que é informação — não uma linha que some.
    """
    inscricao = (
        Inscricao.objects.select_related("edital", "versao_aceita").filter(pk=inscricao_id).first()
    )
    if inscricao is None:
        require_permission(actor, CONSULTAR)
        raise DomainError("not_found", "Recurso não encontrado.", 404)
    _edital_no_escopo(actor, inscricao.edital_id)
    versao = inscricao.versao_aceita or selectors.selecao_publica(edital_id=inscricao.edital_id)
    conteudo = versao.content
    perfil, modalidade = _nome_no_conteudo(conteudo, inscricao)
    enviados = {
        str(documento.requirement_id): documento
        for documento in DocumentoSubmetido.objects.filter(inscricao=inscricao)
    }
    documentos = [
        {
            "id": str(requisito["id"]),
            "nome": requisito.get("name", ""),
            "obrigatorio": requisito.get("required", True),
            "enviado": enviados.get(str(requisito["id"])),
        }
        for requisito in requisitos_da_inscricao(conteudo, inscricao)
    ]
    return {
        "inscricao": inscricao,
        "perfil": perfil,
        "modalidade": modalidade,
        "cpf": mascarar_cpf(inscricao.cpf),
        "versao": versao,
        "documentos": documentos,
    }


def documento_para_consulta(*, actor, inscricao_id, requirement_id):
    """O documento que a equipe abre, conferido antes de sair um byte."""
    inscricao = Inscricao.objects.filter(pk=inscricao_id).first()
    if inscricao is None:
        require_permission(actor, CONSULTAR)
        raise DomainError("not_found", "Recurso não encontrado.", 404)
    _edital_no_escopo(actor, inscricao.edital_id)
    documento = DocumentoSubmetido.objects.filter(
        inscricao=inscricao, requirement_id=requirement_id
    ).first()
    if documento is None:
        raise DomainError("not_found", "Recurso não encontrado.", 404)
    return documento
