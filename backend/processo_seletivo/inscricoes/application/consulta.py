"""O que a equipe consulta — e sob qual autorização.

A permissão é `inscricao:consultar`, e ela é nova. As existentes não serviam: nenhuma delas
significa "pode ler dado pessoal de candidato", e reaproveitar `processo:encerrar` ou
`edital:elaborar` para abrir documento comprobatório seria decidir por omissão o que a
Constituição manda decidir explicitamente. O papel, esse sim, é o que já existia — a permissão
entra no Gestor, que é quem conduz a seleção.

O escopo institucional é conferido junto: um Edital de outro escopo não é "sem permissão", é
inexistente para quem pergunta — a mesma resposta que `require_permission` já dá (FR-072).
"""

from django.db.models import Count

from processo_seletivo.inscricoes.application.rascunho import requisitos_da_inscricao
from processo_seletivo.inscricoes.domain.arquivos import tamanho_legivel
from processo_seletivo.inscricoes.domain.autenticidade import codigo_de_verificacao
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
    vigente = selectors.selecao_publica(edital_id=edital.id)
    enviados = {}
    for documento in DocumentoSubmetido.objects.filter(inscricao__edital=edital):
        enviados.setdefault(documento.inscricao_id, set()).add(str(documento.requirement_id))
    linhas = []
    consulta = Inscricao.objects.filter(edital=edital).select_related("versao_aceita")
    coincidentes = _cpfs_coincidentes(edital)
    for inscricao in consulta.order_by("-submitted_at", "-created_at"):
        # **A versão de cada inscrição, e não a vigente para todas.** Uma inscrição enviada
        # responde à versão que ela aceitou: usar a vigente faria Perfil, modalidade e contagem de
        # documentos mudarem retroativamente na lista a cada Retificação — o passado sendo
        # reescrito na tela de quem confere (princípio II).
        conteudo = _conteudo_da_inscricao(inscricao, vigente)
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
                # Assinalado, e não apenas visível: a coluna mostra o CPF mascarado, e comparar
                # máscaras a olho numa listagem não é detecção (FR-065).
                "cpf_coincidente": (
                    str(inscricao.profile_id),
                    inscricao.cpf_normalizado,
                )
                in coincidentes,
            }
        )
    return edital, linhas


def _cpfs_coincidentes(edital) -> set:
    """Os pares Perfil + CPF com mais de uma inscrição **enviada** neste Edital (FR-064, FR-065).

    O sistema não decide qual das duas vale — essa decisão é institucional, e a regra pertence à
    feature que for avaliar inscrições, junto com o estado, o contraditório e o ato que a
    acompanham. O que ele faz é não deixar a coincidência passar despercebida.

    Só as enviadas: a regra fala do ato de enviar, e rascunho alheio não marca ninguém. E por
    Perfil, porque concorrer a duas vagas distintas é legítimo — a Constituição o diz.
    """
    contagens = (
        Inscricao.objects.filter(edital=edital, status=Inscricao.Status.SUBMETIDA)
        .exclude(cpf_normalizado="")
        .values("profile_id", "cpf_normalizado")
        .annotate(quantas=Count("id"))
        .filter(quantas__gt=1)
    )
    return {
        (str(linha["profile_id"]), linha["cpf_normalizado"]) for linha in contagens
    }


def _conteudo_da_inscricao(inscricao, vigente):
    """O conteúdo sob o qual aquela inscrição existe.

    Enviada, é a versão aceita — congelada no ato. Em preenchimento, é a vigente, porque é a ela
    que o candidato ainda está respondendo.
    """
    return (inscricao.versao_aceita or vigente).content


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
            # O tamanho legível acompanha o nome porque dois arquivos com o mesmo nome quase nunca
            # têm o mesmo tamanho; o resumo, que vem do próprio documento, decide quando têm.
            "tamanho": (
                None
                if enviados.get(str(requisito["id"])) is None
                else tamanho_legivel(enviados[str(requisito["id"])].tamanho)
            ),
        }
        for requisito in requisitos_da_inscricao(conteudo, inscricao)
    ]
    return {
        "inscricao": inscricao,
        "perfil": perfil,
        "modalidade": modalidade,
        # O mesmo código impresso no comprovante do candidato: é comparando os dois que quem
        # confere recusa um papel alterado, sem ter de conferir linha por linha.
        "codigo_de_verificacao": (
            codigo_de_verificacao(inscricao, enviados.values())
            if inscricao.protocolo
            else ""
        ),
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
