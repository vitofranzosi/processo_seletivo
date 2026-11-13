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

**E o despacho a relê de novo, antes de cada tentativa** (FR-4623, D-011). Entre o gesto e o envio
passam minutos, ou horas, com retentativa e chave religada: a pessoa reenvia, a comissão desfecha, o
prazo vence. `motivo_para_nao_enviar` é a mesma regra lida para uma pessoa só, e o aviso que ela
recusa é interrompido em vez de enviado.
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
from processo_seletivo.convocacao.domain import vocabulario_dos_documentos
from processo_seletivo.shared.api.problems import DomainError

# --- As exclusões, na ordem em que se aplicam (FR-4606 a FR-4608) ---------------------------------

COM_DESFECHO = "desfecho registrado"
NAO_COMUNICADA = "convocação ainda não comunicada"
VENCIDA = "vencimento decorrido"
# O nome da página de documentos (154, FR-6212). O texto gravado nos avisos já feitos — no `reason`
# e nas `exclusoes` do `detalhe` — fica com o do dia (FR-6215): nada o relê para comparar.
COMPLEMENTADA = "documento " + vocabulario_dos_documentos.reenviado_em_frase()
JA_AVISADA_HOJE = "já avisada hoje"
SEM_ENDERECO = "sem endereço"

#: A ordem em que a tela e a trilha as listam.
EXCLUSOES = (COM_DESFECHO, NAO_COMUNICADA, VENCIDA, COMPLEMENTADA, JA_AVISADA_HOJE, SEM_ENDERECO)

# --- O que o despacho encontra antes de enviar, além das exclusões do gesto (FR-4623) -------------

CORRIGIDA = "convocação corrigida depois do aviso"
SEM_PENDENCIA = "nenhum documento pendente desde o aviso"
LISTA_MUDOU = "os documentos pendentes mudaram desde o aviso"


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


def proximo_dia_do_pedido(agora):
    """O dia local em que um novo pedido de aviso pode ser feito por quem já foi avisada hoje.

    Só para o texto (157, FR-6541, UX-650): nada é agendado para esse dia, e o pedido continua
    sendo um gesto de quem confere.
    """
    from datetime import timedelta

    return (inicio_do_dia(agora) + timedelta(days=1)).date()


def inicio_do_dia(agora):
    """O começo do dia local da instalação: o "por dia" do limite é o do calendário."""
    fuso = ZoneInfo(settings.TIME_ZONE)
    dia = timezone.localtime(agora, fuso).date()
    return datetime.combine(dia, time.min, tzinfo=fuso)


def _de_modalidade(item):
    """O item exigido por modalidade — `modalityId` ou `modalityCode` no requisito (3ª decisão)."""
    return item.modalidade_id is not None or bool(item.modalidade_codigo)


def _pendentes(leitura):
    """Os itens pendentes de uma chamada, como o texto os trata, e se algum foi complementado."""
    from processo_seletivo.convocacao.domain import nomes as nomes_da_convocacao

    if leitura is None:
        return [], False
    pendentes = [
        texto.Pendente(lido.nome, _de_modalidade(lido.item))
        for lido in leitura.pedidos
        if lido.estado == nomes_da_convocacao.ITEM_PENDENTE
    ]
    complementados = any(
        lido.estado == nomes_da_convocacao.ITEM_COMPLEMENTADO for lido in leitura.pedidos
    )
    return pendentes, complementados


def _raizes_avisadas_hoje(convocacoes, *, agora):
    """As raízes cuja chamada já teve aviso de pendência no dia local de hoje (FR-4606, D-003).

    **A raiz pela regra da condução** (`documentos.raizes_das`), e não por uma subida própria: a
    sucessora corrigida e a convocação que ela sucede precisam cair na mesma chamada que a tela
    mostra. O aviso que o próprio despacho interrompeu não conta (D-011): nada saiu, e o gesto
    seguinte, no mesmo dia, compõe o texto com o que estiver pendente então.
    """
    from processo_seletivo.avisos.models import DestinatarioDoAviso
    from processo_seletivo.convocacao.application import documentos

    por_id = {c.id: c for c in convocacoes}
    avisadas = set(
        DestinatarioDoAviso.objects.filter(
            aviso__origem=nomes.PENDENCIA,
            aviso__solicitado_em__gte=inicio_do_dia(agora),
            convocacao_id__in=list(por_id),
        )
        .exclude(aviso__interrupcao__interrompido_por=nomes.SUJEITO_DO_DESPACHO)
        .values_list("convocacao_id", flat=True)
    )
    if not avisadas:
        return set()
    raizes = documentos.raizes_das(por_id[convocacao_id] for convocacao_id in avisadas)
    return {raiz.id for raiz in raizes.values()}


def selecionar(*, edital, perfil_id, marco_id, lista_id, agora, conducao=None, convocacao_id=None):
    """Quem o gesto alcança neste recorte, agora, e quem fica de fora (FR-4606 a FR-4608).

    **Em número fixo de consultas**: as convocações do recorte com desfechos e comunicações, a
    leitura documental de todas as chamadas, as inscrições, os endereços e os avisos de hoje.
    Nenhuma é por pessoa.

    `conducao` é o que a tela de condução já leu — `{"convocacoes", "raizes", "leituras"}`, as
    três da mesma fotografia —, para que a prévia não leia o recorte e as listas uma segunda vez a
    cada abertura da tela. O gesto não a passa: ele relê tudo sob a trava.

    `convocacao_id` é o **recorte de uma pessoa** (157, FR-6537; FR-4603 da `134`, revista): a
    convocação vigente dela. A regra é a mesma — as exclusões, o dia, os avisados hoje pelo recorte
    inteiro —, só a seleção para nela.
    """
    from processo_seletivo.convocacao.application import documentos
    from processo_seletivo.convocacao.application.selectors import (
        convocacoes_do_recorte,
        vigentes,
    )

    if conducao is None:
        todas = convocacoes_do_recorte(
            edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id
        )
        em_vigor = vigentes(todas)
        raizes = documentos.raizes_das(em_vigor)
        leituras = documentos.leituras_por_chamada(set(raizes.values()))
    else:
        todas = conducao["convocacoes"]
        em_vigor = vigentes(todas)
        raizes, leituras = conducao["raizes"], conducao["leituras"]
    if convocacao_id is not None:
        em_vigor = [vigente for vigente in em_vigor if vigente.id == convocacao_id]
    candidatas = []
    for vigente in em_vigor:
        pendentes, complementados = _pendentes(leituras.get(raizes[vigente.id].id))
        # Quem nunca teve pendência não é "pessoa com pendência": não entra nem na contagem.
        if pendentes or complementados:
            candidatas.append((vigente, pendentes))
    if not candidatas:
        return Selecao()
    return _selecao(candidatas, raizes, todas=todas, agora=agora)


def _exclusao_da_convocacao(convocacao, pendentes, *, agora):
    """O motivo, lido da convocação e da lista, que tira a pessoa do aviso — ou `""`.

    É a parte da regra que não depende do recorte inteiro: a mesma para o gesto e para o despacho.
    """
    from processo_seletivo.convocacao.application.selectors import desfecho_de, envio_de
    from processo_seletivo.convocacao.domain import prazo

    enviado_em = envio_de(convocacao)
    if desfecho_de(convocacao) is not None:
        return COM_DESFECHO
    if enviado_em is None:
        return NAO_COMUNICADA
    if prazo.decorrido(vencimento=convocacao.vencimento, enviado_em=enviado_em, agora=agora):
        return VENCIDA
    if not pendentes:
        return COMPLEMENTADA
    return ""


def _selecao(candidatas, raizes, *, todas, agora):
    from processo_seletivo.identidade.application.endereco import enderecos_das_inscricoes
    from processo_seletivo.inscricoes.models import Inscricao

    inscricoes = Inscricao.objects.in_bulk([c.inscricao_id for c, _ in candidatas])
    enderecos = enderecos_das_inscricoes(inscricoes.values())
    avisadas = _raizes_avisadas_hoje(todas, agora=agora)
    pessoas = []
    for vigente, pendentes in candidatas:
        exclusao = _exclusao_da_convocacao(vigente, pendentes, agora=agora)
        if not exclusao and raizes[vigente.id].id in avisadas:
            exclusao = JA_AVISADA_HOJE
        elif not exclusao and not enderecos.get(vigente.inscricao_id):
            exclusao = SEM_ENDERECO
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


def motivo_para_nao_enviar(destinatario, *, agora):
    """Por que o aviso de pendência desta pessoa não deve sair agora — ou `""` (FR-4623, D-011).

    **A regra do gesto, relida no envio**, para uma pessoa só: o despacho a chama sob a trava do
    aviso, antes de cada tentativa. Além das exclusões do gesto, duas que só o tempo produz: a
    convocação foi corrigida (o vencimento do texto pode não ser mais o dela), ou a lista de
    pendentes já não é a que o texto congelou. O limite do dia e o endereço não se relêem: o
    primeiro é do gesto, e o segundo foi gravado no destinatário.
    """
    from processo_seletivo.avisos.domain.variaveis import escapar
    from processo_seletivo.convocacao.application import documentos
    from processo_seletivo.convocacao.models import Convocacao

    convocacao = Convocacao.objects.prefetch_related("desfechos", "comunicacoes", "sucessoras").get(
        pk=destinatario.convocacao_id
    )
    if convocacao.sucessoras.all():
        return CORRIGIDA
    raiz = documentos.raizes_das([convocacao])[convocacao.id]
    pendentes, _ = _pendentes(documentos.leituras_por_chamada([raiz]).get(raiz.id))
    exclusao = _exclusao_da_convocacao(convocacao, pendentes, agora=agora)
    if exclusao == COMPLEMENTADA:
        return SEM_PENDENCIA
    if exclusao:
        return exclusao
    # **O parágrafo inteiro, e não cada nome**: o de modalidade é uma contagem, e um documento a
    # mais ou a menos muda a linha dela sem mudar nome nenhum.
    if escapar(texto.bloco_dos_documentos(pendentes)) not in destinatario.aviso.corpo.split("\n\n"):
        return LISTA_MUDOU
    return ""


def compor_texto(pessoa, *, edital, unidade, endereco_do_portal, agora):
    """O assunto e o corpo de uma pessoa (FR-4613 a FR-4617), com a unidade do Edital assinando.

    `unidade` vem de quem chama, lida uma vez para o gesto inteiro, e não uma vez por pessoa.
    """
    from processo_seletivo.convocacao.application.comunicar import link_da_convocacao
    from processo_seletivo.convocacao.domain.prazo_apresentado import apresentar
    from processo_seletivo.unidades.application import identificacao

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


def previa(*, actor, edital, perfil_id, marco_id, lista_id, agora=None, conducao=None):
    """O que a tela de condução mostra antes do botão, ou `None` para quem não pode o gesto.

    `conducao`, quando a tela o passa, é o que ela já leu do recorte (ver `selecionar`).
    """
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
        conducao=conducao,
    )
    if not selecao.pessoas:
        return None
    return {
        **selecao.resumo(),
        "habilitado": envio_habilitado(),
        # **O motivo de cada chamada, da mesma seleção** (143, FR-5017): a tela da condução diz,
        # no cartão de cada pessoa, se o gesto a alcançaria agora ou por que não. Uma segunda
        # seleção na interface seria a regra escrita duas vezes. `""` é alcançada.
        "por_chamada": {str(pessoa.raiz.id): pessoa.exclusao for pessoa in selecao.pessoas},
    }


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
    convocacao_id=None,
):
    """O gesto: grava um aviso de pendência por pessoa alcançada, e não envia nada (FR-4618).

    Com `convocacao_id`, o **pedido de uma pessoa** (157, D-008; FR-4603 da `134`, revista): o
    mesmo comando, a mesma trava, a mesma autorização, o mesmo limite de um por dia — o lote e o
    pedido individual se enxergam, porque gravam o mesmo aviso. A recusa diz o motivo daquela
    pessoa, e a trilha diz que o recorte foi de uma pessoa (FR-4620 da `134`, acrescida).

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
    from processo_seletivo.unidades.application import identificacao

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
                **({"convocacao": str(convocacao_id)} if convocacao_id else {}),
            },
        )
        if reserva.response_status is not None:
            return reserva.result_payload
        selecao = selecionar(
            edital=edital,
            perfil_id=perfil_id,
            marco_id=marco_id,
            lista_id=lista_id,
            agora=agora,
            convocacao_id=convocacao_id,
        )
        alcancadas = selecao.alcancadas
        if not alcancadas and convocacao_id is not None:
            raise DomainError(
                nomes.AVISO_SEM_PENDENCIA_A_AVISAR, _por_que_nao_esta(selecao, agora=agora), 409
            )
        if not alcancadas:
            # Dentro da transação: a reserva desfaz junto, e o próximo clique, com outra lista,
            # não encontra uma chave "concluída" sem nada gravado (FR-4609).
            raise DomainError(
                nomes.AVISO_SEM_PENDENCIA_A_AVISAR,
                "Ninguém desta chamada pode receber o aviso de pendência agora: "
                + _por_que_ninguem(selecao),
                409,
            )
        unidade = identificacao.da_unidade(edital.institution_scope)
        avisos = []
        for pessoa in alcancadas:
            assunto, corpo = compor_texto(
                pessoa,
                edital=edital,
                unidade=unidade,
                endereco_do_portal=endereco_do_portal,
                agora=agora,
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
            avisos.append(aviso)
        # **Em lote**: o gesto segura a trava do Processo, e um INSERT por pessoa a seguraria por
        # uma ida ao banco a cada uma. O `id` é UUID gerado aqui, e o destinatário já o encontra.
        Aviso.objects.bulk_create(avisos)
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
                (
                    "Pedido de aviso de pendência documental de uma pessoa"
                    if convocacao_id
                    else "Aviso de pendência documental"
                )
                + f" na chamada do marco {marco_id}"
                f"{f', lista {lista_id}' if lista_id else ''}: {len(avisos)} aviso(s) "
                f"registrado(s) para envio; fora: {exclusoes}."
            ),
            idempotency_key=idempotency_key,
            detalhe={
                "marco": str(marco_id),
                "lista": str(lista_id or ""),
                "avisos": [str(aviso.id) for aviso in avisos],
                **resumo,
                **(
                    {"recorte": "pessoa", "convocacao": str(convocacao_id)}
                    if convocacao_id
                    else {"recorte": "chamada"}
                ),
            },
        )
        declarado = {**resumo, "avisos": [str(aviso.id) for aviso in avisos]}
        finish_batch(reserva, 201, declarado)
        return declarado


def _por_que_nao_esta(selecao, *, agora):
    """A recusa do pedido de uma pessoa: o motivo dela, e quando o tempo o resolve (FR-6541)."""
    if not selecao.pessoas:
        return "O aviso não alcança esta pessoa agora: não há documento pendente."
    motivo = selecao.pessoas[0].exclusao
    if motivo == JA_AVISADA_HOJE:
        dia = proximo_dia_do_pedido(agora)
        return (
            "Esta pessoa já foi avisada hoje nesta chamada. Um novo pedido poderá ser feito a "
            f"partir de {dia:%d/%m/%Y}."
        )
    return f"O aviso não alcança esta pessoa agora: {motivo}."


def _por_que_ninguem(selecao):
    partes = [f"{motivo}: {quantas}" for motivo, quantas in selecao.exclusoes()]
    if not partes:
        return "não há documento pendente."
    return "; ".join(partes) + "."


__all__ = [
    "COMPLEMENTADA",
    "COM_DESFECHO",
    "CORRIGIDA",
    "EXCLUSOES",
    "JA_AVISADA_HOJE",
    "LISTA_MUDOU",
    "NAO_COMUNICADA",
    "Pessoa",
    "SEM_ENDERECO",
    "SEM_PENDENCIA",
    "Selecao",
    "VENCIDA",
    "avisar_pendencias",
    "compor_texto",
    "inicio_do_dia",
    "motivo_para_nao_enviar",
    "previa",
    "proximo_dia_do_pedido",
    "selecionar",
]
