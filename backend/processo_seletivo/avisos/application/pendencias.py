"""O aviso de pendência documental: quem o gesto alcança, e o gesto que o grava (134).

**A quinta situação da FR-084 da `010`, e nenhuma linha que envie.** O gesto grava um aviso da
`066` por pessoa e responde; quem envia é o despacho da `066`, num timer (FR-4619). Não há
`send_mail` aqui — a guarda `tests/test_situacoes_de_mensagem.py` o confere —, e nada aqui grava
`ComunicacaoEmitida`, vencimento ou conferência (FR-4618).

**Por gesto, e nunca por evento** (FR-4604). Registrar uma pendência não chama este módulo: quem
chama é a tela de condução, quando alguém que pode conferir pede *"Avisar as pessoas com pendência
nesta chamada"* (2ª decisão do usuário, 08/11/2026).

**A mesma regra para a prévia e para o gesto** (FR-4605). `selecionar` é o que a tela mostra antes
do botão, e o gesto a relê sob a trava do Processo: dois gestos simultâneos se enfileiram, e o
segundo encontra os avisos do primeiro e não repete ninguém no dia (FR-4611).
"""

from dataclasses import dataclass, field
from datetime import datetime, time
from zoneinfo import ZoneInfo

from django.conf import settings
from django.utils import timezone

from processo_seletivo.avisos.application.comando import (
    nao_encontrado,
    recusar_processo_em_estado_final,
    recusar_se_desabilitado,
)
from processo_seletivo.avisos.domain import nomes
from processo_seletivo.avisos.domain import pendencia as texto
from processo_seletivo.shared.api.problems import DomainError

# --- As exclusões, na ordem em que se aplicam (FR-4606 a FR-4608) ---------------------------------

COM_DESFECHO = "desfecho registrado"
NAO_COMUNICADA = "convocação ainda não comunicada"
VENCIDA = "vencimento decorrido"
COMPLEMENTADA = "documento reenviado, aguardando conferência"
JA_AVISADA_HOJE = "já avisada hoje"
SEM_ENDERECO = "sem endereço"

#: A ordem em que a tela e a trilha as listam.
EXCLUSOES = (COM_DESFECHO, NAO_COMUNICADA, VENCIDA, COMPLEMENTADA, JA_AVISADA_HOJE, SEM_ENDERECO)


@dataclass
class Pessoa:
    """Uma convocação vigente do recorte com pendência — ou com pendência já complementada."""

    convocacao: object
    raiz: object
    inscricao: object
    pendentes: list
    endereco: str = ""
    exclusao: str = ""

    @property
    def alcancada(self):
        return not self.exclusao


@dataclass
class Selecao:
    """O que o gesto alcançaria agora: quem recebe, e quem fica de fora, por motivo."""

    pessoas: list = field(default_factory=list)

    @property
    def alcancadas(self):
        return [pessoa for pessoa in self.pessoas if pessoa.alcancada]

    def exclusoes(self):
        """`[(motivo, quantas)]`, só os motivos que ocorreram, na ordem de `EXCLUSOES`."""
        contagem = {}
        for pessoa in self.pessoas:
            if pessoa.exclusao:
                contagem[pessoa.exclusao] = contagem.get(pessoa.exclusao, 0) + 1
        return [(motivo, contagem[motivo]) for motivo in EXCLUSOES if motivo in contagem]

    def resumo(self):
        return {
            "alcancadas": len(self.alcancadas),
            "exclusoes": [{"motivo": m, "quantas": q} for m, q in self.exclusoes()],
        }


def inicio_do_dia(agora):
    """O começo do dia local da instalação: o "por dia" do limite é o do calendário."""
    fuso = ZoneInfo(settings.TIME_ZONE)
    dia = timezone.localtime(agora, fuso).date()
    return datetime.combine(dia, time.min, tzinfo=fuso)


def _de_modalidade(item):
    """O item exigido por modalidade — `modalityId` ou `modalityCode` no requisito (3ª decisão)."""
    return item.modalidade_id is not None or bool(item.modalidade_codigo)


def _raiz(convocacao, por_id):
    """A raiz da chamada, subindo pela cadeia que o recorte já trouxe — sem consulta (D-003)."""
    atual = convocacao
    while atual.convocacao_anterior_id is not None and atual.convocacao_anterior_id in por_id:
        atual = por_id[atual.convocacao_anterior_id]
    return atual


def _raizes_avisadas_hoje(convocacoes, por_id, *, agora):
    """As raízes cuja chamada já teve aviso de pendência no dia local de hoje (FR-4606, D-003)."""
    from processo_seletivo.avisos.models import DestinatarioDoAviso

    avisadas = DestinatarioDoAviso.objects.filter(
        aviso__origem=nomes.PENDENCIA,
        aviso__solicitado_em__gte=inicio_do_dia(agora),
        convocacao_id__in=[c.id for c in convocacoes],
    ).values_list("convocacao_id", flat=True)
    return {_raiz(por_id[convocacao_id], por_id).id for convocacao_id in avisadas}


def selecionar(*, edital, perfil_id, marco_id, lista_id, agora):
    """Quem o gesto alcança neste recorte, agora, e quem fica de fora (FR-4606 a FR-4608).

    **Em número fixo de consultas**: as convocações do recorte com desfechos e comunicações, a
    leitura documental de todas as chamadas, as inscrições, os endereços e os avisos de hoje.
    Nenhuma é por pessoa.
    """
    from processo_seletivo.convocacao.application import documentos
    from processo_seletivo.convocacao.application.selectors import (
        convocacoes_do_recorte,
        desfecho_de,
        envio_de,
        vigentes,
    )
    from processo_seletivo.convocacao.domain import nomes as nomes_da_convocacao
    from processo_seletivo.convocacao.domain import prazo
    from processo_seletivo.identidade.application.endereco import enderecos_das_inscricoes
    from processo_seletivo.inscricoes.models import Inscricao

    todas = convocacoes_do_recorte(
        edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id
    )
    por_id = {c.id: c for c in todas}
    em_vigor = vigentes(todas)
    raizes = {c.id: _raiz(c, por_id) for c in em_vigor}
    leituras = documentos.leituras_por_chamada(set(raizes.values()))
    candidatas = []
    for vigente in em_vigor:
        leitura = leituras.get(raizes[vigente.id].id)
        if leitura is None:
            continue
        pendentes = [
            texto.Pendente(lido.nome, _de_modalidade(lido.item))
            for lido in leitura.pedidos
            if lido.estado == nomes_da_convocacao.ITEM_PENDENTE
        ]
        complementados = any(
            lido.estado == nomes_da_convocacao.ITEM_COMPLEMENTADO for lido in leitura.pedidos
        )
        # Quem nunca teve pendência não é "pessoa com pendência": não entra nem na contagem.
        if pendentes or complementados:
            candidatas.append((vigente, pendentes))
    if not candidatas:
        return Selecao()
    inscricoes = Inscricao.objects.in_bulk([c.inscricao_id for c, _ in candidatas])
    enderecos = enderecos_das_inscricoes(inscricoes.values())
    avisadas = _raizes_avisadas_hoje(todas, por_id, agora=agora)
    pessoas = []
    for vigente, pendentes in candidatas:
        enviado_em = envio_de(vigente)
        if desfecho_de(vigente) is not None:
            exclusao = COM_DESFECHO
        elif enviado_em is None:
            exclusao = NAO_COMUNICADA
        elif prazo.decorrido(vencimento=vigente.vencimento, enviado_em=enviado_em, agora=agora):
            exclusao = VENCIDA
        elif not pendentes:
            exclusao = COMPLEMENTADA
        elif raizes[vigente.id].id in avisadas:
            exclusao = JA_AVISADA_HOJE
        elif not enderecos.get(vigente.inscricao_id):
            exclusao = SEM_ENDERECO
        else:
            exclusao = ""
        pessoas.append(
            Pessoa(
                convocacao=vigente,
                raiz=raizes[vigente.id],
                inscricao=inscricoes[vigente.inscricao_id],
                pendentes=pendentes,
                endereco=enderecos.get(vigente.inscricao_id, ""),
                exclusao=exclusao,
            )
        )
    pessoas.sort(key=lambda pessoa: (pessoa.inscricao.protocolo, str(pessoa.inscricao.id)))
    return Selecao(pessoas)


def compor_texto(pessoa, *, edital, endereco_do_portal, agora):
    """O assunto e o corpo de uma pessoa (FR-4613 a FR-4617), com a unidade do Edital assinando."""
    from processo_seletivo.convocacao.application.comunicar import link_da_convocacao
    from processo_seletivo.convocacao.domain.prazo_apresentado import apresentar
    from processo_seletivo.unidades.application import identificacao

    unidade = identificacao.da_unidade(edital.institution_scope)
    vencimento = pessoa.convocacao.vencimento
    fuso = ZoneInfo(settings.TIME_ZONE)
    return texto.compor(
        instituicao=identificacao.SIGLA_DA_INSTITUICAO,
        edital=f"Edital {edital.number}/{edital.year}",
        pendentes=pessoa.pendentes,
        prazo=apresentar(vencimento, agora, fuso) if vencimento else None,
        link=link_da_convocacao(endereco_do_portal, pessoa.inscricao.id),
        atendimento=unidade.canal("a comissão do certame"),
        assinatura=unidade.rotulo,
    )


def previa(*, actor, edital, perfil_id, marco_id, lista_id, agora=None):
    """O que a tela de condução mostra antes do botão, ou `None` para quem não pode o gesto."""
    from processo_seletivo.avisos.application.comando import envio_habilitado
    from processo_seletivo.comissoes.domain.autorizacao import pode_conferir_documentos

    if pode_conferir_documentos(actor, edital, perfil_id) is None:
        return None
    selecao = selecionar(
        edital=edital,
        perfil_id=perfil_id,
        marco_id=marco_id,
        lista_id=lista_id,
        agora=agora or timezone.now(),
    )
    if not selecao.pessoas:
        return None
    return {**selecao.resumo(), "habilitado": envio_habilitado()}


def avisar_pendencias(
    *,
    actor,
    edital_id,
    perfil_id,
    marco_id,
    lista_id,
    endereco_do_portal,
    idempotency_key,
    correlation_id,
):
    """O gesto: grava um aviso de pendência por pessoa alcançada, e não envia nada (FR-4618).

    **A ordem dos comandos de aviso** (`comando_de_aviso`): a chave, a transação, a trava do
    Processo filtrado pelo escopo, a autorização, o estado do Processo e a reserva. A autorização é
    a da conferência (FR-3595 da `115`), e não a do aviso da `066`: quem confere decide (2ª
    decisão do usuário).
    """
    from processo_seletivo.avaliacoes.application.trilha import auditar
    from processo_seletivo.avisos.models import Aviso, DestinatarioDoAviso
    from processo_seletivo.comissoes.domain.autorizacao import pode_conferir_documentos
    from processo_seletivo.processos.models import Edital, ProcessoSeletivo
    from processo_seletivo.shared.application.commands import command_context
    from processo_seletivo.shared.idempotency import finish_batch, reservar

    recusar_se_desabilitado()
    if actor is None:
        raise nao_encontrado()
    with command_context() as agora:
        edital = (
            Edital.objects.filter(pk=edital_id, institution_scope=actor.institution_scope)
            .select_related("processo")
            .first()
        )
        if edital is None:
            raise nao_encontrado()
        processo = (
            ProcessoSeletivo.objects.select_for_update()
            .filter(pk=edital.processo_id, institution_scope=actor.institution_scope)
            .first()
        )
        if processo is None:
            raise nao_encontrado()
        base = pode_conferir_documentos(actor, edital, perfil_id)
        if base is None:
            raise nao_encontrado()
        recusar_processo_em_estado_final(processo)
        reserva, _ = reservar(
            actor=actor,
            operation=nomes.ATO_AVISAR_PENDENCIAS,
            key=idempotency_key,
            payload={
                "edital": str(edital.id),
                "marco": str(marco_id),
                "lista": str(lista_id or ""),
            },
        )
        if reserva.response_status is not None:
            return reserva.result_payload
        selecao = selecionar(
            edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id, agora=agora
        )
        alcancadas = selecao.alcancadas
        if not alcancadas:
            # Dentro da transação: a reserva desfaz junto, e o próximo clique, com outra lista,
            # não encontra uma chave "concluída" sem nada gravado (FR-4609).
            raise DomainError(
                nomes.AVISO_SEM_PENDENCIA_A_AVISAR,
                "Ninguém desta chamada pode receber o aviso de pendência agora: "
                + _por_que_ninguem(selecao),
                409,
            )
        avisos = []
        for pessoa in alcancadas:
            assunto, corpo = compor_texto(
                pessoa, edital=edital, endereco_do_portal=endereco_do_portal, agora=agora
            )
            aviso = Aviso(
                edital=edital,
                institution_scope=edital.institution_scope,
                origem=nomes.PENDENCIA,
                motivo=nomes.PRIMEIRO_AVISO,
                perfil_id=pessoa.convocacao.perfil_id,
                marco_id=pessoa.convocacao.marco_id,
                lista_id=pessoa.convocacao.lista_id,
                assunto=assunto,
                corpo=corpo,
                solicitado_por=actor.subject,
                solicitado_em=agora,
                idempotency_key=idempotency_key,
                correlation_id=correlation_id,
            )
            aviso.save()
            avisos.append(aviso)
        DestinatarioDoAviso.objects.bulk_create(
            DestinatarioDoAviso(
                aviso=aviso,
                inscricao=pessoa.inscricao,
                convocacao=pessoa.convocacao,
                elegibilidade=nomes.ELEGIVEL,
                endereco=pessoa.endereco,
            )
            for aviso, pessoa in zip(avisos, alcancadas, strict=True)
        )
        resumo = selecao.resumo()
        exclusoes = "; ".join(f"{m}: {q}" for m, q in selecao.exclusoes()) or "nenhuma"
        # **A trilha diz o que foi decidido, e não para quem** (FR-4620, FR-1278 da `066`): os
        # identificadores dos avisos, e não endereço nem nome.
        auditar(
            actor=actor,
            permissao=base.permissao,
            operation=nomes.OPERACAO_AVISAR_PENDENCIAS,
            aggregate=edital,
            now=agora,
            correlation_id=correlation_id,
            reason=(
                f"Aviso de pendência documental na chamada do marco {marco_id}"
                f"{f', lista {lista_id}' if lista_id else ''}: {len(avisos)} aviso(s) "
                f"registrado(s) para envio; fora: {exclusoes}."
            ),
            idempotency_key=idempotency_key,
            detalhe={
                "marco": str(marco_id),
                "lista": str(lista_id or ""),
                "avisos": [str(aviso.id) for aviso in avisos],
                **resumo,
            },
        )
        declarado = {**resumo, "avisos": [str(aviso.id) for aviso in avisos]}
        finish_batch(reserva, 201, declarado)
        return declarado


def _por_que_ninguem(selecao):
    partes = [f"{motivo}: {quantas}" for motivo, quantas in selecao.exclusoes()]
    if not partes:
        return "não há documento pendente."
    return "; ".join(partes) + "."


__all__ = [
    "COMPLEMENTADA",
    "COM_DESFECHO",
    "EXCLUSOES",
    "JA_AVISADA_HOJE",
    "NAO_COMUNICADA",
    "Pessoa",
    "SEM_ENDERECO",
    "Selecao",
    "VENCIDA",
    "avisar_pendencias",
    "compor_texto",
    "inicio_do_dia",
    "previa",
    "selecionar",
]
