"""Registrar que uma pessoa não pode avaliar determinada inscrição — e o efeito disso.

**O impedimento acompanha a pessoa**, pela identidade institucional estável, e não o vínculo de
comissão: preso ao vínculo, ele morreria quando ela saísse e readicioná-la seria o caminho para
contorná-lo. Ele nomeia razões que não mudam por reorganização administrativa (FR-099).

**Ele age antes da cadeia de autorização, e não dentro dela.** Registrar impedimento sobre uma
Atribuição ativa a inativa no mesmo ato; a autorização continua com duas condições, porque somar
uma terceira acrescentaria uma verificação por linha a toda listagem da feature (FR-080, FR-048).

**A 012 não infere impedimento** por CPF, sobrenome ou coincidência de dado. Declarar é ato de quem
sabe (FR-042).
"""

import hashlib
from uuid import UUID

from processo_seletivo.avaliacoes.application.trilha import auditar
from processo_seletivo.avaliacoes.models import Atribuicao, Avaliacao, Impedimento
from processo_seletivo.comissoes.application import comando_de_comissao
from processo_seletivo.comissoes.models import MembroComissao
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.shared.api.problems import DomainError

IMPEDIR = "AVALIACAO_IMPEDIR"
# O ato que tira uma Avaliação do conjunto elegível tem nome próprio na trilha, e não se confunde
# com a remoção corriqueira de uma atribuição pendente (FR-092, FR-093).
TORNAR_INELEGIVEL = "AVALIACAO_TORNAR_INELEGIVEL"


def resolver_inscricao(processo, valor):
    """A inscrição, pelo **protocolo** ou pelo identificador — e a recusa é de formulário.

    Toda tela do sistema identifica a inscrição pelo protocolo: é o número que o candidato tem em
    mãos ao ligar, e é o que a trilha e a distribuição mostram. Aceitar só o UUID obrigava a
    presidência a achá-lo em outro lugar e colar — e um erro de digitação chegava ao ORM como
    `ValidationError`, virando 500 onde a pessoa deveria ler que aquilo não identifica nada.
    """
    texto = str(valor or "").strip()
    consulta = Inscricao.objects.filter(edital__processo=processo)
    try:
        inscricao = consulta.filter(pk=UUID(texto)).first()
    except (TypeError, ValueError):
        inscricao = consulta.filter(protocolo=texto).first()
    if inscricao is None:
        raise DomainError(
            "inscricao_nao_encontrada",
            "Não há inscrição com este protocolo ou identificador neste Processo.",
            422,
            campo="inscricao_id",
        )
    return inscricao


def exigir_dados(*, identity_subject, inscricao_id, motivo):
    """As três exigências do ato, verificadas **antes** da confirmação e de novo no comando.

    Antes, porque um passo de confirmação que aceita formulário incompleto transforma a validação
    em armadilha: a pessoa confirma e só então descobre que faltava o motivo. De novo no comando,
    porque a tela não é fronteira de segurança — e o comando é chamado de outros lugares.
    """
    if not (identity_subject or "").strip():
        raise DomainError(
            "identidade_obrigatoria", "Informe quem está impedido.", 422, campo="identity_subject"
        )
    if not (inscricao_id or "").strip():
        raise DomainError(
            "inscricao_obrigatoria", "Informe a inscrição.", 422, campo="inscricao_id"
        )
    if not (motivo or "").strip():
        # O motivo é o que faz do impedimento um ato, e não uma preferência (FR-039).
        raise DomainError(
            "motivo_obrigatorio",
            "O impedimento exige motivo: é ele que sustenta o ato.",
            422,
            campo="motivo",
        )


def _assinatura(ids_ativas, ids_concluidas):
    """A identidade do conjunto alcançado, e não só o seu tamanho.

    Contar não basta: entre a confirmação e o ato, uma Atribuição pode ser removida e outra
    criada, e as duas contagens continuariam iguais sobre um conjunto diferente. A conclusão de
    uma avaliação também muda o alcance sem mudar o número de atribuições — e é a diferença entre
    confirmar "nenhuma concluída" e tornar uma conclusão inelegível.
    """
    conteudo = "|".join(
        # `identificador` já é o nome da função que valida UUID neste módulo — a variável de laço
        # se chama `chave` para não sombreá-la.
        sorted(f"{chave}{'C' if chave in ids_concluidas else ''}" for chave in ids_ativas)
    )
    return hashlib.sha256(conteudo.encode()).hexdigest()[:16]


def alcance_do_impedimento(*, processo, identity_subject, inscricao_id):
    """Quantas Atribuições ativas este impedimento inativará — **antes** de ele ser confirmado.

    Retirar trabalho de alguém não pode ser efeito colateral silencioso de registrar um motivo: a
    confirmação declara o alcance, e quem confirma sabe o que está fazendo (FR-041).

    Devolve também a **assinatura** do conjunto, que o ato conferirá sob trava: confirmar um
    alcance e executar outro é a mesma falha que FR-041 existe para impedir, apenas mais difícil
    de ver.
    """
    inscricao = resolver_inscricao(processo, inscricao_id)
    ativas = list(
        Atribuicao.objects.filter(
            membro__processo=processo,
            membro__identity_subject=identity_subject,
            inscricao=inscricao,
            ativo=True,
        ).values_list("id", flat=True)
    )
    concluidas = set(
        Avaliacao.objects.filter(
            atribuicao_id__in=ativas, estado=Avaliacao.Estado.CONCLUIDA
        ).values_list("atribuicao_id", flat=True)
    )
    return {
        "atribuicoes": len(ativas),
        "concluidas": len(concluidas),
        "assinatura": _assinatura(ativas, concluidas),
        # A confirmação nomeia **quem** e **qual inscrição**: declarar o alcance sem dizer sobre
        # quem ele recai deixa a presidência confirmando um UUID que ela acabou de digitar.
        "pessoa": identity_subject,
        "inscricao": inscricao.protocolo or str(inscricao.id),
    }


def _resultados_contestados(inativadas):
    """Os Resultados cuja Avaliação fonte acabou de ser alcançada por este impedimento.

    Import local pelo motivo de sempre (013, T-001). Uma consulta para o conjunto inteiro.
    """
    from processo_seletivo.resultados.models import ResultadoEtapa

    if not inativadas:
        return []
    return [
        {
            "inscricao": resultado.inscricao.protocolo or str(resultado.inscricao_id),
            "resultado": str(resultado.id),
        }
        for resultado in ResultadoEtapa.objects.filter(
            avaliacao__atribuicao__in=[a.id for a in inativadas]
        ).select_related("inscricao")
    ]


def registrar_impedimento(
    *,
    actor,
    processo_id,
    identity_subject,
    inscricao_id,
    motivo,
    idempotency_key,
    correlation_id,
    alcance_confirmado=None,
):
    """Cria o impedimento e inativa as Atribuições ativas do par, na mesma transação.

    Devolve o **resultado declarado** do ato: quantas Atribuições foram inativadas e quantas delas
    tinham conclusão.

    As Avaliações já concluídas são **preservadas e tornadas inelegíveis** — nada nelas é apagado
    ou alterado, e elas deixam de integrar o conjunto que a 013 consome, o que libera a vaga que
    ocupavam (FR-041, FR-079, FR-090).

    **`alcance_confirmado` é a assinatura que a pessoa viu ao confirmar**, e ela é conferida
    depois da trava, contra o conjunto que o ato realmente alcançará. Sem essa conferência a
    confirmação de FR-041 declara um alcance e o ato executa outro: entre os dois passos o
    avaliador pode concluir a avaliação, e quem confirmou "nenhuma concluída" torna uma conclusão
    inelegível sem ter sido avisado. Divergiu, o ato não acontece e a confirmação é refeita.
    """
    exigir_dados(
        identity_subject=identity_subject, inscricao_id=str(inscricao_id or ""), motivo=motivo
    )
    subject = identity_subject.strip()
    texto = motivo.strip()
    with comando_de_comissao(
        actor=actor,
        processo_id=processo_id,
        operation="avaliacao:impedir",
        # O motivo entra no conteúdo da chave: sem ele, reenviar a mesma chave com outro motivo
        # seria tratado como repetição, e o ato registrado não seria o que se pediu (FR-084).
        payload={"pessoa": subject, "inscricao": str(inscricao_id), "motivo": texto},
        idempotency_key=idempotency_key,
    ) as ctx:
        inscricao = resolver_inscricao(ctx.processo, inscricao_id)
        if ctx.repetido:
            # **O desfecho original, e não um vazio.** A tela precisa dizer quantas atribuições o
            # ato inativou, e essa contagem não é reconstruível depois (FR-084, FR-097).
            return ctx.desfecho_anterior
        if not MembroComissao.objects.filter(
            processo=ctx.processo, identity_subject=subject
        ).exists():
            # Impedir quem nunca integrou esta comissão não é ato desta tela — e aceitar criaria
            # registro sobre alguém que o Processo não conhece.
            raise DomainError(
                "pessoa_fora_da_comissao",
                "Só quem integra ou integrou esta comissão pode ser declarado impedido.",
                422,
                campo="identity_subject",
            )
        impedimento, criado = Impedimento.objects.get_or_create(
            identity_subject=subject,
            inscricao=inscricao,
            defaults={"motivo": texto, "criado_em": ctx.now, "criado_por": actor.subject},
        )
        if not criado:
            raise DomainError(
                "impedimento_ja_registrado",
                "Já existe impedimento registrado entre esta pessoa e esta inscrição.",
                409,
                campo="identity_subject",
            )
        auditar(
            actor=actor,
            permissao=ctx.base.permissao,
            operation=IMPEDIR,
            # **O agregado é o próprio Impedimento**: impedir quem não tem Atribuição ativa é ato
            # legítimo — o caso preventivo — e ali não há Atribuição a que ancorar (T-016).
            aggregate=impedimento,
            now=ctx.now,
            correlation_id=correlation_id,
            reason=texto,
            idempotency_key=idempotency_key,
            com_ato_administrativo=True,
        )
        inativadas = []
        # `of=("self",)` porque a Avaliação é junção externa — o Postgres recusa `FOR UPDATE` do
        # lado anulável —, e o que precisa ser travado é a Atribuição, que é a linha que `concluir`
        # também bloqueia.
        ativas = list(
            Atribuicao.objects.select_for_update(of=("self",))
            .filter(
                membro__processo=ctx.processo,
                membro__identity_subject=subject,
                inscricao=inscricao,
                ativo=True,
            )
            .select_related("membro")
        )
        com_conclusao = set(
            Avaliacao.objects.filter(
                atribuicao__in=ativas, estado=Avaliacao.Estado.CONCLUIDA
            ).values_list("atribuicao_id", flat=True)
        )
        assinatura = _assinatura([atribuicao.id for atribuicao in ativas], com_conclusao)
        if alcance_confirmado is not None and alcance_confirmado != assinatura:
            # A trava já está posta: o conjunto conferido aqui é o que será inativado logo abaixo,
            # e nada mais entra nem sai entre uma coisa e outra.
            raise DomainError(
                "alcance_mudou",
                "O que este impedimento alcança mudou desde a confirmação. Confira o novo alcance "
                "antes de registrar.",
                409,
            )
        for atribuicao in ativas:
            Atribuicao.objects.filter(pk=atribuicao.pk).update(
                ativo=False, inativado_em=ctx.now, inativado_por=actor.subject
            )
            inativadas.append(atribuicao)
            auditar(
                actor=actor,
                permissao=ctx.base.permissao,
                operation=TORNAR_INELEGIVEL,
                aggregate=atribuicao,
                now=ctx.now,
                correlation_id=correlation_id,
                reason=texto,
                idempotency_key=idempotency_key,
                com_ato_administrativo=True,
            )
        resultado = {
            "impedimento": str(impedimento.id),
            "pessoa": subject,
            "inativadas": len(inativadas),
            "concluidas_inelegiveis": sum(
                1 for atribuicao in inativadas if atribuicao.id in com_conclusao
            ),
            # **Declaração, e não decisão** (013, FR-032). Nenhuma Atribuição foi preservada e
            # nenhum Resultado foi alterado: o impedimento se aplica por inteiro, porque a cadeia
            # de autorização não pergunta por ele — ela depende de ele ter inativado a Atribuição.
            # Preservá-la para proteger a proveniência deixaria a pessoa recém-declarada impedida
            # com acesso mantido à inscrição e aos documentos dela.
            #
            # O que sobra é dizer o que ficou contestado, para que quem consulta o Resultado saiba
            # que a origem dele foi questionada depois de consolidada.
            "resultados_contestados": _resultados_contestados(inativadas),
        }
        ctx.concluir_sem_resultado(201, resultado)
        return resultado
