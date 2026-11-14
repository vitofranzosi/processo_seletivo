"""Depois da publicação, só ato individual: remarcar, incluir, cancelar (167, US5, `D-006`).

```text
comando_de_comissao(ator, processo, chave)   # trava o Processo, confere a base, reserva a chave
  ↓
trava da AgendaDaEtapa                       # sempre Processo → agenda (T-009)
  ↓
publicada? · motivo · horário · participação · livre      # contracts/recusas.md §5
  ↓
Agendamento atualizado                       # o estado corrente; o UNIQUE barra o horário duplo
  ↓
AtoDaAgenda (motivo, a linha da pessoa) + aviso + HorarioPublicado (substitui o anterior)
  ↓
documento do ato · revision + 1 · trilha com o anterior, o novo e o motivo
```

**Uma pessoa por ato, e só ela muda** (FR-7240): republicar a agenda inteira para mudar alguém
avisaria todo mundo de novo e reescreveria o que foi publicado. O ato grava a linha nova e aponta a
anterior em `substitui`; nada se apaga (FR-7241). O `Agendamento` é o estado corrente, e é a
unicidade dele que faz a segunda de duas remarcações para o mesmo horário perder (FR-7247).

**O motivo fica no ato e na trilha, e nunca no que é público** (FR-7246): nem no conteúdo, nem no
documento, nem no aviso. O conteúdo do ato individual é a linha da pessoa e uma nota do que mudou.

**A remarcação e a inclusão avisam só a pessoa afetada** (FR-7244), pela mesma função da
publicação; o cancelamento não avisa (o aviso de cancelamento seria situação nova de mensagem).
"""

import hashlib

from django.db import IntegrityError, transaction

from processo_seletivo.agendamento.application import leitura
from processo_seletivo.agendamento.application.avisar import Destino, criar_avisos
from processo_seletivo.agendamento.application.conferir import rotulo_do_edital
from processo_seletivo.agendamento.application.configurar import etapa_e_periodo
from processo_seletivo.agendamento.domain import conteudo as conteudo_
from processo_seletivo.agendamento.domain import nomes, recusas
from processo_seletivo.agendamento.domain.horarios import horario_curto
from processo_seletivo.agendamento.models import (
    Agendamento,
    AtoDaAgenda,
    DocumentoDoAtoDaAgenda,
    HorarioPublicado,
)
from processo_seletivo.auditoria.application import record_event
from processo_seletivo.comissoes.application import comando_de_comissao, nao_encontrado
from processo_seletivo.editais.domain.alcance import restrita
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.processos.models import Edital
from processo_seletivo.shared.canonical import canonical_bytes, canonical_sha256

OPERACOES = {
    nomes.REMARCACAO: "agenda:remarcar",
    nomes.INCLUSAO: "agenda:incluir",
    nomes.CANCELAMENTO: "agenda:cancelar",
}
TRILHA = {
    nomes.REMARCACAO: nomes.REMARCACAO_DA_AGENDA,
    nomes.INCLUSAO: nomes.INCLUSAO_NA_AGENDA,
    nomes.CANCELAMENTO: nomes.CANCELAMENTO_NA_AGENDA,
}


def _nome(inscricao):
    return inscricao.nome or inscricao.protocolo


def vigente_da_inscricao(agenda, inscricao_id):
    """O horário publicado que vale hoje para a pessoa, ou `None` (data-model, *Vigente*)."""
    return (
        HorarioPublicado.objects.filter(
            ato__agenda=agenda,
            inscricao_id=inscricao_id,
            situacao=nomes.AGENDADO,
            substituicoes__isnull=True,
        )
        .select_related("banca", "ato", "inscricao")
        .order_by("-ato__praticado_em", "-id")
        .first()
    )


def _estado(protocolo, banca, inicio):
    if inicio is None:
        return None
    return {"protocolo": protocolo, "banca": banca, "inicio": inicio.isoformat()}


def _nota(especie, publicado):
    if especie == nomes.REMARCACAO:
        return (
            f"Este horário substitui o publicado antes para esta inscrição, em "
            f"{horario_curto(publicado.inicio)}, que deixa de valer."
        )
    if especie == nomes.INCLUSAO:
        return "Horário de quem passou a participar da Etapa depois da publicação da agenda."
    return (
        "O horário abaixo deixa de valer: a inscrição saiu da agenda vigente, e o horário ficou "
        "livre."
    )


def _conteudo(*, edital, etapa, agenda, publicacao, especie, item, agora, nota):
    """A linha da pessoa como conteúdo público, com a unidade congelada da publicação."""
    cabecalho = leitura.conteudo_do_ato(publicacao)["cabecalho"]
    return conteudo_.compor(
        unidade=cabecalho.get("unidade"),
        edital=rotulo_do_edital(edital),
        etapa=etapa.get("name") or "",
        publicado_em=agora,
        signatario=None,
        veiculo="",
        forma=agenda.forma,
        duracao=agenda.duracao_minutos,
        bancas=[(banca.nome, banca.acesso) for banca in agenda.bancas_em_ordem],
        itens=[item],
        restrita=restrita(etapa),
        orientacoes=agenda.orientacoes,
        especie=especie,
        nota=nota,
    )


def _gravar_ato(*, agenda, edital, publicacao, especie, actor, agora, motivo, conteudo, chave):
    return AtoDaAgenda.objects.create(
        agenda=agenda,
        edital=edital,
        especie=especie,
        praticado_por=actor.subject,
        praticado_em=agora,
        motivo=motivo,
        # A unidade do ato é a da publicação, congelada: o ato individual não muda de cabeçalho.
        unidade_codigo=publicacao.unidade_codigo,
        unidade_sigla=publicacao.unidade_sigla,
        unidade_nome=publicacao.unidade_nome,
        unidade_cabecalho=publicacao.unidade_cabecalho,
        unidade_local=publicacao.unidade_local,
        conteudo_publico=canonical_bytes(conteudo),
        conteudo_publico_hash=canonical_sha256(conteudo),
        idempotency_key=chave or "",
    )


def _gravar_documento(ato, conteudo):
    """O documento do ato, gravado uma vez, como o da publicação (`D-012`, FR-7248)."""
    from processo_seletivo.agendamento.infrastructure.documento import render_agenda_pdf

    arquivo = render_agenda_pdf(conteudo)
    DocumentoDoAtoDaAgenda.objects.create(
        ato=ato, bytes=arquivo, documento_hash=hashlib.sha256(arquivo).hexdigest()
    )


def _subir_versao(agenda, actor, agora):
    anterior = agenda.revision
    agenda.revision += 1
    agenda.atualizada_por = actor.subject
    agenda.atualizada_em = agora
    agenda.save(update_fields=["revision", "atualizada_por", "atualizada_em"])
    return anterior


def _abrir(ctx, edital_id, etapa_id, inscricao_id):
    """O Edital, a Etapa, a agenda travada e publicada, e a inscrição — ou a recusa."""
    edital = Edital.objects.filter(pk=edital_id, processo=ctx.processo).first()
    if edital is None:
        raise nao_encontrado()
    etapa, _periodo = etapa_e_periodo(edital, etapa_id)
    agenda = leitura.agenda_da_etapa(edital, etapa_id, travar=True)
    if agenda is None:
        raise recusas.sem_configuracao()
    publicacao = leitura.publicacao(agenda)
    if publicacao is None:
        raise recusas.agenda_nao_publicada()
    inscricao = Inscricao.objects.filter(pk=inscricao_id, edital=edital).first()
    if inscricao is None:
        raise nao_encontrado()
    return edital, etapa, agenda, publicacao, inscricao


def _payload(edital, etapa_id, inscricao_id, motivo, banca_id=None, inicio=None):
    return {
        "edital": str(edital.id),
        "etapa": str(etapa_id),
        "inscricao": str(inscricao_id),
        "motivo": motivo,
        "banca": str(banca_id or ""),
        "inicio": inicio.isoformat() if inicio is not None else "",
    }


def _traduzir(erro):
    texto = str(erro)
    if "uq_agendamento_inscricao" in texto:
        # Outra sessão incluiu a mesma pessoa primeiro: para esta, ela já tem horário.
        return None
    return recusas.horario_ocupado()


def remarcar(**kwargs):
    """Leva a pessoa a um horário livre, com motivo (FR-7241). Devolve o `AtoDaAgenda`."""
    return _ato_de_horario(nomes.REMARCACAO, **kwargs)


def incluir(**kwargs):
    """Agenda quem passou a participar depois da publicação, com motivo (FR-7242)."""
    return _ato_de_horario(nomes.INCLUSAO, **kwargs)


def _ato_de_horario(
    especie,
    *,
    actor,
    edital,
    etapa_id,
    inscricao_id,
    banca_id,
    inicio,
    motivo,
    idempotency_key,
    correlation_id="",
):
    motivo = (motivo or "").strip()
    with comando_de_comissao(
        actor=actor,
        processo_id=edital.processo_id,
        operation=OPERACOES[especie],
        payload=_payload(edital, etapa_id, inscricao_id, motivo, banca_id, inicio),
        idempotency_key=idempotency_key,
    ) as ctx:
        if ctx.repetido:
            return AtoDaAgenda.objects.get(pk=ctx.desfecho_anterior["id"])
        agora = ctx.now
        edital, etapa, agenda, publicacao, inscricao = _abrir(
            ctx, edital.id, etapa_id, inscricao_id
        )
        if not motivo:
            raise recusas.motivo_ausente()
        if banca_id is None or inicio is None:
            raise recusas.horario_nao_escolhido()
        montagem = leitura.montagem(edital, etapa_id, agenda)
        publicado = vigente_da_inscricao(agenda, inscricao.id)
        participa = str(inscricao.id) in montagem.participacao.participantes
        if especie == nomes.REMARCACAO:
            if publicado is None:
                raise recusas.sem_horario_publicado(_nome(inscricao))
            if not participa:
                raise recusas.pessoa_nao_participa(
                    _nome(inscricao), montagem.participacao.motivo(inscricao.id)
                )
        else:
            if publicado is not None:
                raise recusas.ja_tem_horario_publicado(_nome(inscricao))
            if not participa:
                raise recusas.inclusao_de_quem_nao_participa(
                    _nome(inscricao), montagem.participacao.motivo(inscricao.id)
                )
        horario = next(
            (item for item in montagem.horarios if item.chave == (str(banca_id), inicio)), None
        )
        if horario is None:
            raise recusas.horario_inexistente()
        if (
            publicado is not None
            and str(publicado.banca_id) == horario.banca_id
            and publicado.inicio == horario.inicio
        ):
            raise recusas.mesmo_horario(_nome(inscricao))
        ocupante = montagem.ocupados.get(horario.chave)
        if ocupante is not None and ocupante.inscricao_id != inscricao.id:
            raise recusas.horario_ocupado()
        atual = montagem.por_inscricao.get(str(inscricao.id))
        try:
            with transaction.atomic():
                if atual is None:
                    Agendamento.objects.create(
                        agenda=agenda,
                        inscricao=inscricao,
                        banca_id=horario.banca_id,
                        inicio=horario.inicio,
                        fim=horario.fim,
                        origem=nomes.MANUAL,
                        feito_por=actor.subject,
                        feito_em=agora,
                    )
                else:
                    atual.banca_id = horario.banca_id
                    atual.inicio = horario.inicio
                    atual.fim = horario.fim
                    atual.origem = nomes.MANUAL
                    atual.feito_por = actor.subject
                    atual.feito_em = agora
                    atual.save()
        except IntegrityError as erro:
            recusa = _traduzir(erro)
            raise (recusa or recusas.ja_tem_horario_publicado(_nome(inscricao))) from erro
        banca = next(b for b in agenda.bancas_em_ordem if str(b.id) == horario.banca_id)
        item = conteudo_.Item(
            inicio=horario.inicio,
            fim=horario.fim,
            banca=banca.nome,
            nome=inscricao.nome or inscricao.protocolo or "",
            protocolo=inscricao.protocolo or "",
        )
        conteudo = _conteudo(
            edital=edital,
            etapa=etapa,
            agenda=agenda,
            publicacao=publicacao,
            especie=especie,
            item=item,
            agora=agora,
            nota=_nota(especie, publicado),
        )
        ato = _gravar_ato(
            agenda=agenda,
            edital=edital,
            publicacao=publicacao,
            especie=especie,
            actor=actor,
            agora=agora,
            motivo=motivo,
            conteudo=conteudo,
            chave=idempotency_key,
        )
        avisos = criar_avisos(
            especie=especie,
            destinos=[Destino(inscricao, banca, horario.inicio)],
            agenda=agenda,
            edital=edital,
            etapa=etapa.get("name") or "Etapa",
            rotulo_do_edital=rotulo_do_edital(edital),
            actor=actor,
            agora=agora,
            idempotency_key=idempotency_key,
            correlation_id=correlation_id,
        )
        HorarioPublicado.objects.create(
            ato=ato,
            inscricao=inscricao,
            situacao=nomes.AGENDADO,
            banca=banca,
            banca_nome=banca.nome,
            inicio=horario.inicio,
            fim=horario.fim,
            substitui=publicado,
            aviso=avisos.get(str(inscricao.id)),
        )
        _gravar_documento(ato, conteudo)
        revisao_anterior = _subir_versao(agenda, actor, agora)
        record_event(
            actor=actor,
            permission=ctx.base.permissao,
            operation=TRILHA[especie],
            aggregate=agenda,
            now=agora,
            correlation_id=correlation_id or f"agenda-{agenda.id}",
            # O motivo fica aqui e no ato, e nunca no que é público (FR-7246, FR-7256); a trilha
            # não leva e-mail nem endereço de sala.
            reason=motivo,
            previous_state="PUBLICADA",
            new_state="PUBLICADA",
            previous_revision=revisao_anterior,
            new_revision=agenda.revision,
            idempotency_key=idempotency_key or "",
            detalhe={
                "ato": str(ato.id),
                "motivo": motivo,
                "anterior": _estado(inscricao.protocolo, publicado.banca_nome, publicado.inicio)
                if publicado is not None
                else None,
                "posterior": _estado(inscricao.protocolo, banca.nome, horario.inicio),
                "avisos": len(avisos),
            },
        )
        ctx.concluir_sem_resultado(201, {"id": str(ato.id)})
        return ato


def cancelar(*, actor, edital, etapa_id, inscricao_id, motivo, idempotency_key, correlation_id=""):
    """Tira da agenda vigente quem deixou de participar, com motivo, sem apagar (FR-7243)."""
    motivo = (motivo or "").strip()
    especie = nomes.CANCELAMENTO
    with comando_de_comissao(
        actor=actor,
        processo_id=edital.processo_id,
        operation=OPERACOES[especie],
        payload=_payload(edital, etapa_id, inscricao_id, motivo),
        idempotency_key=idempotency_key,
    ) as ctx:
        if ctx.repetido:
            return AtoDaAgenda.objects.get(pk=ctx.desfecho_anterior["id"])
        agora = ctx.now
        edital, etapa, agenda, publicacao, inscricao = _abrir(
            ctx, edital.id, etapa_id, inscricao_id
        )
        if not motivo:
            raise recusas.motivo_ausente()
        publicado = vigente_da_inscricao(agenda, inscricao.id)
        if publicado is None:
            raise recusas.sem_horario_publicado(_nome(inscricao))
        participacao = leitura.participacao(edital, etapa_id)
        if str(inscricao.id) in participacao.participantes:
            raise recusas.cancelamento_de_quem_participa(_nome(inscricao))
        # O estado corrente perde a linha e o horário fica livre; o publicado continua no
        # append-only, e a trilha guarda o anterior (data-model, *Agendamento*).
        Agendamento.objects.filter(agenda=agenda, inscricao=inscricao).delete()
        item = conteudo_.Item(
            inicio=publicado.inicio,
            fim=publicado.fim,
            banca=publicado.banca_nome,
            nome=inscricao.nome or inscricao.protocolo or "",
            protocolo=inscricao.protocolo or "",
        )
        conteudo = _conteudo(
            edital=edital,
            etapa=etapa,
            agenda=agenda,
            publicacao=publicacao,
            especie=especie,
            item=item,
            agora=agora,
            nota=_nota(especie, publicado),
        )
        ato = _gravar_ato(
            agenda=agenda,
            edital=edital,
            publicacao=publicacao,
            especie=especie,
            actor=actor,
            agora=agora,
            motivo=motivo,
            conteudo=conteudo,
            chave=idempotency_key,
        )
        HorarioPublicado.objects.create(
            ato=ato,
            inscricao=inscricao,
            situacao=nomes.CANCELADO,
            substitui=publicado,
        )
        _gravar_documento(ato, conteudo)
        revisao_anterior = _subir_versao(agenda, actor, agora)
        record_event(
            actor=actor,
            permission=ctx.base.permissao,
            operation=TRILHA[especie],
            aggregate=agenda,
            now=agora,
            correlation_id=correlation_id or f"agenda-{agenda.id}",
            reason=motivo,
            previous_state="PUBLICADA",
            new_state="PUBLICADA",
            previous_revision=revisao_anterior,
            new_revision=agenda.revision,
            idempotency_key=idempotency_key or "",
            detalhe={
                "ato": str(ato.id),
                "motivo": motivo,
                "anterior": _estado(inscricao.protocolo, publicado.banca_nome, publicado.inicio),
                "posterior": None,
                "avisos": 0,
            },
        )
        ctx.concluir_sem_resultado(201, {"id": str(ato.id)})
        return ato
