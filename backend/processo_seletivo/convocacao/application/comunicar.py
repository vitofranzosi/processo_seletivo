"""A emissão da comunicação da convocação, na forma que o Edital declarou (019, `D-009`).

**Este módulo é a terceira situação em que o sistema envia mensagem**, e a única que não é recibo
de ato praticado pela própria pessoa. A `FR-084` da `010` dizia que havia exatamente duas e que
acrescentar uma terceira **exige revisar a regra**; a revisão está escrita em
`specs/010-area-do-candidato/spec.md`, datada de 2026-09-12, e é a `REVISAO_DA_FR_084` abaixo que a
declara aqui.

**A guarda é de implantação, e não de domínio** (`FR-289`). Não é regra do certame: é recusa de
subir com duas normas contraditórias vigentes no mesmo repositório. Por isso o código dela está
separado dos demais no contrato, e por isso ela alcança só a mensagem individual — a convocação por
publicação não passa por caixa de entrada nenhuma.
"""

import logging

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from processo_seletivo.avaliacoes.application.trilha import auditar
from processo_seletivo.classificacao.domain.universo import por_identidade
from processo_seletivo.comissoes.application import comando_de_comissao
from processo_seletivo.comissoes.application.comissao import identificador
from processo_seletivo.convocacao.domain import nomes, prazo
from processo_seletivo.convocacao.models import ComunicacaoEmitida, Convocacao
from processo_seletivo.publicacoes.domain.vocabulario_da_regra import (
    FORMA_POR_MENSAGEM_INDIVIDUAL,
    FORMA_POR_PUBLICACAO,
    FORMAS_DE_CONVOCACAO,
)
from processo_seletivo.shared.api.problems import DomainError

logger = logging.getLogger("processo_seletivo.convocacao")

COMUNICAR = "CONVOCACAO_COMUNICAR"
ATO = "convocacao:comunicar"

ASSUNTO = "Convocação — {edital}"

# **O mínimo necessário** (`FR-290`): o que fazer, até quando, e por onde falar com a instituição.
# Sem CPF, sem telefone, sem pontuação e sem posição na ordem — dados que não ajudam quem lê e
# viajam para onde a mensagem for encaminhada.
#
# **E sem afirmar direito à vaga** (`FR-292c`): a convocação chama para cumprir uma etapa, e o que
# decide a vaga é o que a pessoa fizer dentro do prazo.
CORPO = """Você foi convocada(o) no {edital}.

{prazo}

O que fazer: acesse a sua área e siga as instruções da convocação em
{endereco}

Em caso de dúvida, fale com {atendimento}.

Cefor/Ifes — Seleções
Esta mensagem é automática; não responda.
"""

COM_PRAZO = "Prazo para atender: até {vencimento}, contado do envio desta mensagem."
SEM_PRAZO = "O prazo para atender é o que o Edital publica."

#: A data da revisão escrita da `FR-084` da `010`, declarada aqui e conferida contra a spec por
#: `tests/test_situacoes_de_mensagem.py`.
#:
#: **Constante, e não leitura da spec em tempo de execução.** Ler `specs/` daqui acoplaria o envio
#: a uma árvore que o contêiner de produção não carrega — e a convocação passaria a falhar por
#: ausência de arquivo de documentação, que é uma falha pior do que a que a guarda existe para
#: impedir. A contradição entre norma e código é achada onde ela pertence: na suíte, que lê as duas.
#:
#: `None` desliga a terceira situação, e é o valor correto enquanto a revisão não estiver escrita.
REVISAO_DA_FR_084 = "2026-09-12"


def guarda_da_revisao_da_010():
    """Recusa a mensagem individual enquanto a `FR-084` da `010` não estiver revisada (`FR-289`).

    A `R-008` fez da revisão uma **fase própria**, anterior a qualquer envio individual, e não uma
    exceção silenciosa dentro desta feature. Implementar o envio sem ela deixaria duas regras
    vigentes e contraditórias no mesmo repositório — e a que o candidato leria seria a errada.
    """
    if not REVISAO_DA_FR_084:
        raise DomainError(
            nomes.ENVIO_SEM_REVISAO_DA_010,
            "A mensagem individual de convocação depende da revisão escrita da FR-084 da 010, "
            "que ainda não foi feita: enquanto ela não existir, o sistema não envia.",
            409,
        )


def forma_declarada(convocacao):
    """A forma que o Perfil publicado declarou, lida da **versão que a convocação citou**.

    **Da versão citada, e não da vigente.** A convocação congelou a norma que valia quando foi
    praticada; uma Retificação posterior não pode mudar por qual canal aquela chamada foi feita.

    `None` significa *"este Edital não declarou forma"*, e nunca a publicação por omissão: as duas
    formas da amostra são normais, e escolher uma decidiria norma no lugar do Edital.
    """
    perfil = por_identidade((convocacao.versao.content or {}).get("profiles"), convocacao.perfil_id)
    forma = (perfil or {}).get("callForm")
    return forma if forma in FORMAS_DE_CONVOCACAO else None


def destinatario_de(convocacao):
    """Para onde a mensagem individual vai: a credencial principal, ou o endereço da Inscrição.

    **A credencial vem primeiro porque ela é provada.** O endereço gravado na Inscrição é indício
    histórico — a `010` o diz com todas as letras —, e a pessoa pode ter trocado de caixa desde
    então. Ele continua sendo a saída quando não há credencial, que é o caso de quem se inscreveu
    antes de o portal existir.
    """
    from processo_seletivo.identidade.models import CandidateEmail

    credencial = (
        CandidateEmail.objects.filter(
            identidade__subject=convocacao.inscricao.identity_subject, principal=True
        )
        .values_list("email_canonico", flat=True)
        .first()
    )
    return credencial or convocacao.inscricao.email or ""


def comunicar(
    *,
    actor,
    processo_id,
    convocacao_id,
    idempotency_key,
    correlation_id,
    endereco_do_portal="",
    referencia_da_publicacao="",
):
    """Emite a comunicação na forma declarada, e registra o que aconteceu — inclusive a falha.

    **A falha não apaga o ato** (`FR-269a`). A convocação continua praticada; o que se registra é
    que a emissão não completou, e o recorte passa a exibir *"convocado, prazo não iniciado"* até
    que uma emissão tenha sucesso. Sem isso, uma queda de SMTP ficaria indistinguível do silêncio
    da pessoa — e o desfecho que decorre de silêncio é perda de vaga.

    **O envio acontece fora da transação, e nunca dentro dela.** É a regra que
    `inscricoes/application/mensagem.py` escreve com todas as letras, e a razão aqui é a mesma
    aumentada de um grau: `comando_de_comissao` trava o Processo com `select_for_update`, de modo
    que um SMTP lento paralisaria **todos** os comandos daquele certame — e um `rollback` posterior
    desfaria o registro sem desfazer a mensagem, deixando na caixa da pessoa uma convocação que o
    sistema esqueceu de ter enviado.

    A ordem é a que `exigir_base_de_comissao` existe para permitir: autorizar, ir à rede, e só
    então abrir a transação que grava e audita.
    """
    from processo_seletivo.comissoes.application import exigir_base_de_comissao

    # **Autorizar antes de trabalhar** (Princípio III): sem isto, um ator sem base faria o sistema
    # ir à rede e entregar a mensagem antes de a pergunta "quem está pedindo" ser feita.
    exigir_base_de_comissao(actor=actor, processo_id=processo_id)
    convocacao = _convocacao_do_processo_id(processo_id, convocacao_id, actor=actor)
    forma = forma_declarada(convocacao)
    if forma is None:
        raise DomainError(
            nomes.FORMA_DE_COMUNICACAO_NAO_DECLARADA,
            "O Perfil publicado não declarou como este Edital comunica a convocação: declare "
            "a forma por Retificação antes de emitir.",
            409,
        )
    agora = timezone.now()
    _recusar_vencimento_anterior_ao_envio(convocacao, agora=agora)

    referencia = (referencia_da_publicacao or "").strip()
    destinatario, detalhe = "", ""
    if forma == FORMA_POR_MENSAGEM_INDIVIDUAL:
        guarda_da_revisao_da_010()
        destinatario = destinatario_de(convocacao)
        detalhe = _enviar(
            convocacao, destinatario=destinatario, endereco_do_portal=endereco_do_portal
        )
    elif not referencia:
        # **O sistema não publica no site do certame**, e registrar `ENVIADA` sem referência
        # iniciaria o prazo de uma convocação que ninguém viu (`FR-288`).
        raise DomainError(
            nomes.REFERENCIA_DA_PUBLICACAO_OBRIGATORIA,
            "Este Edital comunica a convocação por publicação: declare onde ela foi publicada — "
            "o endereço e a data —, porque o prazo corre a partir disso e o sistema não publica "
            "por conta própria.",
            422,
            campo="referencia_da_publicacao",
        )

    with comando_de_comissao(
        actor=actor,
        processo_id=processo_id,
        operation=ATO,
        payload={"convocacao": str(convocacao_id)},
        idempotency_key=idempotency_key,
    ) as ctx:
        if ctx.repetido:
            return ctx.desfecho_anterior
        emitida = ComunicacaoEmitida(
            convocacao=convocacao,
            forma=forma,
            destinatario=destinatario,
            referencia_da_publicacao=referencia if forma == FORMA_POR_PUBLICACAO else "",
            # **`FALHA` não tem instante, e a constraint o exige.** Um registro marcado enviado sem
            # instante faria o prazo correr a partir de nada.
            enviado_em=None if detalhe else agora,
            resultado="FALHA" if detalhe else "ENVIADA",
            detalhe_tecnico=detalhe,
        )
        emitida.save()
        return _concluir(ctx, emitida, actor, correlation_id, idempotency_key)


def _convocacao_do_processo_id(processo_id, convocacao_id, *, actor):
    """A convocação, conferida contra o Processo **antes** de a transação abrir.

    A conferência de autoridade já aconteceu em `exigir_base_de_comissao`; esta confere que a
    convocação pertence ao Processo autorizado — e recusa como não encontrada, pela mesma razão de
    sempre: dizer *"existe, mas não é sua"* já entregaria que existe.
    """
    convocacao = (
        Convocacao.objects.filter(
            id=identificador(convocacao_id), edital__processo_id=identificador(processo_id)
        )
        .select_related("edital", "versao", "inscricao")
        .first()
    )
    if convocacao is None:
        raise DomainError("convocacao_nao_encontrada", "Convocação não encontrada.", 404)
    return convocacao


def _recusar_vencimento_anterior_ao_envio(convocacao, *, agora):
    """`FR-269b`, `vencimento_anterior_ao_envio`: prazo que vence antes de a pessoa poder saber.

    **A conferência é aqui, e não ao convocar**, porque é o envio que inicia o relógio: no instante
    da convocação ainda não existe envio com que comparar. Um vencimento informado com o ano errado
    só se revela quando a mensagem vai partir — e é aí que a recusa precisa acontecer, antes de a
    pessoa receber um prazo já vencido.
    """
    if prazo.vencimento_precede_o_envio(vencimento=convocacao.vencimento, enviado_em=agora):
        raise DomainError(
            nomes.VENCIMENTO_ANTERIOR_AO_ENVIO,
            "O vencimento informado nesta convocação é anterior ao envio: corrija a convocação, "
            "sucedendo-a com motivo, antes de comunicar.",
            409,
        )


def _enviar(convocacao, *, destinatario, endereco_do_portal):
    """Põe a mensagem na fila e devolve o detalhe técnico da falha, ou `""` no sucesso.

    **Sem dado pessoal no detalhe técnico**: ele vai para o registro e para a tela de quem conduz o
    certame, e o endereço de alguém não tem por que estar em nenhum dos dois.
    """
    if not destinatario:
        return "sem endereço de destino para esta Inscrição"
    return enviar_mensagem_de_convocacao(
        para=destinatario,
        dados={
            "edital": f"Edital {convocacao.edital.number}/{convocacao.edital.year}",
            "vencimento": convocacao.vencimento,
            "endereco": endereco_do_portal,
            "atendimento": getattr(settings, "PORTAL_ATENDIMENTO", "") or "a comissão do certame",
        },
    )


def enviar_mensagem_de_convocacao(*, para, dados):
    """A terceira situação em que o sistema envia mensagem (`FR-084` da `010`, revisada).

    **Nada da inscrição além do necessário para identificar a chamada** (`FR-290`): o Edital, o
    prazo e o canal de atendimento. Nem CPF, nem telefone, nem pontuação, nem posição na ordem.

    **Nenhum link que autentica** (P-001 da `010`): a mensagem manda a pessoa à área dela, e a
    entrada continua sendo por código digitado.
    """
    corpo = CORPO.format(
        edital=dados["edital"],
        prazo=(
            COM_PRAZO.format(
                # **No fuso da instalação, e não em UTC.** `strftime` sobre um instante ciente
                # formata no fuso que ele carrega: um vencimento gravado às 17:00 UTC saía
                # como "17:00" numa mensagem lida em São Paulo, onde ele vence às 14:00 — três
                # horas a mais de prazo que a pessoa não tem.
                vencimento=timezone.localtime(dados["vencimento"]).strftime("%d/%m/%Y às %H:%M")
            )
            if dados.get("vencimento")
            else SEM_PRAZO
        ),
        endereco=dados["endereco"] or "a área do candidato, no endereço do certame",
        atendimento=dados["atendimento"],
    )
    try:
        # **O retorno é contado**, e não descartado: `send_mail` devolve quantas mensagens entraram
        # na fila, e um backend que engole a mensagem devolve `0` sem levantar exceção nenhuma.
        # Ignorá-lo gravava `ENVIADA` e iniciava o prazo de uma convocação que não saiu — a falha
        # mais silenciosa possível, porque tudo indica sucesso.
        entregues = send_mail(
            subject=ASSUNTO.format(edital=dados["edital"]),
            message=corpo,
            from_email=settings.DEFAULT_FROM_EMAIL or None,
            recipient_list=[para],
            fail_silently=False,
        )
    except Exception as erro:
        # Sem o endereço: o registro técnico diz que falhou e qual foi o erro, e nada além disso.
        logger.exception("Falha ao emitir a comunicação de convocação.")
        return f"{type(erro).__name__}: falha na emissão"
    if not entregues:
        logger.error("A comunicação de convocação não foi aceita pelo servidor de correio.")
        return "o servidor de correio não aceitou a mensagem"
    return ""


def _concluir(ctx, emitida, actor, correlation_id, idempotency_key):
    convocacao = emitida.convocacao
    auditar(
        actor=actor,
        permissao=ctx.base.permissao,
        operation=COMUNICAR,
        aggregate=emitida,
        now=ctx.now,
        correlation_id=correlation_id,
        # **"Enviada em", e nunca "recebida em"** (`UX-039`, `FR-288a`). A trilha diz o que o
        # sistema fez; o que aconteceu na caixa de entrada da pessoa ele não sabe, e não afirma.
        reason=(
            f"Comunicação {emitida.resultado} da convocação {convocacao.id}, inscrição "
            f"{convocacao.inscricao_id}, na forma {emitida.forma}."
            + (f" Enviada em {emitida.enviado_em.isoformat()}." if emitida.enviado_em else "")
            + (f" Detalhe técnico: {emitida.detalhe_tecnico}" if emitida.detalhe_tecnico else "")
        ),
        idempotency_key=idempotency_key,
    )
    declarado = {
        "id": str(emitida.id),
        "convocacao": str(convocacao.id),
        "forma": emitida.forma,
        "resultado": emitida.resultado,
        "enviadaEm": emitida.enviado_em.isoformat() if emitida.enviado_em else None,
    }
    ctx.concluir_sem_resultado(201, declarado)
    return declarado


__all__ = [
    "REVISAO_DA_FR_084",
    "comunicar",
    "destinatario_de",
    "enviar_mensagem_de_convocacao",
    "forma_declarada",
    "guarda_da_revisao_da_010",
]
