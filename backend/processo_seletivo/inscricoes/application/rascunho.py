"""Abrir, retomar e preencher o rascunho da inscrição.

Três decisões estão aqui, e todas as três valem no servidor:

1. **O período é conferido ao abrir** (FR-019). Conhecer o endereço da vaga não dá direito de
   começar antes ou depois do prazo, e a tela não é fronteira de segurança.
2. **A fonte é o conteúdo publicado** (FR-011). O Perfil escolhido tem de existir na versão
   consolidada vigente — nunca nas tabelas de elaboração, que a Retificação altera depois.
3. **O candidato atravessa idempotência e auditoria sem virar ator institucional.** O `Actor`
   construído aqui tem o escopo do Processo alvo e **conjunto de permissões vazio**: todo comando
   administrativo o recusa por construção, que é a propriedade desejada.
"""


from processo_seletivo.auditoria.application import record_event
from processo_seletivo.inscricoes.domain.periodo import periodo_de_inscricoes
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.portal.identidade import normalizar_cpf
from processo_seletivo.publicacoes.application import selectors
from processo_seletivo.seguranca.domain import Actor
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.application.commands import command_context
from processo_seletivo.shared.concurrency import compare_and_swap

# O rótulo da operação no registro de auditoria. **Não** é permissão concedida a ninguém: o ator do
# candidato tem o conjunto vazio, e nenhum papel institucional contém estes nomes.
ABRIR = "inscricao:abrir"
GRAVAR = "inscricao:gravar"


def ator_do_candidato(identidade, edital) -> Actor:
    """O ator que a idempotência e a auditoria pedem, sem uma permissão sequer.

    O escopo é o do Processo alvo, porque é dele que o ato trata — inventar um escopo para quem
    não pertence à instituição faria a auditoria mentir sobre onde o ato aconteceu (FR-078).
    """
    return Actor(identidade.subject, edital.institution_scope, frozenset())


def _versao_vigente(edital_id):
    return selectors.selecao_publica(edital_id=edital_id)


def _perfil_publicado(conteudo, profile_id):
    return next(
        (
            perfil
            for perfil in conteudo.get("profiles") or []
            if str(perfil.get("id")) == str(profile_id)
        ),
        None,
    )


def abrir_inscricao(*, identidade, edital_id, profile_id, correlation_id=""):
    """Abre o rascunho, ou devolve o que já existe (FR-029).

    Reabrir a mesma vaga leva à mesma Inscrição — a unicidade é por identidade, Edital e Perfil, em
    qualquer estado, e é o banco que a garante. Aqui a consulta vem antes para que o caminho comum
    não dependa de exceção.
    """
    versao = _versao_vigente(edital_id)
    conteudo = versao.content
    perfil = _perfil_publicado(conteudo, profile_id)
    if perfil is None:
        raise DomainError("not_found", "Recurso não encontrado.", 404)
    with command_context() as agora:
        existente = Inscricao.objects.filter(
            identity_subject=identidade.subject, edital_id=edital_id, profile_id=profile_id
        ).first()
        if existente is not None:
            return existente
        periodo = periodo_de_inscricoes(conteudo, agora)
        if not periodo.aberto:
            raise DomainError(
                "registration_closed",
                "As inscrições não estão abertas para esta seleção.",
                409,
            )
        inscricao = Inscricao.objects.create(
            identity_subject=identidade.subject,
            edital=versao.edital,
            profile_id=profile_id,
            nome=identidade.nome,
            cpf=identidade.cpf,
            cpf_normalizado=normalizar_cpf(identidade.cpf),
            email=identidade.email,
            versao_reconhecida=versao,
            created_at=agora,
        )
        record_event(
            actor=ator_do_candidato(identidade, versao.edital),
            permission=ABRIR,
            operation="CRIAR",
            aggregate=inscricao,
            now=agora,
            correlation_id=correlation_id,
        )
        return inscricao


def gravar_dados(*, identidade, inscricao, dados, correlation_id=""):
    """Grava os campos da tela, sem `Salvar` (FR-041).

    A gravação acontece na passagem para a revisão — quem chama é a view, no momento em que a
    pessoa avança. Nada de gravação automática contínua: seria mecanismo novo para uma tela com
    quatro campos.
    """
    versao = _versao_vigente(inscricao.edital_id)
    conteudo = versao.content
    with command_context() as agora:
        if not periodo_de_inscricoes(conteudo, agora).aberto:
            raise DomainError(
                "registration_closed",
                "As inscrições não estão abertas para esta seleção.",
                409,
            )
        _validar_modalidade(conteudo, inscricao.profile_id, dados.get("modality_id"))
        compare_and_swap(
            Inscricao.objects,
            pk=inscricao.pk,
            expected_revision=inscricao.revision,
            nome=dados.get("nome", ""),
            cpf=dados.get("cpf", ""),
            cpf_normalizado=normalizar_cpf(dados.get("cpf", "")),
            email=dados.get("email", ""),
            telefone=dados.get("telefone", ""),
            modality_id=dados.get("modality_id") or None,
            # Confirmar os dados é reconhecer a versão que está na tela (FR-059a): o aviso de
            # Retificação passa a comparar com esta, e não volta a aparecer pela mesma alteração.
            versao_reconhecida=versao,
        )
        inscricao.refresh_from_db()
        record_event(
            actor=ator_do_candidato(identidade, inscricao.edital),
            permission=GRAVAR,
            operation="GRAVAR",
            aggregate=inscricao,
            now=agora,
            correlation_id=correlation_id,
        )
        return inscricao


def _validar_modalidade(conteudo, profile_id, modality_id):
    """A modalidade escolhida tem de ser do Perfil da inscrição — conferido no servidor.

    A tela só oferece as do Perfil; isto é o que responde ao POST forjado, e é onde a regra vale.
    """
    if not modality_id:
        return
    perfil = _perfil_publicado(conteudo, profile_id) or {}
    disponiveis = {
        str(modalidade.get("id")) for modalidade in perfil.get("competitionModalities") or []
    }
    if str(modality_id) not in disponiveis:
        raise DomainError(
            "modality_not_available",
            "A modalidade escolhida não é deste Perfil.",
            422,
        )
