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
from processo_seletivo.inscricoes.storage import ArmazenamentoPrivado
from processo_seletivo.portal.identidade import normalizar_cpf
from processo_seletivo.publicacoes.application import selectors
from processo_seletivo.seguranca.domain import Actor
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.application.commands import after_commit, command_context
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


def gravar_dados(*, identidade, inscricao, dados, descartes_confirmados=(), correlation_id=""):
    """Grava os campos da tela, sem `Salvar` — e o descarte, quando houver, vai junto (FR-041).

    **Um comando, uma transação.** Mudar a modalidade e descartar o que ela torna inaplicável são
    a mesma decisão da pessoa, e separá-las em duas transações deixa o meio termo alcançável: a
    modalidade nova gravada com descarte pela metade, ou o descarte feito sobre uma gravação que
    não aconteceu. A Inscrição é travada, os dois efeitos acontecem juntos, e os arquivos só saem
    do disco depois do commit.

    **O descarte é o confirmado, e nada além.** A lista recomputada sob trava tem de coincidir com
    a que a pessoa viu; divergindo, a confirmação está velha e a gravação é recusada em vez de
    apagar o que ninguém confirmou.
    """
    versao = _versao_vigente(inscricao.edital_id)
    conteudo = versao.content
    with command_context() as agora:
        travada = _rascunho_travado(inscricao, conteudo, agora)
        modalidade = _modalidade_escolhida(conteudo, travada.profile_id, dados.get("modality_id"))
        inaplicaveis = _documentos_inaplicaveis(conteudo, travada, modalidade)
        if set(inaplicaveis) != {str(item) for item in descartes_confirmados}:
            raise DomainError(
                "discard_not_confirmed",
                "A lista de documentos a descartar mudou. Revise a alteração antes de confirmar.",
                409,
            )
        caminhos = []
        for documento in DocumentoSubmetido.objects.filter(
            inscricao=travada, requirement_id__in=inaplicaveis
        ):
            caminhos.append(documento.arquivo.name)
            documento.delete()
            record_event(
                actor=ator_do_candidato(identidade, travada.edital),
                permission=REMOVER,
                operation="REMOVER",
                aggregate=travada,
                now=agora,
                correlation_id=correlation_id,
                reason=f"requisito {documento.requirement_id}",
            )
        compare_and_swap(
            Inscricao.objects,
            pk=travada.pk,
            expected_revision=travada.revision,
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
        travada.refresh_from_db()
        record_event(
            actor=ator_do_candidato(identidade, travada.edital),
            permission=GRAVAR,
            operation="GRAVAR",
            aggregate=travada,
            now=agora,
            correlation_id=correlation_id,
        )
        for caminho in caminhos:
            _apagar_depois_do_commit(caminho)
        return travada


def _documentos_inaplicaveis(conteudo, inscricao, modalidade_nova) -> list[str]:
    """Os requisitos já enviados que a modalidade nova deixaria de exigir.

    **Só quando a modalidade muda.** Um requisito que a Retificação removeu ou restringiu também
    fica inaplicável, e apagá-lo aqui seria apagar arquivo em silêncio a cada `Continuar` — sem
    que a pessoa tivesse mudado nada. A reconciliação por Retificação é decisão explícita e
    pertence ao aviso da entrega 5 (FR-059).
    """
    if str(modalidade_nova or "") == str(inscricao.modality_id or ""):
        return []
    depois = {
        str(requisito["id"])
        for requisito in aplicaveis(
            conteudo.get("documentRequirements") or [],
            profile_id=str(inscricao.profile_id),
            modality_id=str(modalidade_nova) if modalidade_nova else None,
        )
    }
    return [
        str(documento.requirement_id)
        for documento in DocumentoSubmetido.objects.filter(inscricao=inscricao)
        if str(documento.requirement_id) not in depois
    ]


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


def _rascunho_travado(inscricao, conteudo, agora):
    """A Inscrição relida sob trava, e as recusas conferidas sobre o estado **de agora**.

    Sem a releitura, o estado vem do objeto que a view carregou antes: uma requisição que começou
    antes do envio alteraria arquivos depois dele, porque a checagem responderia por um `status`
    obsoleto. A trava também serializa duas requisições do mesmo candidato — dois envios, ou um
    envio e uma mudança de modalidade — em vez de deixá-las se atropelarem.
    """
    travada = (
        Inscricao.objects.select_for_update().select_related("edital").get(pk=inscricao.pk)
    )
    if not recebe_inscricoes(status=travada.edital.status, conteudo=conteudo, agora=agora):
        raise DomainError(
            "registration_closed", "Esta seleção não está recebendo inscrições.", 409
        )
    if travada.status != Inscricao.Status.RASCUNHO:
        raise DomainError(
            "submission_is_final", "Uma inscrição enviada não aceita alterações.", 409
        )
    return travada


def _apagar_depois_do_commit(caminho):
    """O arquivo sai do disco **só** quando o banco confirma.

    O sistema de arquivos não participa da transação: apagar antes do commit significa que um
    rollback devolve o registro apontando para um arquivo que não existe mais. Adiar é o que faz
    o disco seguir o banco, e não o contrário.
    """
    if not caminho:
        return
    armazenamento = ArmazenamentoPrivado()
    after_commit(lambda: armazenamento.delete(caminho))


def anexar_documento(*, identidade, inscricao, requirement_id, arquivo, correlation_id=""):
    """Guarda um arquivo para um requisito — imediatamente, e sem `Salvar` (FR-041).

    Três recusas antes de qualquer escrita, e a ordem importa: fora do período não se anexa nada;
    requisito que não se aplica àquela inscrição não é aceito **ainda que a tela nunca o tenha
    oferecido** (FR-044); e o arquivo é conferido por conteúdo antes de tocar o disco.

    **A ordem entre disco e banco também é regra.** O arquivo novo é escrito primeiro e removido
    no `except` se a transação não chegar ao fim; o registro é atualizado no lugar, sem apagar e
    reinserir; e o arquivo anterior só sai do disco depois do commit. As três coisas juntas são o
    que impede um rollback deixar registro apontando para arquivo inexistente — ou arquivo órfão
    que ninguém mais alcança.
    """
    versao = _versao_vigente(inscricao.edital_id)
    conteudo = versao.content
    with command_context() as agora:
        travada = _rascunho_travado(inscricao, conteudo, agora)
        if _requisito_aplicavel(conteudo, travada, requirement_id) is None:
            raise DomainError("not_found", "Recurso não encontrado.", 404)
        aceitar(
            arquivo,
            nome_original=arquivo.name,
            limite_em_bytes=settings.ARQUIVOS_CANDIDATOS_LIMITE_BYTES,
        )
        conteudo_hash = resumo(arquivo)
        documento = DocumentoSubmetido.objects.filter(
            inscricao=travada, requirement_id=requirement_id
        ).first() or DocumentoSubmetido(inscricao=travada, requirement_id=requirement_id)
        caminho_anterior = documento.arquivo.name if documento.pk else ""
        documento.arquivo.save(arquivo.name, arquivo, save=False)
        caminho_novo = documento.arquivo.name
        try:
            documento.nome_original = arquivo.name[:255]
            documento.tamanho = arquivo.size
            documento.content_hash = conteudo_hash
            documento.uploaded_at = agora
            documento.save()
            record_event(
                actor=ator_do_candidato(identidade, travada.edital),
                permission=ANEXAR,
                operation="ANEXAR",
                aggregate=travada,
                now=agora,
                correlation_id=correlation_id,
                # O requisito atendido, e **não** o nome do arquivo: nome de arquivo carrega dado
                # pessoal com frequência, e a auditoria não precisa dele para responder o que
                # aconteceu (FR-078).
                reason=f"requisito {requirement_id}",
            )
        except Exception:
            ArmazenamentoPrivado().delete(caminho_novo)
            raise
        if caminho_anterior and caminho_anterior != caminho_novo:
            _apagar_depois_do_commit(caminho_anterior)
        return documento


def remover_documento(*, identidade, inscricao, requirement_id, correlation_id=""):
    versao = _versao_vigente(inscricao.edital_id)
    with command_context() as agora:
        travada = _rascunho_travado(inscricao, versao.content, agora)
        documento = DocumentoSubmetido.objects.filter(
            inscricao=travada, requirement_id=requirement_id
        ).first()
        if documento is None:
            raise DomainError("not_found", "Recurso não encontrado.", 404)
        caminho = documento.arquivo.name
        documento.delete()
        record_event(
            actor=ator_do_candidato(identidade, travada.edital),
            permission=REMOVER,
            operation="REMOVER",
            aggregate=travada,
            now=agora,
            correlation_id=correlation_id,
            reason=f"requisito {requirement_id}",
        )
        # Depois do commit: se a transação voltar atrás, o registro volta — e o arquivo precisa
        # continuar lá para que ele não aponte para o vazio.
        _apagar_depois_do_commit(caminho)


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
            "id": requirement_id,
            "requisito": por_id.get(requirement_id, {}).get("name", ""),
            "arquivo": documento.nome_original,
        }
        for requirement_id, documento in enviados.items()
        if requirement_id not in depois
    ]
