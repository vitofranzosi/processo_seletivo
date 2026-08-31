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


from django.conf import settings
from django.db import IntegrityError, transaction

from processo_seletivo.auditoria.application import record_event
from processo_seletivo.editais.domain.documentos import aplicaveis
from processo_seletivo.inscricoes.domain.arquivos import aceitar, resumo
from processo_seletivo.inscricoes.domain.periodo import recebe_inscricoes
from processo_seletivo.inscricoes.models import DocumentoSubmetido, Inscricao
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


def modalidades_publicadas(conteudo, profile_id) -> list[dict]:
    """As modalidades declaradas para aquele Perfil, na ordem do conteúdo publicado."""
    perfil = _perfil_publicado(conteudo, profile_id) or {}
    return [
        modalidade
        for modalidade in perfil.get("competitionModalities") or []
        if isinstance(modalidade, dict) and modalidade.get("id")
    ]


def modalidade_assumida(conteudo, profile_id) -> str | None:
    """A modalidade que não se pergunta.

    Uma única modalidade publicada não é uma escolha — é a condição de todo mundo naquele Perfil.
    Perguntar seria pedir à pessoa que confirme o óbvio, e deixar em branco seria pior: a
    aplicabilidade dos documentos depende dela, e uma inscrição sem modalidade num Perfil que só
    tem uma deixaria de pedir o que aquela modalidade exige (FR-038, FR-040).
    """
    modalidades = modalidades_publicadas(conteudo, profile_id)
    return str(modalidades[0]["id"]) if len(modalidades) == 1 else None


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
        existente = _inscricao_existente(identidade, edital_id, profile_id)
        if existente is not None:
            return existente
        if not recebe_inscricoes(
            status=versao.edital.status, conteudo=conteudo, agora=agora
        ):
            raise DomainError(
                "registration_closed",
                "Esta seleção não está recebendo inscrições.",
                409,
            )
        try:
            # Savepoint próprio: sem ele, a violação de unicidade envenenaria a transação inteira
            # e nem a leitura seguinte seria possível. Duas requisições simultâneas do mesmo
            # convite — dois cliques, duas abas — chegam aqui juntas, e a promessa de FR-029 é que
            # as duas terminem na mesma inscrição, não que uma receba erro de servidor.
            with transaction.atomic():
                inscricao = Inscricao.objects.create(
                    identity_subject=identidade.subject,
                    edital=versao.edital,
                    profile_id=profile_id,
                    modality_id=modalidade_assumida(conteudo, profile_id),
                    nome=identidade.nome,
                    cpf=identidade.cpf,
                    cpf_normalizado=normalizar_cpf(identidade.cpf),
                    email=identidade.email,
                    versao_reconhecida=versao,
                    created_at=agora,
                )
        except IntegrityError:
            return _inscricao_existente(identidade, edital_id, profile_id)
        record_event(
            actor=ator_do_candidato(identidade, versao.edital),
            permission=ABRIR,
            operation="CRIAR",
            aggregate=inscricao,
            now=agora,
            correlation_id=correlation_id,
        )
        return inscricao


def _inscricao_existente(identidade, edital_id, profile_id):
    return Inscricao.objects.filter(
        identity_subject=identidade.subject, edital_id=edital_id, profile_id=profile_id
    ).first()


def gravar_dados(*, identidade, inscricao, dados, correlation_id=""):
    """Grava os campos da tela, sem `Salvar` (FR-041).

    A gravação acontece na passagem para a revisão — quem chama é a view, no momento em que a
    pessoa avança. Nada de gravação automática contínua: seria mecanismo novo para uma tela com
    quatro campos.
    """
    versao = _versao_vigente(inscricao.edital_id)
    conteudo = versao.content
    with command_context() as agora:
        if not recebe_inscricoes(status=inscricao.edital.status, conteudo=conteudo, agora=agora):
            raise DomainError(
                "registration_closed",
                "Esta seleção não está recebendo inscrições.",
                409,
            )
        modalidade = _modalidade_escolhida(
            conteudo, inscricao.profile_id, dados.get("modality_id")
        )
        compare_and_swap(
            Inscricao.objects,
            pk=inscricao.pk,
            expected_revision=inscricao.revision,
            nome=dados.get("nome", ""),
            cpf=dados.get("cpf", ""),
            cpf_normalizado=normalizar_cpf(dados.get("cpf", "")),
            email=dados.get("email", ""),
            telefone=dados.get("telefone", ""),
            modality_id=modalidade,
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


def _modalidade_escolhida(conteudo, profile_id, modality_id):
    """Qual modalidade fica gravada — e quando a ausência dela é recusa.

    Três casos, e a diferença entre eles é o que separa "não perguntar o óbvio" de "aceitar
    inscrição incompleta":

    - **nenhuma publicada**: não há o que escolher, e escolher seria inventar (FR-039);
    - **uma publicada**: é assumida, com ou sem envio do formulário — a pergunta não existe;
    - **duas ou mais**: a escolha é obrigatória. Deixar em branco pareceria inofensivo e não é:
      a aplicabilidade dos documentos depende dela, e o candidato deixaria de receber o que a sua
      modalidade exige, sem que nada acusasse (FR-040).

    A tela só oferece as do Perfil; esta função é o que responde ao POST forjado, e é onde a regra
    vale.
    """
    modalidades = modalidades_publicadas(conteudo, profile_id)
    if not modalidades:
        return None
    if len(modalidades) == 1:
        return str(modalidades[0]["id"])
    if not modality_id:
        raise DomainError(
            "modality_required",
            "Escolha como você concorre nesta vaga.",
            422,
        )
    if str(modality_id) not in {str(modalidade["id"]) for modalidade in modalidades}:
        raise DomainError(
            "modality_not_available",
            "A modalidade escolhida não é deste Perfil.",
            422,
        )
    return str(modality_id)


# ---------------------------------------------------------------------------
# Documentos do rascunho (entrega 4)
# ---------------------------------------------------------------------------

ANEXAR = "inscricao:anexar"
REMOVER = "inscricao:remover"


def requisitos_da_inscricao(conteudo, inscricao) -> list[dict]:
    """Os requisitos que valem para **esta** inscrição, e nenhum além (FR-040).

    A aplicabilidade é função pura sobre o conteúdo publicado e vive no domínio dos Editais, junto
    da regra que a declara. Chamá-la daqui é o que garante que a tela, o envio e a submissão
    respondam a mesma coisa — três leituras da mesma função, e não três interpretações.
    """
    return aplicaveis(
        conteudo.get("documentRequirements") or [],
        profile_id=str(inscricao.profile_id),
        modality_id=None if inscricao.modality_id is None else str(inscricao.modality_id),
    )


def _requisito_aplicavel(conteudo, inscricao, requirement_id):
    return next(
        (
            requisito
            for requisito in requisitos_da_inscricao(conteudo, inscricao)
            if str(requisito.get("id")) == str(requirement_id)
        ),
        None,
    )


def anexar_documento(*, identidade, inscricao, requirement_id, arquivo, correlation_id=""):
    """Guarda um arquivo para um requisito — imediatamente, e sem `Salvar` (FR-041).

    Três recusas antes de qualquer escrita, e a ordem importa: fora do período não se anexa nada;
    requisito que não se aplica àquela inscrição não é aceito **ainda que a tela nunca o tenha
    oferecido** (FR-044); e o arquivo é conferido por conteúdo antes de tocar o disco.
    """
    versao = _versao_vigente(inscricao.edital_id)
    conteudo = versao.content
    with command_context() as agora:
        if not recebe_inscricoes(status=inscricao.edital.status, conteudo=conteudo, agora=agora):
            raise DomainError(
                "registration_closed", "Esta seleção não está recebendo inscrições.", 409
            )
        if inscricao.status != Inscricao.Status.RASCUNHO:
            raise DomainError(
                "submission_is_final", "Uma inscrição enviada não aceita alterações.", 409
            )
        if _requisito_aplicavel(conteudo, inscricao, requirement_id) is None:
            raise DomainError("not_found", "Recurso não encontrado.", 404)
        aceitar(
            arquivo,
            nome_original=arquivo.name,
            limite_em_bytes=settings.ARQUIVOS_CANDIDATOS_LIMITE_BYTES,
        )
        conteudo_hash = resumo(arquivo)
        anterior = DocumentoSubmetido.objects.filter(
            inscricao=inscricao, requirement_id=requirement_id
        ).first()
        if anterior is not None:
            # Substituir é sobrescrever, e o arquivo antigo sai do disco junto: guardar versões
            # que ninguém pediu criaria a pergunta "qual vale?" e um acervo que cresce sozinho.
            anterior.arquivo.delete(save=False)
            anterior.delete()
        documento = DocumentoSubmetido(
            inscricao=inscricao,
            requirement_id=requirement_id,
            nome_original=arquivo.name[:255],
            tamanho=arquivo.size,
            content_hash=conteudo_hash,
            uploaded_at=agora,
        )
        documento.arquivo.save(arquivo.name, arquivo, save=False)
        documento.save()
        record_event(
            actor=ator_do_candidato(identidade, inscricao.edital),
            permission=ANEXAR,
            operation="ANEXAR",
            aggregate=inscricao,
            now=agora,
            correlation_id=correlation_id,
            # O requisito atendido, e **não** o nome do arquivo: nome de arquivo carrega dado
            # pessoal com frequência, e a auditoria não precisa dele para responder o que
            # aconteceu (FR-078).
            reason=f"requisito {requirement_id}",
        )
        return documento


def remover_documento(*, identidade, inscricao, requirement_id, correlation_id=""):
    versao = _versao_vigente(inscricao.edital_id)
    with command_context() as agora:
        if not recebe_inscricoes(
            status=inscricao.edital.status, conteudo=versao.content, agora=agora
        ):
            raise DomainError(
                "registration_closed", "Esta seleção não está recebendo inscrições.", 409
            )
        if inscricao.status != Inscricao.Status.RASCUNHO:
            raise DomainError(
                "submission_is_final", "Uma inscrição enviada não aceita alterações.", 409
            )
        documento = DocumentoSubmetido.objects.filter(
            inscricao=inscricao, requirement_id=requirement_id
        ).first()
        if documento is None:
            raise DomainError("not_found", "Recurso não encontrado.", 404)
        documento.arquivo.delete(save=False)
        documento.delete()
        record_event(
            actor=ator_do_candidato(identidade, inscricao.edital),
            permission=REMOVER,
            operation="REMOVER",
            aggregate=inscricao,
            now=agora,
            correlation_id=correlation_id,
            reason=f"requisito {requirement_id}",
        )


def descartes_por_mudanca_de_modalidade(conteudo, inscricao, modality_id) -> list[dict]:
    """O que deixaria de ser exigido se a modalidade mudasse — e por isso seria descartado.

    Existe para que a confirmação possa **enumerar** o que se perde antes de perder (FR-031).
    Descartar em silêncio e reaproveitar em silêncio são os dois erros simétricos; a lista é o que
    permite não cometer nenhum dos dois.
    """
    if str(modality_id or "") == str(inscricao.modality_id or ""):
        return []
    depois = {
        str(requisito["id"])
        for requisito in aplicaveis(
            conteudo.get("documentRequirements") or [],
            profile_id=str(inscricao.profile_id),
            modality_id=str(modality_id) if modality_id else None,
        )
    }
    enviados = {
        str(documento.requirement_id): documento
        for documento in DocumentoSubmetido.objects.filter(inscricao=inscricao)
    }
    por_id = {
        str(requisito["id"]): requisito
        for requisito in conteudo.get("documentRequirements") or []
    }
    return [
        {
            "requisito": por_id.get(requirement_id, {}).get("name", ""),
            "arquivo": documento.nome_original,
        }
        for requirement_id, documento in enviados.items()
        if requirement_id not in depois
    ]


def descartar_inaplicaveis(*, identidade, inscricao, correlation_id=""):
    """Remove o que deixou de ser exigido depois de a modalidade mudar.

    Roda **depois** da gravação, e recalcula a aplicabilidade sobre a inscrição já atualizada: é a
    mesma função que decide o que a tela pede, e por isso não há como as duas divergirem. Cada
    remoção é auditada como qualquer outra.
    """
    conteudo = _versao_vigente(inscricao.edital_id).content
    aplicaveis_agora = {
        str(requisito["id"]) for requisito in requisitos_da_inscricao(conteudo, inscricao)
    }
    descartados = []
    for documento in DocumentoSubmetido.objects.filter(inscricao=inscricao):
        if str(documento.requirement_id) in aplicaveis_agora:
            continue
        remover_documento(
            identidade=identidade,
            inscricao=inscricao,
            requirement_id=documento.requirement_id,
            correlation_id=correlation_id,
        )
        descartados.append(str(documento.requirement_id))
    return descartados
