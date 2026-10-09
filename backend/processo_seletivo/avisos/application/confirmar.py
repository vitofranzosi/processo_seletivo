"""A confirmação do aviso: grava o ato citado, o universo e o texto — e não envia nada (066).

**Nenhuma mensagem sai daqui** (`FR-1265`). A confirmação grava o aviso e os destinatários e
responde; quem envia é o despacho, fora da requisição. Mandar quinhentas mensagens dentro do clique
prenderia a tela até os 120 s do gunicorn, e uma falha no meio deixaria o aviso pela metade sem
ninguém para retomá-lo.

**Sob a trava do Processo, e com o universo relido** (`R-009`). A prévia mostrou uma lista; a
confirmação a lê de novo, sob a trava, e compara a assinatura. Se outra pessoa avisou as mesmas
publicações, ou uma retificação saiu, ou um desfecho foi registrado no meio, a confirmação é
recusada — e o operador vê a lista nova antes de mandar.
"""

from processo_seletivo.avisos.application import destinatarios, previa
from processo_seletivo.avisos.application.comando import comando_de_aviso, processo_do_ator
from processo_seletivo.avisos.domain import nomes
from processo_seletivo.avisos.domain.mensagem import validar_texto
from processo_seletivo.avisos.domain.variaveis import validar
from processo_seletivo.avisos.models import (
    Aviso,
    DestinatarioDoAviso,
    ModeloDeAviso,
    PublicacaoDoAviso,
)
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.idempotency import finish


def _recusar_defasada(universo, assinatura, *, motivo):
    if previa.assinatura(universo, motivo=motivo) != (assinatura or ""):
        raise DomainError(
            nomes.AVISO_PREVIA_DEFASADA,
            "A lista mudou desde a prévia — uma publicação, um desfecho ou um endereço. Confira a "
            "prévia nova antes de enviar.",
            409,
        )


def _recusar_sem_elegivel(universo):
    if not universo.recebem:
        raise DomainError(
            nomes.AVISO_SEM_ELEGIVEL,
            "Ninguém deste ato pode receber o aviso: não há destinatário elegível com endereço.",
            409,
        )


def _exigir_justificativa(justificativa):
    texto = (justificativa or "").strip()
    if not texto:
        raise DomainError(
            nomes.AVISO_JUSTIFICATIVA_OBRIGATORIA,
            "Avisar de novo sobre o que já foi avisado exige justificativa escrita.",
            422,
            campo="justificativa",
        )
    return texto


def _modelo_da_unidade(actor, modelo_id):
    if not modelo_id:
        return None
    modelo = ModeloDeAviso.objects.filter(
        pk=modelo_id, institution_scope=actor.institution_scope
    ).first()
    if modelo is None:
        raise DomainError(nomes.MODELO_NAO_ENCONTRADO, "Modelo de aviso não encontrado.", 404)
    return modelo


def _gravar(
    ctx,
    universo,
    *,
    actor,
    assunto,
    corpo,
    modelo,
    motivo,
    justificativa,
    anterior,
    idempotency_key,
    correlation_id,
):
    from processo_seletivo.avaliacoes.application.trilha import auditar

    aviso = Aviso(
        edital=universo.edital,
        institution_scope=universo.edital.institution_scope,
        origem=universo.origem,
        motivo=motivo,
        aviso_anterior=anterior,
        justificativa=justificativa,
        perfil_id=universo.perfil_id,
        marco_id=universo.marco_id,
        lista_id=universo.lista_id,
        natureza=universo.natureza,
        referencia_da_publicacao=universo.referencia,
        retificadora=universo.retificadora,
        assunto=assunto,
        corpo=corpo,
        modelo=modelo,
        solicitado_por=actor.subject,
        solicitado_em=ctx.now,
        idempotency_key=idempotency_key,
        correlation_id=correlation_id,
    )
    aviso.save()
    PublicacaoDoAviso.objects.bulk_create(
        PublicacaoDoAviso(aviso=aviso, publicacao=publicacao) for publicacao in universo.publicacoes
    )
    DestinatarioDoAviso.objects.bulk_create(
        DestinatarioDoAviso(
            aviso=aviso,
            inscricao=linha.inscricao,
            convocacao=linha.convocacao,
            elegibilidade=linha.elegibilidade,
            endereco=linha.endereco,
        )
        for linha in universo.linhas
    )
    contagens = universo.contagens()
    # **A trilha diz o que foi decidido, e não para quem**: os endereços já estão nos destinatários,
    # e copiá-los aqui aumentaria a exposição sem acrescentar prova (`FR-1278`).
    ato = (
        f"{len(universo.publicacoes)} publicação(ões) do marco {universo.marco_id}, "
        f"natureza {universo.natureza}"
        if universo.origem == nomes.RESULTADO
        else f"chamada do marco {universo.marco_id} publicada em {universo.referencia!r}"
    )
    auditar(
        actor=actor,
        permissao=ctx.base.permissao,
        operation=nomes.OPERACAO_CONFIRMAR,
        aggregate=aviso,
        now=ctx.now,
        correlation_id=correlation_id,
        reason=(
            f"Aviso {motivo} de {universo.origem} sobre {ato}: universo {contagens['universo']}, "
            f"com endereço {contagens['com_endereco']}, sem endereço {contagens['sem_endereco']}, "
            f"não elegíveis {contagens['nao_elegiveis']}."
            + (f" Justificativa: {justificativa}" if justificativa else "")
        ),
        idempotency_key=idempotency_key,
    )
    declarado = {"aviso": str(aviso.id), "destinatarios": contagens["com_endereco"]}
    finish(ctx.reserva, aviso, 201, declarado)
    return declarado


def confirmar_aviso_do_resultado(
    *,
    actor,
    processo_id,
    edital_id,
    marco_id,
    natureza,
    assunto,
    corpo,
    assinatura,
    enderecos,
    idempotency_key,
    correlation_id,
    modelo_id=None,
    justificativa="",
):
    """Confirma o aviso de resultado (`FR-1246` a `FR-1248`, `FR-1262`, `FR-1263`).

    **Sem justificativa, só as publicações que nenhum aviso citou.** Com ela, é o reenvio
    intencional da publicação inteira já avisada (`R-011`), e alcança todas as vigentes da natureza.
    """
    from processo_seletivo.processos.models import Edital

    processo_do_ator(actor, processo_id)
    justificativa = (justificativa or "").strip()
    motivo = nomes.REENVIO_JUSTIFICADO if justificativa else nomes.PRIMEIRO_AVISO
    payload = {
        "origem": nomes.RESULTADO,
        "marco": str(marco_id),
        "natureza": natureza,
        "assinatura": assinatura,
        "assunto": assunto,
        "corpo": corpo,
        "justificativa": justificativa,
    }
    with comando_de_aviso(
        actor=actor,
        processo_id=processo_id,
        origem=nomes.RESULTADO,
        operation=nomes.ATO_CONFIRMAR,
        payload=payload,
        idempotency_key=idempotency_key,
    ) as ctx:
        if ctx.repetido:
            return ctx.desfecho_anterior
        edital = Edital.objects.get(pk=edital_id, processo_id=processo_id)
        universo = destinatarios.universo_do_resultado(
            edital=edital, marco_id=marco_id, natureza=natureza, reenvio=bool(justificativa)
        )
        if not universo.publicacoes:
            raise DomainError(
                nomes.AVISO_SEM_PUBLICACAO_NOVA,
                "Todas as publicações vigentes desta natureza já foram avisadas. Avisar de novo "
                "exige justificativa escrita.",
                409,
            )
        _recusar_defasada(universo, assinatura, motivo=motivo)
        _recusar_sem_elegivel(universo)
        modelo = _modelo_da_unidade(actor, modelo_id)
        assunto_final, corpo_final = previa.congelar(
            universo, assunto=assunto, corpo=corpo, enderecos=enderecos
        )
        return _gravar(
            ctx,
            universo,
            actor=actor,
            assunto=assunto_final,
            corpo=corpo_final,
            modelo=modelo,
            motivo=motivo,
            justificativa=justificativa,
            anterior=_ultimo_aviso_das(universo.publicacoes) if justificativa else None,
            idempotency_key=idempotency_key,
            correlation_id=correlation_id,
        )


def _ultimo_aviso_das(publicacoes):
    """O aviso anterior que o reenvio justificado de uma publicação sucede (`R-011`)."""
    return (
        Aviso.objects.filter(publicacoes__publicacao__in=publicacoes)
        .order_by("-solicitado_em")
        .first()
    )


def confirmar_aviso_da_chamada(
    *,
    actor,
    processo_id,
    edital_id,
    marco_id,
    lista_id,
    comunicacao_id,
    assunto,
    corpo,
    assinatura,
    enderecos,
    idempotency_key,
    correlation_id,
    modelo_id=None,
    justificativa="",
):
    """Confirma o aviso de uma chamada comunicada por publicação (`FR-1251`, `D-003`)."""
    from processo_seletivo.processos.models import Edital

    processo_do_ator(actor, processo_id)
    justificativa = (justificativa or "").strip()
    payload = {
        "origem": nomes.CHAMADA,
        "marco": str(marco_id),
        "lista": str(lista_id) if lista_id else None,
        "comunicacao": str(comunicacao_id),
        "assinatura": assinatura,
        "assunto": assunto,
        "corpo": corpo,
        "justificativa": justificativa,
    }
    with comando_de_aviso(
        actor=actor,
        processo_id=processo_id,
        origem=nomes.CHAMADA,
        operation=nomes.ATO_CONFIRMAR,
        payload=payload,
        idempotency_key=idempotency_key,
    ) as ctx:
        if ctx.repetido:
            return ctx.desfecho_anterior
        edital = Edital.objects.get(pk=edital_id, processo_id=processo_id)
        universo = destinatarios.universo_da_chamada(
            edital=edital,
            marco_id=marco_id,
            lista_id=lista_id,
            comunicacao_id=comunicacao_id,
            agora=ctx.now,
        )
        if universo.ja_avisado and not justificativa:
            raise DomainError(
                nomes.AVISO_JUSTIFICATIVA_OBRIGATORIA,
                "Esta chamada já foi avisada. Avisar de novo exige justificativa escrita.",
                422,
                campo="justificativa",
            )
        motivo = nomes.REENVIO_JUSTIFICADO if universo.ja_avisado else nomes.PRIMEIRO_AVISO
        _recusar_defasada(universo, assinatura, motivo=motivo)
        _recusar_sem_elegivel(universo)
        modelo = _modelo_da_unidade(actor, modelo_id)
        assunto_final, corpo_final = previa.congelar(
            universo, assunto=assunto, corpo=corpo, enderecos=enderecos
        )
        anterior = None
        if universo.ja_avisado:
            anterior = (
                Aviso.objects.filter(
                    edital=edital,
                    origem=nomes.CHAMADA,
                    marco_id=marco_id,
                    lista_id=lista_id,
                    referencia_da_publicacao=universo.referencia,
                )
                .order_by("-solicitado_em")
                .first()
            )
        return _gravar(
            ctx,
            universo,
            actor=actor,
            assunto=assunto_final,
            corpo=corpo_final,
            modelo=modelo,
            motivo=motivo,
            justificativa=justificativa if universo.ja_avisado else "",
            anterior=anterior,
            idempotency_key=idempotency_key,
            correlation_id=correlation_id,
        )


def confirmar_reenvio(
    *,
    actor,
    aviso_id,
    motivo,
    assinatura,
    enderecos,
    idempotency_key,
    correlation_id,
    assunto="",
    corpo="",
    modelo_id=None,
    justificativa="",
):
    """O aviso filho (`R-011`, `FR-1264`).

    - `REENVIO_DE_FALHAS`: falha definitiva e expirada sem envio. A mensagem não saiu, não há o que
      justificar, e o texto é **o do anterior** — terminar de entregar o que foi confirmado.
    - `REENVIO_JUSTIFICADO`: indeterminada e interrompido antes do envio. Exige justificativa, e o
      texto é editável: a interrupção costuma ser por texto errado, e repetir o errado não serviria.
    """
    from django.utils import timezone

    from processo_seletivo.avisos.application.selectors import aviso_do_ator

    if motivo not in nomes.ALCANCE_DO_REENVIO:
        raise DomainError(nomes.AVISO_SEM_ATO, "Motivo de reenvio desconhecido.", 404)
    anterior = aviso_do_ator(actor, aviso_id)
    justificativa = (justificativa or "").strip()
    if motivo == nomes.REENVIO_JUSTIFICADO:
        justificativa = _exigir_justificativa(justificativa)
    payload = {
        "anterior": str(anterior.id),
        "motivo": motivo,
        "assinatura": assinatura,
        "assunto": assunto,
        "corpo": corpo,
        "justificativa": justificativa,
    }
    with comando_de_aviso(
        actor=actor,
        processo_id=anterior.edital.processo_id,
        origem=anterior.origem,
        operation=nomes.ATO_CONFIRMAR,
        payload=payload,
        idempotency_key=idempotency_key,
    ) as ctx:
        if ctx.repetido:
            return ctx.desfecho_anterior
        universo = destinatarios.universo_do_reenvio(anterior, motivo=motivo, agora=timezone.now())
        _recusar_defasada(universo, assinatura, motivo=motivo)
        _recusar_sem_elegivel(universo)
        if motivo == nomes.REENVIO_DE_FALHAS:
            assunto_final, corpo_final, modelo = anterior.assunto, anterior.corpo, anterior.modelo
        else:
            modelo = _modelo_da_unidade(actor, modelo_id)
            assunto_final, corpo_final = previa.congelar(
                universo, assunto=assunto, corpo=corpo, enderecos=enderecos
            )
        return _gravar(
            ctx,
            universo,
            actor=actor,
            assunto=assunto_final,
            corpo=corpo_final,
            modelo=modelo,
            motivo=motivo,
            justificativa=justificativa,
            anterior=anterior,
            idempotency_key=idempotency_key,
            correlation_id=correlation_id,
        )


def validar_texto_do_modelo(*, assunto, corpo):
    """O texto de um modelo: as mesmas regras de forma, e só a variável desconhecida o recusa."""
    assunto, corpo = validar_texto(assunto=assunto, corpo=corpo)
    validar(assunto, campo="assunto")
    validar(corpo, campo="corpo")
    return assunto, corpo


__all__ = [
    "confirmar_reenvio",
    "confirmar_aviso_da_chamada",
    "confirmar_aviso_do_resultado",
    "validar_texto_do_modelo",
]
